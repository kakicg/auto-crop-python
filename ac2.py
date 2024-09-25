import cv2
import numpy as np

# 画像の読み込み (カラーで読み込む)
image = cv2.imread('./test_images/prd2.jpg')

# グレースケールに変換
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 二値化
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# カーネルの定義
kernel = np.ones((5, 5), np.uint8)

# オープニング処理（ノイズ除去）
opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

# 物体を結合するためのダイレーション処理
dilated = cv2.dilate(opening, kernel, iterations=2)

# ダイレーション後の輪郭を検出
contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 輪郭に基づいてバウンディングボックスを描画
bounding_boxes = []
for contour in contours:
    # 輪郭に外接する長方形（バウンディングボックス）を計算
    x, y, w, h = cv2.boundingRect(contour)
    bounding_boxes.append([x, y, x + w, y + h])
    
 
# バウンディングボックス同士を結合する関数
def merge_boxes(boxes):
    if len(boxes) == 0:
        return []

    # バウンディングボックスの最小と最大の座標を初期化
    x_min = min([box[0] for box in boxes])
    y_min = min([box[1] for box in boxes])
    x_max = max([box[2] for box in boxes])
    y_max = max([box[3] for box in boxes])

    return [[x_min, y_min, x_max, y_max]]

# すべてのバウンディングボックスを結合
merged_boxes = merge_boxes(bounding_boxes)
# 結合されたバウンディングボックスを描画（赤色の矩形）
for box in merged_boxes:
    cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)

# 結果をファイルとして保存する
output_file_path = './output_bounding_box_merged.jpg'
cv2.imwrite(output_file_path, image)

print(f"画像が '{output_file_path}' として保存されました。")