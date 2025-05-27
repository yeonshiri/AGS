import os
import glob
from detector import parse_yolo_label
from grading.objective import predict_answer_objective
from grading.subjective import extract_texts_from_cropped_answers


def run_prediction_objective(label_dir):
    """
    모든 문제에 대해 예측된 객관식 보기 번호를 반환한다.
    Returns:
        dict: { "5.jpg": 3, "6.jpg": 2, ... }
    """
    label_files = sorted(glob.glob(os.path.join(label_dir, "*.txt")))
    predictions = {}

    for label_path in label_files:
        filename = os.path.splitext(os.path.basename(label_path))[0] + ".jpg"
        boxes = parse_yolo_label(label_path)
        predicted = predict_answer_objective(boxes)
        predictions[filename] = predicted

    return predictions


def run_prediction_subjective_from_crop(crop_dir, correct_answers):
    """
    crops/answer_box 디렉토리에서 OCR 수행 후 정답 비교
    
    Parameters:
        crop_dir (str): YOLOv5 crop된 이미지 경로 (예: runs/detect/answerbox_detect/crops/answer_box)
        correct_answers (dict): { "1.jpg": "세포", "2.jpg": "뉴런", ... }

    Returns:
        dict: {
            "1.jpg": { "answer": "세포", "correct": True },
            ...
        }
    """
    predictions = {}
    ocr_results = extract_texts_from_cropped_answers(crop_dir)

    for filename, extracted_text in ocr_results.items():
        correct = correct_answers.get(filename)
        if correct is None:
            continue

        is_correct = extracted_text.strip() == correct.strip()
        predictions[filename] = {
            "answer": extracted_text,
            "correct": is_correct
        }

    return predictions
