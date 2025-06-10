import subprocess
import os
import glob
from pathlib import Path

# detect.py 실행하기기
def yolo_detect(weights, image, img_size=640, conf=0.25,
                    save_crop=False, project="data/detect", name="exp"):
    
    # detect.py 경로 명시적으로 지정
    cwd = Path(__file__).resolve().parent.parent   # AGS/  
    detect_path = cwd / "yolov5" / "detect.py"

    command = [
        "python", detect_path,
        "--weights", weights,
        "--source", image,
        "--img", str(img_size),
        "--conf", str(conf),
        "--save-txt",
        "--save-conf",
        "--project", project,
        "--name", name,
        "--exist-ok"
    ]
    if save_crop:  #detect 이미지가 따로 crop되어서 필요한 경우
        command.append("--save-crop")

    #detect.py를 터미널이 아닌 코드로 실행하기 위한 코드
    subprocess.run(command, cwd=cwd)    

    #저장되는 경로 위차 지정
    output_dir =  Path(project) / name
    label_dir = output_dir / "labels"
    crop_dir = output_dir / "crops" if save_crop else None

    #예외 처리
    if not label_dir.exists():
        raise FileNotFoundError("YOLO detect 결과 라벨 폴더가 없습니다.")

    print("detect 완료")

    #label이 저장되는 위치와 crop이 된 사진 위치 전달
    return str(label_dir), str(crop_dir)


