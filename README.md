# EmployeeHub – Secure Coding Review

## Project Overview

This project was completed as part of the CodeAlpha Cyber Security Internship. It focuses on identifying, analysing and remediating security vulnerabilities in a Python Flask web application.

EmployeeHub is a simulated employee management portal that provides user registration, authentication, employee search and profile management functionality.

Two versions of the application were developed to demonstrate the differences between vulnerable and secure coding practices.

## Project Objectives

- Conduct a manual security code review.
- Identify insecure coding practices and application vulnerabilities.
- Perform automated static application security testing (SAST).
- Identify vulnerable Python packages.
- Implement appropriate security controls.
- Retest the application to evaluate the effectiveness of the implemented controls.
- Document security findings, remediation measures and testing results.

## Technologies and Tools

| Technology / Tool | Purpose |
|---|---|
| Python 3.12 | Backend development |
| Flask | Web application framework |
| SQLite | Database management |
| HTML and CSS | Frontend development |
| Jinja2 | HTML templating |
| Bandit | Static security analysis |
| pip-audit | Dependency vulnerability scanning |
| Flask-WTF | CSRF protection |
| Flask-Limiter | Rate limiting |
| Werkzeug | Secure password hashing |
| cURL | HTTP request testing |
| Browser Developer Tools | Session and security inspection |
| Visual Studio Code | Development environment |

## Security Improvements

| Security Area | Implemented Control |
|---|---|
| SQL Injection | Parameterised SQL queries |
| Cross-Site Scripting (XSS) | Safe template rendering and output escaping |
| Password Storage | Salted scrypt password hashing |
| Hardcoded Secrets | Environment-based secret key management |
| Insecure Configuration | Disabled Flask debug mode |
| Input Validation | Server-side validation and input length restrictions |
| Cross-Site Request Forgery (CSRF) | Global CSRF protection and form tokens |
| Session Management | Session clearing, cookie protection and 15-minute session lifetime |
| Insecure Logout | POST-only logout with CSRF protection |
| Brute-Force Attempts | Login rate limiting of five POST requests per minute |
| Dependency Security | Vulnerability auditing and package updates |

## Security Testing Results

The application was evaluated through manual code inspection, automated security scanning and controlled functional security testing.

### Static Security Analysis

The final Bandit scan of the secure application produced the following results:

- Lines of code scanned: 214
- Low-severity findings: 0
- Medium-severity findings: 0
- High-severity findings: 0
- Lines excluded using nosec: 0
- Files skipped: 0

### Dependency Vulnerability Analysis

The dependency audit initially reported 14 vulnerability entries associated with pip version 23.2.1, including repeated advisory identifiers.

After upgrading pip to version 26.3, the subsequent audit reported no known vulnerabilities.

### Functional Security Testing

The following security controls were evaluated:

- Authentication and password verification
- Secure password storage
- Server-side input validation
- CSRF token enforcement
- Session expiration
- Logout request restrictions
- Login rate limiting
- Legitimate application functionality following remediation

These results demonstrate the effectiveness of the tested controls within the local testing environment. They do not guarantee that the application is free from all vulnerabilities.

## Project Structure

    CodeAlpha_SecureCodingReview/
    ├── vulnerable_app/
    │   ├── static/
    │   ├── templates/
    │   └── app.py
    ├── secure_app/
    │   ├── static/
    │   ├── templates/
    │   └── app.py
    ├── reports/
    │   ├── Security review report
    │   ├── Screenshot evidence
    │   ├── Bandit scan reports
    │   └── Dependency audit reports
    ├── .gitignore
    ├── requirements.txt
    └── README.md

## Installation and Setup

### 1. Create a virtual environment

    python -m venv venv

### 2. Activate the virtual environment (Windows PowerShell)

    .\venv\Scripts\Activate.ps1

### 3. Upgrade pip

    python -m pip install --upgrade pip

### 4. Install dependencies

    python -m pip install -r requirements.txt

## Running the Secure Application

Generate a secret key and store it in an environment variable:

    $env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")

Start the application:

    python secure_app/app.py

Open the following address in your browser:

    http://127.0.0.1:5000

Register a new account to access the employee portal.

## Running the Vulnerable Application

The vulnerable application is intentionally insecure and must only be executed in an isolated local testing environment.

Do not expose it to public networks or deploy it to a production server.

    python vulnerable_app/app.py

## Reproducing Security Scans

Scan the vulnerable application:

    bandit -r vulnerable_app

Scan the secure application:

    bandit -r secure_app

Perform a dependency vulnerability audit:

    pip-audit

## Documentation

The reports directory contains the final security review report, supporting screenshot evidence and automated security scan results.

## Limitations

This project was conducted in a controlled local environment. The implemented application is an educational prototype rather than a production-ready employee management system.

Additional production security requirements include HTTPS, secure cookie transmission, persistent rate-limiting storage and further security testing.

Automated security tools have limitations, and a clean scan does not establish the absence of all security vulnerabilities.

## Skills Demonstrated

- Secure software development
- Manual code review
- Static application security testing (SAST)
- Vulnerability assessment
- Vulnerability remediation
- Dependency security analysis
- Authentication and session security
- Security control validation
- Technical security documentation

## Disclaimer

This project was developed exclusively for educational purposes as part of the CodeAlpha Cyber Security Internship.

The vulnerable application is intentionally insecure. All testing was performed in a controlled local environment for authorised security learning and research purposes.
