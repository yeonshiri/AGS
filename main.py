import os
from pathlib import Path
from detector import load_model, detect_question_boxes, detect_choices
from ocr import extract_text_with_ocr
from grader import AutoGrader
from utils import (
    capture_exam_images,
    extract_roi_and_split,
    load_answer_key,
    cleanup_directories,
)

# 설정 경로
RAW_IMAGE_DIR = "input/raw_images"    #사진을 찍었을 때 저장이 되는 경로
OBJ_IMAGE_DIR = "input/objective"     #객관식 사진 저장 경로
SUBJ_IMAGE_DIR = "input/subjective"   #단답형 사진 저장 경로
ANSWER_KEY_PATH = "data/answer_key.json"   #답안지 저장장소 
WEIGHTS_PATH_QUESTION = "weights/question_box.pt"  #문제 추출 best.pt 
WEIGHTS_PATH_ANSWER_BOX = "weights/answer_box.pt"  #객관식 best.pt
WEIGHTS_PATH_CHOICE = "weights/option_box.pt"      #단답형 best.pt

def main():
    # 1. 시험지 촬영 및 저장
    capture_exam_images(output_dir=RAW_IMAGE_DIR)  # n장의 이미지 촬영하여 저장

    # 2. ROI 추출하여 객관식/단답형 구분 및 저장
    extract_roi_and_split(RAW_IMAGE_DIR, OBJ_IMAGE_DIR, SUBJ_IMAGE_DIR)

    # 3. 모델 및 정답 불러오기
    model_question = load_model(WEIGHTS_PATH_QUESTION)        # 문제 영역 추출용
    model_choice = load_model(WEIGHTS_PATH_CHOICE)            # 객관식 선지 감지용
    model_answer = load_model(WEIGHTS_PATH_ANSWER_BOX)        # 단답형 답안 박스 감지용
    answer_key = load_answer_key(ANSWER_KEY_PATH)

    # 4. 채점기 생성
    grader = AutoGrader(
    model_question=model_question,
    model_choice=model_choice,
    model_answer=model_answer,
    answer_key=answer_key
)

    # 5. 채점 실행
    final_score = grader.run(objective_dir=OBJ_IMAGE_DIR, subjective_dir=SUBJ_IMAGE_DIR)

    print(f"[RESULT] Final Score: {final_score}")

    # 6. 사용자 확인 시 초기화
    confirm = input("채점 완료. 이미지 데이터를 삭제할까요? (y/n): ")
    if confirm.lower() == "y":
        cleanup_directories([RAW_IMAGE_DIR, OBJ_IMAGE_DIR, SUBJ_IMAGE_DIR])
        print("이미지 초기화 완료.")

if __name__ == "__main__":
    main()
