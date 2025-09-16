<div align="center">

    2025 가을 축제 사이트 BE

</div>


<h3>동국대학교 멋쟁이사자처럼 13기, 2025 가을 축제사이트 BE 레포지토리입니다.</h3>

<br>

## ✅ Package Manager

- pip install requirements.txt

<br>

## ⌨️ Code Styling

- **snake_case**
  - 변수명, 함수명에 적용
  - 소문자 사용. 단어 간 구분에 '_' 사용

<br>

## 🔗 Git Convention

### 📌 Git Flow

```
dev ← 작업 브랜치
```

- `main branch` : 배포 브랜치
- `develop branch` : 개발 브랜치, feature 브랜치가 merge됨
- `feature branch` : 페이지/기능 브랜치

<br>

### ✨ Flow
- 이슈 생성
- 이슈 번호에 맞게 `develop 브랜치`에서 새로운 브랜치를 생성
- 작업을 완료하고 커밋 컨벤션에 맞게 커밋
- Pull Request 생성
- 코드 리뷰 후 `develop` 브랜치로 병합

<br>

### 🌱 Code Review
- **두 명**의 승인 필요
- pr 보내고 연락 남기기
- 가장 먼저 보는 사람이 리뷰 남기기
- 머지는 pr 올린 사람이

<br>

### 🔥 Commit Message Convention

- **커밋 유형**
  - 🎉 Init: 프로젝트 세팅
  - ✨ Feat: 새로운 기능 추가
  - 🐛 Fix : 버그 수정
  - 💄 Design : UI(CSS) 수정
  - ✏️ Typing Error : 오타 수정
  - 📝 Docs : 문서 수정
  - 🚚 Mod : 폴더 구조 이동 및 파일 이름 수정
  - 💡 Add : 파일 추가 (ex- 이미지 추가)
  - 🔥 Del : 파일 삭제
  - ♻️ Refactor : 코드 리펙토링
  - 🚧 Chore : 배포, 빌드 등 기타 작업
  - 🔀 Merge : 브랜치 병합

- **형식**: `커밋유형: 상세설명 (#이슈번호)`
- **예시**:
  - 🎉 Init: 프로젝트 초기 세팅 (#1)
  - ✨ Feat: 메인페이지 개발 (#2)

<br>

### 🌿 Branch Convention

**Branch Naming 규칙**

- **브랜치 종류**
  - `init`: 프로젝트 세팅
  - `feat`: 새로운 기능 추가
  - `fix` : 버그 수정
  - `refactor` : 코드 리펙토링

- **형식**: `브랜치종류/#이슈번호/상세기능`
- **예시**:
  - init/#1/init
  - fix/#2/splash

<br>

### 📋 Issue Convention

**Issue Title 규칙**

- **태그 목록**:
  - `Init`: 프로젝트 세팅
  - `Feat`: 새로운 기능 추가
  - `Fix` : 버그 수정
  - `Refactor` : 코드 리펙토링

- **형식**: [태그] 작업 요약
- **예시**:
  - [Init] 프로젝트 초기 세팅
  - [Feat] Header 컴포넌트 구현
