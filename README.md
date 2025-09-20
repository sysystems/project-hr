# HR 인사관리 시스템

Python 기반의 종합 인사관리 웹 애플리케이션입니다. MS365 계정 연동, 조직도 관리, 근태 관리, 급여 관리 등 기업의 모든 HR 프로세스를 통합적으로 관리할 수 있습니다.

## 주요 기능

### 👥 직원 관리
- 직원 정보 관리 (인사기록카드)
- 조직도 기반 부서 관리
- 직원 검색 및 필터링
- 인사 발령 및 이동 관리

### 📊 근태 관리
- 출퇴근 기록 (웹/모바일)
- 연차/휴가 신청 및 승인
- 근태 현황 대시보드
- 근태 통계 및 분석

### 💰 급여/보상 관리
- 급여 대장 자동 생성
- 연봉 및 상여금 관리
- 퇴직연금 관리
- 급여 명세서 발급

### 📈 평가 및 피드백
- 성과 평가 시스템
- 1 on 1 면담 기록
- 동료 피드백 관리
- 평가 결과 분석

### 📱 모바일 지원
- 반응형 웹 디자인
- 모바일 출퇴근 체크
- 연차 신청 모바일 지원
- 푸시 알림

## 기술 스택

### 백엔드
- **Python 3.9+**
- **Django 4.2+** - 웹 프레임워크
- **PostgreSQL** - 데이터베이스
- **Django REST Framework** - API 개발
- **Celery** - 비동기 작업 처리

### 프론트엔드
- **HTML5/CSS3/JavaScript**
- **Bootstrap 5** - 반응형 UI
- **Chart.js** - 데이터 시각화
- **OrgChart.js** - 조직도 구현

### 인증 및 보안
- **Microsoft 365 (Azure AD)** - SSO 인증
- **django-allauth** - 소셜 로그인
- **bcrypt** - 비밀번호 해싱
- **SSL/TLS** - 보안 통신

### 개발 도구
- **Git** - 버전 관리
- **Docker** - 컨테이너화
- **pytest** - 테스트
- **Black** - 코드 포맷팅

## 설치 및 실행

### 1. 사전 요구사항
- Python 3.9 이상
- PostgreSQL 12 이상
- Git

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd hr-management-system
```

### 3. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 환경 변수 설정
`.env` 파일 생성:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/hr_db
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
DEBUG=True
```

### 6. 데이터베이스 설정
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. 개발 서버 실행
```bash
python manage.py runserver
```

서버가 http://localhost:8000 에서 실행됩니다.

## 프로젝트 구조

```
hr-management-system/
├── core/                    # 핵심 설정 및 공통 기능
├── employees/              # 직원 관리 앱
├── organization/           # 조직도 관리 앱
├── attendance/             # 근태 관리 앱
├── payroll/                # 급여 관리 앱
├── evaluation/             # 평가 관리 앱
├── documents/              # 제증명 관리 앱
├── api/                    # REST API 앱
├── templates/              # HTML 템플릿
├── static/                 # 정적 파일 (CSS, JS, 이미지)
├── media/                  # 업로드 파일
└── requirements.txt        # 의존성 목록
```

## 주요 앱 설명

### core
- 사용자 인증 및 권한 관리
- 기본 설정 및 미들웨어
- 공통 모델 및 유틸리티

### employees
- 직원 기본 정보 관리
- 인사기록카드
- 개인정보 보호 (암호화)

### organization
- 부서 및 조직도 관리
- 상하관계 설정
- 조직개편 처리

### attendance
- 출퇴근 기록
- 연차/휴가 관리
- 근태 통계

### payroll
- 급여 계산
- 상여금 관리
- 퇴직금 계산

### evaluation
- 성과 평가
- 1 on 1 면담
- 피드백 관리

### documents
- 제증명서 자동 생성
- 문서 템플릿 관리
- PDF 출력

## API 문서

자동 생성된 API 문서는 `/api/docs/` 에서 확인할 수 있습니다.

## 보안 고려사항

- 모든 민감 정보는 데이터베이스 레벨에서 암호화
- CSRF 보호 및 XSS 방지
- SQL 인젝션 방지
- 세션 하이재킹 방지
- 정기적인 보안 업데이트

## 개발 가이드라인

### 코드 스타일
- PEP 8 준수
- Black 코드 포맷터 사용
- 의미있는 변수명 사용

### 커밋 규칙
- 기능별 브랜치 생성
- 의미있는 커밋 메시지
- Pull Request 기반 코드 리뷰

### 테스트
- pytest를 통한 단위 테스트
- 최소 80% 코드 커버리지
- CI/CD 파이프라인 연동

## 배포

### 개발 환경
```bash
python manage.py runserver
```

### 프로덕션 환경
```bash
# Nginx + Gunicorn 사용 권장
gunicorn hr_management.wsgi:application
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 지원

문의사항은 [이메일] 또는 [이슈 트래커]를 통해 연락해 주세요.

---

**개발자**: HR Management System Team
**버전**: 1.0.0
**최종 업데이트**: 2024년 12월
