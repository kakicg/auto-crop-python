import cv2
import matplotlib.pyplot as plt
import numpy as np

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

# 2つの表示用のウィンドウ（サブプロット）を作成
fig, (ax_cam, ax_capture) = plt.subplots(1, 2, figsize=(10, 5))

# カメラ映像の初期表示
frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
img_display_cam = ax_cam.imshow(frame_rgb)
ax_cam.set_title('Camera View')

# キャプチャー画像の初期表示（黒い画像でスタート）
blank_image = np.zeros_like(frame_rgb)
img_display_capture = ax_capture.imshow(blank_image)
ax_capture.set_title('Latest Capture')

# キャプチャーされた最新の画像を保持
latest_capture = blank_image

while cap.isOpened():
    # 現在のフレームと前フレームの差分を取る
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭ごとに処理
    for contour in contours:
        # ノイズを除くために最小面積を設定
        if cv2.contourArea(contour) < 10000:
            continue

        # 製品の外接矩形を取得
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 画面の中央付近に到達したかチェック
        if (x + w//2) > (frame1.shape[1]//2 - 50) and (x + w//2) < (frame1.shape[1]//2 + 50):
            # 製品の画像をキャプチャ
            product_img = frame1[y:y + h, x:x + w]
            latest_capture = cv2.cvtColor(product_img, cv2.COLOR_BGR2RGB)  # キャプチャした画像をRGBに変換
            cv2.imwrite("product_image.png", product_img)  # 画像を保存
            print("製品をキャプチャしました")

    # カメラ映像ウィンドウを更新
    frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
    img_display_cam.set_data(frame_rgb)
    ax_cam.set_title('Camera View')

    # キャプチャー画像ウィンドウを更新
    img_display_capture.set_data(latest_capture)
    ax_capture.set_title('Latest Capture')

    # 表示を更新
    plt.draw()
    plt.pause(0.03)

    # 次のフレームに移動
    frame1 = frame2
    ret, frame2 = cap.read()

    if not ret:
        break

# カメラとウィンドウを解放
cap.release()
plt.ioff()
plt.show()