import os
import glob
from detector import parse_yolo_label
from grading.objective import predict_answer_objective

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
