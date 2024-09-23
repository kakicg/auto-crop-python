import cv2
import matplotlib.pyplot as plt

# カメラの初期化
cap = cv2.VideoCapture(0)  # 0はデフォルトのカメラ

if not cap.isOpened():
    print("カメラを開けませんでした")
    exit()

# 最初の2フレームを取得
ret, frame1 = cap.read()
ret, frame2 = cap.read()

# Matplotlibのインタラクティブモードを有効にする
plt.ion()

# 画像表示用のウィンドウを作成
fig, ax = plt.subplots()

# 画像の初期表示 (RGBに変換して表示)
frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
img_display = ax.imshow(frame_rgb)

while cap.isOpened():
    # 現在のフレームと前フレームの差分を取る
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭ごとに処理
    for contour in contours:
        # ノイズを除くために最小面積を設定
        if cv2.contourArea(contour) < 1000:
            continue

        # 製品の外接矩形を取得
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 画面の中央付近に到達したかチェック
        if (x + w//2) > (frame1.shape[1]//2 - 50) and (x + w//2) < (frame1.shape[1]//2 + 50):
            # 製品の画像をキャプチャ
            product_img = frame1[y:y + h, x:x + w]
            cv2.imwrite("product_image.png", product_img)
            print("製品をキャプチャしました")

    # フレームをRGB形式に変換してMatplotlibで表示更新
    frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
    img_display.set_data(frame_rgb)
    plt.draw()
    plt.pause(0.01)  # 0.01秒ごとにフレームを更新

    # 次のフレームに移動
    frame1 = frame2
    ret, frame2 = cap.read()

    if not ret:
        break

# カメラとウィンドウを解放
cap.release()
plt.ioff()
plt.show()