from paddleocr import PaddleOCR
import os
import re
from PIL import Image

ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    det_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_det_infer',
    rec_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_rec_infer'
)

def sa_answer(crop_dir):
    
    predictions = {}
    #이미지 확장자 모두 불러오기
    exts = ('.jpg', '.jpeg', '.png', '.bmp')

    #문제 번호 숫자 추출
    def extract_number(filename):
        match = re.match(r'(\d+)', filename)
        return int(match.group(1)) if match else float('inf')

    #이미지 파일들 가져오기
    images = [f for f in os.listdir(crop_dir) if f.lower().endswith(exts)]
    images.sort(key=extract_number)

    for filename in images:
        img_path = os.path.join(crop_dir, filename)

        try:
            Image.open(img_path).verify()
        except Exception as e:
            print(f"{filename} → 이미지 열기 실패: {e}")
            continue
        
        #답에 ocr 적용해서 읽기
        result = ocr.ocr(img_path)
        
        #ocr 결과에서 좌표를 제외하고 읽은 문자만 불러오기
        extracted = ""
        if result and isinstance(result[0], list):
            for line in result[0]:
                extracted += line[1][0]
       
        #dictionary 키를 '%번 문제'로 바꾸기기
        match = re.match(r'(\d+)', filename)
        if match:
            question_key = f"{int(match.group(1))}번 문제"
        else:
            question_key = filename
            
        #dictionary에 저장하기
        predictions[question_key] = extracted.strip()

    return predictions
