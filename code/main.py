import os
from pathlib import Path

from roi import extract_roi_and_split
from detector import run_yolo_detect
from utils import capture_exam_images, compare_dictionary, load_answer_key, cleanup_directories, cleanup_yolo_exp
from grading.subjective import extract_texts_from_cropped_answers
from grading.objective import predict_answer_objective_dict

# 설정 경로
RAW_IMAGE_DIR = "input/raw_images"
OBJ_IMAGE_DIR = "input/objective"
SUBJ_IMAGE_DIR = "input/subjective"
SUB_CROP = "runs/detect/answerbox_detect/crops/answer_box"
ANSWER_KEY_PATH = "data/answer_key.json"
ROI_WEIGHT = "weights/roi.pt"   # 경로 오탈자 수정 (weight → weights)
SA_WEIGHT =  "weights/sa.pt"
MC_WEIGHT =  "weights/mc.pt"


def main():
    cleanup_directories([
    OBJ_IMAGE_DIR,
    SUBJ_IMAGE_DIR,
    SUB_CROP,
    "runs/detect/roi_detect",
    "runs/detect/objective_detect",
    "runs/detect/answerbox_detect"
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
    print("\n🚀 객관식 YOLO detect 시작")
    label_dir_obj, _ = run_yolo_detect(
        weights_path= MC_WEIGHT,
        image_dir=OBJ_IMAGE_DIR,
        img_size=640,
        conf=0.5,
        save_crop=False,
        name="objective_detect"
    )

    # 5. 주관식 문제 영역 YOLO 탐지 + crop 저장
    print("\n🚀 주관식 YOLO detect 시작")
    _, label_subj = run_yolo_detect(
        weights_path=SA_WEIGHT,
        image_dir=SUBJ_IMAGE_DIR,
        img_size=640,
        conf=0.5,
        save_crop=True,
        name="answerbox_detect"
    )

    # 6. 답안 예측
    print("\n📋 답안 예측 중...")

    student_answers = predict_answer_objective_dict(label_dir_obj)
    student_answers.update(extract_texts_from_cropped_answers(SUB_CROP))

    print(student_answers)
    # 7. 채점
    print("\n📝 채점 시작")
    final_score = compare_dictionary(answer_key, student_answers)

    # 8. 이미지 정리 여부 확인
    confirm = input("채점 완료. 이미지 데이터를 삭제할까요? (y/n): ")
    if confirm.lower() == "y":
        cleanup_directories([
            OBJ_IMAGE_DIR,
            SUBJ_IMAGE_DIR,
            SUB_CROP,
            "runs/detect/roi_detect",
            "runs/detect/objective_detect",
            "runs/detect/answerbox_detect"
        ])

    cleanup_yolo_exp()  # ← exp, exp1, exp2 등 삭제
    print("🧹 이미지 및 YOLO 결과 초기화 완료.")
    
if __name__ == "__main__":
    main()
