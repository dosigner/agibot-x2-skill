---
name: agibot-x2-motion-retargeting
description: 사람 영상/모션에서 GVHMR/FlowHMR/GMR를 거쳐 X2 기준 클립을 만들거나 31축 모델과 29축 정책 매핑, 영상/자세 동기 재생, 접지 가설을 검증할 때 사용한다.
---

# X2 영상 모션과 리타겟팅

## 입력과 단계 분리

원본 영상 → 사람 추정 → retargeted 기준 → 물리 추종 → viewer를 서로 다른 결과로 저장한다. [시간/관절/접촉 교훈](references/lessons.md)을 읽는다. 원본 hash, 실제 frame PTS, crop 시작, sample 시각, 모델/추정기 revision을 보존한다. 사람 검출/가림/중복 인물/신장 추정의 실패를 합성 clip으로 조용히 대체하지 않는다.

## X2 모델과 관절 매핑

이 프로젝트의 원본은 `src/x2_teleop/assets/agibot_x2_urdf/X2_URDF-v1.3.0`의 scene/XML/meshes다. 배치 위치와 include/meshdir 관계를 유지한다. clone 내부와 외부 workspace의 `src`가 다를 수 있으므로 실제 소스 경로를 resolve한다.

31개 모터 모델에서 29축 정책을 만들 때 이름으로 다음을 각각 대조한다: GMR 열, MuJoCo qpos/dof 주소, actuator 순서, 정책 순서, HAL motor ID. 기존 BlinkMimic 경로는 leg 12→waist 3→arm 14이며 머리 2축은 모델에 남겨 별도 제어했다. 이 순서를 임의의 새 정책에 강제하지 않고 그 정책의 계약을 읽는다. HAL 영점/부호 미확인은 null/unknown으로 유지한다.

위치는 m, 관절각 rad, 월드는 오른손 +X 전방/+Y 왼쪽/+Z 위를 명시한다. 골반 quaternion 방향과 wxyz 순서를 적고, 선형/각속도의 표현 frame을 확인한다. 제한된 hinge 각을 무조건 wrap하지 않는다.

## 보간과 viewer

- 원본 FPS/PTS와 목표 control grid를 분리한다. upstream이 보간한다면 원본을 넣어 한 번만 보간한다. 마지막 표본 포함 여부와 남는 꼬리를 명시한다.
- 위치/관절 선형 보간과 quaternion 최단 경로 SLERP를 사용하고 파일 재읽기/왕복 복원과 독립 FK를 검사한다.
- 브라우저 `currentTime`은 요청값이다. `requestVideoFrameCallback`의 실제 `mediaTime`을 확인한 뒤 원본 PTS에 대응하는 비교 표본을 표시한다. seek/교체/종료에서 오래된 callback을 취소한다.
- 물리 실행이 조기 종료되면 그 뒤 구간을 빈 상태/종료로 표시한다. 원본 기준이나 보간 자세를 물리 결과처럼 이어 붙이지 않는다.

## 접촉과 길이 변경

발이 낮다는 이유만으로 접촉을 확정하지 않는다. 영상, 발 형상 거리, 속도와 접촉력 근거를 구분하며 지지/비행 경계는 가설로 남긴다. 접지 보정본은 새 hash와 가정을 가진 별도 후보로 만든다.

영상 길이 제한을 늘릴 때 upload bytes, frame count, decoded RAM, inference timeout, response bytes, renderer를 함께 추적한다. 숫자 하나의 제한 해제로 완료하지 않는다. 전체 추론을 안 돌렸다면 합성 변환 시험과 구분한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
