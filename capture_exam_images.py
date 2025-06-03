import os
import time
import json
import subprocess
from datetime import datetime

def capture_exam_images(page_count,                             # 총 채점할 시험지 수
                         gdrive_dir="gdrive:ags_image",         # 구글드라이브 원격 경로
                         rasp_dir="./data/image/raw_images"):   # 시험지가 저장될 라즈베리파이 경로

    os.makedirs(rasp_dir, exist_ok=True)
    image_paths = []        # 최종 이미지 리스트
    paper_idx = 1           # 페이지 index

    # 기준 시점 (촬영 시작 전 시각 기준) → 파일명 비교용
    timestamp_baseline = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[기준 타임스탬프] {timestamp_baseline}")

    while len(image_paths) < page_count:                                                                # 모든 시험지가 촬영될 때까지 반복
        result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)

        file_list = json.loads(result.stdout)       # 구글 드라이브에서 파일 목록 가져오기

        new_files = [
            f['Name'] for f in file_list
            if f['Name'].lower().endswith(('.jpg', '.jpeg', '.png')) and f['Name'][:15] > timestamp_baseline
        ]       # 이미지 파일만 + 코드 실행 후에 촬영된 이미지만 가져오기

        for fname in sorted(new_files):                                 
            local_path = os.path.join(rasp_dir, fname)                  # 해당 경로 + 파일명 합치기
            if os.path.exists(local_path):
                continue                                                # 이미 다운로드된 파일이면 건너뜀  

            subprocess.run(["rclone", "copyto", f"{gdrive_dir}/{fname}", local_path], check=True)       # 해당 파일 다운로드

            new_name = f"exam_{paper_idx}.jpg"                          # 페이지 이름 변경
            new_path = os.path.join(rasp_dir, new_name)                 # 이름에 맞게 경로 수정

            os.rename(local_path, new_path)                             # 파일 바꾸기
            image_paths.append(new_path)                                # 리스트에 추가
            paper_idx += 1                                              # 다음 페이지

        if len(image_paths) < page_count:
            print(f"{page_count}장 중 {len(image_paths)}장 입력")
            time.sleep(2)                                               # 2초 후 재확인

    print(f"시험지 {page_count}장 모두 입력.")
    # return image_paths

# -----------------------------------------------------
# SMB 방식

# import os
# import time
# from datetime import datetime

# def capture_exam_images_from_shared(page_count,
#                                     shared_dir="/home/pi/shared"):  # SMB 공유 폴더 경로

#     os.makedirs(shared_dir, exist_ok=True)
#     downloaded = set()           # 처리된 파일명 추적
#     image_paths = []             # 최종 결과 리스트
#     paper_idx = 1                # exam_1, exam_2 이름 지정용

#     print(f"[시작] 공유 폴더 감시 시작: {shared_dir}")

#     while len(image_paths) < page_count:
#         # 공유 폴더 내 모든 이미지 파일 목록 (처리되지 않은 것만)
#         files = sorted([
#             f for f in os.listdir(shared_dir)
#             if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f not in downloaded
#         ])

#         for fname in files:
#             full_path = os.path.join(shared_dir, fname)
#             if not os.path.isfile(full_path):  # 혹시 디렉토리면 제외
#                 continue

#             new_name = f"exam_{paper_idx}.jpg"
#             new_path = os.path.join(shared_dir, new_name)

#             # 이름 변경
#             os.rename(full_path, new_path)

#             image_paths.append(new_path)
#             downloaded.add(new_name)
#             paper_idx += 1

#             print(f"[처리됨] {fname} → {new_name}")

#             if len(image_paths) >= page_count:
#                 break

#         if len(image_paths) < page_count:
#             print(f"{page_count}장 중 {len(image_paths)}장 감지됨. 대기 중...")
#             time.sleep(2)

#     print(f"[완료] 시험지 {page_count}장 모두 입력 완료.")
#     return image_paths
