# Birth Defect AI 연구 맥락 및 데이터셋 조사

작성자: 고현수
작성일: 2026-07-17

## 1. 연구가 진행되는 맥락

수달팀은 9~10월 학회/저널 투고를 목표로 선천성 기형을 자동 탐지·분석하는 베이스 아키텍처를 정하려고 한다. 실제 임상에서 중요한 문제는 정상/이상 이진 분류 하나가 아니라, 태아 심장의 표준면을 찾고, 심방·심실·대혈관의 해부학적 관계를 해석하며, 영상의 시간적 변화까지 반영해 전문가의 판독을 보조하는 것이다.

이 문제는 다음 이유로 어렵다.

- CHD는 종류가 많고 각 유형의 표본 수가 작다.
- 초음파는 speckle noise, 낮은 대비, 시야·각도·장비 차이가 크다.
- 한 비디오의 프레임들은 독립 표본이 아니며, 환자 단위 분할이 아니면 leakage가 발생한다.
- 기형은 구조의 관계/연결 문제라 단순 texture 분류만으로는 일반화가 어렵다.
- 의료 라벨은 전문의 판독과 기관 승인에 의존해 비라벨 데이터가 많다.

따라서 목표는 “높은 accuracy”보다 임상적으로 유용한 screening tool이다. 민감도, 특이도, AUROC/AUPRC, 환자 단위 성능, calibration, 외부 기관 일반화와 불확실성까지 봐야 한다.

## 2. 현수님 담당: HVSMR-2.0

HVSMR-2.0은 CHD 환자 60명의 3D cardiovascular MR(CMR) 스캔과 4개 심장 방·4개 대혈관의 수동 분할 마스크를 제공한다. 라벨은 LV, RV, LA, RA, AO, PA, SVC, IVC이며, 각 환자의 진단·수술·변이 정보도 제공된다. 데이터는 NIfTI(`.nii.gz`)이고 `orig`, `cropped`, `cropped_norm` 세 변형으로 제공된다. 원본/크롭/정규화 변형을 섞지 않는 것이 권장된다.

### 왜 의미가 있는가

기존 HVSMR 2016은 20개 영상과 2개 foreground 구조 중심의 challenge였지만, HVSMR-2.0은 60개 영상, 8개 구조, 다양한 기형과 수술 후 해부학, vessel endpoint 범위를 제공한다. 즉 CHD에서 “이상 여부”를 직접 분류하기보다 해부학적 구조를 복원하고 정량화하는 연구의 공용 기준점이다. 환자별 3D surface model은 수술 계획, 시뮬레이션, 기능 지표 계산에 연결될 수 있다.

### 현재 해야 할 분석

- 세 변형의 파일 수, shape, voxel spacing, intensity range, label histogram 확인
- 환자 단위로 진단·수술 metadata와 segmentation의 연결 확인
- 8개 구조별 voxel 수, 빈 라벨, 연결 성분, vessel endpoint 범위 점검
- 3D volume과 mask를 axial/coronal/sagittal 및 surface로 시각화
- 작은 데이터이므로 random slice split 대신 subject-level split 사용
- baseline은 3D U-Net/nnU-Net 계열, 평가는 Dice, HD95/ASSD, per-class recall

주의할 점은 60건이 매우 작고 진단 분포가 균등하지 않다는 것이다. HVSMR-2.0은 태아 초음파 비디오와 modality/domain이 다르므로 최종 fetal-video classifier의 직접 학습 데이터라기보다 3D 구조 분할·표현·전처리 검증용으로 보는 편이 타당하다.

## 3. 데이터셋 비교

| 데이터셋 | modality/type | 규모·라벨 | 접근성 | 적합한 과제 |
|---|---|---|---|---|
| HVSMR-2.0 | 3D CMR, NIfTI | 60 scans, 8 cardiac structures, diagnosis metadata | Figshare, 공개 | 3D whole-heart segmentation, 구조 정량화 |
| FOCUS | fetal 4-chamber US image | 300 images, cardiac/thoracic region annotation | Zenodo, CC-BY 4.0 | CTR/biometric measurement, detection/segmentation |
| ImageCHD | 3D CT | 110 labeled CT, 7 cardiac structures와 CHD 진단 | Kaggle, Apache 2.0 | CHD classification, 3D segmentation, generative anatomy |
| FeTA | reconstructed fetal MRI | 50 volumes, 7 fetal brain tissue labels, 20–33 gestational weeks | 논문/benchmark 경로 확인 필요 | fetal brain multi-class segmentation |
| Fetal brain abnormalities | ultrasound image | Kaggle summary상 1,773 files, train/valid/test; 정상/이상 분류 계열 | Kaggle, card/license 확인 필요 | low-cost 2D classification baseline |
| Abnormal Fetal Roboflow | ultrasound image | 174 images/410 exported instances, 3 classes: choroid plexus, CSP, midline falx | Roboflow, CC-BY 4.0 | fetal brain part detection; 데이터 규모·버전 주의 |
| CLP-NC | 2D JPG | 3,987 images, CLP vs non-cleft, 전문가 검증 주장, 640×640 | Mendeley, CC-BY 4.0 | cleft lip/palate classification/detection |
| ZCHSound | pediatric heart sound, WAV | 1,259 participants: normal 693, CHD 566; 8 kHz | 공식 DB 확인 필요 | PCG 기반 CHD screening |
| CARDIUM | fetal US/echo + maternal records | multimodal prenatal CHD dataset; access request 필요 | project/GitHub, request | image-tabular fusion, multimodal CHD detection |

공개 여부만으로 데이터의 임상 신뢰도를 보장할 수는 없다. 특히 Kaggle/Roboflow 자료는 원 논문, 환자 단위 중복, annotation provenance, split 생성 방식을 반드시 확인해야 한다.

## 4. 두 논문의 아키텍처를 현재 문제에 적용하는 방법

### SELSA

SELSA는 가까운 프레임만 optical flow/RNN으로 연결하는 대신, 시퀀스 전체의 feature를 semantic similarity로 가중 집계하는 video object detection 방법이다. ImageNet VID와 EPIC-KITCHENS에서 검증되었고, full-sequence aggregation이 핵심이다.

fetal echo video에는 다음처럼 옮길 수 있다.

`frame encoder → proposal/view/structure feature → sequence-level similarity aggregation → temporal detector/classifier → patient/video decision`

단, 초음파의 프레임은 객체 tracking보다 cardiac phase와 anatomical view 안정화가 더 중요할 수 있다. 따라서 처음부터 SELSA를 그대로 복제하기보다 2D CNN/ViT frame baseline, mean/max temporal pooling, then attention aggregation 순으로 ablation하는 것이 안전하다.

### SAD

SAD는 dynamic graph에서 time-equipped memory bank와 pseudo-label contrastive learning으로 소량의 이상 라벨과 다량의 비라벨 샘플을 함께 쓰는 반지도 anomaly detection 방법이다.

의료 영상에 직접 그래프가 존재하는 것은 아니므로 다음과 같은 명시적 설계가 필요하다.

- node: frame, cardiac cycle, view, patient 또는 segmented structure
- edge: 시간 인접성, 같은 환자/검사 연결, 구조 인접성, feature similarity
- anomaly: 정상 해부학/시간 패턴에서 벗어난 frame·cycle·patient

이 방식은 “기형 종류를 충분히 다 본 적이 없는” 초기 연구에 유리하지만, pseudo-label 오류가 임상 편향을 증폭할 수 있다. 정상/이상 label noise, patient-level split, temporal leakage, false negative CHD를 따로 검증해야 한다.

## 5. 긍정적 평가와 한계

긍정적으로 평가할 근거는 분명하다. 공개 CHD 데이터가 부족한 상황에서 HVSMR-2.0은 희귀 질환의 구조적 다양성을 공개하고 재현 가능한 benchmark를 제공한다. FeTA도 태아 MRI의 7 tissue multi-class benchmark를 만들었고, FOCUS는 공개된 4-chamber annotated resource를 추가한다. 영상만이 아니라 CARDIUM처럼 임상 metadata를 결합하는 흐름도 실제 진료 의사결정에 가까워진다.

그러나 현재 문헌의 높은 수치는 임상 배포 성능과 동일하지 않다. 작은 단일기관 retrospective dataset, class imbalance, leakage, selective prediction, external validation 부족이 반복되는 한계다. 따라서 논문의 novelty는 “새 모델 + 높은 accuracy”보다 (1) 환자 단위·기관 외 검증, (2) label-efficient temporal learning, (3) 구조적으로 설명 가능한 결과, (4) calibration/uncertainty와 임상 workflow 통합에서 찾는 것이 설득력 있다.

## 6. 권장 연구 방향

가장 현실적인 주제는 다음이다.

> Label-efficient temporal and structural learning for congenital heart defect screening from fetal echocardiography videos.

1단계: frame/view quality 및 standard-plane detection baseline

2단계: temporal pooling/SELSA-style aggregation으로 video-level screening

3단계: segmentation 또는 structure-aware auxiliary task 추가

4단계: 비라벨 영상에 pseudo-label contrastive learning 적용

5단계: patient-level, site/device-level split과 calibration/ablation 보고

HVSMR-2.0은 3단계의 구조 표현 사전 검증과 3D segmentation benchmark로 병행한다. FOCUS/ImageCHD/FeTA는 modality-specific pretraining·transfer 가능성을 탐색하되, modality가 다른 데이터를 단순히 합쳐 성능을 주장하지 않는다.

## 참고 링크

- HVSMR-2.0 dataset: https://figshare.com/collections/HVSMR-2_0_A_3D_cardiovascular_MR_dataset_for_whole-heart_segmentation_in_congenital_heart_disease/7074755
- HVSMR-2.0 paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11219801/
- FOCUS: https://zenodo.org/records/14597550
- ImageCHD: https://www.kaggle.com/datasets/xiaoweixumedicalai/imagechd
- FeTA paper: https://www.nature.com/articles/s41597-021-00946-3
- SELSA: https://arxiv.org/abs/1907.06390
- SAD: https://arxiv.org/abs/2305.13573
- CARDIUM: https://bcv-uniandes.github.io/CardiumPage/
- CLP-NC: https://data.mendeley.com/datasets/yxp6fxdymp
- ZCHSound: http://zchsound.ncrcch.org.cn/
