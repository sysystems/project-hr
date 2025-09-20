# HR Management Project - Development Log

## Overview

This document summarizes the steps taken to set up and develop the HR Management project.

## Steps Completed

1.  **Initial Setup:**
    *   Created a Django project named `hr_management`.
    *   Created several apps: `core`, `employees`, `organization`, `attendance`, `payroll`, `evaluation`, `documents`, and `api`.
2.  **VSCode Configuration:**
    *   Resolved an error related to environment variables in VSCode by enabling the `python.terminal.useEnvFile` setting.
3.  **Database Migrations:**
    *   Modified the `core/models.py` file to resolve reverse accessor clashes between `auth.User` and `core.User` models by adding `related_name` and `related_query_name` arguments to the `groups` and `user_permissions` fields.
    *   Created and applied migrations to update the database schema.
4.  **Static Files Configuration:**
    *   Created `static` and `core/static` directories to store static files.
    *   Created `core/static/core/css/org_chart.css` for styling the organization chart.
    *   Created `core/static/core/js/org_chart.js` for drag-and-drop functionality.
    *   Updated `hr_management/settings.py` to configure static files settings, including `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, and `STATICFILES_FINDERS`.
    *   Collected static files using `python3 manage.py collectstatic --noinput`.
5.  **URL Configuration:**
    *   Created `core/urls.py` to define URL patterns for the `core` app.
    *   Updated `hr_management/urls.py` to include the `core` app's URL patterns.
6.  **Views and Templates:**
    *   Created a `home` view in `core/views.py` and a corresponding template `core/templates/core/home.html`.
    *   Created an `org_chart` view in `core/views.py` and a corresponding template `core/templates/core/org_chart.html` with a basic split layout.
7.  **Superuser Creation:**
    *   Created a superuser account using `python3 manage.py createsuperuser`.
8.  **Organization Chart Interface:**
    *   Implemented a basic split layout in `core/templates/core/org_chart.html` with a menu on the left and a display area on the right.
    *   Added sample departments and employees to `core/templates/core/org_chart.html`.
    *   Implemented basic drag-and-drop functionality using JavaScript in `core/static/core/js/org_chart.js`.

## Current Issues

*   The drag-and-drop functionality is not working correctly.
*   There are still 404 errors for static files, indicating that the static files are not being served correctly.

## Next Steps

1.  Debug the drag-and-drop functionality in `core/static/core/js/org_chart.js` and `core/templates/core/org_chart.html`.
2.  Troubleshoot the static files configuration in `hr_management/settings.py` and ensure that static files are being served correctly.
3.  Implement the organization management menu functionality (create, move, delete departments).
4.  Implement the personnel management section (hire, assign, move, terminate employees).
5.  Implement the drag-and-drop interface for moving employees between departments.
6.  Improve the styling and design of the organization chart interface.
