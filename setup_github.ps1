# GitHub 저장소 설정 스크립트
# 사용법: .\setup_github.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub 저장소 설정" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# GitHub 사용자명 입력
$username = Read-Host "GitHub 사용자명을 입력하세요"

if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "사용자명이 입력되지 않았습니다." -ForegroundColor Red
    exit 1
}

# 저장소 이름
$repoName = "ai_research"

Write-Host ""
Write-Host "다음 단계를 따라주세요:" -ForegroundColor Yellow
Write-Host "1. https://github.com/new 에서 새 저장소를 생성하세요"
Write-Host "2. Repository name: $repoName"
Write-Host "3. Public 또는 Private 선택"
Write-Host "4. README, .gitignore, license는 추가하지 마세요 (이미 있음)"
Write-Host "5. 'Create repository' 클릭"
Write-Host ""

$continue = Read-Host "저장소를 생성하셨나요? (y/n)"

if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "저장소 생성 후 다시 실행해주세요." -ForegroundColor Yellow
    exit 0
}

# 원격 저장소 추가
$remoteUrl = "https://github.com/$username/$repoName.git"
Write-Host ""
Write-Host "원격 저장소 추가 중: $remoteUrl" -ForegroundColor Green

git remote add origin $remoteUrl
if ($LASTEXITCODE -ne 0) {
    Write-Host "원격 저장소가 이미 존재합니다. 업데이트합니다..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
}

# 브랜치 이름 확인
git branch -M main

# Push
Write-Host ""
Write-Host "GitHub에 Push 중..." -ForegroundColor Green
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "성공! 저장소가 GitHub에 업로드되었습니다." -ForegroundColor Green
    Write-Host "저장소 URL: https://github.com/$username/$repoName" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Push 실패. GitHub 인증이 필요할 수 있습니다." -ForegroundColor Red
    Write-Host "GitHub Personal Access Token을 사용하거나 GitHub Desktop을 사용해주세요." -ForegroundColor Yellow
}
