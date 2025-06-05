import os
import re
import torch
import cv2
from paddleocr import PaddleOCR
from PIL import Image
from torchvision import transforms
import torch.nn as nn

ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    det_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_det_infer',
    rec_model_dir='/home/pi/paddleocr_lite/inference/en_PP-OCRv3_rec_infer'
)

def sa_answer_eng(crop_dir):
    
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
        result = ocr.ocr(img_path) #라즈베리파이에서 cls 삭제제
        
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



# CRNN 모델 정의
class CRNN(nn.Module):
    def __init__(self, num_classes=100):
        super(CRNN, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.rnn = nn.LSTM(64 * 25, 128, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(128 * 2, num_classes)

    def forward(self, x):
        x = self.cnn(x)
        b, c, h, w = x.size()
        x = x.permute(0, 3, 1, 2).contiguous().view(b, w, c * h)
        x, _ = self.rnn(x)
        x = x[:, -1, :]
        return self.fc(x)

# 숫자 인식 함수
def sa_answer_num(image_dir, model_path, device="cpu"):
    device = torch.device(device)

    # 전처리
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Grayscale(),
        transforms.Resize((100, 100)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # 모델 로드
    model = CRNN(num_classes=100)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    predictions = {}

    for file in sorted(os.listdir(image_dir)):
        if not file.lower().endswith(('.jpg', '.png', '.jpeg')):
            continue

        img_path = os.path.join(image_dir, file)
        img = cv2.imread(img_path)
        if img is None:
            print(f"[❌ 로딩 실패] {img_path}")
            continue

        input_tensor = transform(img).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(input_tensor)
            predicted_class = outputs.argmax(dim=1).item()

        # 🔑 문제 번호 추출해서 key로 사용
        match = re.match(r"(\d+)", file)
        if match:
            question_key = f"{int(match.group(1))}번 문제"
        else:
            question_key = file  # fallback

        predictions[question_key] = predicted_class
        print(f"[🔢 인식] {file} → {predicted_class} → {question_key}")

    return predictions