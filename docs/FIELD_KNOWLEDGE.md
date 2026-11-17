# X2 field knowledge skills, 2026-11-17

이 배포는 공식 문서 탐색 스킬 1개와 프로젝트 경험을 정리한 전문 스킬 10개다. AimDK 기준은 1.0.0이며 배포 버전 1.2.0과 다르다. MuJoCo 4.0.x는 이 프로젝트의 사용자 선택이며 모든 X2의 제조사 요구사항이 아니다.

## 선택

| 스킬 | 쓰는 경우 |
|---|---|
| [agibot-x2-runtime](../skills/agibot-x2-runtime/SKILL.md) | X2 보드와 ROS 실행 진단 |
| [agibot-x2-sensors](../skills/agibot-x2-sensors/SKILL.md) | X2 카메라와 LiDAR 보정 |
| [agibot-x2-voice](../skills/agibot-x2-voice/SKILL.md) | X2 PC2 음성 파이프라인 |
| [agibot-x2-face](../skills/agibot-x2-face/SKILL.md) | X2 PC3 얼굴과 표정 |
| [agibot-x2-hri](../skills/agibot-x2-hri/SKILL.md) | X2 터치와 밀림 반응 |
| [agibot-x2-slam-navigation](../skills/agibot-x2-slam-navigation/SKILL.md) | X2 SLAM과 지도 위치 추정 |
| [agibot-x2-control](../skills/agibot-x2-control/SKILL.md) | X2 MC와 프리셋 제어 |
| [agibot-x2-dashboard](../skills/agibot-x2-dashboard/SKILL.md) | X2 공유 대시보드 운영 |
| [agibot-x2-motion-retargeting](../skills/agibot-x2-motion-retargeting/SKILL.md) | X2 영상 모션과 리타겟팅 |
| [agibot-x2-simulation](../skills/agibot-x2-simulation/SKILL.md) | X2 MuJoCo와 정책 평가 |

각 전문 스킬은 instructions, lessons, 근거 파일의 상대 경로/hash를 포함한다. 다른 스킬의 설치가 없어도 핵심 절차를 읽을 수 있다. 원 프로젝트 소스가 있으면 해당 근거를 대조하고 없으면 현재 설치에서 다시 확인한다.

## 조사 범위와 정직한 한계

로컬 Codex의 활성/보관/압축 세션 파일 3,931개를 인벤토리로 확인했다. 작업 경로가 aimdk 또는 agibot-x2인 2,558개 파일, 중복 ID를 제외한 2,550개 세션에서 사용자/최종 답변 계열 메시지를 추출해 주제별 검색과 중복 제거를 했다. 기간은 2026-10-10~11-17이다. 이 수에는 하위 작업과 재개/상속 기록이 포함된다. 사람이 나눈 독립 채팅 2,550개라는 뜻이 아니다.

대화는 근거를 찾는 단서로 사용하고, 채택한 지식은 프로젝트 작성 문서/실행 산출물과 대조했다. 모든 도구 출력과 모든 문장을 사람이 정독한 전수 감사, 삭제된 대화 복구, 다른 앱/호스트의 전체 기록 조사 또는 모든 가능한 유용한 정보의 완전 수집을 주장하지 않는다. X2와 무관한 논문 앱/투자/크레인 업무는 이 스킬 묶음에 넣지 않았다. 대화 원문과 식별자 목록은 공개하지 않는다.

## 이력 충돌을 해소한 예

- 중앙 RGB의 초기 무수신 기록 뒤 실제 수신 기록이 있으므로 영구 미지원으로 기록하지 않는다.
- LiDAR point timestamp는 초기 미확정 뒤 설치 HAL 감사에서 상대 ns로 확인됐다. 해당 설치/버전의 근거로만 쓴다.
- RGB-D registration 활성/같은 K와 실제 경계 오차 관측은 함께 성립한다. 정합 활성화를 정밀 융합 검증으로 바꾸지 않는다.
- 제조사 내장 nav 조사와 현재 자체 nav 개발 선택을 구분한다. 내장 옵션 활성화를 자체 경로의 blocker로 추가하지 않는다.
- 합성/오프라인, 실제 수신, 현장 청취, 물리 제어 성공을 각각 다른 근거로 보존한다.
- 학습 실행과 FK/기하 검사, 물리 추종 성공, 실기 배포 자격을 분리한다.

## 공개 범위

새 내용은 독자적으로 작성한 운영 절차와 날짜가 있는 현장 교훈이다. 제조사 문서/타입 정의/endpoint 전체 표/사양표/바이너리/영상/원시 점군/음성/자격증명은 재배포하지 않는다. 근거 경로/hash는 출처를 찾는 단서이며 공개 다운로드나 현재 상태의 증거가 아니다. 원본 대화와 로컬 검토 자료는 공개 allowlist 밖에 둔다.
