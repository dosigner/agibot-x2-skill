---
name: agibot-x2-runtime
description: X2 Ultra의 PC2/PC3 식별, SSH 연결, AimDK Python 타입 로딩, DDS 탐색과 실제 센서 수신 문제를 진단할 때 사용한다.
---

# X2 보드와 ROS 실행 진단

## 진단 순서

1. 대상 보드, 실제 접속 주소, 설치 버전과 실행 프로세스의 소유자를 확인한다. 원 프로젝트의 기준은 AimDK 1.0.0이다. 다른 설치/업그레이드가 확인되면 해당 버전을 우선하고 과거 환경 경로를 자동 적용하지 않는다. PC2는 `soc_index=1`의 개발 보드, PC3는 `soc_index=2`의 상호작용 보드다. 이름이나 IP만으로 판정하지 않고 설치 식별값과 대조한다. PC1은 제조사 모션 제어 보드이며 사용자 개발 실행 장소로 선택하지 않는다.
2. 연결을 `호스트 경로 → SSH 인증/공유 소켓 → ROS 환경 → 그래프 → 실제 메시지 → 기능 결과`로 나누어 검사한다. Wi-Fi 전환 뒤에는 기존 주소 상수를 덮어쓰지 말고 공유 SSH master의 실제 목적지와 새 요청 목적지가 같은지 확인한다. 소켓 파일 존재는 살아 있는 연결의 증거가 아니다.
3. Python 타입 import가 실패하면 `.msg` 존재와 생성 Python/type-support 라이브러리를 구분한다. [설치 환경에서 얻은 교훈](references/lessons.md)을 보고 현재 인터프리터의 모듈 경로, ament prefix, 공유 라이브러리 경로를 대조한다. 곧바로 SDK 재빌드나 전역 환경 수정을 하지 않는다.
4. DDS domain, RMW 구현, 인터페이스 허용 목록과 QoS를 실제 발행자에 맞춘다. PC2 내부 구독 성공과 개발 PC까지 전달 성공을 별도로 시험한다. 장치별 DDS 프로필을 다른 호스트에 그대로 복사하지 않는다.
5. 구독은 작은 allowlist와 제한 시간으로 수행한다. 실제 endpoint 정의와 생성자/콜백/종료 경로를 읽고 조회 범위에 모션이 섞이지 않는지 확인한다. ROS 도구 부재는 로봇 기능 부재로 판정하지 않는다.

## 실행 환경의 재현

과거 PC2에서는 ROS Humble, `rmw_fastrtps_cpp`, domain 0과 제조사 common prefix가 동작했다. 아래는 확인 명령이며 현재 셸의 실행 파일을 먼저 확인한다.

```sh
command -v python3
command -v ros2
printenv ROS_DISTRO
ros2 pkg prefix aimdk_msgs
```

당시 생성 모듈의 prefix는 `/agibot/software/common`, Python 경로는 그 아래 `local/lib/python3.10/dist-packages`, 라이브러리는 `lib`였다. 현재 설치를 확인한 뒤 해당 조사 셸에만 필요한 경로를 적용한다. 자격증명이나 전체 환경변수/프로세스 인자를 결과에 덤프하지 않는다.

## 완료 기준

각 계층에서 실제로 확인한 마지막 지점, 관측창, 수신 수, 사용한 환경과 미확인 원인을 기록한다. 서비스 발견 실패와 발견 후 응답 timeout을 구분한다. 읽기 전용 GET의 제한된 재시도와 모션 요청 재전송은 별개다. 현재 코드/설치본/실행본이 다르면 각각의 해시와 적용 상태를 표시한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
