# 부스 데이터 동기화 시스템 (dorders.py)

## 개요

`dorders.py`는 외부 API에서 부스 정보를 5분마다 자동으로 가져와서 Django 데이터베이스에 동기화하는 시스템입니다.

## 주요 기능

### 1. 자동 동기화 (5분 주기)
- Django 앱 시작 시 자동으로 백그라운드에서 동기화 시작 (PRODUCTION 환경에서만)
- 5분마다 API를 호출하여 최신 부스 정보를 가져옴
- 부스, 테이블, 메뉴 정보를 자동으로 업데이트

### 2. 수동 제어
- Django Management Command를 통한 동기화 제어
- REST API를 통한 동기화 제어 (관리자용)

### 3. 에러 처리 및 로깅
- 네트워크 오류, API 오류, DB 오류에 대한 종합적인 예외 처리
- 상세한 로그 기록으로 문제 추적 가능

## 설정 방법

### 1. API 설정 수정

`booth/dorders.py` 파일에서 실제 API 정보를 설정하세요:

```python
# 실제 API URL로 변경
self.api_url = api_url or "https://your-actual-api-endpoint.com/booth/all"

# 필요한 경우 Authorization 헤더 추가
self.api_headers = api_headers or {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token-here"  # 필요시 주석 해제
}
```

### 2. 로깅 설정

`project/settings.py`에 로깅 설정을 추가하세요:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'booth_sync.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'booth.dorders': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 사용 방법

### 1. Django Management Command

```bash
# 동기화 시작
python manage.py booth_sync start

# 동기화 중지
python manage.py booth_sync stop

# 한 번만 동기화 실행
python manage.py booth_sync sync

# 동기화 상태 확인
python manage.py booth_sync status
```

### 2. REST API (관리자용)

#### 동기화 시작
```http
POST /booths/sync/start/
Content-Type: application/json

Response:
{
    "statusCode": 200,
    "message": "부스 데이터 동기화가 시작되었습니다.",
    "data": {}
}
```

#### 동기화 중지
```http
POST /booths/sync/stop/
Content-Type: application/json

Response:
{
    "statusCode": 200,
    "message": "부스 데이터 동기화가 중지되었습니다.",
    "data": {}
}
```

#### 한 번 동기화
```http
POST /booths/sync/once/
Content-Type: application/json

Response:
{
    "statusCode": 200,
    "message": "부스 데이터 동기화가 완료되었습니다.",
    "data": {}
}
```

#### 동기화 상태 확인
```http
GET /booths/sync/status/

Response:
{
    "statusCode": 200,
    "message": "동기화 상태 조회 성공",
    "data": {
        "is_running": true,
        "sync_interval": 300,
        "api_url": "https://your-api-endpoint.com/booth/all",
        "thread_alive": true,
        "last_update": "2024-01-01T12:00:00Z"
    }
}
```

### 3. Python 코드에서 직접 사용

```python
from booth.dorders import (
    start_booth_sync,
    stop_booth_sync,
    sync_booth_data_once,
    get_sync_status
)

# 동기화 시작
success = start_booth_sync()

# 한 번 동기화
success = sync_booth_data_once()

# 상태 확인
status = get_sync_status()

# 동기화 중지
success = stop_booth_sync()
```

## 데이터 매핑

### API 응답 → Django 모델 매핑

| API 필드 | Django 모델 | 필드 | 설명 |
|----------|-------------|------|------|
| `boothName` | `Booth` | `name` | 부스 이름 |
| `boothAllTable` | `BoothDetail` | `all_table` | 총 테이블 수 |
| `boothUsageTable` | `BoothDetail` | `usage_table` | 사용 중인 테이블 수 |
| `menuName` | `Menu` | `name` | 메뉴 이름 |
| `menuIngredidentReminder` | `Menu` | `ingredient` | 재고량 |
| `menuSalesQuantity` | `Menu` | `sold` | 판매량 |

### 자동 생성 필드

- `Booth.category`: 자동으로 'BOOTH'로 설정
- `Booth.is_dorder`: 자동으로 `True`로 설정 (dorder 시스템 관리 표시)
- `BoothDetail.can_usage`: `usage_table < all_table`일 때 `True`
- `BoothDetail.description`: 자동 업데이트 시간 포함한 설명
- `Menu.price`: API에서 제공하지 않으므로 기본값 0

## 로그 확인

### 로그 레벨별 내용

- **INFO**: 동기화 시작/완료, API 호출 성공/실패
- **WARNING**: 데이터 없음, 이미 실행 중 등의 경고
- **ERROR**: API 오류, DB 오류, 네트워크 오류
- **DEBUG**: 개별 부스/메뉴 처리 상세 내역

### 주요 로그 메시지

```
부스 데이터 API 호출 시작
부스 데이터 API 호출 성공: 5개 부스
부스 데이터 저장 완료: 5개 부스 처리됨
부스 데이터 동기화 완료 (소요시간: 2.34초)
```

## 트러블슈팅

### 1. API 호출 실패
- API URL이 올바른지 확인
- 네트워크 연결 상태 확인
- API 서버 상태 확인
- Authorization 토큰이 필요한지 확인

### 2. 데이터 저장 실패
- 데이터베이스 연결 상태 확인
- 필수 필드가 누락되지 않았는지 확인
- Django 모델 마이그레이션 상태 확인

### 3. 동기화가 시작되지 않음
- DEBUG 모드에서는 자동 시작되지 않음 (수동으로 시작 필요)
- 이미 실행 중인 동기화가 있는지 확인
- 로그에서 오류 메시지 확인

### 4. 메모리 누수 문제
- 장시간 실행 시 메모리 사용량 모니터링
- 필요시 Django 서버 재시작

## 보안 고려사항

### 1. API 엔드포인트 관리
- 실제 운영 환경에서는 API URL을 환경 변수로 관리
- Authorization 토큰은 반드시 환경 변수 또는 비밀 관리 시스템 사용

### 2. 관리자 API 접근 제어
- 동기화 제어 API는 관리자만 접근할 수 있도록 권한 설정 추가 필요
- IP 화이트리스트 또는 추가 인증 메커니즘 고려

### 3. 로그 보안
- 로그에 민감한 정보(토큰, 비밀번호 등)가 기록되지 않도록 주의
- 로그 파일 접근 권한 적절히 설정

## 성능 최적화

### 1. 데이터베이스 최적화
- 대량 데이터 처리 시 bulk_create/bulk_update 사용 고려
- 인덱스 최적화
- 트랜잭션 범위 최소화

### 2. API 호출 최적화
- 연결 재사용을 위한 Session 객체 사용 고려
- 타임아웃 설정 적절히 조정
- 실패 시 재시도 로직 추가 고려

### 3. 동기화 주기 조정
- 시스템 부하에 따라 동기화 주기 조정
- 피크 시간대 동기화 빈도 조절