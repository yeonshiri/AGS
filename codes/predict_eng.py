import os
import re
import torch
import cv2
from paddleocr import PaddleOCR
from PIL import Image
from torchvision import transforms
import torch.nn as nn
#paddleocr lite 불러오기
ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    det_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_det_infer',
    rec_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_rec_infer'
)

def sa_answer_eng(crop_dir):
    
    predictions = {}
    exts = ('.jpg', '.jpeg', '.png', '.bmp')

    def extract_number(filename):
        match = re.match(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    images = [f for f in os.listdir(crop_dir) if f.lower().endswith(exts)]
    images.sort(key=extract_number)

    for filename in images:
        img_path = os.path.join(crop_dir, filename)

        try:
            Image.open(img_path).verify()
        except Exception as e:
            print(f"{filename} → 이미지 열기 실패: {e}")
            continue
        #ocr 적용
        result = ocr.ocr(img_path)
        extracted = ""
        if result and isinstance(result[0], list):
            for line in result[0]:
                extracted += line[1][0]

        match = re.match(r'(\d+)', filename)
        if match:
            question_key = f"{int(match.group(1))}번 문제"
        else:
            question_key = filename

        predictions[question_key] = extracted.strip().lower()  # 이 부분에서 소문자 처리

    return predictions
