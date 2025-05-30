import os
from pathlib import Path

from codes.roi import extract_roi_and_split
from codes.detector import yolo_detect
from codes.utils import capture_exam_images, compare_dictionary, load_answer_key, cleanup_directories
from codes.grading.subjective import sa_answer
from codes.grading.objective import mc_answer

# 설정 경로
RAW_IMAGE_DIR = "data/image/raw_images"
OBJ_IMAGE_DIR = "data/image/objective"
SUBJ_IMAGE_DIR = "data/image/subjective"
SUB_CROP = "data/detect/answerbox_detect/crops/answer_box"
ANSWER_KEY_PATH = "data/answer/answer_key.json"
ROI_WEIGHT = "data/weights/roi.pt"   
SA_WEIGHT =  "data/weights/sa.pt"
MC_WEIGHT =  "data/weights/mc.pt"


def main():
    #0 data 파일 초기화 후 진행
    cleanup_directories([
    SUBJ_IMAGE_DIR,
    OBJ_IMAGE_DIR,
    "data/detect"
    ])
    
    # 1. 시험지 촬영
    image_dir = [
        os.path.join(RAW_IMAGE_DIR, f)
        for f in sorted(os.listdir(RAW_IMAGE_DIR))
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
    ]

    # 2. ROI 추출 및 분리
    extract_roi_and_split(
        input_dir=RAW_IMAGE_DIR,       
        weights_path=ROI_WEIGHT,          
        output_mc_dir=OBJ_IMAGE_DIR,
        output_sa_dir=SUBJ_IMAGE_DIR
    )


    # 3. 정답 불러오기
    answer_key = load_answer_key(ANSWER_KEY_PATH)

    # 4. 객관식 문제 영역 YOLO 탐지
    print("\n 객관식 YOLO detect 시작")
    mc_label, _ = yolo_detect(
        weights= MC_WEIGHT,
        image=OBJ_IMAGE_DIR,
        img_size=640,
        conf=0.5,
        save_crop=False,
        name="objective_detect"
    )

    # 5. 주관식 문제 영역 YOLO 탐지, crop 저장
    print("\n 주관식 YOLO detect 시작")
    _, label_subj = yolo_detect(
        weights=SA_WEIGHT,
        image=SUBJ_IMAGE_DIR,
        img_size=640,
        conf=0.5,
        save_crop=True,
        name="answerbox_detect"
    )

    # 6. 답안 예측
    print("\n 답안 정리 중")

    student_answers = mc_answer(mc_label)
    student_answers.update(sa_answer(label_subj))
    print("\n 답안: ")
    print(student_answers)
    print("\n 정답답: ")
    print(answer_key)
    # 7. 채점
    print("\n 채점 시작")
    final_score = compare_dictionary(answer_key, student_answers)

    
if __name__ == "__main__":
    main()
