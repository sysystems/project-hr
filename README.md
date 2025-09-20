# HR Management Project

## Overview

This project is a Django-based HR Management system designed to streamline HR processes, including employee management, organization charting, attendance tracking, payroll, and performance evaluation.

## Features

### Implemented Features:
*   **Project Setup:** Django project and app structure initialized.
*   **Database Migrations:** Initial migrations applied, including resolving model clashes.
*   **Static Files Configuration:** Basic configuration for serving static files.
*   **URL Configuration:** Basic URL routing for core app features.
*   **Organization Chart Interface:**
    *   Basic split layout for organization chart view.
    *   Sample departments and employees displayed.
    *   Basic drag-and-drop functionality for employees (currently not working correctly).
*   **Superuser Account:** Created for admin access.

### Planned Features:
*   **Static File Serving:** Resolve 404 errors for CSS and JavaScript files.
*   **Drag-and-Drop Functionality:** Debug and fix the drag-and-drop feature for employees.
*   **Organization Management:** Implement functionality for creating, moving, and deleting departments.
*   **Personnel Management:** Implement features for hiring, assigning, moving, and terminating employees.
*   **Data Model Integration:** Integrate with Django models to manage real-time data for the organization chart and other features.
*   **Styling and UI/UX Improvements:** Enhance the overall look and feel of the organization chart and other interfaces.

## Technologies Used

*   **Backend:** Python, Django
*   **Frontend:** HTML, CSS, JavaScript
*   **Database:** SQLite (default)
*   **Other Libraries:** Django REST framework, django-filters, django-extensions, auditlog, encrypted-model-fields, mptt, allauth, allauth.socialaccount.providers.microsoft

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
    python3 manage.py runserver
    ```
2.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8000/`.
    *   **Home Page:** `http://127.0.0.1:8000/`
    *   **Organization Chart:** `http://127.0.0.1:8000/org_chart/`

## Current Issues

*   The drag-and-drop functionality for employees is not working correctly.
*   Static files (CSS, JavaScript) are not being served correctly, resulting in 404 errors.

## Contributing

(Optional: Add contribution guidelines here if applicable)

## License

(Optional: Add license information here if applicable)
