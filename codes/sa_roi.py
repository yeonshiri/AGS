import os
import cv2
import numpy as np

distance_threshold = 150

def xywh2xyxy(box, img_w, img_h):
    x_c, y_c, w, h = box
    x1 = int((x_c - w / 2) * img_w)
    y1 = int((y_c - h / 2) * img_h)
    x2 = int((x_c + w / 2) * img_w)
    y2 = int((y_c + h / 2) * img_h)
    return [x1, y1, x2, y2]

def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def box_area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)

def euclidean_dist(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

def select_answer(marked_box, answer_boxes):
    if not marked_box or not answer_boxes:
        return None
    m_center = box_center(marked_box)
    close_answers = [
        (box, euclidean_dist(box_center(box), m_center))
        for box in answer_boxes
    ]
    filtered = [box for box, dist in close_answers if dist <= distance_threshold]
    return (
        min(filtered, key=box_area) if filtered
        else min(answer_boxes, key=lambda b: euclidean_dist(box_center(b), m_center))
    )
def crop_selected_answers(original_image_dir, label_dir, output_dir="answer_crops_selected"):
    import os
    import cv2
    import numpy as np

    def xywh2xyxy(box, img_w, img_h):
        x_c, y_c, w, h = box
        x1 = int((x_c - w / 2) * img_w)
        y1 = int((y_c - h / 2) * img_h)
        x2 = int((x_c + w / 2) * img_w)
        y2 = int((y_c + h / 2) * img_h)
        return [x1, y1, x2, y2]

    def box_center(box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def box_area(box):
        x1, y1, x2, y2 = box
        return (x2 - x1) * (y2 - y1)

    def euclidean_dist(c1, c2):
        return np.linalg.norm(np.array(c1) - np.array(c2))

    def select_answer(marked_box, answer_boxes):
        if not marked_box or not answer_boxes:
            print("❗ marked 또는 answer 없음")
            return None
        m_center = box_center(marked_box)
        close_answers = [
            (box, euclidean_dist(box_center(box), m_center))
            for box in answer_boxes
        ]
        filtered = [box for box, dist in close_answers if dist <= 500]  # 일단 threshold 크게
        return (
            min(filtered, key=box_area) if filtered
            else min(answer_boxes, key=lambda b: euclidean_dist(box_center(b), m_center))
        )

    os.makedirs(output_dir, exist_ok=True)

    for label_file in sorted(os.listdir(label_dir)):
        base_name = os.path.splitext(label_file)[0]

        # 이미지 찾기
        image_path = next(
            (os.path.join(original_image_dir, base_name + ext)
             for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
             if os.path.exists(os.path.join(original_image_dir, base_name + ext))),
            None
        )
        if not image_path:
            print(f"[❌ 이미지 없음] {base_name}")
            continue

        print(f"[🔍 처리 중] {base_name} → 이미지: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            print(f"[❌ 이미지 로딩 실패] {image_path}")
            continue

        h, w = img.shape[:2]

        with open(os.path.join(label_dir, label_file), 'r') as f:
            lines = f.readlines()

        marked_boxes = []
        answer_boxes = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            cls, xc, yc, bw, bh = map(float, parts[:5])
            box = xywh2xyxy((xc, yc, bw, bh), w, h)
            if int(cls) == 0:
                marked_boxes.append(box)
            elif int(cls) == 1:
                answer_boxes.append(box)

        print(f"→ marked: {len(marked_boxes)}, answer: {len(answer_boxes)}")

        for i, marked_box in enumerate(marked_boxes):
            selected = select_answer(marked_box, answer_boxes)
            if selected:
                x1, y1, x2, y2 = map(int, selected)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = img[y1:y2, x1:x2]
                crop_name = f'{base_name}_answer_{i}.jpg'
                save_path = os.path.join(output_dir, crop_name)
                cv2.imwrite(save_path, crop)
                print(f"[✔️ 저장] {save_path}")
            else:
                print(f"[⚠️ 선택된 answer 없음] {base_name}_{i}")


