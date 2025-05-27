import subprocess
import os
import glob

def run_yolo_detect(weights_path, image_dir, img_size=640, conf=0.25,
                    save_crop=False, project="runs/detect", name="exp"):
    """
    yolov5/detect.py를 실행하고 최신 라벨 및 crop 디렉토리 경로를 반환
    Returns:
        (str, str): 라벨 디렉토리 경로, crop 디렉토리 경로 (없으면 None)
    """
    print("🚀 YOLO detect 실행 중...")

    command = [
        "python", "detect.py",
        "--weights", weights_path,
        "--source", image_dir,
        "--img", str(img_size),
        "--conf", str(conf),
        "--save-txt",
        "--save-conf",
        "--project", project,
        "--name", name,
        "--exist-ok"
    ]
    if save_crop:
        command.append("--save-crop")

    subprocess.run(command, cwd="yolov5")

    output_dir = os.path.join("yolov5", project, name)
    label_dir = os.path.join(output_dir, "labels")
    crop_dir = os.path.join(output_dir, "crops") if save_crop else None

    if not os.path.exists(label_dir):
        raise FileNotFoundError("YOLO detect 결과 라벨 폴더가 없습니다.")

    print(f"✅ detect 완료 → 라벨 경로: {label_dir}")
    if crop_dir and os.path.exists(crop_dir):
        print(f"📦 crop 경로: {crop_dir}")

    return label_dir, crop_dir

    


def parse_yolo_label(label_path):
    """
    YOLO 형식 라벨 파일을 파싱하여 클래스별 중심 좌표 목록을 반환

    Returns:
        dict: {
            'option_box': [(x, y), ...],
            'marked': [(x, y), ...]
        }
    """
    result = {
        'option_box': [],
        'marked': []
    }

    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # 잘못된 라인 무시
            cls_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])

            if cls_id == 0:  # 'option_box' 클래스
                result['option_box'].append((x_center, y_center))
            elif cls_id == 1:  # 'marked' 클래스
                result['marked'].append((x_center, y_center))

    return result
