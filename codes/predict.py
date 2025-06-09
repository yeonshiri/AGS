import torch
import os
import cv2
import re
import numpy as np
from .num_model import CRNN

# 문자셋 정의
charset = "0123456789"

# 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 하이퍼파라미터 정의
nclass = 10 + 1  # 숫자 0~9 + CTC blank
nh = 256

# 디코딩 함수
def ctc_decode(pred):
    pred = pred.argmax(dim=2).permute(1, 0)
    results = []
    for seq in pred:
        s = ""
        prev = -1
        for i in seq:
            i = i.item()
            if i != prev and i != len(charset):
                s += charset[i]
            prev = i
        results.append(s)
    return results

# 전처리 함수
def preprocess_image_like_dataset(path, img_size=(64, 64)):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, img_size)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    img_tensor = torch.tensor(img).unsqueeze(0)
    return img_tensor

# 예측 함수
def predict_all(image_dir="images", weight_path="num_v3.pth"):
    model = CRNN(imgH=64, nc=1, nclass=nclass, nh=nh).to(device)
    state_dict = torch.load(weight_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    predictions = {}
    image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith((".png", ".jpg"))])

    for fname in image_files:
        path = os.path.join(image_dir, fname)
        input_tensor = preprocess_image_like_dataset(path)

        # 문제 번호 키 생성
        name_only = os.path.splitext(fname)[0]
        if "_" not in name_only and name_only.isdigit():
            key = f"{name_only}번 문제"
        else:
            key = fname

        if input_tensor is None:
            predictions[key] = "❌ 이미지 로드 실패"
            continue

        input_tensor = input_tensor.to(device)

        with torch.no_grad():
            pred = model(input_tensor)
            pred_str = ctc_decode(pred.cpu())[0]

        predictions[key] = pred_str

    return predictions

