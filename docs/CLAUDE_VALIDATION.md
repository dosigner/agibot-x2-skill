# Claude Code와 Codex 요청 비교, 1.2.2

2026-11-17. Claude Code 2.1.326의 초기화 이벤트에서 모델은 `claude-fable-5-2`로 관측됐으며 모델을 명시적으로 바꾸지 않았다. 비교 대상은 이전 Codex CLI 0.169.0의 기본 모델 실행 기록이다. 클라이언트와 모델이 모두 다르므로 결과 차이를 클라이언트만의 효과나 모델의 일반적인 우열로 해석하지 않는다.

## 같은 시나리오의 결과

기존 [16개 요청과 fixture](../tests/behavior_cases.json)는 그대로 유지했다. 각 요청은 새 임시 프로젝트에서 실행했고 기대 스킬/정답을 모델에 주지 않았다. Claude에는 `.claude/skills/`와 CLAUDE.md, Codex에는 `.agents/skills/`와 AGENTS.md를 사용했다. 환경 제약의 뜻은 동일하게 유지했다. 모델 호출은 온라인이며 작업은 합성 로컬 데이터로 제한했다.

- 기존 16개 모두 필수 스킬 선택과 구조화 값/독립 수치 검사에 통과했다.
- 기본 스킬 포함 11개가 모두 실제로 사용됐다. 일반 문장/조화진동자 요청 두 개에는 X2 스킬을 호출하지 않았다.
- sensors/control 단독 설치에서도 통과했다.
- 역투영, 강체 변환, 제어 ledger와 단독 sensors 생성 코드는 기존 [독립 검사](../tests/behavior_oracles.py)를 그대로 통과했다.
- 설명 검토에서는 HRI의 다음 시험 제안 한 곳에서 기준 벡터 차감과 중력 제거를 혼동할 수 있는 표현을 발견했다. 구조화 값이 맞다는 이유로 설명 전체를 합격 처리하지 않았다.
- HRI 보완 뒤 Claude와 Codex 모두 원래 HRI 요청과 새 기울기 반례 두 개를 다시 통과했다. 나머지 15개는 본문이 바뀌지 않았으며 최종 평가에 사용한 본문의 SHA-256을 배포 파일과 대조했다.

[결과와 산출물 hash](validation/claude-forward-testing.json)에 요청별 필수 선택, 실제 소비한 스킬과 비교를 기록한다. Claude는 성공한 native `Skill` 호출 또는 SKILL.md 읽기로 확인했고, Codex는 실제 파일 읽기로 확인했다. 초기화 목록에 등록된 것만으로 사용했다고 판정하지 않았다. 원시 모델 trace, 개인 경로와 계정 정보는 공개하지 않는다.

## 차이 1: 설정 로딩이 스킬 발견을 막음

동일한 스킬 파일을 사용한 초기화 대조 결과:

| setting-sources | restricted | 등록된 X2 스킬 |
|---|---|---:|
| 빈 목록 | 켬 | 0 |
| project | 켬 | 0 |
| 빈 목록 | 끔 | 0 |
| project | 끔 | 11 |

다른 옵션을 맞춘 restricted 재검사에서도 0개였다. 빈 setting-sources는 Codex의 ignore-user-config와 같은 의미가 아니었다. 프로젝트 source를 제외하면 프로젝트 스킬도 빠진다. 이 버전의 restricted 모드도 프로젝트 스킬을 숨겼다. 설치 파일이나 한국어 description을 바꿔 해결할 문제가 아니었다.

실제 평가는 vetted 임시 폴더의 project source를 사용하고, 파일 도구의 외부 접근 차단, 셸 sandbox, 명시적 도구 목록과 dontAsk를 별도로 적용했다. managed 정책이나 원래 프로젝트 설정은 변경하지 않았고 bypassPermissions/skip-permissions를 사용하지 않았다. 이 결과를 제한 모드를 무조건 해제하라는 설치 지침으로 쓰지 않는다.

공식 문서는 [스킬 위치와 로딩](https://code.claude.com/docs/en/skills#choose-where-skills-load), [설정 source와 추가 디렉터리](https://code.claude.com/docs/en/permissions#additional-directories-grant-file-access-not-configuration)를 설명한다. restricted의 효과는 설치 CLI help와 위 대조 실행에 근거한다.

## 차이 2: 좁은 셸 허용 목록과 복구 경로

16개 중 10개에서 cd를 포함한 복합 명령이나 shell redirection이 허용 목록에 맞지 않아 거부됐다. 모델은 허용된 Read/Write와 직접 Python 명령으로 계속했다. 거부된 검사를 실행했다고 보고하지 않았고, 코드 산출물은 평가자가 별도 검사했다. 원래 세 코드 구현 요청과 단독 sensors에서는 실제 자체 검사 실행도 관측됐다. interface 요청도 뒤이은 직접 lookup 실행을 확인했다.

이 차이는 평가 도구 정책 차이다. 스킬에 넓은 allowed-tools 권한을 추가하거나 제한을 우회하지 않았다. 최종 결과가 필요한 경우 개별 도구의 성공/거부와 artifact를 각각 확인해야 한다.

## 차이 3: HRI 설명의 조건 누락

첫 HRI 결과의 다음 시험 제안에는 안정 구간 기준 벡터로 중력을 제거한다는 표현이 있었다. 기존 기록과 구현은 기준 벡터와 측정 벡터의 차이를 다룬다. 자세가 바뀌면 센서 축의 중력 성분도 바뀌므로, 차감만으로 중력이 제거됐다고 할 수 없다.

동일 요청 재실행에서는 그 혼동이 반복되지 않았다. 수정 전에도 별도 기울기 반례를 제시하자 정확히 설명했다. 따라서 지속적인 계산 오류나 일반적인 물리 이해 부족으로 단정하지 않는다. 수정은 [HRI 스킬](../skills/agibot-x2-hri/SKILL.md)의 한 문단에 한정했다. 기준 차감과 중력 보상을 구분하고 후자에는 같은 시각의 자세/좌표/부호 계약이 필요하다고 명시했다.

추가한 합성 반례는 병진 가속도 없이 센서만 90° 기울어진 두 상태다. 비력 벡터가 `(0,0,g)`에서 `(g,0,0)`으로 바뀌면 단순 차이의 노름은 `sqrt(2)g = 약 13.868697 m/s²`다(`g=9.80665 m/s²`). 이 값으로 외력을 계산할 수 없다. 수치 비교 허용치는 출력 반올림을 고려해 `1e-5 m/s²`이며 원래 16개 검사 조건은 바꾸지 않았다.

보완 후 두 클라이언트 모두 기준 차감을 중력 제거로 판정하지 않았고 force_newtons를 null로 남겼다. 한 번의 보완 후 성공이 모든 향후 표현을 보장하는 것은 아니다.

## 추가 경계값: 결측과 잘못된 설정이 동시에 있을 때

같은 생성 코드에 `raw=0`, `scale_m_per_raw=0`을 함께 넣어 대조했다. Codex의 원래 sensors 산출물은 결측 판정을 먼저 해 None을 반환했고, Claude의 일반/단독 sensors 산출물은 calibration 검증을 먼저 해 ValueError를 냈다. 개별 결측과 개별 invalid calibration 검사는 양쪽 모두 통과했다.

원래 요청은 두 조건이 동시에 발생했을 때의 우선순위를 지정하지 않았다. 따라서 이 교차 조건을 기존 합격/불합격 기준에 소급 추가하거나 동일한 코드라고 주장하지 않는다. 스킬에 전역 우선순위를 새로 강제하는 수정도 하지 않았다. 실제 제품에 이 함수를 채택할 때는 결측 처리와 설정 검증의 우선순위를 계약으로 정하고 해당 조합을 회귀 검사에 포함해야 한다. 이 차이는 [비교 결과](validation/claude-forward-testing.json)에 별도로 기록했다.

## 선택의 부수적 차이

일부 요청에서 Codex는 관련 보조 스킬을 추가로 읽고 Claude는 주 스킬만 호출했다. 예를 들어 모션 비교는 Codex가 motion-retargeting과 simulation, Claude가 motion-retargeting을 사용했다. 필수 계약과 결과는 같았으므로 보조 스킬 개수에 맞추기 위한 수정은 하지 않았다. runtime diagnosis의 JSON 구조처럼 요청이 타입을 지정하지 않은 부가 설명 차이도 실패로 세지 않았다.

## 재현

[기존 준비 절차](BEHAVIOR_VALIDATION.md#한-요청-재현)에서 스킬 경로를 `.claude/skills`, 제약 파일을 CLAUDE.md로 바꾸고 같은 prompt/files를 사용한다. TRIAL에 생성된 실제 경로를 지정한 뒤 그 폴더에서 아래 명령을 실행한다. 인증된 CLI와 모델 사용량이 필요하다.

```sh
claude -p --no-session-persistence --setting-sources project \
  --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
  --settings '{"disableAllHooks":true,"permissions":{"blockReadsOutsideWorkingDirectories":true,"blockWritesOutsideWorkingDirectories":true},"sandbox":{"enabled":true,"autoAllowBashIfSandboxed":false}}' \
  --tools 'Read,Write,Edit,Bash,Glob,Grep,Skill' \
  --permission-mode dontAsk \
  --allowedTools 'Read,Write,Edit,Glob,Grep,Skill,Bash(python3 *),Bash(python *),Bash(cat *),Bash(ls *),Bash(pwd)' \
  --output-format stream-json --verbose \
  < prompt.txt > events.jsonl
```

모델 init의 skills 목록, 성공한 Skill/Read 호출, 요청 artifact와 Python oracle을 각각 확인한다. 기록의 permission_denials를 숨기지 않는다. 이 CLI 설정은 격리된 평가용 예시이며 다른 작업에 필요한 정책을 대체하지 않는다.

데스크톱 선택 UI, Cursor 모델 동작, 여러 모델/반복 분포, 실제 로봇과 새 물리 시뮬레이션은 안 돌려 봤음. 공유 8908과 로봇 서비스는 조작하지 않았다.
