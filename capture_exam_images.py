import os
import time
import json
import subprocess

def capture_exam_images(page_count,                             # 총 채점할 시험지 수
                         gdrive_dir="gdrive:ags_image",         # 구글드라이브 원격 경로
                         rasp_dir="./data/image/raw_images"):   # 시험지가 저장될 라즈베리파이 경로

    os.makedirs(rasp_dir, exist_ok=True)
    image_paths = []        # 최종 이미지 리스트
    paper_idx = 1           # 페이지 index

    result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)
    file_list = json.loads(result.stdout)
    existing_files = set(f['Name'] for f in file_list)

    print(f"구글 드라이브 기존 파일 개수 : {len(existing_files)}")

    while len(image_paths) < page_count:                                                                # 모든 시험지가 촬영될 때까지 반복
        result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)

        file_list = json.loads(result.stdout)       # 구글 드라이브에서 파일 목록 가져오기

        new_files = sorted([
            f['Name'] for f in file_list
            if f['Name'].lower().endswith(('.jpg', '.jpeg', '.png')) and f['Name'] not in existing_files
        ])       # 이미지 파일만 + 코드 실행 후에 촬영된 이미지만 가져오기

        if new_files:
            fname = new_files[0]                                 
            local_path = os.path.join(rasp_dir, fname)                  # 해당 경로 + 파일명 합치기
            subprocess.run(["rclone", "copyto", f"{gdrive_dir}/{fname}", local_path], check=True)       # 해당 파일 다운로드

            new_name = f"exam_{paper_idx}.jpg"                          # 페이지 이름 변경
            new_path = os.path.join(rasp_dir, new_name)                 # 이름에 맞게 경로 수정

            os.rename(local_path, new_path)                             # 파일 바꾸기
            image_paths.append(new_path)                                # 리스트에 추가
            paper_idx += 1                                              # 다음 페이지
            print(f"[download] : {fname} --> {new_name}")
            existing_files.add(fname)

        else:
            time.sleep(0.1)                                              # 2초 후 재확인

    print(f"시험지 {page_count}장 모두 입력.")
    # return image_paths