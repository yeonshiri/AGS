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
import re

#딕셔너리에서 key 추출출
def extract_number(key):
    match = re.search(r'\d+', str(key))
    return int(match.group()) if match else float('inf')

#답안 채점 구버전전
def compare_dictionary(answer_dic, student_answers):
    result_list = []

    for q_num in sorted(answer_dic.keys(), key=extract_number):  # 숫자만 추출해 정렬
        correct_ans = answer_dic[q_num]
        student_ans = student_answers.get(q_num, "")
        is_correct = (student_ans == correct_ans)
        result_list.append((q_num, correct_ans, student_ans, is_correct))

    total = len(answer_dic)
    num_correct = sum(1 for _, _, _, is_correct in result_list if is_correct)
    num_incorrect = total - num_correct
    score = round((num_correct / total) * 100) if total > 0 else 0

    print("\n[채점 결과]")
    for q_num, correct_ans, student_ans, is_correct in result_list:
        mark = "O" if is_correct else "X"
        print(f"{str(q_num):>6} 문제: 정답={correct_ans:<5} 제출={student_ans:<5}  {mark}")

    print(f"\n총 문제 수: {total}")
    print(f"맞은 문제 수: {num_correct}")
    print(f"틀린 문제 수: {num_incorrect}")
    print(f"최종 점수: {score}점")

    if total == len(student_answers):
        student_answers.clear()
        print("\n(디버깅용) student_answers 초기화됨:", student_answers)

#시작하기전 기존 이미지,라벨 파일 제거거 
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
            
#정답지 불러오기기     
def load_answer_key(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError("파일이 존재하지 않습니다.")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        answer_dict = json.load(f)
    return answer_dict





import tkinter as tk
from tkinter import ttk


def compare_and_show_gui(answer_dic, student_answers):
    result_list = []

    for q_num in sorted(answer_dic.keys(), key=extract_number):
        correct_ans = answer_dic[q_num]
        student_ans = student_answers.get(q_num, "")
        is_correct = (student_ans == correct_ans)
        result_list.append((q_num, correct_ans, student_ans, is_correct))

    total = len(answer_dic)
    num_correct = sum(1 for _, _, _, correct in result_list if correct)
    num_incorrect = total - num_correct
    score = round((num_correct / total) * 100) if total > 0 else 0

    # Tkinter GUI
    root = tk.Tk()
    root.title("📊 채점 결과 보기")
    root.geometry("600x800")
    root.lift()
    root.attributes('-topmost', True)
    root.after(1000, lambda: root.attributes('-topmost', False))  # 선택

    root.bind("<Escape>", lambda e: root.destroy())

    # 요약 정보
    summary = tk.Label(root, text=f"총 {total}문제 중 {num_correct}개 정답!   점수: {score}점",
                       font=("Arial", 14), pady=10)
    summary.pack()

    # 테이블 생성
    tree = ttk.Treeview(root, columns=("문제", "정답", "제출", "채점"), show="headings", height=25)
    tree.column("문제", width=80, anchor="center")
    tree.column("정답", width=100, anchor="center")
    tree.column("제출", width=100, anchor="center")
    tree.column("채점", width=80, anchor="center")

    tree.heading("문제", text="문제 번호")
    tree.heading("정답", text="정답")
    tree.heading("제출", text="제출")
    tree.heading("채점", text="결과")

    for q_num, correct, submitted, is_correct in result_list:
        mark = "O" if is_correct else "X"
        tree.insert("", "end", values=(q_num, correct, submitted, mark))

    tree.pack(padx=10, pady=10)

    # 닫기 버튼
    tk.Button(root, text="닫기", command=root.destroy).pack(pady=10)

    root.mainloop()