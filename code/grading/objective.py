import math

def deduplicate_option_boxes(option_list, distance_threshold=0.045):
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
    if not boxes:
        return []

    boxes.sort(key=lambda b: b[1])
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
        sorted_boxes.extend(sorted(row, key=lambda b: b[0]))

    return sorted_boxes

def get_closest_option(mark_center, option_centers):
    if not option_centers:
        return None
    dists = [math.hypot(mark_center[0] - opt[0], mark_center[1] - opt[1]) for opt in option_centers]
    return dists.index(min(dists)) + 1

def predict_answer_objective_dict(label_dir):
    """
    디렉토리 내 모든 라벨 파일을 읽고, 객관식 선택지를 dict 형태로 저장

    Returns:
        dict: { '1.jpg': 3, '2.jpg': 2, ... }
    """
    import os
    import glob
    from detector import parse_yolo_label  # YOLO 라벨 파싱 함수 필요

    answer_dict = {}
    label_files = sorted(glob.glob(os.path.join(label_dir, "*.txt")))

    for label_path in label_files:
        filename = os.path.splitext(os.path.basename(label_path))[0] + ".jpg"
        boxes = parse_yolo_label(label_path)

        option_boxes = deduplicate_option_boxes(boxes.get('option_box', []))
        marked_boxes = boxes.get('marked', [])

        if not option_boxes or not marked_boxes:
            answer_dict[filename] = None
            continue

        sorted_options = sort_boxes_gridwise(option_boxes)
        selected = get_closest_option(marked_boxes[0], sorted_options)
        answer_dict[filename] = selected

    return answer_dict
