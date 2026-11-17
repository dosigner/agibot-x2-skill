# 센서 관측과 후속 수정

| 시점 | 특정 설치에서 확인한 것 | 현재 적용 방법/한계 |
|---|---|---|
| 2026-10-19 | RGB-D 1280×720, RGB rgb8, depth 16UC1, 약 30 Hz. stereo/rear는 2064×1552, 약 10 Hz | 관측 프로파일이며 모든 펌웨어의 사양이 아님 |
| 2026-10-19 | SW/COLOR depth registration과 frame sync 활성, RGB/depth nearest stamp 차이 중앙 약 2.65 ms, 동일 stamp 교집합 0 | exact stamp join을 기본으로 잡지 않음. 정합 정확도 미측정 |
| 2026-10-19 → 11-17 | 중앙 RGB는 최초 영상 미수신, 후속 실제 영상 수신 기록은 약 30 Hz | 과거 무수신 상태를 고정 능력 제한으로 남기지 않음 |
| 2026-11-16 | 한 RGB-D 표본의 94개 행에서 depth 결측 시작과 RGB 경계 차이 중앙 7.36 px, 결측 폭 중앙 10 px | 하나의 장면에서 얻은 반례. 결측 끝을 실제 실루엣 정답으로 간주하지 않음 |
| 2026-11-16 | 해당 replay에서 추정 40,574 pixels, 원본 raw 파일 byte 일치 및 mask 대조 | 보간이 실제 깊이를 측정했다는 의미가 아님 |
| 2026-11-17 | RGB-D 컬러와 CameraInfo에서 stamp 역행 각각 2회 | 센서 clock 결함으로 원인을 단정하지 않고 입력에서 역행 탐지 |
| 2026-11-17 | 중앙 영상 frame과 TF child 이름이 다르고 alias 미관측 | 카메라 융합 전에 연결 근거 확보. LiDAR-only 작업의 불필요한 선행조건으로 만들지 않음 |

LiDAR point timestamp는 10월 19일 기록에서는 미확정이었으나 **10월 20일 설치 HAL 감사에서는 프레임 기준 상대 ns**로 확인했다. 해당 설치에 한해 `point_time_s = timestamp * 1e-9`이며 scan header에 더한다. 유효점의 최소 상대시각을 빼서 시작을 재정의하지 않는다. raw message header와 `meas_stamp`의 생성점도 달랐다. 설치 바이너리/설정 변경 시 다시 확인한다. 호스트 system clock 사용은 광학 취득 시각과 IMU의 물리 동기화 보장이 아니다.

10월 19일 LiDAR→torso TF에는 장착 -90° X 회전이 이미 들어 있었다. 센서 장착 모습만 보고 추가 회전하면 두 번 보정한다. LiDAR→IMU는 별도 변환이다. 당시 point_step은 32 bytes였으며 실제 fields를 읽어야 한다. 공개 decoder의 DIFOP offset은 설치 HAL과 달랐으므로 제품명이 같다는 이유로 decoder를 그대로 적용하지 않는다.

원본 RGB와 depth의 payload 합만 약 138 MB/s였던 관측이 있다. 이는 DDS/Ethernet overhead를 제외한 PC2 내부 데이터량이다. 압축 미리보기는 전송 부하를 줄이지만 codec, keyframe, 원래 stamp/frame 보존과 실제 디코더 지연을 별도로 확인한다.

[근거 파일과 해시](evidence.md)
