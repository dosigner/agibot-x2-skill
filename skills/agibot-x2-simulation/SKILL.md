---
name: agibot-x2-simulation
description: X2 Ultra MuJoCo/TrackingSim, 하체 강화학습, CPU/GPU 비교, 모델 보존, 체크포인트 재개와 물리 추종 평가를 구현하거나 검증할 때 사용한다.
---

# X2 MuJoCo와 정책 평가

## 실행 기준

원래 aimdk 프로젝트의 사용자 선택은 **MuJoCo 4.0.x**다. 다른 프로젝트의 명시적 버전 요구를 이 과거 선택으로 덮어쓰지 않는다. 현재 요청 버전을 기준으로 호환성을 확인하며 임의 업그레이드/다운그레이드를 하지 않는다. Python package뿐 아니라 native engine과 MuJoCo Warp 버전을 확인한다. 과거 3.x 실험은 역사 자료이며 새 실행 버전의 근거가 아니다. upstream lock 충돌은 별도 환경에서 명시하고 원본 package metadata를 수정해 호환되는 것처럼 만들지 않는다.

[실험과 실패 교훈](references/lessons.md)을 읽고 모델, scene/XML/mesh hash, 제어 계약, dt/control decimation, solver, contact 설정, 초기 qpos/qvel, seed, 종료식과 평가 시계를 고정한다. 기존 HoloMotion/checkpoint와 원본 자산은 보존한다. 명령 성공/학습 exit 0은 정책 성능 성공이 아니다.

## 모델/제어 검증

- 관절 이름으로 actuator/qpos/dof/policy 매핑을 검사한다. free base, 머리 축과 전신 질량/관성을 유지한다. 모델 관절 범위는 실물 영점/토크 보정의 증거가 아니다.
- actor 관측과 privileged critic 관측을 구분한다. export 시 history, normalization, action scale, joint order, PD gains를 함께 검증한다.
- 같은 초기 상태/입력의 CPU↔GPU 및 native↔Warp 짧은 궤적을 대조한다. 위치/속도/접촉/토크 오차와 비교 시간을 기록한다. 장시간 chaos로 인한 차이와 즉시 구현 오류를 구분한다.
- TrackingSim 기존 경로는 물리 1 ms, 제어 20 ms를 사용한 기록이 있다. 실행 중 모델의 실제 timestep/substeps를 assert하며 문서 숫자로 대신하지 않는다.
- 후보용 복제 상태에서 qpos/qvel만 덮어쓰면 solver warm-start/actuator/history가 남을 수 있다. 같은 action sequence를 단일 환경에 재생해 실제 trajectory와 대조한다. reset의 의미도 코드에서 확인한다.

## 평가 계약

원본 기준과 수정 기준을 둘 다 보존하고, 종료식/시간축을 고정해 각각의 최초 위반 시각을 기록한다. 종료한 길이가 다른 rollout의 RMSE를 단독으로 비교하지 않는다. 원본 기준을 수정하거나 threshold를 높여 완주로 만들지 않는다.

표본별 root 위치/회전, joint error, joint/torque limits, 발 sliding, penetration과 contact를 기록한다. 20 ms output만 있으면 1 ms 내부 peak를 확인했다고 하지 않는다. 정적/근사 ZMP 합격은 실제 접촉 동역학 합격이 아니다. 별도 WBC나 retiming 결과는 원래 TrackingSim 성공과 구분한다.

## 학습과 재개

다른 GPU 작업/소유권을 확인하고 종료하거나 자원을 빼앗지 않는다. checkpoint가 model/optimizer만 보존한다면 RNG, replay buffer, simulator 상태까지 포함한 정확한 재개라고 부르지 않는다. 여러 seed와 교란, 원래 평가 조건으로 검증한 뒤 정책 성능을 판정한다. 실기 배포 자격은 별도 보정/평가가 충족될 때만 부여한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
