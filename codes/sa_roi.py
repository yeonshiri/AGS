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
        if not marked_box or not answer_boxes:
            return None
        m_center = box_center(marked_box)
        close_answers = [
            (box, cls, euclidean_dist(box_center(box), m_center))
            for (box, cls) in answer_boxes
        ]
        filtered = [(box, cls) for (box, cls, dist) in close_answers if dist <= 500]
        return (
            min(filtered, key=lambda x: box_area(x[0])) if filtered
            else min(answer_boxes, key=lambda x: euclidean_dist(box_center(x[0]), m_center))
        )

    # 클래스에 따라 하위 폴더 설정
    class_name_map = {
        1: "number",
        2: "english"
    }

    for label_file in sorted(os.listdir(label_dir)):
        base_name = os.path.splitext(label_file)[0]

        # 이미지 경로 탐색
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
            elif int(cls) in [1, 2]:  # 숫자/영어 답안
                answer_boxes.append((box, int(cls)))

        print(f"→ marked: {len(marked_boxes)}, answer: {len(answer_boxes)}")

        saved = False  # 중복 저장 방지

        for i, marked_box in enumerate(marked_boxes):
            if saved:
                break  # 하나만 저장하고 끝냄

            selected = select_answer(marked_box, answer_boxes)
            if selected:
                box, cls = selected
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                crop = img[y1:y2, x1:x2]

                # 클래스 이름 기반 저장 디렉토리
                label_name = class_name_map.get(cls, "unknown")
                save_dir = os.path.join(output_dir, label_name)
                os.makedirs(save_dir, exist_ok=True)

                crop_name = f'{base_name}.jpg'  # ← 원래 이미지 이름 사용
                save_path = os.path.join(save_dir, crop_name)
                cv2.imwrite(save_path, crop)
                print(f"[✔️ 저장] {save_path} (class {cls})")
                saved = True
            else:
                print(f"[⚠️ 선택된 answer 없음] {base_name}_{i}")
