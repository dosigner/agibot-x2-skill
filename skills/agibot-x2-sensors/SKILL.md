---
name: agibot-x2-sensors
description: X2 Ultra RGB-D, 스테레오, LiDAR, IMU의 인코딩, 깊이 단위, 시간 대응, TF, 점군 이진 배치 또는 센서 시각화를 구현하거나 검증할 때 사용한다.
---

# X2 카메라와 LiDAR 보정

## 먼저 고정할 계약

AimDK 1.0.0과 현재 설치를 기준으로 스트림별 타입, frame, stamp 생성점, encoding, width/height/step, CameraInfo, QoS, 단위의 출처를 기록한다. SDK 최신 문서의 변경을 구형 기체에 자동 적용하지 않는다. [보정과 시간에서 얻은 교훈](references/lessons.md)을 해당 센서에 맞춰 읽는다.

- **RGB-D:** `16UC1`은 저장 형식이다. `depth_scale`의 근거가 확인된 프로파일에만 m 변환을 적용한다. raw zero/invalid mask를 보존하고 컬러맵의 min/max와 clipping을 거리 측정과 구분한다.
- **정합:** 드라이버의 depth registration 활성화, 같은 K/P, 같은 해상도는 물체 경계 일치의 증거가 아니다. RGB와 depth의 원본 frame/왜곡 계수/취득 시각을 각각 유지하고, 여러 거리와 화면 위치의 표적에서 잔차를 px 및 m로 측정한다.
- **시간:** nearest stamp 진단은 일대일 동기화가 아니다. 중복, 역행, 누락, 허용 오차와 매칭 정책을 명시한다. 수신 시각, ROS header, 점별 상대 시각과 장치 시각을 섞지 않는다.
- **PointCloud2:** fields의 offset/datatype과 point_step, row_step, endian으로 디코딩한다. 필드 사이 padding을 고려한다. ring의 최대값으로 물리 채널 수를 추론하지 않는다.
- **TF:** `T(A←B)`는 B의 좌표를 A로 옮긴다. 현재 TF에 포함된 장착 회전을 다시 적용하지 않는다. ROS xyzw와 MuJoCo wxyz를 변환 경계에서 명시한다. 서로 다른 frame 이름을 추정 alias로 합치지 않는다.
- **IMU:** orientation covariance의 -1은 자세 미제공, 0은 오차 0의 증거가 아니다. specific force의 축/부호와 중력 포함 여부를 확인한 뒤 사용한다.

## 표시와 추정

표시용 180° 영상 회전은 raw pixel/frame 좌표를 바꾸지 않는다. 클릭 좌표는 표시 역변환 후 원본 보정에 넣는다. Depth completion은 측정값과 추정값을 분리하고 filled mask와 원본 raw 배열을 함께 내보낸다. 알려진 깊이를 가린 holdout 시험과 실제 결측 영역의 정확도는 별개다.

새 입력 파서는 작은 합성 binary fixture로 padding, endian, 잘린 payload, NaN과 stride를 검사한다. 투영/TF는 알려진 점이나 독립 계산과 대조한다. 단위 미확정이면 raw로 표시하고 물리 거리를 주장하지 않는다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
