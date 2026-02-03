![License](https://img.shields.io/badge/License-MIT-green.svg)
![Release](https://img.shields.io/github/v/release/studiojin-dev/adr-index-skill)

# adr-index 스킬

**TL;DR**  
아키텍처 결정을 ADR로 기록하고, 가벼운 `index.json`을 생성하며,  
`AGENTS.md`를 작게 유지하세요.  
ADR 변경 후 `$adr-index`(Codex) 또는 `/adr-index`(Claude/Gemini)를 실행합니다.

`adr-index`는 Codex / Claude / Gemini용 경량 스킬로, 에이전트 컨텍스트 사용을 최소화하면서
Architecture Decision Records(ADR)을 위한 검색 가능한 인덱스를 생성합니다.

이 스킬은 `AGENTS.md`가 무한히 커지는 것을 방지하고, 전체 문서 스캔이나 비싼 RAG 구성을
피하도록 설계되었습니다.

---

## 목적

이 스킬의 목적은 다음과 같습니다:

- 에이전트 컨텍스트를 비대하게 하지 않고 아키텍처 결정 이력 보관
- 관련 ADR을 빠르고 결정적으로 찾는 방법 제공
- 일관된 ADR 메타데이터 형식 강제
- 결정 이력과 에이전트 운영 규칙 분리

완료된 작업이나 긴 이력을 `AGENTS.md`에 저장하는 대신,
결정은 ADR로 기록하고 에이전트가 효율적으로 읽을 수 있는 작은 `index.json`에 요약합니다.

---

## 설치

### 옵션 1: 전역 설치(권장)

전역 Codex 스킬 디렉터리에 설치합니다:

```bash
git clone https://github.com/studiojin-dev/adr-index-skill.git \
  ~/.codex/skills/adr-index
```

설치 후 스킬이 감지되도록 Codex를 재시작하세요.

---

### 옵션 2: 리포지토리 단위 설치

리포지토리별로도 설치할 수 있습니다:

```bash
mkdir -p .codex/skills
git clone https://github.com/studiojin-dev/adr-index-skill.git \
  .codex/skills/adr-index
```

스킬 설정이 특정 프로젝트와 밀접하게 연결되어 있을 때 유용합니다.

---

### 도구별 설치 참고

```
#### Codex CLI
- 전역 사용 시 `~/.codex/skills/adr-index`에 설치합니다.
- `$adr-index`로 스킬을 실행합니다.
- 설치 후 스킬이 감지되도록 Codex를 재시작합니다.

#### Claude Code
- 스킬 디렉터리를 `.claude/skills/adr-index`(리포지토리 범위)
  또는 `~/.claude/skills/adr-index`(전역)에 둡니다.
- `/adr-index`로 스킬을 실행합니다.

#### Gemini CLI
- 스킬 디렉터리를 `.gemini/skills/adr-index` 또는
  환경에 맞는 전역 Gemini 스킬 디렉터리에 둡니다.
- `/adr-index`로 스킬을 실행합니다.
```

## 사용법

### ADR 형식

각 ADR은 `docs/adr/*.md`에 작성해야 합니다.

각 파일의 상단에 다음 형식을 사용하세요:

```md
# ADR-YYYYMMDD-####-XXX: Short descriptive title

Tags: api, database, performance
Status: Proposed | Accepted | Deprecated
Date: YYYY-MM-DD
TL;DR: One short sentence summarizing the decision.
```

헤더만 필수이며, 메타데이터 줄은 선택 사항이지만
인덱싱과 검색 품질을 높이기 위해 강력히 권장합니다.

---

### ADR 인덱스 생성

CLI에서 스킬을 실행하세요:

```
$adr-index        # Codex CLI
/adr-index        # Claude Code, Gemini CLI
```

스킬은 다음을 수행합니다:

1. ADR 파일(상단 섹션만) 스캔
2. `docs/adr/index.json` 생성 또는 업데이트
3. 최소 요약(ADR 개수와 출력 경로) 출력

생성된 인덱스에는 가벼운 메타데이터만 포함됩니다:

```json
{
  "id": "ADR-YYYYMMDD-####-XXX",
  "title": "Short descriptive title",
  "tags": ["api", "database"],
  "status": "Accepted",
  "date": "2026-01-31",
  "tldr": "One short sentence summarizing the decision.",
  "path": "docs/adr/ADR-YYYYMMDD-####-XXX-short-title.md"
}
```

에이전트는 이 파일을 사용해 모든 ADR 문서를 읽지 않고도 관련 결정을 찾을 수 있습니다.

---

## 권장 AGENTS.md 스니펫

```md
## Documentation Workflow

- ADRs MUST be written in `docs/adr/*.md`.
- When an ADR is added or modified, `docs/adr/index.json` MUST be updated.
- The ADR index MUST be generated using the `adr-index` skill.
- AGENTS.md MUST NOT accumulate completed work logs.
  Decisions MUST be recorded in ADRs; only links or short summaries are allowed here.

### ADR Detection Rule

If you make or rely on a decision that:
- introduces architectural constraints,
- involves trade-offs,
- or is not obvious from code alone,

you MUST pause and explicitly state:
"An ADR is required for this decision."
```

## ADR을 작성해야 할 때

다음 중 **하나라도** 해당하면 ADR을 작성하세요:

- 나중에 설명해야 할 결정을 내렸다.
- 대안을 비교한 뒤 하나를 선택했다(트레이드오프가 있었다).
- 결정이 향후 코드나 아키텍처에 제약을 만든다.
- 나중에 되돌리기 비용이 크다.
- `AGENTS.md`에 결정을 기록하고 싶어진다.
- “왜 이렇게 선택했나?”라는 질문이 다시 나올 가능성이 높다.

다음은 ADR을 작성하지 **말아야** 합니다:
- 단순한 버그 수정
- 동작이나 아키텍처 변화 없는 순수 리팩터링
- 아직 결론이 나지 않은 실험 작업
- 기존 ADR을 그대로 따르는 구현

---

## 빠른 ADR 판단 규칙(에이전트용)

문서 작업을 시작하기 전에 이 규칙을 사용하세요:

> 이 변경이 **시스템이 설계되거나 제약되는 방식**에 영향을 주고,  
> 그 이유가 **코드만으로는 명확하지 않다면**,  
> ADR이 필요합니다.

확신이 없다면 ADR을 작성하는 쪽을 기본값으로 하세요.
ADR 문서는 싸고, 결정 컨텍스트를 잃는 비용은 큽니다.

## 실전 예시

### 예시 1: 새로운 오류 응답 형식 도입

RFC 7807을 사용해 모든 API 오류 응답을 표준화하기로 결정합니다.

- 여러 서비스와 클라이언트에 영향을 준다.
- 대안들을 비교했다.
- 나중에 되돌리기 비용이 크다.

✅ 조치:
- 결정 내용을 설명하는 ADR을 새로 작성한다.
- `$adr-index` 또는 `/adr-index`를 실행한다.
- 필요하다면 AGENTS.md에 남은 완료 항목을 제거하고 링크만 남긴다.

---

### 예시 2: 아키텍처 영향 없는 리팩터링

외부 동작이나 제약을 바꾸지 않고 내부 함수를 가독성 개선 목적으로 리팩터링한다.

- 새로운 규칙이나 계약이 추가되지 않는다.
- 시스템 설계는 그대로다.

❌ 조치:
- ADR을 작성하지 않는다.
- `adr-index`를 실행하지 않는다.

---

### 예시 3: 데이터베이스 기술 선택

JSONB 지원과 인덱싱 요구 때문에 MySQL 대신 PostgreSQL을 선택한다.

- 여러 대안을 평가했다.
- 이 결정이 향후 스키마 설계를 제약한다.
- 다른 컴포넌트가 이 선택에 의존한다.

✅ 조치:
- 맥락, 결정, 결과를 담은 ADR을 작성한다.
- 커밋 전에 `adr-index`를 실행한다.
- AGENTS.md에 결정 상세가 남지 않도록 한다.

---

### 예시 4: 에이전트 보조 작업 완료

에이전트가 기능 구현을 끝내고 AGENTS.md에 완료 표시를 남긴다.

- 작업이 새로운 아키텍처 규칙이나 제약을 도입했다.

✅ 조치:
- 완료 항목을 ADR로 전환한다.
- `adr-index`를 실행한다.
- AGENTS.md에서 완료 항목을 제거한다.

## 참고 사항, 주의점, 장점

- 이 스킬은 완료된 작업 로그를 **저장하지 않습니다**.
  결정은 ADR에 기록하고, 실행 이력은 이슈/PR/체인지로그에 남겨야 합니다.

- `adr-index`를 사용하면 `AGENTS.md`를 작고 안정적으로 유지할 수 있습니다.
  `AGENTS.md`는 다음에 집중할 수 있습니다:
  - 프로젝트 규칙
  - 현재 컨텍스트
  - ADR로 향하는 링크나 짧은 요약

- 가벼운 `index.json`에 의존함으로써 모든 ADR 문서를 스캔하지 않고도
  관련 결정을 찾을 수 있습니다.
  이는 컨텍스트 사용량과 토큰 소비를 크게 줄입니다.

- 이 워크플로는 임베딩, 벡터 데이터베이스, RAG 파이프라인 없이도
  장기적인 결정 추적을 가능하게 합니다.
  모든 출력은 결정적이고 로컬이며 감사하기 쉽습니다.

- ADR 파일의 상단 섹션만 스캔합니다.
  이를 통해 실행이 빠르고 불필요한 내용을 컨텍스트로 가져오지 않습니다.

- 리포지토리 루트 감지가 실패하면 스크립트는 현재 작업 디렉터리를
  기본값으로 사용하고 경고를 출력합니다.

---

## 권장 PR 체크리스트(선택 사항)

GitHub(또는 유사 플랫폼)를 사용하는 팀이라면
PR 템플릿에 **“ADR 필요?”** 체크리스트를 추가하는 것을 권장합니다.

이 스킬은 리포지토리 워크플로나 PR 템플릿을 자동으로 수정하지 않습니다.
이 체크리스트는 **사람과 팀 수준의 가드레일**이며, `adr-index` 스킬의 기능이 아닙니다.

### 예시 PR 체크리스트

다음을 `.github/pull_request_template.md`에 추가하세요:

```
### ADR Check

- [ ] This PR introduces a new architectural or design decision
- [ ] An ADR has been added or updated
- [ ] `adr-index` has been run and `docs/adr/index.json` is up to date

If no ADR is required, briefly explain why:
```

### 왜 도움이 되나요

- 아키텍처 결정을 문서화하지 않고 머지하는 것을 방지
- 리뷰 중 ADR을 고려하도록 유도
- `AGENTS.md`가 장기 기록 로그로 변하지 않도록 유지
- 사람과 에이전트의 행동을 같은 결정 기준으로 정렬

---

## 라이선스

MIT License
