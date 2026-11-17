# 실제 요청 기반 스킬 평가, 1.2.1

2026-11-17, codex-cli 0.169.0. 새 임시 프로젝트마다 스킬을 설치하고 자연어 요청을 실행했다. 이전 대화, 의도한 스킬 이름, 기대 결과와 독립 검사용 정답은 모델 프롬프트에 주지 않았다. 모델 호출은 온라인이며 작업은 로컬 합성 fixture에 한정했다. 로봇, SSH, 공유 8908과 외부 자료에 접근하지 않았다.

## 결과

1.2.0 기준 13개 요청이 통과했다. 정적 검토에서 보완한 1.2.1은 16개 고유 요청이 통과했고, 제어 문서의 시간 정규화 표기 보완 뒤 관련 두 요청도 새 실행으로 다시 통과했다. 기본 스킬을 포함한 11개 스킬을 모두 한 번 이상 실제로 읽었다. 문장 교정과 로봇 무관 조화진동자 계산에서는 X2 스킬을 읽지 않았다. 이 수치는 작은 표본의 관측이며 일반적인 자동 선택 정확도 100%나 무스킬 대비 성능 향상을 의미하지 않는다.

선택 판정은 답변의 자기 보고만 사용하지 않았다. 실행 trace에서 해당 SKILL.md를 읽은 명령과 반환 내용을 확인했다. 결과 JSON의 값, 생성한 파일과 아래 독립 계산을 대조했다. 최종 요청별로 실제 읽은 스킬 본문의 SHA-256이 배포 본문과 같음을 검사했다. [기계 판독 결과](validation/forward-testing.json)에 스킬/산출물 hash를 보존한다. 원시 모델 trace와 개인 환경 경로는 공개하지 않는다.

| 요청 | 확인한 결과 |
|---|---|
| PC2 Python 타입 import 실패 | runtime 선택, 생성 모듈/타입 지원과 환경 경로 진단, 실기 검증으로 과장하지 않음 |
| RGB-D 역투영 구현 | sensors 선택, 광축 깊이와 range 구분, 결측/비유한/잘못된 보정 입력 처리 |
| Canis 연결 뒤 무응답 | voice 선택, 연결 성공을 대화 성공으로 보지 않고 스피커 고장을 확정하지 않음 |
| PC3 얼굴 영상 fit | face 선택, 콘텐츠 800×480, fit 800×450, 상하 15 px, 패널 Hz는 미확인 |
| 터치/IMU 해석 | hri 선택, contact_only, 힘 N 환산과 접촉 횟수 정확도 주장 거부 |
| 지도→몸체 변환 구현 | slam-navigation 선택, 곱셈 순서와 센서 변환 역행렬, 비강체 입력 거부 |
| 모션 요청 ledger 구현 | control 선택, not_sent/accepted/running/finished/unknown, 전송 후 재시도 차단 |
| 공유 8908 재시작 검토 | dashboard 선택, 활성 채팅 미확인 상태에서 restart_allowed=false |
| 원본 영상/자세 시각 | motion-retargeting 선택, 요청 currentTime 대신 디코딩 PTS 사용, 종료 이후 물리 결과 미표시 |
| TrackingSim 평가 | simulation 선택, 원본 실패와 수정 기준 완료 구분, 불완전 checkpoint의 정확 재개 주장 거부 |
| 공식 RGB-D 예제 탐색 | interfaces의 실제 lookup 실행, 링크 발견과 계약 검증 구분 |
| 다른 프로젝트 버전 요구 | 명시한 AimDK 1.1.0/MuJoCo 3.11 유지, 원 프로젝트 선택을 강요하지 않음 |
| sensors만 설치 | core 스킬 없이도 역투영 산출물 독립 검사 통과 |
| control만 설치 | 내부 최대 1 rad 계산, ±0.5 rad 궤적 거부, N/A=0 및 좌우 대칭 추정 거부 |
| 일반 문장 교정 | X2 스킬 미선택, 요청한 파일 생성 |
| 일반 조화진동자 | X2 스킬 미선택, 주기 π s와 가정 기록 |

## 독립 산출물 검사

생성 코드의 자체 테스트와 별개로 [수치/실패 입력 검사](../tests/behavior_oracles.py)를 실행했다.

- 센서: optical-Z=2.5 m에서 XYZ=(0.5, 0.25, 2.5) m, range의 단위 ray 계산 또는 명시적 미지원 거부, NaN/Inf/음수/scale=0/초점거리=0/raw-fisheye 거부.
- 지도: 90° 회전과 병진, 센서 offset의 역변환을 조합해 기대 좌표 대조. 반사, scale, 비유한 값, 잘못된 마지막 행/shape를 네 입력 위치 각각에 주입.
- 제어: 일관된 상태 전이 6개와 전송 여부별 retry, bool 대신 int/string/null을 각 필드에 주입. 수락 응답 및 cleanup 미확인 경계를 검사.

이 검사는 좌표/상태 로직을 검증하며 물리 보정, 네트워크나 실제 로봇 운동 검증이 아니다.

## 발견과 수정의 근거

이번 baseline에서 잘못된 선택/산출물 실패를 재현한 것은 없다. 아래는 문서 간 대조에서 발견한 누락/모호성으로, 행동 실패를 관측했다고 보고하지 않는다.

1. runtime/interfaces/sensors/control/simulation의 버전 문구가 원 프로젝트와 대상 프로젝트를 분명히 구분하지 않는 부분을 보완했다. 명시적 업그레이드/별도 버전 요구가 우선이다.
2. 단독 설치 sensors에 core의 역투영 적용 조건이 빠져 있었다. optical-Z/range, pinhole/왜곡, optical 축과 body TF를 추가했다.
3. 단독 설치 control에 core의 N/A, 좌우 비대칭, 연속 궤적 극값 규칙이 빠져 있었다. 짧은 반례와 함께 추가했다.
4. 설치 안내의 공통 확인 단계가 전문 스킬에도 lookup.py를 요구했다. core만 lookup을 실행하고 전문 스킬은 자기 verifier/references를 확인하도록 고쳤다.

## 한 요청 재현

[요청/fixture 목록](../tests/behavior_cases.json)의 expected_skills와 checks는 평가자용이다. 모델에는 prompt와 files만 준다. 아래 준비 코드는 로컬 파일만 만들며 모델은 실행하지 않는다. 저장소 루트에서 실행한다.

```sh
python3 - <<'PY'
from pathlib import Path
import json, shutil, tempfile
repo = Path.cwd()
case = next(c for c in json.loads((repo/'tests/behavior_cases.json').read_text())
            if c['id'] == 'sensors')
work = Path(tempfile.mkdtemp(prefix='x2-behavior-'))
for name in case.get('installed_skills', [p.name for p in (repo/'skills').iterdir()]):
    shutil.copytree(repo/'skills'/name, work/'.agents/skills'/name)
for name, content in case['files'].items():
    (work/name).write_text(content)
(work/'prompt.txt').write_text(case['prompt'])
(work/'AGENTS.md').write_text('Use only this workspace. No robot, SSH, network data access, other project access or subagents. Use available skills where relevant. Complete the task and report actual checks. Fixtures are synthetic. Do not modify skills.\n')
print(work)
PY
```

출력된 경로를 사용해 새 Codex 실행을 시작한다. 모델 사용량이 발생하며 인증된 CLI가 필요하다. 모델/개인 스킬 설정이 바뀌면 결과도 달라질 수 있다. 실제 실행에서는 사용자 config를 읽지 않는 옵션을 사용했지만 개인 스킬 catalog는 함께 제공됐다. 모델/추론 강도를 명시적으로 덮어쓰지 않았다.

```sh
codex exec --ignore-user-config --ephemeral --skip-git-repo-check \
  --sandbox workspace-write -c 'approval_policy="never"' \
  -C "$TRIAL" --json -o "$TRIAL/answer.md" - \
  < "$TRIAL/prompt.txt" > "$TRIAL/events.jsonl"
python3 tests/behavior_oracles.py sensors "$TRIAL"
```

TRIAL에는 위에서 출력한 실제 경로를 지정한다. 읽기 trace와 artifact를 확인하기 전 모델의 완료 문구만으로 합격시키지 않는다. Claude/Cursor의 모델 실행, Codex 데스크톱 picker UI, 다른 모델/반복 분포, 실기와 새로운 물리 시뮬레이션은 이번 평가에 포함하지 않았다.
