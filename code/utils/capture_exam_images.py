# 스마트폰으로 이미지 캡처 후 데이터로 변환

# 라즈베리파이에서 먼저 수행해야 할 것 (구글 드라이브 연동을 위해)
# 1. 아이폰에 구글 드라이브 앱 설치

# 2. 설정 -> 사진 -> google photos 백업 활성화

# 3. 라즈베리파이에 rclone 설치
#   sudo apt update
#   sudo apt install rclone -y

# 4. rclone config 설정 (지피티 참고)

# -----------------------------------------------------

# import cv2
# import os

# def capture_exam_images(save_dir="/home/pi/yolov5/picture"):    # 저장 경로 라즈베리파이에 맞게 수정
#     os.makedirs(save_dir, exist_ok=True)
#     image_paths = []
#     paper_idx = 1

#     cap = cv2.VideoCapture(0)
#     print("s: 촬영, q: 중지")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("캡처 실패")
#             break

#         cv2.imshow("Test Paper Shot", frame)
#         key = cv2.waitKey(1)

#         if key == ord('s'):   # 's' 키를 누르면 저장
#             filename = f"exam_{paper_idx}.jpg"
#             save_path = os.path.join(save_dir, filename)
#             cv2.imwrite(save_path, frame)
#             image_paths.append(save_path)
#             paper_idx += 1

#         elif key == ord('q'):
#             print("촬영 종료")
#             break

#     print(f"시험지 {paper_idx-1}장 저장됨")
#     cap.release()
#     cv2.destroyAllWindows()
#     return image_paths

# -----------------------------------------------------

import os
import time
import subprocess

def capture_exam_images(page_count,                               # 총 채점할 시험지 수
                         gdrive_dir="gdrive:시험지업로드",          # 각 경로에 맞게 수정
                         rasp_dir="/home/pi/exam_images"):

    os.makedirs(rasp_dir, exist_ok=True)
    downloaded = set()
    image_paths = []
    paper_idx = 1

    while len(image_paths) < page_count:
        subprocess.run(["rclone", "copy", gdrive_dir, rasp_dir, "--update"], check=True)                  # 동기화: 구글드라이브 → 로컬 폴더

        files = [f for f in os.listdir(rasp_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]        # 폴더 내 이미지 파일 리스트

        for fname in sorted(files):                                     # 정렬해서 순서 유지
            full_path = os.path.join(rasp_dir, fname)
            if fname.startswith("exam_") or fname in downloaded:        # 새로운 이미지가 들어오면 리스트 추가
                continue                 
            new_name = f"exam_{paper_idx}.jpg"
            new_path = os.path.join(rasp_dir, new_name)

            os.rename(full_path, new_path)
            image_paths.append(new_path)
            downloaded.add(new_name)
            paper_idx += 1

        if len(image_paths) < page_count:
            print(f"{page_count}장 중 {len(image_paths)}장 입력")
            time.sleep(3)  # 3초 후 재확인

    print(f"시험지 {page_count}장 모두 입력.")
    return image_paths