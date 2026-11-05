# 제출 완료까지 진행할 순서

## 현재 상태

- 로컬 프로그램과 기본 8문제 구현 완료
- 최소 2개 클래스, UTF-8 state.json 저장·불러오기 구현 완료
- 숫자 입력, 공백, 빈 입력, 범위, 중단, 파일 오류 처리 구현 완료
- 기능별 10개 이상의 커밋 및 feature/play 브랜치 생성·병합 기록 있음
- 자동 검증 15개 통과
- GitHub 공개 저장소 생성·push: 계정 연결 후 진행 필요
- GitHub 저장소 clone → 복제본 수정·commit·push → 원본 pull: 진행 필요
- 실제 개발환경·프로그램·Git 로그 화면 캡처: 진행 필요

## 1. 실행하고 화면 확인

VS Code에서 `scalp_hair_quiz` 폴더를 열고 **터미널 → 새 터미널**을 누릅니다.
PowerShell에서 아래 명령을 한 줄씩 실행합니다.

```powershell
python --version
git --version
git config user.name
git config user.email
python main.py
```

이 작업 환경에서 `python` 별칭이 실행되지 않으면 실제 설치 경로를 사용합니다.

```powershell
& "$env:LOCALAPPDATA\Python\bin\python.exe" -X utf8 main.py
```

다른 컴퓨터에서는 이 경로가 다를 수 있습니다. 설치된 Python 경로 또는 `py main.py`를 사용하세요.

메뉴 4로 아직 기록이 없다는 메시지, 메뉴 3으로 기본 문제 8개를 확인하세요.
메뉴 2로 본인이 만든 문제를 추가하고, 메뉴 1로 풀고, 메뉴 4로 점수를 확인합니다.
메뉴 5로 종료한 다음 다시 실행해 새 문제와 점수가 남아 있는지 확인합니다.

## 2. GitHub에 새 공개 저장소 생성 및 push

GitHub 로그인 후 새 저장소를 만듭니다. 이름 예: `scalp-hair-quiz`.
공개(Public)로 선택하고 README, .gitignore, license 자동 생성 옵션은 선택하지 않습니다.
이미 로컬에 해당 파일과 커밋 이력이 있기 때문입니다.

아래 `YOUR_ID`는 실제 GitHub 사용자 이름으로 바꾸세요.

```powershell
git status
git remote add origin https://github.com/YOUR_ID/scalp-hair-quiz.git
git push -u origin main
git push origin feature/play
```

GitHub 인증창이 나오면 본인 계정으로 로그인합니다. 비밀번호나 토큰을 코드·README에 적지 마세요.
`origin`이 이미 있으면 `git remote -v`로 주소를 먼저 확인하고 무조건 다시 추가하지 않습니다.

과제의 “첫 커밋 직후 push”는 로컬 개발 이후 나중에 수행한 push와 시점이 다릅니다.
이 프로젝트는 계정 연결 전 로컬 기능별 커밋을 먼저 만들었습니다.
초기 push 시점까지 엄격히 평가한다면 이 사실을 설명하거나,
담당 강사의 지침에 따라 본인이 새 저장소에서 단계별 실습을 진행하세요.
실제로 수행하지 않은 명령이나 스크린샷을 완료한 것처럼 제출하지 않습니다.

## 3. 별도 폴더에서 clone·수정·push 후 기존 폴더에서 pull

프로그램을 종료한 상태에서 진행하세요. 원래 프로젝트 폴더에서 시작합니다.
`YOUR_ID`를 실제 이름으로 바꾸고 복제 폴더가 이미 있다면 다른 새 이름을 사용하세요.

```powershell
cd ..
git clone https://github.com/YOUR_ID/scalp-hair-quiz.git scalp-hair-quiz-practice
cd scalp-hair-quiz-practice
```

VS Code로 복제본 README를 열어 끝에 다음 문장을 실제로 추가하고 저장합니다.

> 별도 복제 폴더에서 README를 수정하고 원격 동기화를 실습했습니다.

```powershell
git add README.md
git commit -m "Docs: 복제 저장소에서 원격 동기화 실습 기록 추가"
git push origin main
cd ..\scalp_hair_quiz
git pull --ff-only origin main
Get-Content README.md -Tail 3
git log --oneline --graph --all
```

이 단계는 GitHub의 실제 원격 저장소로 수행해야 합니다.
`Get-Content` 결과에 새 문장이 보이는지 확인하고 clone·pull 명령과 결과를 함께 캡처하세요.

## 4. 제출 스크린샷

Windows의 **Win+Shift+S**로 실제 실행 화면을 캡처합니다.
`docs/screenshots` 폴더를 만들고 아래 이름으로 저장하세요.

| 파일 이름 | 캡처할 내용 |
|---|---|
| environment.png | VS Code, Python 버전, Git 버전·설정 |
| menu.png | 프로그램 메뉴 |
| add_quiz.png | 직접 문제를 추가한 입력과 성공 메시지 |
| list.png | 추가한 문제가 포함된 목록 |
| play.png | 문제 풀이, 정답·오답 안내, 최종 결과 |
| score.png | 최고 점수 |
| reload.png | 재실행 후 추가 문제와 최고 점수 유지 |
| git_log.png | git log --oneline --graph --all 결과 |
| clone_pull.png | clone과 pull 명령 및 반영 확인 |

스크린샷을 저장한 다음 프로젝트 루트에서 업로드합니다.

```powershell
git add docs/screenshots
git commit -m "Docs: 실행 결과와 Git 실습 스크린샷 추가"
git push
```

최종 제출물은 실제 공개 GitHub 저장소 URL과 위 스크린샷입니다.
현재 README의 설명만으로 실제 캡처나 원격 실습이 대체되지는 않습니다.
