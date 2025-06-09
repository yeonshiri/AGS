import os
import cv2
import glob
import numpy as np
import subprocess
import shutil


def extract_roi_and_split(
    input_dir,
    weights_path,
    output_mc_dir,
    output_sa_dir,
    img_size=960,
    conf_thres=0.4
):
    detect_output_dir = "data/detect/roi_detect"
    if os.path.exists(detect_output_dir):
        shutil.rmtree(detect_output_dir)
    # YOLOv5 detect.py 실행
    
    subprocess.run([
    "python", "yolov5/detect.py",
    "--weights", weights_path,
    "--source", input_dir,
    "--img", str(img_size),
    "--conf", str(conf_thres),
    "--save-txt",
    # "--save-conf",  # ❌ 이 줄 삭제!
    "--project", "data/detect",
    "--name", "roi_detect",
    "--exist-ok"
    ])


    # 경로 설정
    label_dir = "data/detect/roi_detect/labels"
    image_dir = "data/detect/roi_detect"

    os.makedirs(output_mc_dir, exist_ok=True)
    os.makedirs(output_sa_dir, exist_ok=True)

    idx = 1
    for label_file in sorted(glob.glob(f"{label_dir}/*.txt")):
        base = os.path.splitext(os.path.basename(label_file))[0]
        img_path = os.path.join(input_dir, f"{base}.jpg")
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        rois = []
        with open(label_file, 'r') as f:
            for line in f:
                cls, x, y, bw, bh = map(float, line.strip().split()[:5])
                cx, cy = x * w, y * h
                x1 = int((x - bw/2) * w)
                y1 = int((y - bh/2) * h)
                x2 = int((x + bw/2) * w)
                y2 = int((y + bh/2) * h)
                rois.append({'class': int(cls), 'cx': cx, 'cy': cy, 'box': (x1, y1, x2, y2)})

        # 좌우로 나누고 상하 정렬
        cx_mean = np.mean([r['cx'] for r in rois])
        left = sorted([r for r in rois if r['cx'] < cx_mean], key=lambda r: r['cy'])
        right = sorted([r for r in rois if r['cx'] >= cx_mean], key=lambda r: r['cy'])
        sorted_rois = left + right

        for roi in sorted_rois:
            x1, y1, x2, y2 = roi['box']
            crop = img[y1:y2, x1:x2]
            save_dir = output_mc_dir if roi['class'] == 0 else output_sa_dir
            save_path = os.path.join(save_dir, f"{idx}.jpg")
            cv2.imwrite(save_path, crop)
            print(f"[✅] Saved {save_path}")
            idx += 1

    print("\n ROI 저장 완료.")
