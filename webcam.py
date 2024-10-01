import cv2

cap = cv2.VideoCapture(0)  # 0はカメラID

# 試したい解像度を設定
width = 1920
height = 1080
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# 実際に設定された解像度を取得
actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

print(f"Requested resolution: {width}x{height}")
print(f"Actual resolution: {int(actual_width)}x{int(actual_height)}")

cap.release()

# v4l2-ctl --list-formats-ext