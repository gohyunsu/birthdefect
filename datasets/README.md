# Dataset workspace

원본 파일은 이 디렉터리에 커밋하지 않는다. 원본 저장 위치, checksum, 다운로드 날짜, license만 `manifest.csv`에 기록한다.

현재 우선순위:

1. HVSMR-2.0: 담당 데이터, 3D CMR/NIfTI, 60 subjects, 8 structure masks
2. FOCUS: 공개 4-chamber fetal ultrasound, 300 annotated images
3. ImageCHD: 공개 3D CT, 110 labeled images, CHD diagnosis/structure labels

샘플 분석은 다음을 기록한다.

- image/mask pairing
- dimensions/spacing/intensity
- label IDs and counts
- overlay/surface visualization
- subject-level split feasibility
- license and redistribution restrictions
