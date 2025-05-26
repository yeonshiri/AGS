import math

def deduplicate_option_boxes(option_list, distance_threshold=0.045):
    """
    중복된 보기 박스를 클러스터링하여 평균 좌표 반환
    """
    if not option_list:
        return []

    clusters = []
    for opt in option_list:
        added = False
        for cluster in clusters:
            if any(math.hypot(opt[0] - c[0], opt[1] - c[1]) < distance_threshold for c in cluster):
                cluster.append(opt)
                added = True
                break
        if not added:
            clusters.append([opt])

    return [
        (sum(p[0] for p in cluster) / len(cluster),
         sum(p[1] for p in cluster) / len(cluster))
        for cluster in clusters
    ]

def sort_boxes_gridwise(boxes, row_threshold=0.05):
    """
    보기 박스를 y축 기준 행 정렬 후, 각 행을 x축 기준 정렬
    """
    if not boxes:
        return []

    boxes.sort(key=lambda b: b[1])  # y 기준 정렬
    rows = []
    current_row = [boxes[0]]

    for box in boxes[1:]:
        if abs(box[1] - current_row[-1][1]) < row_threshold:
            current_row.append(box)
        else:
            rows.append(current_row)
            current_row = [box]
    rows.append(current_row)

    sorted_boxes = []
    for row in rows:
        sorted_boxes.extend(sorted(row, key=lambda b: b[0]))  # x 기준 정렬

    return sorted_boxes

def get_closest_option(mark_center, option_centers):
    """
    마킹 위치에서 가장 가까운 보기 박스를 찾고 번호 반환 (1부터 시작)
    """
    if not option_centers:
        return None
    dists = [math.hypot(mark_center[0] - opt[0], mark_center[1] - opt[1]) for opt in option_centers]
    return dists.index(min(dists)) + 1

def predict_answer_objective(boxes):
    """
    YOLO 라벨 기반으로 예측된 보기 번호 반환

    Parameters:
        boxes (dict): {
            'option_box': [(x, y), ...],
            'marked': [(x, y)]
        }

    Returns:
        int or None: 선택된 보기 번호, 없으면 None
    """
    option_boxes = deduplicate_option_boxes(boxes.get('option_box', []))
    marked_boxes = boxes.get('marked', [])

    if not option_boxes or not marked_boxes:
        return None

    sorted_options = sort_boxes_gridwise(option_boxes)
    return get_closest_option(marked_boxes[0], sorted_options)
