def crop_selected_answers(original_image_dir, label_dir, output_dir):
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
        if marked_box and answer_boxes:
            m_center = box_center(marked_box)
            close_answers = [
                (box, cls, conf, euclidean_dist(box_center(box), m_center))
                for (box, cls, conf) in answer_boxes
            ]
            filtered = [(box, cls, conf) for (box, cls, conf, dist) in close_answers if dist <= 500]
            if filtered:
                return max(filtered, key=lambda x: x[2])  # conf 높은 것
            else:
                return max(answer_boxes, key=lambda x: x[2])  # fallback
        elif answer_boxes:
            return max(answer_boxes, key=lambda x: x[2])  # marked 없어도 하나 선택
        else:
            return None

    class_name_map = {
        1: "number",
        2: "english"
    }

    for label_file in sorted(os.listdir(label_dir)):
        base_name = os.path.splitext(label_file)[0]

        image_path = next(
            (os.path.join(original_image_dir, base_name + ext)
             for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
             if os.path.exists(os.path.join(original_image_dir, base_name + ext))),
            None
        )
        if not image_path:
            print(f"[이미지 없음] {base_name}")
            continue

        print(f"[처리 중] {base_name} → 이미지: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            print(f"[이미지 로딩 실패] {image_path}")
            continue

        h, w = img.shape[:2]

        with open(os.path.join(label_dir, label_file), 'r') as f:
            lines = f.readlines()

        marked_boxes = []
        answer_boxes = []

        for line in lines:
            parts = line.strip().split()
            if len(parts) < 6:
                continue
            cls, xc, yc, bw, bh, conf = map(float, parts[:6])
            box = xywh2xyxy((xc, yc, bw, bh), w, h)
            if int(cls) == 0:
                marked_boxes.append(box)
            elif int(cls) in [1, 2]:
                answer_boxes.append((box, int(cls), conf))

        print(f"→ marked: {len(marked_boxes)}, answer: {len(answer_boxes)}")

        saved = False

        for i, marked_box in enumerate(marked_boxes):
            if saved:
                break

            selected = select_answer(marked_box, answer_boxes)
            if selected:
                box, cls, _ = selected
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = img[y1:y2, x1:x2]
                label_name = class_name_map.get(cls, "unknown")
                save_dir = os.path.join(output_dir, label_name)
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'{base_name}.jpg')
                cv2.imwrite(save_path, crop)
                print(f"[✔️ 저장] {save_path} (class {cls})")
                saved = True

        # marked가 없거나 아무 것도 저장되지 않은 경우 answer_box 중 conf 높은 것 저장
        if not saved and answer_boxes:
            selected = max(answer_boxes, key=lambda x: x[2])  # conf 가장 높은 것
            box, cls, _ = selected
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            crop = img[y1:y2, x1:x2]
            label_name = class_name_map.get(cls, "unknown")
            save_dir = os.path.join(output_dir, label_name)
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f'{base_name}.jpg')
            cv2.imwrite(save_path, crop)
            print(f"[✔️ (fallback 저장)] {save_path} (class {cls})")
