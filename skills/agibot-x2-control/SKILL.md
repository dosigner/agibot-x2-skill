---
name: agibot-x2-control
description: X2 이동/회전, MC 입력원, 프리셋 실행, 제어권 복구, 관절 명령과 상태 판정을 구현하거나 진단할 때 사용한다.
---

# X2 MC와 프리셋 제어

## 명령 전 계약

사용자가 요청한 실행은 현재 권한 범위에서 수행하되 대상 보드/연결, 설치 AimDK 1.0.0 계약, 제어 모드, 입력원과 미결 실행을 먼저 확인한다. [제어 경계의 교훈](references/lessons.md)을 읽는다. 스킬 호출 자체는 모션 요청이 아니다.

사용자가 준 관절 위치/속도/토크/kp/kd를 그대로 사용하고 실제 한계와 충돌하면 이유를 보고한다. 값을 몰래 clamp하거나 반응이 없다고 속도를 높이지 않는다. 새 명령 인터페이스의 dry-run/ramp는 요청 시 선택하는 옵션이며 기본 off다. 기존 mandatory guard는 유지한다. 가상 GLB 슬라이더 범위와 실기 허용 범위는 별개다.

## 상태와 소유권

- 모드 이름, 상태 enum, freshness, 플레이어 IDLE과 입력원은 각각 검사한다. 현재 GET은 선택 입력원 조회일 수 있으며 전체 등록 목록이 아니다.
- 등록 수락과 실제 source 선택을 구분한다. 명령 이전에 발행한 GET의 늦은 응답을 명령 후 제어권 획득 증거로 사용하지 않는다.
- 모션 요청의 의도를 durable ledger에 먼저 기록하고 operation/run ID로 중복을 막는다. **not_sent, accepted, observed_running, finished, unknown**을 구분한다. 전송 후 응답 유실에서 재전송하지 않는다.
- 입력원 timeout/DELETE/zero 발행은 물리 정지 보장이 아니다. 상위 입력원을 끄거나 우선순위를 올려 제어권을 빼앗지 않는다. 종료에서 자기 소유 입력원만 정리한다.
- 브라우저 heartbeat와 PC2 worker의 monotonic lease를 각각 둔다. 입력 해제/blur/hidden/route leave/취소/통신 유실에서 stop 경로를 검사하고 재접속 후 자동 재개하지 않는다.
- cleanup 결과 불명은 잠금 이유를 보존한다. 과거 현장 정지 확인을 새 복구 시도에 재사용하지 않는다. source 해제와 물리 정지 확인은 별도 기록이다.

## 단위와 관측

관례는 +X 전방, +Y 왼쪽, +Z 위, 좌회전 양수, 선속도 m/s, 각속도 rad/s다. 현재 설치 문서/예제를 대조한다. UI deg/s, 기존 API deg/s, ROS rad/s 변환 경계를 하나씩 확인한다. 이동거리/회전을 IMU odometry에서 계산하면 허리 포함 base 변환이 필요하다.

## 검증

가짜 sender/ROS와 시계로 discovery 지연, 응답 유실, stale 상태, 모드 변경, source 상실, 중복 요청, 종료 중 관측 오류를 시험한다. 브라우저의 숫자 입력/IME/키 반복/시작 응답 전 key-up도 검사한다. 소프트웨어 상태 전이 합격과 실물 이동/정지 거리/관절 영점 보정은 구분한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
