# 정답지
answer_dic = {1: 1,
              2: 3,
              3: 51,
              4: 5,
              5: 24,
              6: 3}

# 학생 답안
student_answers = {1: 2,
                   2: 3,
                   3: 51,
                   4: 4,
                   5: 23,
                   6: 3}
print(student_answers)

# 채점 결과
correct = []
incorrect = []

for q_num, correct_ans in answer_dic.items():
    student_ans = student_answers.get(q_num)
    if student_ans == correct_ans:
        correct.append(q_num)
    else:
        incorrect.append(q_num)

# 결과 출력
print(f"총 문제 수: {len(answer_dic)}")
print(f"맞은 문제 수: {len(correct)}")
print(f"틀린 문제 수: {len(incorrect)}")
print(f"맞은 문제 번호: {correct}")
print(f"틀린 문제 번호: {incorrect}")

if len(answer_dic) == len(student_answers):
    student_answers.clear()
    print(student_answers)