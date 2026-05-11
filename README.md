# Online Quiz System

A web-based quiz application built using **Python Flask**, **SQLite**, **HTML**, **CSS**, **JavaScript**, and **Bootstrap**.

---

# Features

## User Features
- User Registration
- User Login & Logout
- Quiz Dashboard
- Attend Quiz
- Quiz Timer
- Instant Score Calculation
- Result Percentage
- Leaderboard

## Admin Features
- Add Questions
- Edit Questions
- Delete Questions
- View All Questions

## Extra Features
- Random Question Generation
- Responsive Design
- Dark Mode

---

# Technologies Used

## Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

## Backend
- Python
- Flask

## Database
- SQLite

## Tools
- VS Code
- Git
- GitHub

---

# Project Structure

```plaintext
online-quiz-system/
│
├── app.py
├── database.py
├── database.db
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── images/
│
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── quiz.html
│   ├── result.html
│   ├── leaderboard.html
│   │
│   └── admin/
│       ├── dashboard.html
│       ├── add_question.html
│       └── edit_question.html
│
└── README.md
```

---

# Requirements

Make sure the following are installed:

- Python 3.x
- pip
- VS Code (recommended)

---

# Install Python

Download Python:

https://www.python.org/downloads/

While installing:
- Enable **Add Python to PATH**

Verify installation:

```bash
python --version
```

---

# Clone Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_LINK
```

Go inside project folder:

```bash
cd online-quiz-system
```

---

# Create Virtual Environment (Recommended)

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install flask werkzeug
```

Or create a `requirements.txt` file:

```txt
flask
werkzeug
```

Install using:

```bash
pip install -r requirements.txt
```

---

# Setup Database

Run:

```bash
python database.py
```

This creates:
- `database.db`
- Required database tables

Expected output:

```plaintext
Database Created Successfully
```

---

# Run the Application

Start Flask server:

```bash
python app.py
```

Expected output:

```plaintext
Running on http://127.0.0.1:5000
```

---

# Open in Browser

Visit:

```plaintext
http://127.0.0.1:5000
```

---

# Default Application Flow

1. Register User
2. Login
3. Open Dashboard
4. Start Quiz
5. Submit Answers
6. View Result
7. View Leaderboard

---

# Admin Access

Open:

```plaintext
http://127.0.0.1:5000/admin
```

Admin can:
- Add Questions
- Edit Questions
- Delete Questions

---

# Database Tables

## users

| Column | Type |
|---|---|
| id | INTEGER |
| name | TEXT |
| email | TEXT |
| password | TEXT |

---

## questions

| Column | Type |
|---|---|
| id | INTEGER |
| question | TEXT |
| option1 | TEXT |
| option2 | TEXT |
| option3 | TEXT |
| option4 | TEXT |
| correct_answer | TEXT |

---

## results

| Column | Type |
|---|---|
| id | INTEGER |
| user_name | TEXT |
| score | INTEGER |

---

# Screenshots

Add screenshots here later.

Example:

```plaintext
screenshots/
├── home.png
├── login.png
├── dashboard.png
├── quiz.png
└── result.png
```

---

# Future Improvements

- Admin Authentication
- Email Verification
- Quiz Categories
- Certificate Generation
- Profile Management
- Timer per Question
- Analytics Dashboard
- API Integration

---

# Common Errors

## 1. sqlite3.DatabaseError: file is not a database

Solution:
- Delete `database.db`
- Run:

```bash
python database.py
```

---

## 2. 404 Not Found

Check:
- Route exists in `app.py`
- Flask server restarted
- Correct template path

---

## 3. ModuleNotFoundError: flask

Install Flask:

```bash
pip install flask
```

---

# Git Commands

Initialize Git:

```bash
git init
```

Add files:

```bash
git add .
```

Commit:

```bash
git commit -m "Initial Commit"
```

Push to GitHub:

```bash
git remote add origin YOUR_REPOSITORY_URL
git branch -M main
git push -u origin main
```

---

# Author

Your Name

---

# License

This project is for educational purposes.

