# HR Management Project

## Overview

This project is a Django-based HR Management system designed to streamline HR processes, including employee management, organization charting, attendance tracking, payroll, performance evaluation, and recruitment. The goal is to create a comprehensive, user-friendly, and data-driven HR platform, inspired by industry leaders like Workday, SAP SuccessFactors, and Oracle HCM.

## Features

### Core Features:

*   **Employee Self-Service Portal:**
    *   MS365 계정 연동 로그인.
    *   개인 정보 (프로필 사진, 학력, 경력) 조회 및 수정 요청 기능.
*   **Attendance Management:**
    *   출근/퇴근 기록 및 조회.
    *   휴가 신청 및 승인 프로세스.
    *   잔여 연차 계산.
*   **Payroll Management:**
    *   월별 급여 명세서 생성 및 관리.
    *   급여 항목 (기본급, 수당, 공제 등) 관리.
    *   전월 급여 데이터 복사 기능.
*   **Recruitment Management:**
    *   PDF 이력서 자동 파싱.
    *   채용 단계별 관리 (서류 전형, 면접, 합격/불합격).
    *   MS Outlook 일정 연동 면접 제안 자동 발송.
*   **Meeting Room Booking System:**
    *   회의 일정 생성 및 관리.
    *   참석자 일정 확인 및 초대.
*   **Organization Chart:**
    *   Dynamic, interactive organization chart with D3.js or GoJS.
    *   Display employee information (photo, name, title, etc.).
    *   Employee profile details on click (side panel).
    *   Drag-and-drop functionality for basic organization changes.
*   **Performance Management (Basic):**
    *   1:1 미팅 기록.
    *   개인 목표 설정 (OKR).
    *   동료 피드백.

### Planned Features (Future Development):

*   **AI-Powered Talent Management:**
    *   AI 기반 인재 추천 및 이탈 예측.
    *   자동화된 HR 프로세스 (채용, 온보딩, 급여 정산).
    *   개인화된 경력 개발 제안.
*   **Data Analytics and Reporting:**
    *   HR 지표 시각화 대시보드 (인력 현황, 퇴사율, 성과 등).
    *   성과 및 보상 연동.
    *   조직 개편 시뮬레이션.

## Technologies Used

*   **Backend:** Python, Django, Django REST Framework
*   **Frontend:** HTML, CSS, JavaScript (D3.js or GoJS for organization chart)
*   **Database:** SQLite (default)
*   **Authentication:** Django Allauth (MS365 integration)
*   **Other Libraries:** django-filters, django-extensions, auditlog, encrypted-model-fields, mptt, celery, redis, django-celery-beat, Pillow, pandas, numpy, matplotlib, openpyxl, python-dateutil, requests, bcrypt, cryptography, django-encrypted-model-fields, django-auditlog, gunicorn, whitenoise, sentry-sdk, black, flake8, pytest, pytest-django, factory-boy, coverage, pre-commit

## Project Structure

The project follows a standard Django project structure with multiple apps for different functionalities:

*   `core`: Core functionalities, including the organization chart view and home page.
*   `employees`: Manages employee data.
*   `organization`: Manages organizational structure (departments).
*   `attendance`: Tracks employee attendance.
*   `payroll`: Handles payroll processing.
*   `evaluation`: Manages performance evaluations.
*   `documents`: For document management.
*   `api`: For API-related functionalities.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sysystems/project-hr.git
    cd project-hr
    ```
2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure environment variables:**
    Create a `.env` file in the project root and add your environment-specific settings, such as:
    ```
    SECRET_KEY='your-secret-key'
    FIELD_ENCRYPTION_KEY='your-encryption-key'
    DATABASE_URL='sqlite:///db.sqlite3'
    ALLOWED_HOSTS='localhost,127.0.0.1'
    AZURE_CLIENT_ID='your-azure-client-id'
    AZURE_CLIENT_SECRET='your-azure-client-secret'
    AZURE_TENANT_ID='your-azure-tenant-id'
    ```
5.  **Apply database migrations:**
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```
6.  **Create a superuser:**
    ```bash
    python3 manage.py createsuperuser
    ```

## Usage

1.  **Run the development server:**
    ```bash
    python3 manage.py runserver 8001
    ```
2.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8001/`.
    *   **Home Page:** `http://127.0.0.1:8001/`
    *   **Organization Chart:** `http://127.0.0.1:8001/org_chart/`

## Current Issues

*   The drag-and-drop functionality for employees is not working correctly.
*   Static files (CSS, JavaScript) are not being served correctly, resulting in 404 errors.
*   The project is in the early stages of development, and many features are yet to be implemented.

## Contributing

(Optional: Add contribution guidelines here if applicable)

## License

(Optional: Add license information here if applicable)
