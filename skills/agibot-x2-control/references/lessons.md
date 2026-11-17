# 제어에서 발견한 함정

- 프리셋의 `Service unavailable`은 발견 실패, `Preflight response missing`은 발견 뒤 유효 응답 미확보다. 첫 GET 지연을 보완한 것과 DDS 근본 원인 해결은 다르다.
- 과거 실패 이력이 카드에 남아 있어도 현재 연결이 실패했다는 의미는 아니다. 요청 시각과 현재 readiness를 함께 표시한다.
- 성공 code와 task state의 기본값 의미가 설치에서 다를 수 있다. 특정 state=0을 보편적인 성공으로 처리하지 말고 response code, 현재 설치 계약과 후속 관측으로 판정한다.
- 이동 status 생성이 필요 없는 자세 이력 6,000개를 두 번 복사한 경로를 제거한 분리 시험에서 약 85 ms→약 2 ms가 관측됐다. 전체 3 s timeout 원인을 모두 설명한 것은 아니다. 제어 readiness 조회는 최소한의 최신 상태 요약을 사용한다.
- 앱 속도 입력 범위는 제조사 보증/실측 안전 범위가 아니다. 시작 임계값은 펌웨어별로 다를 수 있고 값 조정은 사용자 요청과 검증 범위에 맞춘다.
- body/leg odometry 기준점이 LiDAR IMU일 수 있다. 센서 변위를 몸체 중심 변위로 바로 표시하지 않는다.
- cleanup 중 관측 오류가 재발하더라도 zero/source 해제 응답 처리를 불필요하게 끊지 않도록 오류 기록과 cleanup을 분리한다. 실패를 숨기지 않고 최종 unknown 여부를 유지한다.

실제 제어 구현은 프로젝트의 `LOCOMOTION.md`, worker/controller와 관련 회귀 검사를 우선 재사용한다. 아래 근거는 원격 장치를 지금 검사한 결과가 아니다.

[근거 파일과 해시](evidence.md)
