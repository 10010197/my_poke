# 포켓몬 도감

**배포 주소:** https://mypoke-porc9mctvvecmv2vywyqpe.streamlit.app/

전국도감 포켓몬(No.001 ~ No.1025)을 지역별로 이어서 볼 수 있는 Streamlit 웹 페이지입니다.
[PokeAPI](https://pokeapi.co/)의 GraphQL API에서 데이터를 받아 가로 8칸 바둑판 형태로 보여줍니다.

## 링크

| 구분 | 주소 |
|---|---|
| 배포 주소 | https://mypoke-porc9mctvvecmv2vywyqpe.streamlit.app/ |
| GitHub | https://github.com/10010197/my_poke |

## 주요 기능

- **로고 타이틀**: 상단에 `assets/logo.png` 로고를 가운데 정렬로 표시합니다. 이미지를 못 불러오면 글자 타이틀 "포켓몬 도감"이 대신 보입니다.
- **카드 바둑판**: 가로 8칸 그리드에 카드마다 **이미지 · 번호 · 이름 · 속성**을 표시합니다. 이름과 속성은 한국어(없으면 영어)이고, 이미지는 공식 일러스트입니다.
- **속성 색상 배지**: 속성마다 고유한 색 배지로 보여주고, 글자는 배경색에 따라 흰색/검은색 중 읽기 쉬운 색을 씁니다.
- **마우스 강조**: 기본은 이미지가 투명도 0.3으로 흐리게 보이고, 카드에 마우스를 올리면 1.0으로 선명해집니다. 마우스가 없는 기기(휴대폰·태블릿)에서는 처음부터 선명하게 보입니다.
  - `app.py`의 `HOVER_STYLE`을 `"grayscale"`로 바꾸면 회색 → 칼라 방식으로 바뀝니다.
- **지역별 이어 불러오기**: 처음에는 관동(1~151)만 보여주고, 맨 아래 **"다음 지역 불러오기"** 버튼을 누르면 성도 → 호연 → … → 팔데아 순서로 지역 구분선과 함께 이어서 불러옵니다.
  - `st.html`이 JavaScript를 지워 스크롤 끝을 감지할 수 없어서 버튼을 사용합니다.
- **캐시**: 지역별 API 응답은 하루 동안 캐시되어, 새로고침해도 다시 요청하지 않습니다.

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 언어 | Python 3.12 |
| 웹 프레임워크 | Streamlit |
| 데이터 | PokeAPI GraphQL (`https://graphql.pokeapi.co/v1beta2`) |
| HTTP 요청 | requests |
| 테스트 | unittest (파이썬 기본) |
| CI | GitHub Actions |

## 프로젝트 구조

```
my_poke/
├── app.py                  # 도감 페이지 (데이터 조회 + 화면 구성)
├── pokedex.py              # 테스트할 수 있는 작은 함수 (속성 색상, 지역 범위 등)
├── tests/
│   ├── test_pokedex.py     # 속성 색상·배지 글자색 테스트
│   └── test_region.py      # 지역 → 도감 번호 범위 테스트
├── assets/
│   └── logo.png            # 상단 로고 (투명 배경 PNG)
├── .github/
│   └── workflows/
│       └── tests.yml       # PR·master·develop 변경 시 테스트 자동 실행
├── CLAUDE.md               # 작업 규칙 (Git·Gitflow·이슈·개발 방식)
├── DESIGN.md               # 화면 디자인 가이드 (Clay 스타일)
├── requirements.txt        # 의존 패키지 목록
├── .claude/
│   └── launch.json         # Claude Code 미리보기용 실행 설정
└── .gitignore
```

## 시작하기

아래 명령은 Windows PowerShell 기준입니다.

### 1. 저장소 받기

```bash
git clone https://github.com/10010197/my_poke.git
```

```bash
cd my_poke
```

### 2. 가상환경 만들기

```bash
py -3.12 -m venv .venv
```

> `python` 명령이 Microsoft Store로 연결되는 PC에서는 위처럼 `py` 런처를 사용하세요.

### 3. 패키지 설치

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. 실행

```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

브라우저에서 http://localhost:8501 이 열리면 도감이 표시됩니다.
처음 실행할 때는 PokeAPI에서 데이터를 받아오느라 몇 초 걸릴 수 있습니다.

> 가상환경을 활성화(`.venv\Scripts\Activate.ps1`)했다면 `streamlit run app.py`만 입력해도 됩니다.

## 테스트

`pokedex.py`의 함수는 `tests/` 폴더의 unittest로 확인합니다. 저장소 맨 위 폴더에서 실행하세요.

```bash
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Pull Request를 올리거나 `master`·`develop`에 변경이 생기면 GitHub Actions(`.github/workflows/tests.yml`)가 같은 테스트를 자동으로 실행합니다. 결과는 PR의 Checks 탭이나 저장소의 Actions 탭에서 볼 수 있습니다.

## 개발 가이드

자세한 규칙은 [CLAUDE.md](CLAUDE.md)에 있습니다. 요약하면 다음과 같습니다.

### 브랜치 (Gitflow)

| 브랜치 | 역할 |
|---|---|
| `master` | 운영 배포본 |
| `develop` | 개발 통합본 (GitHub 기본 브랜치) |
| `feature/<이름>` | 기능 작업. `develop`에서 만들고 `develop`으로 PR |
| `feature/issue-<번호>` | 이슈 작업. 이슈 하나당 브랜치 하나, PR 하나 |
| `release/<버전>` | 출시 준비. `develop`에서 만들고 `master`로 PR, 머지 후 `develop`에도 반영 |
| `hotfix/<이름>` | 긴급 수정. `master`에서 만들고 `master`로 PR, 머지 후 `develop`에도 반영 |

- `master`, `develop`에는 직접 커밋하지 않습니다. PR 머지는 사람이 합니다.
- 브랜치 삭제나 강제 덮어쓰기는 하지 않습니다.

### 커밋 메시지

`[feat]` / `[fix]` / `[docs]` / `[test]` / `[refactor]` 로 시작하고, 무엇을 왜 했는지 한국어로 씁니다.

### 이슈 처리

1. 이슈 본문의 "완료 기준"과 "건드리지 말 것"을 먼저 읽습니다.
2. `feature/issue-<번호>` 브랜치에서 작업합니다.
3. `develop`으로 PR을 만듭니다. 제목은 이슈 제목과 같게, 본문 첫 줄은 `closes #<번호>`, 그 아래 변경 요약과 확인 방법을 씁니다.

### 개발 방식 (테스트 먼저)

1. 테스트할 수 있는 작은 함수는 `pokedex.py`에 둡니다.
2. `tests/test_<대상>.py`에 unittest를 먼저 쓰고, 실패하는 것을 확인한 뒤 `[test]`로 커밋합니다.
3. 구현해서 테스트가 통과하면 `[feat]`로 커밋합니다.
4. 이미 있는 테스트는 지우거나 느슨하게 바꾸지 않습니다.
5. 화면(`app.py`) 변경은 테스트 대신 눈으로 확인하는 방법을 PR에 적습니다.
6. 새 패키지를 쓰면 `requirements.txt`에 추가합니다.

### 디자인

화면은 [DESIGN.md](DESIGN.md)(Clay 스타일)를 따릅니다. 크림색 배경에 6색 카드가 순서대로 반복됩니다.

이전에 다른 디자인 가이드를 시험한 브랜치도 남아 있습니다.
각 브랜치의 `DESIGN.md`는 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)에서 가져왔습니다.

| 브랜치 | 디자인 |
|---|---|
| `clay-design` | Clay 스타일 (지금 디자인의 출발점) |
| `pinterest-design` | Pinterest 스타일 — 크림톤 카드, 이미지 위 속성 태그 |

## 데이터 출처

- 포켓몬 데이터와 이미지: [PokeAPI](https://pokeapi.co/)
- 포켓몬 관련 이름과 이미지의 저작권은 Nintendo, Creatures Inc., GAME FREAK inc.에 있습니다. 이 프로젝트는 학습용입니다.
