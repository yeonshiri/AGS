# Auto Grading System


## 프로젝트 설명
객관식과 단답형으로 이루어진 시험지를 이미지 데이터로 변환 후 각 문제 영역을 구분하여 ROI로 추출하고, 문제에 기입된 답안을 정답과 비교하며 자동으로 채점이 이루어지는 시스템. 라즈베리파이 환경에서 구현한다.


## 목차
1. 프로젝트 전체 흐름
2. 설치
3. 데이터 준비
4. ROI 추출
5. 객관식 인식
6. 단답형 인식식
7. 답안과 정답 비교


## 1. 프로젝트 전체 흐름
프로젝트의 전체 흐름은 다음과 같습니다.

1. 시험지에서 객관식과 단답형 ROI 구분 추출
2. 객관식 답안 인식
    1. 문제 번호 인식
    2. 번호 인식 알고리즘
3. 단답형 답안 인식
    1. 문제 답안 인식 및 추출
    2. OCR을 이용한 답안 인식
4.  채점 후 결과 정리

![flow 사진](readme_image/flow.jpg)

## 2. 설치
git에서 yolov5을 다운을 받은 후 다음과 같은 directory를 만들면 실행이 가능합니다.
<pre>git clone https://github.com/ultralytics/yolov5.git
cd yolov5  
install requirement.txt </pre>   

<pre>
├── ags
│   ├── yolov5
│   ├── main.py
│   ├── roi.py
│   ├── detector.py
│   ├── utils.py
│   ├── grading
│   │   ├── objective.py
│   │   └── subjective.py
│   ├── weights
│   │   ├── mc.pt
│   │   ├── sa.pt
│   │   └── roi.pt
</pre> 

### 환경
- Python 3.9.21
- PaddleOCR 2.6.1.3
- YOLOv5 v7.0
  
## 3. 데이터 준비

![시험지 사진들](readme_image/testpapers.png)

다양한 데이터 모집을 위해 모의고사, 수능, 공무원, 검정고시, 경찰지 시험지를 수집하였습니다. 학습 알고리즘 개발을 목적으로 실제 시험지 사진이 아닌 pdf로 진행 중입니다. 다만 실제 시험지와 같은 효과를 내기 위해 밝기, 노이즈, y축 비틀기와 같은 데이터 증강을 적용하였습니다. 객관식 문항은 다양한 형태의 마킹 형태를 삽입하였으며, 단답형 문항은 풀이 과정과 답안 영역을 삽입하여 dataset로 구성하였습니다. 

### 모델 학습
![라벨링](readme_image/labeling.png)
labelimg 라는 툴을 사용하여 모든이미지를 수작업으로 라벨링을 진행하였습니다. 전체 시험지에서는 문제 구역을 라벨링, 객관식과 단답형의 경우 미리 이미지들을 편집한 후 단답을 라벨링하는 과정을 거쳤습니다.


## 4. ROI 추출
![ROI 과정](readme_image/roi.jpg)

위 사진과 같이 객관식과 단답형 문제를 서로 다른 class로 학습을 진행한 후 detect를 통해 감지할 수 있게 만들었습니다.

![문제 번호 정렬](readme_image/quesnum.jpg)
시험지의 특성상 왼쪽 위에서 문제가 시작해서 문제 번호가 아래로 순서대로 정렬한 후 오른쪽에서 다시 아래로 정렬되는 특성 이용하여 좌표 시스템을 기반으로 한 알고리즘을 만들었습니다. 문제의 bounding box 좌표를 이용하여 객체들을 문제 번호에 따라 순서대로 정렬한 후 문제 번호를 추정하는 알고리즘을 사용하였습니다.

![문제 인식 과정정 이미지](readme_image/roi.png)


## 5. 객관식 답안 인식
### 1. 문제 번호 인식
![객관식 roi 이미지](img/multians/test.png)
yolo를 활용하여 2개의 class option_box와 marked_box로 구분하여 객관식 선택지와 선택된 답안을 학습시켰습니다.
![번호 인식 과정 이미지](readme_image/objective.png)

### 2. 번호 인식 알고리즘
![객관식 정렬 이미지지](readme_image/mc.jpg)
detect를 진행한 후 label에서 얻은 좌표값을 추출 한후 x좌표와 y좌표를 얻습니다. y좌표로 오름차순 정렬을 진행한 후 x좌표로 오름차순 정렬을 차례로 하면 다음과 같이 번호에 따른 객체들을 유추할 수 있습니다. 그 후 정답이라 고른 선지의 좌표와 가장 거리가 가까운 선지를 고른 답이라고 인지할 수 있게 만듭니다.

## 6. 단답형 답안 인식
### 1. 문제 답안안 인식 및 추출
![단답형 roi 이미지](readme_image/sa.png)
yolo를 활용하여 답안 표시 형식의 answer_box를 학습 후 시험지에서 detect하고, 얻은 label의 좌표값을 활용하여 답안 부분만 crop 저장합니다.
![답안 인식 과정 이미지](readme_image/subjective.png)

### 2. OCR을 이용한 답안 인식
![단답형 ocr 이미지](readme_image/ocr_result.png)
PaddleOCR lite를 이용하여 저장된 답안을 인식하는 과정을 거치고 dictionary 형태로 저장합니다. 

## 7. 답안과 정답 비교 채점
![채점 결과 이미지](readme_image/grading.png)
위 그림처럼 json 파일로 답안지를 입력을 미리해두면 선택한 답안과 비교하여 먼저 선택 답들을 보여준 후 맞은 문제, 틀린 문제, 최종 점수를 알려줍니다.
