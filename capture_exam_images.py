# import os
# import time
# import json
# import subprocess

# def capture_exam_images(page_count,                             # 총 채점할 시험지 수
#                          gdrive_dir="gdrive:ags_image",         # 구글드라이브 원격 경로
#                          rasp_dir="./data/image/raw_images"):   # 시험지가 저장될 라즈베리파이 경로

#     os.makedirs(rasp_dir, exist_ok=True)
#     image_paths = []        # 최종 이미지 리스트
#     paper_idx = 1           # 페이지 index

#     result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)
#     file_list = json.loads(result.stdout)
#     existing_files = set(f['Name'] for f in file_list)

#     print(f"구글 드라이브 기존 파일 개수 : {len(existing_files)}")

#     while len(image_paths) < page_count:                                                                # 모든 시험지가 촬영될 때까지 반복
#         result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)

#         file_list = json.loads(result.stdout)       # 구글 드라이브에서 파일 목록 가져오기

#         new_files = sorted([
#             f['Name'] for f in file_list
#             if f['Name'].lower().endswith(('.jpg', '.jpeg', '.png')) and f['Name'] not in existing_files
#         ])       # 이미지 파일만 + 코드 실행 후에 촬영된 이미지만 가져오기

#         if new_files:
#             fname = new_files[0]                                 
#             local_path = os.path.join(rasp_dir, fname)                  # 해당 경로 + 파일명 합치기
#             subprocess.run(["rclone", "copyto", f"{gdrive_dir}/{fname}", local_path], check=True)       # 해당 파일 다운로드

#             new_name = f"exam_{paper_idx}.jpg"                          # 페이지 이름 변경
#             new_path = os.path.join(rasp_dir, new_name)                 # 이름에 맞게 경로 수정

#             os.rename(local_path, new_path)                             # 파일 바꾸기
#             image_paths.append(new_path)                                # 리스트에 추가
#             paper_idx += 1                                              # 다음 페이지
#             print(f"[download] : {fname} --> {new_name}")
#             existing_files.add(fname)

#         else:
#             time.sleep(0.1)                                              # 2초 후 재확인

#     print(f"시험지 {page_count}장 모두 입력.")
#     # return image_paths

import os
import time
import json
import subprocess
import keyboard  # pip install keyboard

def capture_exam_images(page_count,
                         gdrive_dir="gdrive:ags_image",
                         rasp_dir="./data/image/raw_images"):

    os.makedirs(rasp_dir, exist_ok=True)
    image_paths = []
    paper_idx = 1

    print("[초기화] 구글 드라이브 폴더를 비우는 중...")

    # 구글 드라이브 폴더 내 모든 파일 삭제
    result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)
    file_list = json.loads(result.stdout)

    for f in file_list:
        fname = f['Name']
        subprocess.run(["rclone", "deletefile", f"{gdrive_dir}/{fname}"], check=True)

    print(f"[완료] 드라이브 폴더 초기화됨. 시험지를 업로드한 후 'k' 키를 누르세요.")

    # 사용자가 'k' 키 입력할 때까지 대기
    while True:
        if keyboard.is_pressed('k'):
            print("[입력 감지] 'k' 키가 눌렸습니다.")
            break
        time.sleep(0.1)

    # k 입력 시점 이후 구글 드라이브에 올라온 모든 이미지 파일 수집
    time.sleep(0.5)  # 약간의 업로드 여유시간
    result = subprocess.run(["rclone", "lsjson", gdrive_dir], capture_output=True, text=True)
    file_list = json.loads(result.stdout)

    image_files = sorted([
        f['Name'] for f in file_list
        if f['Name'].lower().endswith(('.jpg', '.jpeg', '.png'))
    ])

    print(f"[이미지 감지] 총 {len(image_files)}개의 이미지가 감지됨.")

    for fname in image_files:
        local_path = os.path.join(rasp_dir, fname)
        subprocess.run(["rclone", "copyto", f"{gdrive_dir}/{fname}", local_path], check=True)

        new_name = f"exam_{paper_idx}.jpg"
        new_path = os.path.join(rasp_dir, new_name)

        os.rename(local_path, new_path)
        image_paths.append(new_path)
        print(f"[download] : {fname} --> {new_name}")

        paper_idx += 1

    if len(image_paths) == page_count:
        print(f"[성공] 총 {page_count}장의 시험지가 정상적으로 입력되었습니다.")
    else:
        print(f"[오류] 예상한 {page_count}장과 실제 다운로드된 수({len(image_paths)})가 다릅니다.")

    # return image_paths

