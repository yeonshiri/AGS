from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='korean')

import os
import re
from PIL import Image

def extract_texts_from_cropped_answers(crop_dir):
    """
    crops/answer_box 디렉토리에서 OCR로 텍스트 추출
    Returns:
        dict: { "1.jpg": "세포", "2.jpg": "뉴런", ... }
    """
    predictions = {}
    valid_exts = ('.jpg', '.jpeg', '.png', '.bmp')

    def extract_number(filename):
        match = re.match(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    images = [f for f in os.listdir(crop_dir) if f.lower().endswith(valid_exts)]
    images.sort(key=extract_number)

    for filename in images:
        img_path = os.path.join(crop_dir, filename)

        try:
            Image.open(img_path).verify()
        except Exception as e:
            print(f"❌ {filename} → 이미지 열기 실패: {e}")
            continue

        result = ocr.ocr(img_path, cls=True)

        extracted = ""
        if result and isinstance(result[0], list):
            for line in result[0]:
                extracted += line[1][0]

        predictions[filename] = extracted.strip()

    return predictions
