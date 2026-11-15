# FG1000 — Proje Özeti

**Gömülü yazılım, görüntü işleme ve elektronik şema tasarımını bir araya getiren bitirme projesi.**

Bu depo; Arduino Mega ve ESP32 kaynaklarını, Python kamera uygulamalarını ve Altium tasarım belgelerini incelemeyi kolaylaştıracak bir yapıda sunar.

[Elektronik, donanım tasarımı ve yazılım: FurkanUstaoglu](https://github.com/FurkanUstaoglu) · [English overview](../README.md)

## Projenin kapsamı

| Alan | Teknolojiler | Depodaki karşılığı |
| --- | --- | --- |
| Gömülü yazılım | Arduino Mega 2560, ESP32, C/C++ | Kartlara göre ayrılmış kaynak dosyaları |
| Görüntü işleme | Python, OpenCV, NumPy | Balon algılama ve kamera uygulamaları |
| Kamera çalışmaları | OpenCV, RealSense | Kamera kontrolü ve derinlik kamerası kaynakları |
| Elektronik tasarım | Altium Designer | Proje dosyası, şemalar ve bileşen kütüphaneleri |

## İncelemeye nereden başlamalı?

1. [Arduino Mega kaynakları](../firmware/arduino-mega/): özgün `RCWS_v1` dosyaları ve ayrı Arduino denemesi.
2. [ESP32 kaynakları](../firmware/esp32/ESP32_Code/): ESP32 uygulaması ve gömülü web arayüzü.
3. [Python kaynakları](../software/balloon-vision/src/): görüntü işleme ve kamera uygulamaları.
4. [Altium tasarımı](../hardware/altium/FG1000/): şema belgeleri ve proje kütüphaneleri.
5. [İnceleme rehberi](project-guide.md): dosyaların kısa açıklamaları.

## Teknik sunumun sınırları

Depo hazırlığı sırasında derleme, donanım çalıştırma veya uçtan uca test yapılmadı. Burada kaynakların bulunması, bütün bileşenlerin birlikte doğrulandığı anlamına gelmez. Ölçülmüş doğruluk, menzil veya güvenilirlik sonucu sunulmuyor.

Altium içeriğinde şemalar ve bileşen ayak izi kütüphaneleri bulunuyor; tamamlanmış `.PcbDoc` kart yerleşimi paylaşılmamış. Örnek kamera kayıtları geliştirme arşividir; başarı gösterimi veya performans kanıtı değildir.

## Projedeki katkım

Bu depoda sunulan elektronik, donanım tasarımı ve yazılım çalışmalarını bir bitirme projesi kapsamında geliştirdim. Elektronik şema tasarımı, Arduino Mega ve ESP32 yazılımları ile Python görüntü işleme uygulamaları benim çalışma kapsamımdı. Bu portföy bu katkılara odaklanır.

## Dosya düzeni

`firmware/` kart yazılımlarını, `software/` Python uygulamalarını, `hardware/` elektronik tasarımı, `docs/` ise proje belgelerini içerir. Arduino taslaklarının adları ve Altium'un iç dosya yolları korunmuştur. Dış kaynaklı bileşen kütüphaneleri `vendor-libraries/` altında ayrılmıştır.

## Haklar

Depoya genel bir lisans eklenmemiştir. Dış kaynaklı kütüphanelerin hakları ilgili sahiplerine aittir.
