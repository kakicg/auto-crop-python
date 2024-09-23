import cv2
import matplotlib.pyplot as plt

# カメラの初期化
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラを開けませんでした")
    exit()

# フレームを取得
ret, frame = cap.read()

if ret:
    # OpenCVのBGR画像をRGBに変換
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Matplotlibで画像を表示
    plt.imshow(frame_rgb)
    plt.title('Captured Image')
    plt.show()
else:
    print("フレームの取得に失敗しました")

cap.release()