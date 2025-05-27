# full shot 시험지 ROI로 자르기 (객관식, 단답형 구분)

import cv2
import os
import glob
import numpy as np
import subprocess
import sys

def extract_roi_and_split(image_paths):
    # best_path = f"/home/pi/bbox_full_exam/best.pt"      # 라즈베리파이에 맞게 수정
    best_path = f"C:/Users/5004b/embedded/best/best.pt"     # 데탑 로컬 경로
    input_dir = os.path.dirname(image_paths[0])

    # yolov5n으로 bbox 추론
    python_exe = sys.executable  # 현재 사용 중인 파이썬 인터프리터 경로
    yolov5_dir = "C:/Users/5004b/embedded/yolov5"
    detect_script = os.path.join(yolov5_dir, "detect.py")

    subprocess.run([
        python_exe, detect_script,
        "--weights", best_path,
        "--img", "960",
        "--conf", "0.4",
        "--source", input_dir,
        "--save-txt",
        "--save-conf"
    # ], cwd="yolov5")
    ], cwd=yolov5_dir, capture_output=True, text=True)        # 데탑 로컬 경로

    # runs/detect 하위의 exp* 폴더 모두 찾기
    # exp_folders = glob.glob('/home/pi/yolov5/runs/detect/exp*')       # 라즈베리파이에 맞게 수정
    exp_folders = glob.glob('C:/Users/5004b/embedded/yolov5/runs/detect/exp*')       # 데탑 로컬 경로
    latest_exp = max(exp_folders, key=os.path.getmtime)

    # 이미지 경로 설정
    # output_mc_dir = '/home/pi/multiple_choice_roi'
    # output_sa_dir = '/home/pi/short_answer_roi'
    output_mc_dir = 'C:/Users/5004b/embedded/multiple_choice_roi'       # 데탑 로컬 경로
    output_sa_dir = 'C:/Users/5004b/embedded/short_answer_roi'       # 데탑 로컬 경로
    os.makedirs(output_mc_dir, exist_ok=True)
    os.makedirs(output_sa_dir, exist_ok=True)

    # 페이지 번호 카운트 (페이지 넘어도 문제 번호 연속성 유지)
    page_idx = 1

    for image_path in sorted(image_paths):  # 정렬된 이미지 순서대로 진행
        image_filename = os.path.basename(image_path)
        image_basename = os.path.splitext(image_filename)[0]

        # 이미지 및 라벨 경로
        label_path = os.path.join(latest_exp, 'labels', f'{image_basename}.txt')
        if not os.path.exists(label_path):
            print(f"라벨 없음: {label_path}")
            continue

        # 이미지 로드
        image = cv2.imread(image_path)
        h, w = image.shape[:2]

        # 라벨 로딩 및 ROI 복원
        rois = []
        with open(label_path, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                cls_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:5])
                cx_abs = x_center * w
                cy_abs = y_center * h
                x1 = int((x_center - width / 2) * w)
                y1 = int((y_center - height / 2) * h)
                x2 = int((x_center + width / 2) * w)
                y2 = int((y_center + height / 2) * h)
                rois.append({
                    'class': cls_id,
                    'cx': cx_abs,
                    'cy': cy_abs,
                    'coords': (x1, y1, x2, y2)
                })

        # 좌우 정렬 및 상하 정렬 (페이지마다 일관되게)
        rois_arr = np.array([[r['class'], r['cx'], r['cy']] for r in rois])
        x_threshold = np.mean(rois_arr[:, 1])
        left_col = [r for r in rois if r['cx'] < x_threshold]
        right_col = [r for r in rois if r['cx'] >= x_threshold]
        left_sorted = sorted(left_col, key=lambda r: r['cy'])
        right_sorted = sorted(right_col, key=lambda r: r['cy'])
        sorted_rois = left_sorted + right_sorted

        # ROI 저장
        for roi in sorted_rois:
            x1, y1, x2, y2 = roi['coords']
            roi_img = image[y1:y2, x1:x2]
            if roi['class'] == 0:       # 객관식
                qtype = "multiple_choice"
                save_dir = output_mc_dir
            else:                       # 단답형
                qtype = "short_answer"
                save_dir = output_sa_dir

            roi_filename = f"{qtype}_{page_idx}.jpg"
            roi_path = os.path.join(save_dir, roi_filename)
            cv2.imwrite(roi_path, roi_img)
            # success = cv2.imwrite(roi_path, roi_img)
            # if success:
            #     print(f"[✅] 저장됨: {roi_path}")           # 저장 디버깅용
            # else:
            #     print(f"[❌] 저장 실패: {roi_path} (크기: {roi_img.shape if roi_img is not None else 'None'})")
            page_idx += 1

    print(f"모든 이미지에서 ROI 총 {page_idx - 1}개 생성.")
    return output_mc_dir, output_sa_dir