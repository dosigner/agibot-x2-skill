---
name: agibot-x2-slam-navigation
description: X2 FAST-LIO2/GLIM, 저장 지도와 PLY, 재위치추정, 좌표 변환, 자체 navigation 준비 상태 또는 LiDAR/IMU 입력 지연을 다룰 때 사용한다.
---

# X2 SLAM과 지도 위치 추정

## 현재 개발 방향과 경계

이 프로젝트는 2026-11-17에 **자체 SLAM/navigation, 제조사 MC를 보행 실행 경계로 유지**하는 방향을 선택했다. 내장 nav 활성화는 이 경로의 필수 조건이 아니다. 사용자가 내장 nav를 요청하면 그 설치/기동 계약을 별도로 조사한다. 이 선택을 다른 X2 프로젝트에 강제하지 않는다.

[좌표와 저장 교훈](references/lessons.md)을 읽고 현재 mapper, 저장 지도 정합, planner, 실제 follower/장애물 검사 연결을 각각 확인한다. A* 경로 표시나 HTTP 202는 실제 A→B 실행이 아니다. 현재 코드에 실행기가 없으면 미연결로 표시하며 waypoint마다 기존 단발 이동을 호출하는 것으로 대체하지 않는다.

## 좌표와 시간

`T(A←B)`는 B 좌표를 A로 변환한다. M=저장 지도 원본, O=현재 SLAM 원점, I=LiDAR IMU, B=base_link, N=실제 바닥/위쪽 축을 검증한 navigation 평면이다. 병진은 m, 계산 각도는 rad, quaternion 순서는 입력별로 명시한다.

```text
T(N←B,t) = T(N←M) T(M←O) T(O←I,t) inverse(T(B←I,waist(t)))
```

- 같은 `camera_init` 이름이어도 run이 바뀌면 원점이 다르다. 지도 SHA-256, frame instance, run/epoch와 원본 stamp를 함께 보존한다.
- leg odometry/FAST-LIO body가 IMU 기준이면 base 위치로 바로 쓰지 않는다. 같은 시각의 허리 상태를 포함한 센서 변환을 사용한다.
- 물리 바닥, 표시용 X-up, 기하 평면 hypothesis를 구분한다. 바닥 fitting 잔차가 낮다고 실제 지면임이 증명되지는 않는다.
- LiDAR 상대 ns, 원래 scan header, IMU 시각 생성점을 확인한다. deskew를 각 점에 정확히 한 번 적용하고 첫 점과 구간 경계를 별도 시험한다. 원시 입력 이상을 smoothing/보간으로 숨기지 않는다.

## 운영과 저장

1. 지도 계산 지연은 동일 run의 발행→callback→계산→저장→호스트→화면으로 분리 계측한다. 같은 단조 시계 또는 명시한 시계 변환 오차를 사용한다.
2. 원본 입력률, mapper 공급률, 정합 필터, 저장 voxel, 표시 voxel을 분리한다. 필터 크기 변경은 정확도/부하 실험이며 보장 개선이 아니다.
3. raw, registered scan, SQLite voxel 저장, PLY export, 브라우저 preview를 구분한다. 전체 저장 voxel도 무손실 raw LiDAR가 아니다.
4. 실행 중 SQLite 사본은 WAL을 포함하는 backup API로 만든다. 큐 drain/commit과 PLY hash/header/bytes 확인을 마친 뒤 완료로 표시한다. pending/incomplete를 새로고침으로 complete로 바꾸지 않는다.
5. 기존 지도와 raw 기록을 보존한다. 시작/종료는 소유한 run에만 적용하고 정상 cleanup, 로그 복구와 lock 해제를 확인한다. mapper 중지는 물리 로봇 정지가 아니다.

## navigation으로 넘기기 전

정합 tracking, 내부 RMSE, 반복성, 외부 기준 위치 정확도를 분리한다. 저장 위치는 초기 가설이며 현재 pose가 아니다. 표시용 pose 유효시간을 MC 제어용으로 사용하지 않는다. occupied-only grid와 1 Hz 정합용 축약 scan을 실시간 자유 공간/장애물 감시로 사용하지 않는다. stale/unknown을 free로 바꾸지 않는다. 고정 평지 A→B, 취소/통신 단절/수동 takeover의 실제 오차와 정지 거리를 확인한 뒤 실행 준비로 판정한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
