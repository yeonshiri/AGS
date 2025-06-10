import os
from pathlib import Path

from codes.roi import extract_roi_and_split
from codes.detector import yolo_detect
from codes.utils import capture_exam_images, compare_dictionary, load_answer_key, cleanup_directories, compare_and_show_gui
from codes.grading.subjective import  sa_answer_eng
from codes.grading.objective import mc_answer
from codes.sa_roi import crop_selected_answers  # post-processing 로직 import
from codes.predict import predict_all

# 설정 경로
RAW_IMAGE_DIR = "data/image/raw_images"
OBJ_IMAGE_DIR = "data/image/objective"  
SUBJ_IMAGE_DIR = "data/image/subjective"
SUB_CROP = "data/detect/answerbox_detect/crops"
SUB_CROP_NUM = "data/detect/answerbox_detect/crops/number"
SUB_CROP_ENG = "data/detect/answerbox_detect/crops/english"
ANSWER_KEY_PATH = "data/answer/answer_key.json"
ROI_WEIGHT = "data/weights/roi_fine.pt"   
SA_WEIGHT =  "data/weights/sa_fine.pt"
MC_WEIGHT =  "data/weights/mc_fine.pt"
NUM_WEIGHT = "data/weights/num_fine.pth"
image_exts = ('.jpg', '.jpeg', '.png', '.bmp')

def main():
    #0 data 파일 초기화 후 진행
    cleanup_directories([
    SUBJ_IMAGE_DIR,
    OBJ_IMAGE_DIR,
    "data/detect"
    ])
    student_answers = {}
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
    if(any(file.lower().endswith(image_exts) for file in os.listdir(OBJ_IMAGE_DIR))):
        print("\n 객관식 YOLO detect 시작")
        i=1
        mc_label, _ = yolo_detect(
            weights= MC_WEIGHT,
            image=OBJ_IMAGE_DIR,
            img_size=640,
            conf=0.5,
            save_crop=False,
            name="objective_detect"
        )
    else:
        print("객관식 이미지 없음")
        mc_label = []  # 빈 결과라도 정의해두는 게 안전함
        
    # 5. 주관식 문제 영역 YOLO 탐지, crop 저장
    if any(file.lower().endswith(image_exts) for file in os.listdir(SUBJ_IMAGE_DIR)):
        print("\n 주관식 YOLO detect 시작")

        # 1. YOLO detect (save_crop 없이)
        sa_label, _ = yolo_detect(
            weights=SA_WEIGHT,
            image=SUBJ_IMAGE_DIR,
            img_size=640,
            conf=0.4,
            save_crop=False,  # ❌ crop하지 말고 결과 라벨만 저장
            name="answerbox_detect"
        )

        # 2. marked-answer 관계 기반 후처리 → crop 수행
        crop_selected_answers(
            original_image_dir=SUBJ_IMAGE_DIR,
            label_dir=sa_label,
            output_dir=SUB_CROP
        )

    else:
        print("단답형 이미지 없음")
        sa_label = []

    # 6. 답안 예측
    print("\n 답안 정리 중")

    try:
        if i:
            student_answers.update(mc_answer(mc_label))
    except Exception as e:
        print("객관식 오류")
        
    num_crop_dir = Path(SUB_CROP_NUM)
    eng_crop_dir = Path(SUB_CROP_ENG)
           
    if num_crop_dir.exists() and any(f.suffix.lower() in ['.jpg', '.jpeg', '.png'] for f in num_crop_dir.iterdir()):
        print("\n🔢 숫자 인식 시작")
        student_answers.update(predict_all(image_dir=SUB_CROP_NUM,weight_path=NUM_WEIGHT))
    else:
        print("⚠️ 숫자 답안 없음")
        
    if eng_crop_dir.exists() and any(f.suffix.lower() in ['.jpg', '.jpeg', '.png'] for f in eng_crop_dir.iterdir()):
        print("\n🔢 영어 인식 시작")
        try:
            student_answers.update(sa_answer_eng(SUB_CROP_ENG))
        except Exception as e:
            print("❌ 영어 인식 오류:", e)
    else:
        print("⚠️ 영어 답안 없음")
            
    compare_and_show_gui(answer_key, student_answers)

    
if __name__ == "__main__":
    main()
