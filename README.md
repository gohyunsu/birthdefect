# BirthDefect

Multimodal AI for congenital anomaly screening and structural analysis.

Project website: `https://gohyunsu.github.io/birthdefect/` (published after the GitHub repository is created).

## 목적

선천성 기형(birth defect), 특히 태아·소아 심장 및 뇌 영상에서 공개 데이터와 실제 임상 비디오를 이용해 다음을 연구한다.

- 표준 영상면과 이상 구조의 검출/분할
- 짧은 초음파 비디오의 시간적 정보 활용
- 적은 양의 라벨과 많은 비라벨 데이터에 대한 반지도 학습
- 영상·3D 구조·임상 메타데이터의 멀티모달 융합

## 폴더

- `research/`: 문헌·데이터셋 조사
- `datasets/`: 원본 데이터는 저장하지 않고 다운로드 안내, 라이선스, manifest, 샘플 분석만 관리
- `experiments/`: 재현 가능한 실험 설정과 결과
- `reports/`: 미팅/논문용 산출물
- `src/`: 전처리·학습·평가 코드

## 현재 우선순위

1. HVSMR-2.0을 이용한 3D whole-heart segmentation 데이터 파이프라인 확인
2. FOCUS·ImageCHD·FeTA 등 공개 데이터셋의 상호보완성 비교
3. 확보 예정 fetal echocardiography video에 SELSA류 temporal aggregation 적용 가능성 검토
4. 라벨이 적은 비디오에는 pseudo-label/contrastive learning을 적용하는 실험 설계

원본 의료 데이터는 저장소에 커밋하지 않는다. 환자 식별정보, 다운로드 토큰, 기관 내부 데이터도 저장하지 않는다.
