import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Kamera açılamadı. Başka index deneyin (1,2...) veya RealSense SDK gerekebilir.")
    exit()

print("Kamera açıldı. Çıkmak için ESC tuşuna bas.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Kare okunamadı, çıkılıyor.")
        break
    cv2.imshow("Kamera Testi", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        print("ESC ile çıkılıyor.")
        break

cap.release()
cv2.destroyAllWindows()
