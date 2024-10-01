def are_bboxes_close(bbox1, bbox2, threshold=20):
    """
    2つのバウンディングボックスが指定された閾値以内に接近しているか、または重なっているかを判定する。
    
    bbox1: [ul_x_1, ul_y_1, db_x_1, db_y_1] -> バウンディングボックス1の座標
    bbox2: [ul_x_2, ul_y_2, db_x_2, db_y_2] -> バウンディングボックス2の座標
    threshold: int -> 距離の閾値（デフォルトは20ピクセル）
    
    Returns:
    bool: 2つのバウンディングボックスが閾値以内に接近している場合True、そうでなければFalse。
    """
    
    # バウンディングボックス1の座標
    ul_x_1, ul_y_1, db_x_1, db_y_1 = bbox1
    
    # バウンディングボックス2の座標
    ul_x_2, ul_y_2, db_x_2, db_y_2 = bbox2
    
    # X方向の距離を計算
    x_distance = max(ul_x_1 - db_x_2, ul_x_2 - db_x_1, 0)
    
    # Y方向の距離を計算
    y_distance = max(ul_y_1 - db_y_2, ul_y_2 - db_y_1, 0)
    
    # X方向とY方向のいずれかが閾値以下なら接近していると判定
    return x_distance <= threshold and y_distance <= threshold

# 例: 2つのバウンディングボックスの間の距離を確認
bbox1 = [50, 50, 100, 100]  # バウンディングボックス1
bbox2 = [120, 60, 160, 120]  # バウンディングボックス2

result = are_bboxes_close(bbox1, bbox2, threshold=20)
print(f"2つのバウンディングボックスは接近しているか: {result}")