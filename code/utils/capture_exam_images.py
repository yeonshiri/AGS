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