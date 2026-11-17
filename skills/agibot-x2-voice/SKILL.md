---
name: agibot-x2-voice
description: X2 PC2의 x2_gemini_voice, Canis 호출어, raw/processed 음성 전환, 오디오 소유권, Gemini 연결 이후 무응답 또는 PC3 HAL 재생 문제를 진단할 때 사용한다.
---

# X2 PC2 음성 파이프라인

## 보드와 실행본

PC2 (`soc_index=1`)는 사용자 `x2_gemini_voice`, PC3 (`soc_index=2`)는 제조사 `aima-agent-app`과 출력 경로를 담당한다. 현재 서비스의 실행 경로, 선택 config, source hash, Audio Coordinator/lease 상태를 확인한다. 저장소 README의 기본값과 실제 systemd 선택본을 구분한다. 모델/공급자 이름은 현재 설정에서 읽는다.

[실제 실패와 후보의 경계](references/lessons.md)를 읽고 한 시도의 같은 시간선으로 다음을 추적한다.

```text
Raw PCM → VAD → 호출어 ASR/matcher → Audio lease
→ 공급자 연결 → 최초 입력 PCM → 발화 종료 → 응답 audio/turn
→ 출력 focus/큐 → HAL publish → play_state → 현장 청취 → 해제
```

각 단계에 건수/바이트 수와 시각을 남긴다. transcript나 원본 음성이 필요하지 않으면 저장하지 않는다. `connected`, `active`, `ready`, `segments` 중 어느 것도 대화 성공 횟수가 아니다. `turn_complete`와 실제 재생 완료도 별개다.

## 입력과 수명주기

- 관측된 raw 포맷은 16 kHz S16LE, 마이크 4채널과 참조 2채널이었다. 실제 frame shape를 먼저 확인한다. channel index, interleave, endian과 clipping을 검사한 뒤 mono로 변환한다.
- 여러 마이크 평균, 단일 큰 RMS 후보, beamforming을 구분한다. 큰 RMS가 더 좋은 음성이란 보장은 없다. 호출어 후보와 공급자에 보낸 신호가 같은지도 기록한다.
- raw/processed 입력은 한 번에 한 소스가 소유한다. 호출어 발화와 연결 중 버퍼를 보존하며, 전환 전의 오래된 processed 활동을 새 발화로 인정하지 않는다. 짧은 raw 발화가 종료돼도 fallback 판단 전까지 보존한다.
- 이전 session/stream의 늦은 PCM/VAD callback을 generation으로 거부한다. BEGIN/END sentinel payload와 실제 음성을 구분한다.
- half-duplex echo guard가 입력을 막는 동안 barge-in을 지원한다고 표시하지 않는다. AEC 합성 시험 결과와 실기 echo 감쇠를 분리한다.
- lease, playback focus, flush와 종료를 별도 상태로 둔다. 결과 불명인 소유 표식은 강제로 지우지 않는다. 승인된 적용에서는 기존 release를 보존하고 idle/owner 확인 후 전환한다.

## 검증

합성 짧은 발화, 연결 지연, 오래된 processed 패킷, source 전환, 취소 및 재접속을 모의 공급자로 먼저 검사한다. 실기 평가는 호출어+첫 질문, 후속 질문과 맥락 유지, 언어 전환, 종료/재호출을 각각 확인한다. 호출어 성공률의 분모는 실제 의도한 발화 수이며 음성 구간 수가 아니다. 클라우드 전송은 사용자가 요청한 범위와 참여자 동의를 확인한다.

근거의 날짜, 출처 및 재확인 조건은 [근거 목록](references/evidence.md)을 따른다. 과거 보고서의 확인과 이번 실행의 확인을 분리해서 보고한다.
