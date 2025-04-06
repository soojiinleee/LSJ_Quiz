# 퀴즈 서비스

## 1. 구현 기능
### 관리자
- [x] 퀴즈 생성 / 수정 / 삭제 (soft delete)
- [x] 퀴즈 목록 및 상세 조회 

### 일반 사용자
- [x] 퀴즈 목록 / 상세 조회 (응시 여부 포함)
- [x] 퀴즈 응시 (문제 및 선택지 순서 저장 / 조회)
- [x] 퀴즈 제출 (정답 자동 채점 및 결과 저장)

### 추가 구현 기능
- [x] 문제 및 선택지 생성 (관리자 전용)
- [X] 퀴즈 - 문제 연결 (관리자 전용)

## 2. 주요 폴더 구조
```text
  .
  ├── config
  ├── core
  ├── question
  ├── quiz
  ├── quiz_attempt
  └── tests
```
### 앱 별 역할 및 책임
| 앱 이름 | 역할 및 책임                          |
|--------|----------------------------------|
| config | Django 설정과 라우팅, 환경 구성 파일 관리      |
| core | 공통 유틸, 믹스인, 상수 등 재사용 가능한 로직 제공   |
| question | 문제 및 선택지 관련 모델과 로직 관리            |
| quiz | 퀴즈 자체의 생성, 수정, 삭제, 목록/상세 조회 기능, 관리자와 일반 사용자 접근 권한을 분리 |
| quiz_attempt | 퀴즈 응시, 선택지 저장, 채점 및 결과 기록        |
| tests | 기능 검증을 위한 테스트 코드 모음              |

## 3. 환경 설정
- poetry를 이용해서 의존성 파일 설치
  ```shell
    poetry instal
  ```
- 프로젝트 루트 디렉토리에 `.env`생성
- 아래 항목 설정에 맞게 변경
  ```text
    SECRET_KEY='example'
    POSTGRES_DB='example'
    POSTGRES_USER='example'
    POSTGRES_PASSWORD='example'
  ```

## 4. 실행 방법
### Docker 컨테이너 실행
- `docker compose`를 통해 `Django` 와 `PostgreSQL` 컨테이너로 실행
  ```shell
    docker compose up --build -d
  ```

## 5. 테스트 코드 실행
- 테스트 결과 확인
  ```shell
  docker compose -f docker-compose.test.yml up --build
  ```

## 6. 구현 의도 및 설계 포인트
- 퀴즈의 출제 문제는 퀴즈와 문제는 n : m 관계 전제 하에 랜덤으로 추출
- 퀴즈 삭제는 soft delete 적용 (`is_deleted`, `deleted_at`)
- 퀴즈 제출은 개별 문제 풀고 제출이 아닌, 제출 버튼 클릭 시점으로 간주


