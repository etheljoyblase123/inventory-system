# Backend Team Repository

Welcome to the Backend processing module. This directory holds all server logic, API routes, and database connectivity.

## Responsibilities
- `app.py` serves HTML templates and handles forms via Flask
- Business logic (checking stock levels, calculating totals)
- Database I/O using `mysql-connector-python`

## Usage Instructions
1. Make sure the **Database Team** has run `schema.sql` in MariaDB.
2. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python app.py
   ```
4. Hand off port `5000` to the Frontend team for integration checks.

> **Note**: We serve templates from `../frontend/templates` and static assets from `../frontend/static`. Do not store frontend assets here.
