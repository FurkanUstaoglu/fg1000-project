"""
BALON ALGILAMA SİSTEMİ
Kırmızı balonları (düşman) algılar ve stabil şekilde ekranda gösterir
Özellikler:
- Git-gel sorunu çözüldü (3 kare üst üste algılama)
- Hareket ortalaması ile stabil pozisyon
- Işık yansıması toleransı
- Ten rengi engelleme
- Yakın ve uzak mesafe desteği
"""

import cv2
import numpy as np
import datetime
import math
from collections import deque

# =====================================================
# 1. KONFIGÜRASYON PARAMETRELERİ (AYARLAR)
# =====================================================

# --- HSV RENK ARALIKLARI (KIRMIZI - DÜŞMAN) ---
# Not: Kırmızı HSV'de iki aralıkta bulunur: 0-10 ve 160-179

# 1. ARALIK: Koyu kırmızıdan turuncuya (0-10 arası)
# Varsayılanlar: kullanıcı tarafından iletilen stabil değerler
LOWER_RED1 = np.array([0, 255, 200])        # [Hue, Saturation, Value] minimum (R H MIN 0, R S MIN 255, R V MIN 200)
UPPER_RED1 = np.array([5, 255, 255])     # maksimum

# 2. ARALIK: Morumsu kırmızı (160-179 arası)
LOWER_RED2 = np.array([160, 80, 40])      # minimum
UPPER_RED2 = np.array([179, 255, 255])    # maksimum

# --- BOYUT AYARLARI (piksel cinsinden) ---
MIN_AREA = 1500       # Minimum balon alanı (uzaktaki çok küçük balonlar için) - kullanıcı isteği
MAX_AREA = 200000     # Maksimum balon alanı (yakındaki büyük balonlar)

# --- ŞEKİL AYARLARI ---
CIRCULARITY_THRESH = 0.50   # Yuvarlaklık eşiği (daha esnek algılama için)

# --- KARARLILIK (GİT-GEL ÇÖZÜMÜ) ---
STABLE_FRAMES_NEEDED = 3    # Kaç kare üst üste algılanırsa gösterilsin
MEMORY_SIZE = 10            # Kaç karelik hafıza tutulsun

# --- GÖRÜNTÜ İŞLEME ---
BLUR_KERNEL = (5, 5)        # Bulanıklaştırma boyutu (tek sayı olmalı)
MORPH_KERNEL = (3, 3)       # Morfolojik işlem kernel boyutu

# --- KAMERA SEÇİMİ ---
MAX_CAMERA_INDEX = 3        # Denenecek maksimum kamera indeksi

# --- HSV RENK ARALIKLARI (YEŞİL - DOST) ---
# Kullanıcının verdiği varsayılanlar (güncellendi)
LOWER_GREEN = np.array([25, 70, 70])     # Yeşil tonlarının başlangıcı (G H Min 25, G S Min 70, G V Min 70)
UPPER_GREEN = np.array([70, 255, 255])    # Yeşil tonlarının sonu (G H Max 70)

# =====================================================
# 2. YARDIMCI FONKSİYONLAR
# =====================================================

def circularity(contour):
    """
    Bir konturun ne kadar yuvarlak olduğunu hesaplar.
    
    Formül: 4 × π × Alan / (Çevre²)
    - Tam daire için = 1.0
    - Elips için ≈ 0.7
    - Dikdörtgen için ≈ 0.5
    - Üçgen için ≈ 0.4
    
    Parametreler:
        contour: OpenCV kontur nesnesi
    
    Dönüş:
        float: Yuvarlaklık değeri (0-1 arası)
    """
    # Konturun alanını hesapla (piksel cinsinden)
    area = cv2.contourArea(contour)
    
    # Konturun çevre uzunluğunu hesapla
    perimeter = cv2.arcLength(contour, True)  # True = kontur kapalı
    
    # Sıfıra bölünmeyi engelle
    if perimeter == 0:
        return 0.0
    
    # Yuvarlaklık formülü
    return 4 * math.pi * area / (perimeter * perimeter)


def get_center(contour):
    """
    Bir konturun merkez noktasını bulur.
    
    Parametreler:
        contour: OpenCV kontur nesnesi
    
    Dönüş:
        tuple: (x, y) merkez koordinatları
    """
    # Konturu çevreleyen dikdörtgeni bul
    x, y, w, h = cv2.boundingRect(contour)
    
    # Dikdörtgenin merkezini hesapla
    center_x = x + w // 2
    center_y = y + h // 2
    
    return (center_x, center_y)


def apply_morphology(mask):
    """
    Maskeye morfolojik işlemler uygular.
    - Kapatma (CLOSE): Küçük delikleri doldurur (yansıma sorunu çözümü)
    - Erosion: İki balonu ayırmak için
    - Açma (OPEN): Küçük gürültüleri temizler
    """
    kernel = np.ones(MORPH_KERNEL, np.uint8)
    
    # Kapatma: Boşlukları doldur
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # İki balonu ayırmak için hafif erosion (1 iterasyon)
    # Bu adım iki bitişik balonu ayırmaya yardımcı olur
    mask = cv2.erode(mask, kernel, iterations=1)
    
    # Açma: Gürültüyü temizle (1 iterasyon olarak azalt)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Genişletme: Erosion'dan kaybolan pikselleri geri getir
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    # Bulanıklaştırma ve threshold
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    return mask


def split_adjacent_balloons(mask, min_area):
    """
    Yan yana duran balonları ayırmaya çalışır.
    Büyük birleşik bileşenleri distance transform ve watershed ile parçalara böler.
    """
    if mask is None or mask.size == 0:
        return mask

    output = np.zeros_like(mask)
    num_labels, labels = cv2.connectedComponents(mask)

    for label in range(1, num_labels):
        component = np.uint8(labels == label) * 255
        area = cv2.countNonZero(component)

        if area < min_area * 1.5:
            output = cv2.bitwise_or(output, component)
            continue

        dist = cv2.distanceTransform(component, cv2.DIST_L2, 5)
        _, max_val, _, _ = cv2.minMaxLoc(dist)
        if max_val < 10:
            output = cv2.bitwise_or(output, component)
            continue

        _, sure_fg = cv2.threshold(dist, max_val * 0.45, 255, cv2.THRESH_BINARY)
        sure_fg = np.uint8(sure_fg)
        num_peaks, peak_labels = cv2.connectedComponents(sure_fg)

        if num_peaks <= 2:
            output = cv2.bitwise_or(output, component)
            continue

        markers = np.int32(peak_labels)
        markers[component == 0] = 0
        cv2.watershed(cv2.cvtColor(component, cv2.COLOR_GRAY2BGR), markers)

        any_split = False
        for m in range(1, num_peaks):
            part = np.uint8(markers == m) * 255
            if cv2.countNonZero(part) >= min_area:
                part = cv2.morphologyEx(part, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=1)
                output = cv2.bitwise_or(output, part)
                any_split = True

        if not any_split:
            output = cv2.bitwise_or(output, component)

    return output


def filter_oversized_components(mask, max_area):
    """
    Çok büyük sahne bileşenlerini kaldırır.
    Tam ekran veya neredeyse tam ekran beyaz maskeleri azaltmak için kullanılır.
    """
    if mask is None or mask.size == 0:
        return mask

    ref = np.zeros_like(mask)
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) <= max_area:
            cv2.drawContours(ref, [cnt], -1, 255, -1)
    return ref if cv2.countNonZero(ref) > 0 else mask


def normalize_hsv_v(hsv):
    """
    HSV görüntüsündeki V kanalını CLAHE ile iyileştirir.
    Bu sayede gölge ve parlama etkileri daha dengeli hale gelir.
    """
    h, s, v = cv2.split(hsv)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    v = clahe.apply(v)
    return cv2.merge([h, s, v])


def enclosing_circle_ratio(contour):
    area = cv2.contourArea(contour)
    if area == 0:
        return 0.0
    (_, _), radius = cv2.minEnclosingCircle(contour)
    if radius == 0:
        return 0.0
    circle_area = math.pi * radius * radius
    return area / circle_area


def mean_hsv_in_contour(contour, hsv):
    """Konturun içindeki ortalama H,S,V değerlerini döndürür."""
    mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean = cv2.mean(hsv, mask=mask)
    # mean -> (h, s, v, a)
    return int(mean[0]), int(mean[1]), int(mean[2])


def contour_solidity(contour):
    area = cv2.contourArea(contour)
    if area == 0:
        return 0.0
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    if hull_area == 0:
        return 0.0
    return area / hull_area


def open_camera_prefer_external():
    """
    Harici kameralar (USB) varsa onu ilk açar, yoksa laptop kamerasını açar.
    Tüm kameraları test eder ve gerçekten çalışan olanlardan seçim yapar.
    Depth kameralarını (açılıyor ama frame almayan) atlayıp çalışan normal kamerayı tercih eder.
    """
    print("🔎 Tüm kameralar aranıyor ve test ediliyor...")
    working_external_cameras = []
    working_internal_cameras = []
    
    # Tüm potansiyel kamera indekslerini kontrol et (0'dan MAX_CAMERA_INDEX'e)
    for index in range(MAX_CAMERA_INDEX + 1):
        try:
            print(f"   Kamera {index} test ediliyor...", end=" ")
            
            # Farklı backend'lerle deneme
            cap = None
            for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2]:
                try:
                    cap = cv2.VideoCapture(index, backend)
                    if cap.isOpened():
                        break
                except:
                    pass
            
            # Eğer backend başarısız olursa default backend'i dene
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(index)
            
            if cap.isOpened():
                # Kameranın gerçekten çalışıp çalışmadığını kontrol et
                # (frame alabiliyorsa)
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    camera_type = "HARICI (USB)" if index != 0 else "DAHILI (Laptop)"
                    frame_info = f"{frame.shape[1]}x{frame.shape[0]}"
                    print(f"✅ ÇALIŞIYOR [{camera_type}] - {frame_info}")
                    
                    if index != 0:
                        working_external_cameras.append(index)
                    else:
                        working_internal_cameras.append(index)
                else:
                    print(f"❌ (Frame almıyor - Depth kamera olabilir)")
                cap.release()
            else:
                print(f"❌ (Açılamıyor)")
        except Exception as e:
            print(f"❌ (Hata: {e})")
    
    if not working_external_cameras and not working_internal_cameras:
        print("\n" + "=" * 60)
        print("❌ HATA: Hiçbir çalışan kamera bulunamadı!")
        print("=" * 60)
        print("\n🔧 ÇÖZÜM ÖNERILERI:")
        print("  1. Kamera sürücülerini kontrol edin")
        print("  2. USB kamerayı bilgisayardan çıkarıp tekrar takın")
        print("  3. Cihaz Yöneticisi'nde kameraları kontrol edin")
        print("  4. Windows'u yeniden başlatın")
        print("=" * 60 + "\n")
        return None, None
    
    # Harici kamera varsa ondan seç (en yüksek indeks = en son taklı = tercih edilen)
    if working_external_cameras:
        chosen_index = max(working_external_cameras)  # En yüksek indeksi seç
        camera_type = "HARICI (USB)"
    else:
        chosen_index = working_internal_cameras[0]
        camera_type = "DAHILI (Laptop)"
    
    print(f"\n📱 ÖZET:")
    print(f"   ✓ Çalışan harici kameralar: {sorted(working_external_cameras) if working_external_cameras else 'Yok'}")
    print(f"   ✓ Çalışan dahili kameralar: {sorted(working_internal_cameras) if working_internal_cameras else 'Yok'}")
    print(f"   🎯 Seçilen: İndeks {chosen_index} ({camera_type})")
    
    # Seçilen kamerayu aç ve test et
    cap = None
    try:
        # Farklı backend'lerle deneme
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2]:
            try:
                cap = cv2.VideoCapture(chosen_index, backend)
                if cap.isOpened():
                    break
            except:
                pass
        
        # Backend başarısız olursa
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(chosen_index)
    except Exception as e:
        print(f"❌ Backend seçim hatası: {e}")
        cap = cv2.VideoCapture(chosen_index)
    
    if cap.isOpened():
        ret, test_frame = cap.read()
        if ret and test_frame is not None:
            print(f"\n✅ Kamera {chosen_index} başarıyla açıldı ve test edildi.\n")
            return cap, chosen_index
        else:
            print(f"❌ Kamera {chosen_index} açıldı ama frame alamıyor!")
            cap.release()
            return None, None
    else:
        print(f"❌ Kamera {chosen_index} açılamadı!")
        return None, None


def skin_mask(frame):
    """
    Cilt tonlarını algılar ve kırmızı maskeden çıkarır.
    """
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    lower_skin = np.array([0, 133, 77], np.uint8)
    upper_skin = np.array([255, 173, 127], np.uint8)
    mask = cv2.inRange(ycrcb, lower_skin, upper_skin)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    return apply_morphology(mask)


def is_valid_contour(contour, min_area, max_area, circ_thresh):
    """
    Bir konturun balon olarak kabul edilip edilmediğini kontrol eder.
    """
    area = cv2.contourArea(contour)
    if area < min_area or area > max_area:
        return False

    x, y, w, h = cv2.boundingRect(contour)
    if w == 0 or h == 0:
        return False

    rect_area = w * h
    extent = area / rect_area if rect_area else 0
    # Extent kontrolü daha gevşek: 0.30 -> 0.25
    if extent < 0.25:
        return False

    circ = circularity(contour)
    circle_ratio = enclosing_circle_ratio(contour)
    solidity = contour_solidity(contour)
    
    # DAHA GEVŞEK KONTROL:
    # circ_thresh kontrol yerine 0.45 minimum (daire benzerlikleri artmış)
    # circle_ratio >= 0.58 -> 0.50 ve solidity >= 0.72 -> 0.60
    return circ >= max(0.45, circ_thresh - 0.10) or (circle_ratio >= 0.50 and solidity >= 0.60)


def select_best_contour(contours, min_area, max_area, circ_thresh):
    """
    Geçerli konturlar arasından en uygun balonu seçer.
    """
    best_contour = None
    best_area = 0
    for cnt in contours:
        if not is_valid_contour(cnt, min_area, max_area, circ_thresh):
            continue
        area = cv2.contourArea(cnt)
        if area > best_area:
            best_area = area
            best_contour = cnt
    return best_contour


def select_best_contour_for_color(contours, min_area, max_area, circ_thresh, color='red'):
    """
    Kontur seçiminde renk bazlı farklılaştırma uygular.
    Kırmızı için daha gevşek yuvarlaklık/solidity kontrolü uygula (algılama esnekliği).
    """
    best = None
    best_area = 0
    for cnt in contours:
        # renk özel kontur doğrulaması
        if color == 'red':
            # kırmızıda DAHA TOLERANLI kontur kabulü
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            if w == 0 or h == 0:
                continue
            
            # Daha düşük yuvarlaklık eşiği
            circ = circularity(cnt)
            circle_ratio = enclosing_circle_ratio(cnt)
            solidity = contour_solidity(cnt)
            
            # DAHA GEVŞEK KONTROL:
            # circ_thresh - 0.15 yerine - 0.25 (daha esnek)
            # solidity >= 0.60 yerine >= 0.50 (daha esnek)
            min_circ = max(0.30, circ_thresh - 0.25)  # 0.35 -> 0.30 ve 0.25 sapma
            min_circle_ratio = 0.45  # 0.50 -> 0.45
            min_solidity = 0.45  # 0.60 -> 0.45
            
            if circ < min_circ and not (circle_ratio >= min_circle_ratio and solidity >= min_solidity):
                continue
            
            if area > best_area:
                best_area = area
                best = cnt
        else:
            # varsayılan seçim (ör. yeşil)
            if not is_valid_contour(cnt, min_area, max_area, circ_thresh):
                continue
            area = cv2.contourArea(cnt)
            if area > best_area:
                best_area = area
                best = cnt
    return best


def is_same_balloon(prev_center, curr_center, max_distance=50):
    """
    İki algılamanın aynı balona ait olup olmadığını kontrol eder.
    
    Parametreler:
        prev_center: Önceki algılamanın merkezi (x, y)
        curr_center: Şimdiki algılamanın merkezi (x, y)
        max_distance: Maksimum mesafe (piksel)
    
    Dönüş:
        bool: Aynı balon ise True
    """
    if prev_center is None or curr_center is None:
        return False
    
    # Öklid mesafesini hesapla
    distance = math.sqrt((prev_center[0] - curr_center[0])**2 + 
                         (prev_center[1] - curr_center[1])**2)
    
    return distance < max_distance


# =====================================================
# 3. BALON TRACKER SINIFI (Git-gel çözümü)
# =====================================================

class BalloonTracker:
    """
    Balon algılamasını kararlı hale getiren sınıf.
    
    Nasıl çalışır?
    1. Her karede algılama durumunu kaydeder
    2. STABLE_FRAMES_NEEDED kadar üst üste algılanırsa "kararlı" sayar
    3. Algılanmazsa sayacı düşürür
    4. Pozisyonların hareket ortalamasını alır (daha stabil görüntü)
    """
    
    def __init__(self):
        # Algılama sayacı (kaç kare üst üste algılandı)
        self.detection_counter = 0
        
        # Önceki merkez noktası (hareket ortalaması için)
        self.prev_center = None
        
        # Son pozisyonların hafızası (son MEMORY_SIZE kare)
        self.position_history = deque(maxlen=MEMORY_SIZE)
        self.lost_frames = 0
        
        # Şu an kararlı mı?
        self.is_stable = False
    
    def update(self, detected, current_center=None, stable_needed=STABLE_FRAMES_NEEDED):
        """
        Her karede çağrılır. Algılama durumunu günceller.
        
        Parametreler:
            detected: Bu karede balon algılandı mı? (bool)
            current_center: Algılanan balonun merkezi (x, y)
            stable_needed: Kaç kare üst üste algılanırsa kararlı sayılacağı
        
        Dönüş:
            bool: Şu an kararlı algılama var mı?
            tuple: Stabil merkez noktası (x, y)
        """
        
        # === 1. ALGILAMA SAYACINI GÜNCELLE ===
        if detected:
            self.detection_counter = min(self.detection_counter + 1, MEMORY_SIZE)
            self.lost_frames = 0
        else:
            self.detection_counter = max(self.detection_counter - 1, 0)
            self.lost_frames += 1
        
        # === 2. KARARLILIK KONTROLÜ ===
        self.is_stable = self.detection_counter >= stable_needed
        
        # === 3. POZİSYON HAFIZASI ===
        if detected and current_center is not None:
            self.position_history.append(current_center)
        
        # === 4. HAREKET ORTALAMASI (STABİL POZİSYON) ===
        stable_center = None
        
        if len(self.position_history) > 0:
            avg_x = int(sum(p[0] for p in self.position_history) / len(self.position_history))
            avg_y = int(sum(p[1] for p in self.position_history) / len(self.position_history))
            running_center = (avg_x, avg_y)

            if self.prev_center is not None:
                running_center = (
                    int(self.prev_center[0] * 0.65 + running_center[0] * 0.35),
                    int(self.prev_center[1] * 0.65 + running_center[1] * 0.35)
                )
            
            if self.is_stable:
                stable_center = running_center
                self.prev_center = running_center
            elif detected:
                stable_center = running_center
                self.prev_center = running_center
        elif self.prev_center is not None and self.lost_frames <= 3:
            stable_center = self.prev_center
        
        return self.is_stable, stable_center


# =====================================================
# 4. ANA PROGRAM
# =====================================================

def main():
    """
    Ana program:
    1. Kamerayı açar
    2. Her karede görüntüyü işler
    3. Kırmızı balonları tespit eder
    4. Kararlı algılamayı ekranda gösterir
    """
    
    print("=" * 50)
    print("BALON ALGILAMA SİSTEMİ BAŞLATILIYOR...")
    print("=" * 50)
    print(f"Minimum balon boyutu: {MIN_AREA} piksel")
    print(f"Maksimum balon boyutu: {MAX_AREA} piksel")
    print(f"Yuvarlaklık eşiği: {CIRCULARITY_THRESH}")
    print(f"Kararlılık için gereken kare: {STABLE_FRAMES_NEEDED}")
    print("=" * 50)
    print("KONTROLLER:")
    print("  ESC → Çıkış")
    print("  s → Ayarları kaydet")
    print("  r → Trackbar'ları sıfırla")
    print("=" * 50)
    
    # === KAMERAYI AÇ ===
    cap, cam_index = open_camera_prefer_external()
    if cap is None:
        print("❌ HATA: Hiçbir kamera açılamadı!")
        return
    print(f"📷 Kullanılan kamera indeksi: {cam_index}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # === TRACKER OLUŞTUR ===
    tracker = BalloonTracker()
    # Mask stabilizasyonu için küçük zaman penceresi
    from collections import deque as _dq
    mask_history = _dq(maxlen=3)
    
    # === TRACKBAR'LAR (CANLI AYAR İÇİN) ===
    cv2.namedWindow("Balon Algilama", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Balon Algilama", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow("Balon Algilama", 720, 720)
    
    # HSV ayarları için trackbar'lar
    cv2.createTrackbar("R H Min", "Balon Algilama", LOWER_RED1[0], 179, lambda x: None)
    cv2.createTrackbar("R H Max", "Balon Algilama", UPPER_RED1[0], 179, lambda x: None)
    cv2.createTrackbar("R S Min", "Balon Algilama", LOWER_RED1[1], 255, lambda x: None)
    cv2.createTrackbar("R V Min", "Balon Algilama", LOWER_RED1[2], 255, lambda x: None)
    cv2.createTrackbar("G H Min", "Balon Algilama", LOWER_GREEN[0], 179, lambda x: None)
    cv2.createTrackbar("G H Max", "Balon Algilama", UPPER_GREEN[0], 179, lambda x: None)
    cv2.createTrackbar("G S Min", "Balon Algilama", LOWER_GREEN[1], 255, lambda x: None)
    cv2.createTrackbar("G V Min", "Balon Algilama", LOWER_GREEN[2], 255, lambda x: None)
    cv2.createTrackbar("Yuvarlaklik", "Balon Algilama", int(CIRCULARITY_THRESH * 100), 100, lambda x: None)
    cv2.createTrackbar("Min Alan", "Balon Algilama", MIN_AREA, 2000, lambda x: None)
    cv2.createTrackbar("Max Alan", "Balon Algilama", MAX_AREA, 500000, lambda x: None)
    cv2.createTrackbar("Kararlilik", "Balon Algilama", STABLE_FRAMES_NEEDED, 10, lambda x: None)
    
    # === ANA DÖNGÜ ===
    frame_count = 0
    
    while True:
        # 1. KAMERADAN GÖRÜNTÜ AL
        ret, frame = cap.read()
        
        if not ret:
            print("❌ HATA: Kameradan görüntü alınamıyor!")
            break
        
        frame_count += 1
        
        # Kare görünümü için ortadan kare kırpma
        min_dim = min(frame.shape[0], frame.shape[1])
        start_x = (frame.shape[1] - min_dim) // 2
        start_y = (frame.shape[0] - min_dim) // 2
        frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]
        
        # 2. GÖRÜNTÜYÜ ÖN İŞLE
        # Bulanıklaştırma: Gürültüyü azaltır, algılamayı kararlı hale getirir
        frame_blurred = cv2.GaussianBlur(frame, BLUR_KERNEL, 0)
        
        # BGR'den HSV'ye dönüştür
        hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_BGR2HSV)
        hsv = normalize_hsv_v(hsv)
        
        # 3. TRACKBAR DEĞERLERİNİ OKU (Canlı ayar için)
        h1_min = cv2.getTrackbarPos("R H Min", "Balon Algilama")
        h1_max = cv2.getTrackbarPos("R H Max", "Balon Algilama")
        r_s_min = cv2.getTrackbarPos("R S Min", "Balon Algilama")
        r_v_min = cv2.getTrackbarPos("R V Min", "Balon Algilama")
        gh_min = cv2.getTrackbarPos("G H Min", "Balon Algilama")
        gh_max = cv2.getTrackbarPos("G H Max", "Balon Algilama")
        g_s_min = cv2.getTrackbarPos("G S Min", "Balon Algilama")
        g_v_min = cv2.getTrackbarPos("G V Min", "Balon Algilama")
        circ_thresh = cv2.getTrackbarPos("Yuvarlaklik", "Balon Algilama") / 100.0
        min_area = cv2.getTrackbarPos("Min Alan", "Balon Algilama")
        max_area = cv2.getTrackbarPos("Max Alan", "Balon Algilama")
        stable_needed = cv2.getTrackbarPos("Kararlilik", "Balon Algilama")
        
        # Değişkenleri güncelle (trackbar'lardan)
        if h1_min > h1_max:
            h1_min, h1_max = h1_max, h1_min
        if gh_min > gh_max:
            gh_min, gh_max = gh_max, gh_min

        current_lower1 = np.array([h1_min, r_s_min, r_v_min])
        current_upper1 = np.array([h1_max, 255, 255])
        current_lower2 = np.array([160, r_s_min, r_v_min])
        current_upper2 = np.array([179, 255, 255])
        current_lower_green = np.array([gh_min, g_s_min, g_v_min])
        current_upper_green = np.array([gh_max, 255, 255])

        # 4. KIRMIZI MASKE OLUŞTUR
        mask1 = cv2.inRange(hsv, current_lower1, current_upper1)
        mask2 = cv2.inRange(hsv, current_lower2, current_upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Cilt tonlarını çıkar — ancak balonun kendisi yanlışlıkla silinmesin diye
        skin = skin_mask(frame)
        # Skin ve red mask kesişimini hesapla
        overlap = cv2.bitwise_and(mask, skin)
        mask_area = cv2.countNonZero(mask)
        overlap_area = cv2.countNonZero(overlap)
        overlap_ratio = (overlap_area / mask_area) if mask_area > 0 else 0
        # Eğer mask ile cilt maskesi arasındaki çakışma yüksekse (ör. %30+), cildi çıkar
        if overlap_ratio > 0.30:
            mask = cv2.bitwise_and(mask, cv2.bitwise_not(skin))
        
        # Morfolojik işlemler (yansıma ve gölge boşlukları kapatma)
        strict_mask = apply_morphology(mask)

        # Takviye: parlaklık/yansıma nedeniyle H değeri kaymış bölgeler için genişletilmiş kırmızı aralıkları ile yedek maske
        loose_lower1 = np.array([0, max(50, r_s_min // 2), max(30, r_v_min // 2)])
        loose_upper1 = np.array([h1_max, 255, 255])
        loose_lower2 = np.array([160, max(50, r_s_min // 2), max(30, r_v_min // 2)])
        loose_upper2 = np.array([179, 255, 255])
        loose_mask1 = cv2.inRange(hsv, loose_lower1, loose_upper1)
        loose_mask2 = cv2.inRange(hsv, loose_lower2, loose_upper2)
        loose_mask = cv2.bitwise_or(loose_mask1, loose_mask2)
        loose_mask = apply_morphology(loose_mask)

        # Combine primary mask with loose mask to recover washed-out highlights
        combined_mask = cv2.bitwise_or(strict_mask, loose_mask)
        frame_area = combined_mask.shape[0] * combined_mask.shape[1]

        # Eğer mask çok büyükse önce yalnızca sıkı maskeyi dene
        if cv2.countNonZero(combined_mask) > frame_area * 0.40:
            filtered_mask = filter_oversized_components(combined_mask, max_area=frame_area * 0.75)
            if cv2.countNonZero(filtered_mask) < cv2.countNonZero(combined_mask) * 0.6:
                combined_mask = strict_mask
            else:
                combined_mask = filtered_mask

        mask = combined_mask
        mask = split_adjacent_balloons(mask, min_area)

        # Temporal smoothing: küçük dalgalanmaları azaltmak için son birkaç maskenin çoğunluğunu al
        try:
            mask_history.append(mask.copy())
            if len(mask_history) >= 2:
                stack = np.stack([m == 255 for m in mask_history], axis=0).astype(np.uint8)
                votes = np.sum(stack, axis=0)
                thresh = max(1, (len(mask_history) // 2) + 1)
                mask = np.where(votes >= thresh, 255, 0).astype(np.uint8)
        except Exception:
            pass

        # Doldurma: konturları konveks hull ile doldurarak kesik/yarım algılamaları azalt
        contours_for_fill, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours_for_fill:
            if cv2.contourArea(c) < min_area:
                continue
            hull = cv2.convexHull(c)
            cv2.drawContours(mask, [hull], -1, 255, -1)
        
        # 5. YEŞİL MASKE OLUŞTUR
        green_mask = cv2.inRange(hsv, current_lower_green, current_upper_green)
        green_mask = apply_morphology(green_mask)
        
        # 6. KONTURLARI BUL
        red_contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_red_contours = [cnt for cnt in red_contours if is_valid_contour(cnt, min_area, max_area, circ_thresh)]
        valid_green_contours = [cnt for cnt in green_contours if is_valid_contour(cnt, min_area, max_area, circ_thresh)]
        
        red_count = len(valid_red_contours)
        green_count = len(valid_green_contours)
        
        # Ek filtreleme: her konturun içindeki ortalama HSV'ye bak, renk tutarsızsa ele
        filtered_red_contours = []
        for cnt in valid_red_contours:
            h_mean, s_mean, v_mean = mean_hsv_in_contour(cnt, hsv)
            
            # DAHA GEVŞEK KRİTERLER (algılama başarısını artırmak için):
            # Minimum doyma/parlaklık gereksinimi (daha düşük eşik)
            if s_mean < 50 or v_mean < 30:  # 70/40 -> 50/30 (daha toleranslı)
                continue
            
            # Hue kırmızı aralığına yakın mı? (0-h1_max veya 160-179) - biraz daha geniş
            h_tolerance = 15  # Hue toleransı
            if not (h_mean <= (h1_max + h_tolerance) or h_mean >= (160 - h_tolerance)):
                continue
            
            # Aspect ratio kontrolü: çok uzun ince bölgeleri ele (daha esnek)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / float(h) if h != 0 else 0
            # 0.35-3.0 -> 0.2-4.5 (çok daha geniş aralık, eliptik şekiller için)
            if aspect < 0.2 or aspect > 4.5:
                continue
            
            # Solidity kontrolü: çok dağılmış şekilleri ele (balona yakın olmalı)
            solidity = contour_solidity(cnt)
            if solidity < 0.45:  # %45 solidity (daha az sıkı)
                continue
            
            filtered_red_contours.append(cnt)

        best_red_contour = select_best_contour_for_color(filtered_red_contours, min_area, max_area, circ_thresh, 'red')
        best_green_contour = select_best_contour_for_color(valid_green_contours, min_area, max_area, circ_thresh, 'green')
        
        detected = False
        best_center = None
        best_contour = None
        best_color = None
        label = None
        
        if max_area < min_area:
            max_area = min_area * 5
        
        # Öncelikle tüm tespitleri ekran üzerinde göster (kırmızı ve yeşil tümü)
        # Aynı anda birden çok hedef gözüksün; takip (tracker) için en yakına öncelik verilecek.
        detected = False
        best_contour = None
        best_center = None
        best_color = None
        label = None

        # Tüm adayları ekranda göster (yeşil/dostlar gösterilecek ama ASLA takip hedefi olmaz)
        # Takip hedefi yalnızca kırmızılar arasından seçilecek: en yakına öncelik ver.
        all_display_candidates = []
        for cnt in filtered_red_contours:
            all_display_candidates.append((cnt, 'red'))
        for cnt in valid_green_contours:
            all_display_candidates.append((cnt, 'green'))

        # TRACKING: sadece kırmızı adaylar arasından en yakını seç
        if len(filtered_red_contours) > 0:
            frame_cx = frame.shape[1] // 2
            frame_cy = frame.shape[0] // 2
            best_dist = float('inf')
            for cnt in filtered_red_contours:
                c = get_center(cnt)
                dist = math.hypot(c[0] - frame_cx, c[1] - frame_cy)
                if dist < best_dist:
                    best_dist = dist
                    best_contour = cnt
                    best_center = c
                    best_color = 'red'
            detected = True
            label = 'ENEMY'
        else:
            detected = False
        
        # 7. TRACKER İLE KARARLI HALE GETİR (takip: seçilen en yakın hedefe göre)
        is_stable, stable_center = tracker.update(detected, best_center, stable_needed)

        # Ekranda debug: kırmızı HSV değerlerini göster (canlı ayar kolaylığı için)
        try:
            cv2.putText(frame, f"R1: {current_lower1.tolist()}-{current_upper1.tolist()}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 150, 255), 1)
            # Ayrıca ara sıra mask ile cilt çakışma oranını consola yaz
            if frame_count % 60 == 0:
                print(f"[DEBUG] Mask area: {mask_area} Overlap area: {overlap_area} Overlap ratio: {overlap_ratio:.2f}")
        except Exception:
            pass
        
        # 8. EKRANA ÇİZİMLERİ YAP
        
        # ---- ALGILAMA DURUMU (sol üst) ----
        if is_stable and stable_center:
            status_color = (0, 255, 0)
            status_text = f"STABLE ({tracker.detection_counter}/{stable_needed})"
        elif detected:
            status_color = (0, 255, 255)
            status_text = f"DETECTING... ({tracker.detection_counter}/{stable_needed})"
        else:
            status_color = (0, 0, 255)
            status_text = f"NO BALLOON ({tracker.detection_counter}/{stable_needed})"
        
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # ---- TÜM BULUNANLARI KUTU İLE GÖSTER (aynı anda) ----
        for cnt in valid_green_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
            cv2.putText(frame, "ALLY", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1, cv2.LINE_AA)

        for cnt in filtered_red_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Kalınlık 2 ile çiz, takipte olan kırmızı daha sonra kalın vurguyla öne çıkacak
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "ENEMY", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # ---- TAKİP EDİLEN HEDEFİ VURGULA (kararlıysa kalın çizgi + daire) ----
        if is_stable and stable_center is not None and best_contour is not None:
            x, y, w, h = cv2.boundingRect(best_contour)
            rect_color = (0, 255, 255) if best_color == 'green' else (0, 0, 255)
            circle_color = (255, 0, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), rect_color, 3)
            cv2.circle(frame, stable_center, 8, circle_color, -1)
            radius = max(w, h) // 2
            cv2.circle(frame, stable_center, radius, rect_color, 2)
            cv2.putText(frame, label, (x, y - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.8, rect_color, 2)
            area = cv2.contourArea(best_contour)
            cv2.putText(frame, f"Area: {int(area)}", (x, y + h + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        
        # ---- AYAR BİLGİLERİ (sağ üst) ----
        info_y = 30
        cv2.putText(frame, f"R: H{h1_min}-{h1_max} S{r_s_min}+ V{r_v_min}+", 
                   (frame.shape[1] - 360, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"G: H{gh_min}-{gh_max} S{g_s_min}+ V{g_v_min}+", 
                   (frame.shape[1] - 360, info_y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, f"Circ: {circ_thresh:.2f} MinA:{min_area} MaxA:{max_area}", 
                   (frame.shape[1] - 360, info_y + 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # ---- MASKELERİ GÖSTER (opsiyonel) ----
        cv2.imshow("Kirmizi Maske", mask)
        cv2.imshow("Yesil Maske", green_mask)

        # ---- SAĞ-ALT HUD: DÜŞMAN / DOST SAYISI ----
        hud_x = frame.shape[1] - 260
        hud_y = frame.shape[0] - 10
        cv2.putText(frame, f"ENEMY: {len(filtered_red_contours)}", (hud_x, hud_y - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"ALLY:  {green_count}", (hud_x + 130, hud_y - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
        
        # ---- ANA GÖRÜNTÜYÜ GÖSTER ----
        cv2.imshow("Balon Algilama", frame)
        
        # 9. KLAVYE KONTROLLERİ
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            print("\n⚠️ Program kullanıcı tarafından durduruldu.")
            break
        
        elif key == ord('s'):  # 's' tuşu: ayarları kaydet
            print("\n" + "=" * 50)
            print("📝 MEVCUT AYARLAR KAYDEDİLDİ:")
            print("=" * 50)
            print(f"LOWER_RED1 = np.array([{h1_min}, {r_s_min}, {r_v_min}])")
            print(f"UPPER_RED1 = np.array([{h1_max}, 255, 255])")
            print(f"LOWER_RED2 = np.array([{current_lower2[0]}, {current_lower2[1]}, {current_lower2[2]}])")
            print(f"UPPER_RED2 = np.array([{current_upper2[0]}, {current_upper2[1]}, {current_upper2[2]}])")
            print(f"LOWER_GREEN = np.array([{gh_min}, {g_s_min}, {g_v_min}])")
            print(f"UPPER_GREEN = np.array([{gh_max}, 255, 255])")
            print(f"MIN_AREA = {min_area}")
            print(f"MAX_AREA = {max_area}")
            print(f"CIRCULARITY_THRESH = {circ_thresh:.2f}")
            print(f"STABLE_FRAMES_NEEDED = {stable_needed}")
            print("=" * 50)
            # Ayrıca dosyaya da kaydet (geçmiş kayıtları sakla)
            try:
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open('saved_settings.txt', 'a', encoding='utf-8') as f:
                    f.write(f"[{ts}]\n")
                    f.write(f"LOWER_RED1 = np.array([{h1_min}, {r_s_min}, {r_v_min}])\n")
                    f.write(f"UPPER_RED1 = np.array([{h1_max}, 255, 255])\n")
                    f.write(f"LOWER_RED2 = np.array([{current_lower2[0]}, {current_lower2[1]}, {current_lower2[2]}])\n")
                    f.write(f"UPPER_RED2 = np.array([{current_upper2[0]}, {current_upper2[1]}, {current_upper2[2]}])\n")
                    f.write(f"LOWER_GREEN = np.array([{gh_min}, {g_s_min}, {g_v_min}])\n")
                    f.write(f"UPPER_GREEN = np.array([{gh_max}, 255, 255])\n")
                    f.write(f"MIN_AREA = {min_area}\n")
                    f.write(f"MAX_AREA = {max_area}\n")
                    f.write(f"CIRCULARITY_THRESH = {circ_thresh:.2f}\n")
                    f.write(f"STABLE_FRAMES_NEEDED = {stable_needed}\n")
                    f.write("\n")
                # Görüntüleri de kaydet
                cv2.imwrite('saved_frame.png', frame)
                cv2.imwrite('saved_mask.png', mask)
                print("✅ Ayarlar ve görüntüler 'saved_settings.txt','saved_frame.png','saved_mask.png' olarak kaydedildi.")
            except Exception as e:
                print(f"⚠️ Kaydetme sırasında hata: {e}")
        
        elif key == ord('r'):  # 'r' tuşu: trackbar'ları sıfırla
            cv2.setTrackbarPos("R H Min", "Balon Algilama", LOWER_RED1[0])
            cv2.setTrackbarPos("R H Max", "Balon Algilama", UPPER_RED1[0])
            cv2.setTrackbarPos("R S Min", "Balon Algilama", LOWER_RED1[1])
            cv2.setTrackbarPos("R V Min", "Balon Algilama", LOWER_RED1[2])
            cv2.setTrackbarPos("G H Min", "Balon Algilama", LOWER_GREEN[0])
            cv2.setTrackbarPos("G H Max", "Balon Algilama", UPPER_GREEN[0])
            cv2.setTrackbarPos("G S Min", "Balon Algilama", LOWER_GREEN[1])
            cv2.setTrackbarPos("G V Min", "Balon Algilama", LOWER_GREEN[2])
            cv2.setTrackbarPos("Yuvarlaklik", "Balon Algilama", int(CIRCULARITY_THRESH * 100))
            cv2.setTrackbarPos("Min Alan", "Balon Algilama", MIN_AREA)
            cv2.setTrackbarPos("Max Alan", "Balon Algilama", MAX_AREA)
            cv2.setTrackbarPos("Kararlilik", "Balon Algilama", STABLE_FRAMES_NEEDED)
            print("\n🔄 Ayarlar varsayılana sıfırlandı!")
    
    # === TEMİZLİK ===
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Program sonlandırıldı. İyi günler!")


# =====================================================
# 5. PROGRAMI ÇALIŞTIR
# =====================================================
if __name__ == "__main__":
    main()