import math

def label_organize(label_path):
    
    result = {
        'option_box': [],
        'marked': []
    }

    with open(label_path, 'r') as f:
        for line in f:
            parts = line.strip().split()  #한줄씩 읽는다.
            if len(parts) < 5:
                continue  # 필요없는 정보는 무시
            class_id = int(parts[0])   #class 정보 입력력
            x_center = float(parts[1]) #x좌표
            y_center = float(parts[2]) #y좌표표

            if class_id == 0:  # 'option_box' 클래스
                result['option_box'].append((x_center, y_center))
            elif class_id == 1:  # 'marked' 클래스
                result['marked'].append((x_center, y_center))

    return result

def deduplicate_boxes(boxes, distance_threshold=0.05):
    if not boxes:
        return []
    #cluster는 가까운 위치의 option_box를 모아두는 그룹
    clusters = []
    for box in boxes:
        added = False
        for cluster in clusters:
            #두점 사이 거리 계산으로 threshold거리 미만이면 cluster 추가 
            if any(math.hypot(box[0] - c[0], box[1] - c[1]) < distance_threshold for c in cluster):
                cluster.append(box)
                added = True
                break
        if not added:
            clusters.append([box])

    return [
        (   
            #겹치는 부분들 즉 cluster에서 좌표들의 평균으로 바꿔서 반환함
            sum(p[0] for p in cluster) / len(cluster),
            sum(p[1] for p in cluster) / len(cluster)
        )
        for cluster in clusters
    ]


def box_sort(boxes, row_threshold=0.05):
    if not boxes:
        return []

    boxes.sort(key=lambda b: b[1])
    rows = []
    current_row = [boxes[0]]

    for box in boxes[1:]:
        #y축으로 거리를 계산해서 threshold보다 낮으면 같은 열로 인식식
        if abs(box[1] - current_row[-1][1]) < row_threshold:
            #box 가로 열에 추가하기
            current_row.append(box)
        else:
            #box 다음 열 진행하기
            rows.append(current_row)
            current_row = [box]
    rows.append(current_row)

    sorted_boxes = []
    #같은 열에서 x축의 값에 따라 번호 순서대로 정렬렬
    for row in rows:
        sorted_boxes.extend(sorted(row, key=lambda b: b[0]))

    return sorted_boxes

def get_closest_option(mark_center, option_centers):
    if not option_centers:
        return None
    #거리를 계산해서 각 option_box마다 저장
    dists = [math.hypot(mark_center[0] - opt[0], mark_center[1] - opt[1]) for opt in option_centers]
    #가장 거리가 적은 선지를 반환
    return dists.index(min(dists)) + 1



def mc_answer(label_dir):
    
    import os
    import glob

    answer_objective = {}  #고른 답을 dictionary 형태로 저장
    label_files = sorted(glob.glob(os.path.join(label_dir, "*.txt")))  #label들을 순서대로 정렬하며 합친다.

    for label_path in label_files:
        # 문제들을 dictionary에 각 문제번호 지정
        idx = os.path.splitext(os.path.basename(label_path))[0]
        filename = f"{idx}번 문제"

        #dic형태로 문제 선지와 고른 선지의 label을 정리 
        boxes = label_organize(label_path)

        #중복되서 감지가 된 선지들을 하나로 합친다.
        option_boxes = deduplicate_boxes(boxes.get('option_box', 0.045))
        
        marked_boxes = boxes.get('marked', [])

        if not option_boxes or not marked_boxes:
            answer_objective[filename] = None
            continue
        #번호 선지 좌표를 이용해 순서대로 정렬
        sorted_options = box_sort(option_boxes)
        
        #고른 정답을 거리를 계산해서 어떤 번호의 선지인지 구별
        selected = get_closest_option(marked_boxes[0], sorted_options)
        
        #선택 답안 dictionary에 업데이트
        answer_objective[filename] = selected

    return answer_objective
