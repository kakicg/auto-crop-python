import os
import subprocess
import time
import signal

# 背景画像の保存パス
background_image_path = "./images/background.jpg"

def kill_gvfsd_gphoto2():
    # 'ps -A | grep gphoto2' を実行して、gvfsd-gphoto2 プロセスがあるか確認
    result = subprocess.run(['ps', '-A'], stdout=subprocess.PIPE)
    processes = result.stdout.decode()

    # 'gvfsd-gphoto2' がプロセスにあるかを確認
    for line in processes.splitlines():
        if 'gvfsd-gphoto2' in line:
            # プロセスID (PID) を取得
            pid = int(line.split(None, 1)[0])
            print(f"gvfsd-gphoto2 プロセスが見つかりました。PID: {pid}")
            
            # プロセスを終了させる
            os.kill(pid, signal.SIGKILL)
            print("gvfsd-gphoto2 プロセスを終了しました。")
            return
    print("撮影に障害となるプロセス(gvfsd-gphoto2)は見つかりませんでした。")

def take_picture(save_path):
    """
    GPhoto2を使ってカメラで写真を撮影し、指定されたパスに保存する関数
    """
    # 撮影や他の処理を行う前に、gvfsd-gphoto2 プロセスを終了する
    kill_gvfsd_gphoto2()

    try:
        # gphoto2で写真撮影を実行
        subprocess.run(["gphoto2", "--capture-image-and-download", "--filename", save_path], check=True)
        print(f"Image saved at {save_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to take picture: {e}")
        return False

def capture_background_image():
    """
    背景画像を撮影するための関数
    """
    input("背景画像を撮影する準備ができたらキーを押してください: ")
    
    success = False
    max_retries = 3  # リトライ回数
    retry_count = 0
    
    # リトライのためのループ
    while not success and retry_count < max_retries:
        success = take_picture(background_image_path)
        if not success:
            retry_count += 1
            print(f"撮影に失敗しました。リトライ {retry_count}/{max_retries}")
            time.sleep(2)  # 少し待機してから再試行
        else:
            print("背景画像が正常に保存されました。")
    
    if not success:
        print("背景画像の撮影に失敗しました。プログラムを終了します。")
        exit(1)

# 商品画像の差分から商品の輪郭を検出する関数
def detect_product(image_path, background_image_path):
    # 画像を読み込む
    image = cv2.imread(image_path)
    background = cv2.imread(background_image_path)

    # 差分を計算する
    diff = cv2.absdiff(image, background)

    # 差分画像を二値化する
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # 最大の輪郭を取得
        max_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(max_contour)
        return (x, y, w, h)
    else:
        print("No product detected")
        return None

# トリミングと保存を行う関数
def crop_and_save(image_path, rect, output_folder):
    image = cv2.imread(image_path)
 

def main_loop():
    """
    撮影ループを開始する前に、背景画像を撮影し、その後通常の撮影ループに入る
    """
    # 背景画像を先に撮影
    capture_background_image()

    print("背景画像が保存されました。これから商品撮影に入ります。")

    while True:
        # 撮影ループの開始
        barcode = input("商品バーコードをスキャンしてください (終了するには'q'を入力): ")
        if barcode.lower() == 'q':
            print("撮影ループを終了します。")
            break

        # 撮影した商品画像の保存パス
        product_image_path = f"./images/product_{barcode}.jpg"

        # 商品画像を撮影
        success = take_picture(product_image_path)
        if success:
            print(f"商品画像を保存しました: {product_image_path}")
        else:
            print("商品画像の撮影に失敗しました。再試行してください。")

        # 差分で商品の位置を検出
        rect = detect_product(product_image_path, background_image_path)
        if rect:
            # トリミングして保存
            crop_and_save(product_image_path, rect, output_folder)
            
            # 高さを推定して記録
            height = estimate_product_height(rect, pixel_to_cm_ratio)
            print(f"Estimated height of product {barcode}: {height} cm")
        else:
            print(f"Failed to detect product for barcode {barcode}")


if __name__ == "__main__":
    main_loop()