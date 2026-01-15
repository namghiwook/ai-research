# GitHub에 Push하는 방법

현재 프로젝트는 Git 저장소로 초기화되었고 커밋이 완료되었습니다.

## 빠른 방법

### 1단계: GitHub에서 저장소 생성

1. https://github.com/new 접속
2. Repository name: **ai_research** 입력
3. Public 또는 Private 선택
4. **README, .gitignore, license는 추가하지 마세요** (이미 있음)
5. "Create repository" 클릭

### 2단계: 원격 저장소 연결 및 Push

터미널에서 다음 명령어를 실행하세요 (YOUR_USERNAME을 본인의 GitHub 사용자명으로 변경):

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai_research.git
git branch -M main
git push -u origin main
```

또는 PowerShell 스크립트 사용:

```powershell
.\setup_github.ps1
```

## 현재 커밋된 파일

- ✅ 모든 Python 소스 코드
- ✅ README.md
- ✅ requirements.txt
- ✅ .gitignore
- ✅ doc/plan.md
- ✅ 메타데이터 파일들 (JSON, TXT)

**참고**: 큰 CSV/PKL 파일들은 .gitignore에 의해 제외되어 있습니다.
