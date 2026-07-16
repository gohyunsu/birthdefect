# 2026-07-17 미팅 준비 체크리스트

## 현수님 담당: HVSMR-2.0

- [ ] Figshare에서 `orig`, `cropped`, `cropped_norm` 접근 권한/다운로드 경로 확인
- [ ] 원본은 저장소 밖에 두고 `datasets/README.md`에 경로만 기록
- [ ] 최소 3개 subject의 image/segmentation overlay 확인
- [ ] NIfTI shape, spacing, dtype, intensity percentile 기록
- [ ] 8개 foreground label별 voxel count와 빈 label 확인
- [ ] diagnosis/surgery metadata와 subject ID 매칭
- [ ] 3D U-Net 또는 nnU-Net baseline 후보 조사
- [ ] Dice, HD95, ASSD를 class별로 보고하는 평가표 작성

## 공통 베이스라인 논의

```text
2D/3D frame encoder
  -> view/structure auxiliary head
  -> temporal pooling or SELSA-style aggregation
  -> video-level CHD classifier
  -> optional pseudo-label contrastive branch (SAD-inspired)
```

반드시 비교할 항목: single-frame, mean pooling, max pooling, attention/SELSA-style aggregation, label-only vs semi-supervised.

## 논문/저널 관점의 핵심 주장 후보

“희소한 fetal echocardiography labels와 다량의 unlabeled video를 이용해 temporal aggregation과 structure-aware auxiliary learning으로 congenital heart defect screening을 개선한다.”

주장에 필요한 검증: 환자 단위 split, device/site split 가능 여부, confidence interval, AUROC/AUPRC, sensitivity at fixed specificity, calibration, subgroup analysis.
