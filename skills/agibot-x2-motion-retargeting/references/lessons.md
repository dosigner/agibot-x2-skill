# 리타겟팅에서 얻은 교훈

- 기존 30→50 Hz 경로는 30 Hz 입력을 upstream loader가 보간하도록 연결했다. 이미 만든 50 Hz를 다시 넣으면 floating-point floor 때문에 일부 길이에서 마지막 frame이 사라졌다.
- 2026-11-16 browser seek에서 frame 시작 경계를 요청하면 이전 frame이 표시되는 반례가 있었다. 실제 디코딩 PTS를 검사해야 한다. 10 μs 경계 보정은 해당 구현의 제한된 workaround이며 임의 FPS의 보편 해법은 아니다.
- 29.97 fps와 시작 offset, 첫/마지막 frame, 정방향/역방향, 연속 seek, 재생속도 변경을 fixture로 검사했다. container duration이 마지막 frame 내부보다 짧은 잘못된 fixture도 별도로 발견했다.
- 단안 영상 접촉 판독에서 발 높이 threshold 20 mm와 40 mm가 서로 다른 비행 분류를 만들었다. 지면 높이 threshold만으로 contact truth를 생성하지 않는다.
- 원본 2.60 s GMR 기준의 발이 모든 frame에서 지면 위에 있는 사례가 있었다. 기하학적으로 그럴듯한 retargeting은 동역학적으로 추종 가능한 기준이 아닐 수 있다.
- 정적 충돌 표본/FK 일치는 연속 충돌, 동역학 안정, 실물 하드웨어 보정을 보증하지 않는다.
- 영상/사람/GMR/시뮬레이션을 비교하려고 골반을 각각 중앙 정렬했으면 표시 transform을 밝힌다. 원본 월드 이동을 숨긴 정렬 화면에서 추종 위치 오차를 읽지 않는다.

[근거 파일과 해시](evidence.md)
