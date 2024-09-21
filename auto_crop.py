import os
import subprocess
import time
import signal
import cv2
import numpy as np

# 背景画像の保存パス
background_image_path = "./images/background.jpg"
output_folder = "./cropped_images/"  # トリミング画像の保存フォルダ
pixel_to_cm_ratio = 0.1  # ピクセルからcmへの変換比率（適宜調整）

def kill_gvfsd_gphoto2():
    result = subprocess.run(['ps', '-A'], stdout=subprocess.PIPE)
    processes = result.stdout.decode()

    for line in processes.splitlines():
        if 'gvfsd-gphoto2' in line:
            pid = int(line.split(None, 1)[0])
            print(f"gvfsd-gphoto2 プロセスが見つかりました。PID: {pid}")
            os.kill(pid, signal.SIGKILL)
            print("gvfsd-gphoto2 プロセスを終了しました。")
            return
    print("撮影に障害となるプロセス(gvfsd-gphoto2)は見つかりませんでした。")

def take_picture(save_path):
    kill_gvfsd_gphoto2()

    try:
        subprocess.run(["gphoto2", "--capture-image-and-download", "--filename", save_path], check=True)
        print(f"Image saved at {save_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to take picture: {e}")
        return False

def capture_background_image():
    input("背景画像を撮影する準備ができたらキーを押してください: ")
    
    success = False
    max_retries = 3
    retry_count = 0
    
    while not success and retry_count < max_retries:
        success = take_picture(background_image_path)
        if not success:
            retry_count += 1
            print(f"撮影に失敗しました。リトライ {retry_count}/{max_retries}")
            time.sleep(2)
        else:
            print("背景画像が正常に保存されました。")
    
    if not success:
        print("背景画像の撮影に失敗しました。プログラムを終了します。")
        exit(1)

import cv2
import os


def preprocess_diff_image(diff_image):
    """
    微妙な背景のズレを除去するためにフィルタを適用し、閾値処理を行う関数
    """
    # ガウシアンブラーを適用してノイズを除去
    blurred = cv2.GaussianBlur(diff_image, (31, 31), 0)

    # 適応的閾値処理を行い、背景の微細な違いを削除
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('./images/diff.jpg', diff_image)
    cv2.imwrite('./images/gray_diff.jpg', gray)

    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite('./images/thresh.jpg', thresh)


    # 膨張と収縮を適用して商品を強調し、背景のノイズを削除
    kernel = np.ones((3, 3), np.uint8)

    eroded = cv2.erode(thresh, kernel, iterations=2)
    dilated = cv2.dilate(eroded, kernel, iterations=2)

    return eroded

def detect_product(image_path, background_image_path):
    # 画像を読み込む
    image = cv2.imread(image_path)
    background = cv2.imread(background_image_path)

    # 差分を計算する
    diff = cv2.absdiff(image, background)

    # 差分画像にフィルタと閾値処理を適用
    processed_diff = preprocess_diff_image(diff)

    # 輪郭を検出
    contours, _ = cv2.findContours(processed_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 最大の輪郭を取得
        max_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(max_contour)
        return (x, y, w, h)
    else:
        print("No product detected.")
        return None

def crop_and_save(image_path, rect, output_folder):
    image = cv2.imread(image_path)
    x, y, w, h = rect
    cropped_image = image[y:y+h, x:x+w]

    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # トリミング画像を保存
    cropped_image_path = os.path.join(output_folder, os.path.basename(image_path))
    cv2.imwrite(cropped_image_path, cropped_image)
    print(f"トリミングされた画像を保存しました: {cropped_image_path}")

def estimate_product_height(rect, pixel_to_cm_ratio):
    _, _, _, h = rect
    return h * pixel_to_cm_ratio

def main_loop():
    capture_background_image()
    print("背景画像が保存されました。これから商品撮影に入ります。")

    while True:
        barcode = input("商品バーコードをスキャンしてください (終了するには'q'を入力): ")
        if barcode.lower() == 'q':
            print("撮影ループを終了します。")
            break

        product_image_path = f"./images/product_{barcode}.jpg"
        success = take_picture(product_image_path)
        if success:
            print(f"商品画像を保存しました: {product_image_path}")
        else:
            print("商品画像の撮影に失敗しました。再試行してください。")
            continue

        rect = detect_product(product_image_path, background_image_path)
        if rect:
            crop_and_save(product_image_path, rect, output_folder)
            height = estimate_product_height(rect, pixel_to_cm_ratio)
            print(f"Estimated height of product {barcode}: {height} cm")
        else:
            print(f"Failed to detect product for barcode {barcode}")

if __name__ == "__main__":
    main_loop()