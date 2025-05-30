# capture_exam_images.py

# 라즈베리파이에서 먼저 수행해야 할 것 (Droidcam 사용을 위해)
# 1. 라즈베리파이에 Droidcam client 설치
#   sudo apt update
#   sudo apt install v4l2loopback-dkms

# 2. git에서 리눅스 클라이언트 설치
#   git clone https://github.com/aramg/droidcam.git
#   cd droidcam
#   ./install-client

# 3. Droidcam 스트리밍 연결 (이건 라즈베리파이 부팅마다 실행해야 함)
#   ./droidcam-cli <WiFi_IP> <port>
#   ex) ./droidcam-cli 192.168.0.17 4747

import cv2
import os
import shutil
import json
import glob

def capture_exam_images(save_dir="/home/pi/yolov5/picture"):    # 저장 경로 라즈베리파이에 맞게 수정
    os.makedirs(save_dir, exist_ok=True)
    image_paths = []
    paper_idx = 1

    cap = cv2.VideoCapture(0)
    print("s: 촬영, q: 중지")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("캡처 실패")
            break

        cv2.imshow("Test Paper Shot", frame)
        key = cv2.waitKey(1)

        if key == ord('s'):   # 's' 키를 누르면 저장
            filename = f"exam_{paper_idx}.jpg"
            save_path = os.path.join(save_dir, filename)
            cv2.imwrite(save_path, frame)
            image_paths.append(save_path)
            paper_idx += 1

        elif key == ord('q'):
            print("촬영 종료")
            break

    print(f"시험지 {paper_idx-1}장 저장됨")
    cap.release()
    cv2.destroyAllWindows()
    return image_paths


def compare_dictionary(answer_dic, student_answers):
    # 채점 결과
    correct = []
    incorrect = []

    for q_num, correct_ans in answer_dic.items():
        student_ans = student_answers.get(q_num)
        if student_ans == correct_ans:
            correct.append(q_num)
        else:
            incorrect.append(q_num)

    total = len(answer_dic)
    num_correct = len(correct)
    num_incorrect = len(incorrect)

    # 점수 계산 (정답률 기반, 정수로 반올림)
    score = round((num_correct / total) * 100) if total > 0 else 0

    # 결과 출력
    print(f"총 문제 수: {total}")
    print(f"맞은 문제 수: {num_correct}")
    print(f"틀린 문제 수: {num_incorrect}")
    print(f"맞은 문제 번호: {correct}")
    print(f"틀린 문제 번호: {incorrect}")
    print(f"최종 점수: {score}점")

    if total == len(student_answers):
        student_answers.clear()
        print("(디버깅용) student_answers 초기화됨:", student_answers)

    return score  # 필요하면 외부에서 점수 활용할 수 있도록 반환


def cleanup_directories(dirs):
    for d in dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                fp = os.path.join(d, f)
                if os.path.isfile(fp) or os.path.islink(fp):
                    os.remove(fp)
                elif os.path.isdir(fp):
                    shutil.rmtree(fp)
        else:
            os.makedirs(d)
            
             
def load_answer_key(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError("파일이 존재하지 않습니다.")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        answer_dict = json.load(f)
    return answer_dict
