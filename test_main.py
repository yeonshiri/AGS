from detector import run_yolo_detect
from grader import run_prediction_objective
import os, glob

IMAGE_DIR = "input/objective_images"
WEIGHTS_PATH = "weights/mc.pt"

def main():
    label_dir = run_yolo_detect(WEIGHTS_PATH, IMAGE_DIR)
    predictions = run_prediction_objective(label_dir)

    print("✅ 예측 결과:\n")
    image_files = sorted(glob.glob(os.path.join(IMAGE_DIR, "*.jpg")))

    for image_path in image_files:
        filename = os.path.basename(image_path)
        pred = predictions.get(filename)
        if pred is None:
            print(f"❌ {filename}: 예측 실패 (라벨 없음)")
        else:
            print(f"✅ {filename}: 선택된 보기 → {pred}")

if __name__ == "__main__":
    main()
