# 포켓몬 도감

1세대 포켓몬(No.001 ~ No.151)을 한눈에 볼 수 있는 Streamlit 웹 페이지입니다.
[PokeAPI](https://pokeapi.co/)의 GraphQL API에서 데이터를 받아 가로 8칸 바둑판 형태로 보여줍니다.

## 링크

| 구분 | 주소 |
|---|---|
| 배포 주소 | https://mypoke-porc9mctvvecmv2vywyqpe.streamlit.app/ |
| GitHub | https://github.com/10010197/my_poke |

## 주요 내용

- 1세대 포켓몬 151마리를 가로 8칸 그리드로 나열
- 카드마다 **이미지 · 번호 · 이름 · 속성**만 표시
- 이름과 속성은 한국어로 표시 (한국어 데이터가 없으면 영어)
- 이미지는 공식 일러스트(official artwork) PNG 사용
- API 응답은 하루 동안 캐시되어, 새로고침해도 다시 요청하지 않음

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 언어 | Python 3.12 |
| 웹 프레임워크 | Streamlit |
| 데이터 | PokeAPI GraphQL (`https://graphql.pokeapi.co/v1beta2`) |
| HTTP 요청 | requests |

## 프로젝트 구조

```
my_poke/
├── app.py              # 도감 페이지 (데이터 조회 + 화면 구성)
├── DESIGN.md           # 화면 디자인 가이드 (Clay 스타일)
├── requirements.txt    # 의존 패키지 목록
├── .claude/
│   └── launch.json     # Claude Code 미리보기용 실행 설정
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

## 디자인 브랜치

같은 도감을 다른 디자인 가이드로 꾸민 브랜치가 있습니다.
각 브랜치의 `DESIGN.md`는 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)에서 가져왔습니다.

| 브랜치 | 디자인 |
|---|---|
| `master` | Clay 스타일 — 크림 배경, 6색 카드가 순서대로 반복 |
| `clay-design` | Clay 스타일 (`master`에 반영됨) |
| `pinterest-design` | Pinterest 스타일 — 크림톤 카드, 이미지 위 속성 태그 |

다른 디자인을 보려면 브랜치를 바꾼 뒤 다시 실행하세요.

```bash
git switch pinterest-design
```

## 데이터 출처

- 포켓몬 데이터와 이미지: [PokeAPI](https://pokeapi.co/)
- 포켓몬 관련 이름과 이미지의 저작권은 Nintendo, Creatures Inc., GAME FREAK inc.에 있습니다. 이 프로젝트는 학습용입니다.
