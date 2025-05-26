import subprocess
import os
import glob

def run_yolo_detect(weights_path, image_dir, img_size=640, conf=0.25):
    """
    yolov5/detect.py를 실행하고 최신 라벨 디렉토리 경로를 반환
    Returns:
        str: 생성된 labels 디렉토리 경로
    """
    print("🚀 YOLO detect 실행 중...")

    command = [
        "python", "detect.py",
        "--weights", weights_path,
        "--source", image_dir,
        "--img", str(img_size),
        "--conf", str(conf),
        "--save-txt",
        "--save-conf"
    ]

    subprocess.run(command, cwd="yolov5")

    exp_dirs = sorted(
        glob.glob("yolov5/runs/detect/exp*"), 
        key=os.path.getmtime
    )
    if not exp_dirs:
        raise FileNotFoundError("YOLO detect 결과 폴더가 생성되지 않았습니다. detect.py 실행 실패 가능성 있음.")

    label_dir = os.path.join(exp_dirs[-1], "labels")
    print(f"✅ detect 완료 → 라벨 경로: {label_dir}")
    return label_dir

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
