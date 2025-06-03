# 스마트폰으로 이미지 캡처 후 데이터로 변환

# 라즈베리파이에서 먼저 수행해야 할 것 (구글 드라이브 연동을 위해)
# 1. 아이폰에 구글 드라이브 앱 설치

# 2. 설정 -> 사진 -> google photos 백업 활성화

# 3. 라즈베리파이에 rclone 설치
#   sudo apt update
#   sudo apt install rclone -y

# 4. rclone config 설정 (지피티 참고)

import os
import time
import subprocess

def capture_exam_images(page_count,                             # 총 채점할 시험지 수
                         gdrive_dir="gdrive:시험지업로드",        # 구글드라이브 원격 경로.(수정 필요)
                         rasp_dir="/home/pi/exam_images"):      # 시험지가 저장될 라즈베리파이 경로.(수정 필요)

    os.makedirs(rasp_dir, exist_ok=True)
    downloaded = set()      # 다운로드 된 이미지 및 변경 파일 추적
    image_paths = []        # 최종 이미지 리스트
    paper_idx = 1           # 페이지 index

    while len(image_paths) < page_count:                                                    # 모든 시험지가 촬영될 때까지 반복
        subprocess.run(["rclone", "copy", gdrive_dir, rasp_dir, "--update"], check=True)    # 동기화: 구글드라이브 → 로컬 폴더
        # --update : 최신 파일이 있을 때만 rasp_dir → gdrive_dir로 copy

        files = [f for f in os.listdir(rasp_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]      # rasp_dir 경로 내 이미지 파일만 리스트로 추출

        for fname in sorted(files):                                     # 리스트 내의 파일명들에 대해 (이름순으로 정렬한다는데 이러면 들어온 순서 안 섞이나?)
            full_path = os.path.join(rasp_dir, fname)                   # 해당 경로 + 파일명 합치기
            if fname.startswith("exam_") or fname in downloaded:        # 이전에 처리한 파일은 생략
                continue                 
            new_name = f"exam_{paper_idx}.jpg"                          # 페이지 이름 변경
            new_path = os.path.join(rasp_dir, new_name)                 # 이름에 맞게 경로 수정

            os.rename(full_path, new_path)                              # 파일 바꾸기
            image_paths.append(new_path)                                # 리스트에 추가
            downloaded.add(new_name)                                    # 이미 처리한 파일이라고 등록
            paper_idx += 1                                              # 다음 페이지

        if len(image_paths) < page_count:
            print(f"{page_count}장 중 {len(image_paths)}장 입력")
            time.sleep(3)                                               # 3초 후 재확인

    print(f"시험지 {page_count}장 모두 입력.")
    # return image_paths