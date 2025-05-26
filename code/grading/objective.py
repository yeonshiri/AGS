import math

def deduplicate_option_boxes(option_list, distance_threshold=0.045):
    """
    겹쳐진 option_box들을 거리 기반으로 하나로 합친다.
    (예: 한 보기에 중복 detect된 박스를 평균으로 하나로 만듦)
    """
    if not option_list:
        return []

    clusters = []

    for opt in option_list:
        added = False
        for cluster in clusters:
            for c in cluster:
                dist = math.hypot(opt[0] - c[0], opt[1] - c[1])
                if dist < distance_threshold:
                    cluster.append(opt)
                    added = True
                    break
            if added:
                break
        if not added:
            clusters.append([opt])

    deduplicated = []
    for cluster in clusters:
        avg_x = sum(p[0] for p in cluster) / len(cluster)
        avg_y = sum(p[1] for p in cluster) / len(cluster)
        deduplicated.append((avg_x, avg_y))

    return deduplicated


def sort_boxes_gridwise(boxes, row_threshold=0.05):
    """
    보기 박스를 행 우선(row-wise), 좌→우로 정렬한다.
    ex) [1, 2]
         [3, 4]  → 순서대로 정렬된 리스트 반환
    """
    if not boxes:
        return []

    boxes = sorted(boxes, key=lambda b: b[1])  # y 기준 정렬
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
        row_sorted = sorted(row, key=lambda b: b[0])  # x 기준 정렬
        sorted_boxes.extend(row_sorted)

    return sorted_boxes


def get_closest_option(mark_center, option_centers):
    """
    마킹 위치와 가장 가까운 보기 박스의 index(=답 번호)를 반환
    """
    def dist(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    dists = [dist(mark_center, opt) for opt in option_centers]
    return dists.index(min(dists)) + 1  # 보기 번호는 1부터 시작


def predict_answer_objective(boxes):
    """
    YOLO 라벨로부터 사용자가 선택한 보기 번호를 예측한다.

    Parameters:
        boxes (dict): {
            'option_box': [(x, y), ...],
            'marked': [(x, y)]
        }

    Returns:
        predicted (int or None): 선택된 보기 번호, 없으면 None
    """
    option_boxes = deduplicate_option_boxes(boxes.get('option_box', []))
    marked_boxes = boxes.get('marked', [])

    if not marked_boxes or not option_boxes:
        return None  # 마킹이나 보기 없으면 판단 불가

    sorted_options = sort_boxes_gridwise(option_boxes)
    predicted = get_closest_option(marked_boxes[0], sorted_options)
    return predicted
