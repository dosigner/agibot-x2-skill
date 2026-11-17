---
name: agibot-x2-dashboard
description: X2 공유 8908 대시보드의 배포/재시작 조율, 서버와 worker 버전 불일치, stale UI, 폴링 지연, 지도/음성/모션 GUI 검증을 수행할 때 사용한다.
---

# X2 공유 대시보드 운영

## 공유 서버 작업

공유 8908을 조작하거나 재시작하기 전 프로젝트의 `src/x2_teleop_dashboard/RESTART_COORDINATION.md`를 실제로 읽는다. 포트 번호만 같고 다른 프로젝트라면 그 프로젝트의 소유/조율 계약부터 확인한다. [배포와 상태 교훈](references/lessons.md)을 읽는다.

- 여러 명령/브라우저 작업은 coordination hold/work로 등록하고 보호 등록 성공 뒤 시작한다. 완료/오류 모두 등록을 해제한다.
- 재시작 전 활성 Codex 채팅과 등록 상태를 함께 확인한다. 미등록 작업의 종료를 기다린다. 채팅 활동, 서버 지원 또는 필수 상태를 모르면 서버를 유지한다.
- guarded restart를 사용한다. 상태 스냅샷만 보고 kill/launchctl로 우회하지 않는다. health의 `restart_coordination` 지원, 실제 감독 프로세스 소유 관계와 모든 실행 상태가 필요하다.
- 조율은 협력 작업용이다. 외부 앱/직접 로봇 작업까지 잠그거나 물리 정지를 보장하지 않는다.

## 적용 여부 판정

저장 파일, 실제 HTTP가 제공한 JS, 현재 Python 프로세스, 매 요청마다 전송하는 remote worker, PC2 서비스 설치본을 별도로 확인한다. JS가 최신이어도 Python API는 구버전일 수 있고, 과거 worker 설치 파일과 실제 전송 소스도 다를 수 있다. 실제 응답/해시/실행 경로를 근거로 재시작 필요 여부를 결정한다.

## 상태 UI와 성능

- `loading / running / complete / cancelling / failed / unknown / stale`를 실제 서버 상태에 연결한다. accepted를 complete로 표시하지 않는다. 상태의 원본 관측 시각을 보존한다.
- 숨김/탭 이탈에서 polling, pending fetch, animation, listener를 정리하고 generation으로 늦은 응답을 거부한다. 이전 프레임을 유지하면 과거 표시임을 명시한다.
- 제어 readiness에는 필요한 상태 요약만 사용한다. 전체 pose history/점군 복사나 매 poll 대형 JSON 직렬화를 피한다. 독립 실험과 실제 서버 지연을 같은 성능 결과로 섞지 않는다.
- 누락 값은 unavailable/unknown으로 표시한다. 수집하지 않는 GPU/VRAM을 0%로 만들지 않는다. 연결 오류는 비밀을 제거한 실패 계층을 남긴다.

## GUI 검증

로봇 미연결 격리 서버와 현재 fixture로 데스크톱/모바일, 키보드, 실패/취소/stale를 검사한다. 적어도 한 표시값을 실제 API/저장 데이터와 대조한다. synthetic/replay/live 출처를 표시한다. 관련 테스트를 삭제/skip해 통과시키지 않는다. 공유 8908 확인이 필요할 때만 위 조율을 적용한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
