from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, init_db
from helpers import admin_required, faculty_required, student_required
from datetime import datetime

app = Flask(__name__)
app.secret_key = "quizmaster_secret_key_2024"
app.config["REMEMBER_COOKIE_DURATION"] = 604800  # 7 days

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


class User(UserMixin):
    def __init__(self, id, name, email, password, role, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user["id"], user["name"], user["email"], user["password"], user["role"], user["created_at"])
    return None


@app.context_processor
def inject_theme():
    theme = request.cookies.get("theme", "dark")
    return dict(current_theme=theme)


# ─── GENERAL ROUTES ─────────────────────────────────────────

@app.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif current_user.role == "faculty":
            return redirect(url_for("faculty_dashboard"))
        return redirect(url_for("student_dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")
        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("Email already registered.", "error")
            return render_template("register.html")
        conn.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                     (name, email, generate_password_hash(password), "student"))
        conn.commit()
        conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            u = User(user["id"], user["name"], user["email"], user["password"], user["role"])
            login_user(u, remember=remember)
            flash(f"Welcome back, {u.name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("home"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in ("dark", "light", "violet"):
        theme = "dark"
    response = make_response(redirect(request.referrer or url_for("home")))
    response.set_cookie("theme", theme, max_age=31536000)
    return response


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            conn = get_db()
            conn.execute("UPDATE users SET name = ? WHERE id = ?", (name, current_user.id))
            conn.commit()
            conn.close()
            flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html")


@app.route("/leaderboard")
def leaderboard():
    conn = get_db()
    results = conn.execute("""
        SELECT u.name, COUNT(qa.id) as attempts, 
               ROUND(AVG(qa.percentage), 1) as avg_score,
               MAX(qa.percentage) as best_score
        FROM quiz_attempts qa JOIN users u ON qa.user_id = u.id
        WHERE qa.completed_at IS NOT NULL
        GROUP BY qa.user_id ORDER BY avg_score DESC LIMIT 20
    """).fetchall()
    conn.close()
    return render_template("leaderboard.html", results=results)


# ─── STUDENT ROUTES ─────────────────────────────────────────

@app.route("/dashboard")
@student_required
def student_dashboard():
    conn = get_db()
    quizzes = conn.execute("""
        SELECT q.*, c.name as course_name, c.code as course_code,
               u.name as faculty_name,
               (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) as question_count
        FROM quizzes q
        JOIN courses c ON q.course_id = c.id
        JOIN users u ON q.faculty_id = u.id
        WHERE q.is_active = 1
        ORDER BY c.name, q.title
    """).fetchall()
    stats = conn.execute("""
        SELECT COUNT(*) as total, ROUND(AVG(percentage), 1) as avg_score,
               MAX(percentage) as best
        FROM quiz_attempts WHERE user_id = ? AND completed_at IS NOT NULL
    """, (current_user.id,)).fetchone()
    conn.close()
    return render_template("student/dashboard.html", quizzes=quizzes, stats=stats)


@app.route("/quiz/<int:quiz_id>")
@student_required
def take_quiz(quiz_id):
    conn = get_db()
    quiz = conn.execute("""
        SELECT q.*, c.name as course_name FROM quizzes q
        JOIN courses c ON q.course_id = c.id WHERE q.id = ? AND q.is_active = 1
    """, (quiz_id,)).fetchone()
    if not quiz:
        conn.close()
        flash("Quiz not found or not active.", "error")
        return redirect(url_for("student_dashboard"))
    questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ? ORDER BY RANDOM()", (quiz_id,)).fetchall()
    if not questions:
        conn.close()
        flash("This quiz has no questions yet.", "error")
        return redirect(url_for("student_dashboard"))
    attempt = conn.execute("INSERT INTO quiz_attempts (user_id, quiz_id, total) VALUES (?, ?, ?)",
                           (current_user.id, quiz_id, len(questions)))
    conn.commit()
    attempt_id = attempt.lastrowid
    conn.close()
    return render_template("student/quiz.html", quiz=quiz, questions=questions, attempt_id=attempt_id)


@app.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
@student_required
def submit_quiz(quiz_id):
    attempt_id = request.form.get("attempt_id", type=int)
    conn = get_db()
    questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    score = 0
    for q in questions:
        selected = request.form.get(f"q_{q['id']}", "")
        is_correct = 1 if selected == q["correct_answer"] else 0
        if is_correct:
            score += 1
        conn.execute("INSERT INTO attempt_answers (attempt_id, question_id, selected_answer, correct_answer, is_correct) VALUES (?,?,?,?,?)",
                     (attempt_id, q["id"], selected, q["correct_answer"], is_correct))
    total = len(questions)
    percentage = round((score / total) * 100, 1) if total > 0 else 0
    conn.execute("UPDATE quiz_attempts SET score=?, percentage=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                 (score, percentage, attempt_id))
    conn.commit()
    conn.close()
    flash(f"Quiz submitted! You scored {score}/{total} ({percentage}%)", "success")
    return redirect(url_for("view_result", attempt_id=attempt_id))


@app.route("/results")
@student_required
def results_history():
    conn = get_db()
    results = conn.execute("""
        SELECT qa.*, qz.title as quiz_title, c.name as course_name
        FROM quiz_attempts qa
        JOIN quizzes qz ON qa.quiz_id = qz.id
        JOIN courses c ON qz.course_id = c.id
        WHERE qa.user_id = ? AND qa.completed_at IS NOT NULL
        ORDER BY qa.completed_at DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    return render_template("student/results.html", results=results)


@app.route("/results/<int:attempt_id>")
@student_required
def view_result(attempt_id):
    conn = get_db()
    attempt = conn.execute("""
        SELECT qa.*, qz.title as quiz_title, c.name as course_name
        FROM quiz_attempts qa JOIN quizzes qz ON qa.quiz_id = qz.id
        JOIN courses c ON qz.course_id = c.id
        WHERE qa.id = ? AND qa.user_id = ?
    """, (attempt_id, current_user.id)).fetchone()
    if not attempt:
        conn.close()
        flash("Result not found.", "error")
        return redirect(url_for("results_history"))
    answers = conn.execute("""
        SELECT aa.*, q.question, q.option1, q.option2, q.option3, q.option4
        FROM attempt_answers aa JOIN questions q ON aa.question_id = q.id
        WHERE aa.attempt_id = ?
    """, (attempt_id,)).fetchall()
    conn.close()
    return render_template("student/result.html", attempt=attempt, answers=answers)


# ─── FACULTY ROUTES ──────────────────────────────────────────

@app.route("/faculty/dashboard")
@faculty_required
def faculty_dashboard():
    conn = get_db()
    courses = conn.execute("""
        SELECT c.* FROM courses c
        JOIN faculty_courses fc ON c.id = fc.course_id
        WHERE fc.faculty_id = ?
    """, (current_user.id,)).fetchall()
    quizzes = conn.execute("""
        SELECT q.*, c.name as course_name,
               (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) as question_count,
               (SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = q.id AND completed_at IS NOT NULL) as attempt_count
        FROM quizzes q JOIN courses c ON q.course_id = c.id
        WHERE q.faculty_id = ?
        ORDER BY q.created_at DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    return render_template("faculty/dashboard.html", courses=courses, quizzes=quizzes)


@app.route("/faculty/quizzes", methods=["GET", "POST"])
@faculty_required
def faculty_quizzes():
    conn = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        course_id = request.form.get("course_id", type=int)
        duration = request.form.get("duration", 300, type=int)
        if title and course_id:
            conn.execute("INSERT INTO quizzes (title, description, course_id, faculty_id, duration) VALUES (?,?,?,?,?)",
                         (title, description, course_id, current_user.id, duration))
            conn.commit()
            flash("Quiz created successfully!", "success")
        else:
            flash("Title and course are required.", "error")
        conn.close()
        return redirect(url_for("faculty_quizzes"))
    courses = conn.execute("""
        SELECT c.* FROM courses c JOIN faculty_courses fc ON c.id = fc.course_id
        WHERE fc.faculty_id = ?
    """, (current_user.id,)).fetchall()
    quizzes = conn.execute("""
        SELECT q.*, c.name as course_name,
               (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) as question_count
        FROM quizzes q JOIN courses c ON q.course_id = c.id
        WHERE q.faculty_id = ? ORDER BY q.created_at DESC
    """, (current_user.id,)).fetchall()
    conn.close()
    return render_template("faculty/quizzes.html", courses=courses, quizzes=quizzes)


@app.route("/faculty/quizzes/<int:quiz_id>/questions", methods=["GET", "POST"])
@faculty_required
def manage_questions(quiz_id):
    conn = get_db()
    quiz = conn.execute("SELECT q.*, c.name as course_name FROM quizzes q JOIN courses c ON q.course_id = c.id WHERE q.id = ? AND q.faculty_id = ?",
                        (quiz_id, current_user.id)).fetchone()
    if not quiz:
        conn.close()
        flash("Quiz not found.", "error")
        return redirect(url_for("faculty_quizzes"))
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            q = request.form.get("question", "").strip()
            o1 = request.form.get("option1", "").strip()
            o2 = request.form.get("option2", "").strip()
            o3 = request.form.get("option3", "").strip()
            o4 = request.form.get("option4", "").strip()
            ans = request.form.get("correct_answer", "").strip()
            if all([q, o1, o2, o3, o4, ans]):
                conn.execute("INSERT INTO questions (quiz_id, question, option1, option2, option3, option4, correct_answer) VALUES (?,?,?,?,?,?,?)",
                             (quiz_id, q, o1, o2, o3, o4, ans))
                conn.commit()
                flash("Question added!", "success")
            else:
                flash("All fields are required.", "error")
        elif action == "delete":
            qid = request.form.get("question_id", type=int)
            conn.execute("DELETE FROM questions WHERE id = ? AND quiz_id = ?", (qid, quiz_id))
            conn.commit()
            flash("Question deleted.", "success")
        conn.close()
        return redirect(url_for("manage_questions", quiz_id=quiz_id))
    questions = conn.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    conn.close()
    return render_template("faculty/questions.html", quiz=quiz, questions=questions)


@app.route("/faculty/quizzes/<int:quiz_id>/toggle", methods=["POST"])
@faculty_required
def toggle_quiz(quiz_id):
    conn = get_db()
    quiz = conn.execute("SELECT is_active FROM quizzes WHERE id = ? AND faculty_id = ?", (quiz_id, current_user.id)).fetchone()
    if quiz:
        new_state = 0 if quiz["is_active"] else 1
        conn.execute("UPDATE quizzes SET is_active = ? WHERE id = ?", (new_state, quiz_id))
        conn.commit()
        flash(f"Quiz {'activated' if new_state else 'deactivated'}.", "success")
    conn.close()
    return redirect(url_for("faculty_dashboard"))


@app.route("/faculty/quizzes/<int:quiz_id>/results")
@faculty_required
def faculty_quiz_results(quiz_id):
    conn = get_db()
    quiz = conn.execute("SELECT q.*, c.name as course_name FROM quizzes q JOIN courses c ON q.course_id = c.id WHERE q.id = ? AND q.faculty_id = ?",
                        (quiz_id, current_user.id)).fetchone()
    if not quiz:
        conn.close()
        flash("Quiz not found.", "error")
        return redirect(url_for("faculty_dashboard"))
    results = conn.execute("""
        SELECT qa.*, u.name as student_name, u.email as student_email
        FROM quiz_attempts qa JOIN users u ON qa.user_id = u.id
        WHERE qa.quiz_id = ? AND qa.completed_at IS NOT NULL
        ORDER BY qa.percentage DESC
    """, (quiz_id,)).fetchall()
    conn.close()
    return render_template("faculty/results.html", quiz=quiz, results=results)


# ─── ADMIN ROUTES ────────────────────────────────────────────

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db()
    stats = {
        "students": conn.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0],
        "faculty": conn.execute("SELECT COUNT(*) FROM users WHERE role='faculty'").fetchone()[0],
        "courses": conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0],
        "quizzes": conn.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0],
        "attempts": conn.execute("SELECT COUNT(*) FROM quiz_attempts WHERE completed_at IS NOT NULL").fetchone()[0],
    }
    recent = conn.execute("""
        SELECT qa.*, u.name as student_name, qz.title as quiz_title
        FROM quiz_attempts qa JOIN users u ON qa.user_id = u.id
        JOIN quizzes qz ON qa.quiz_id = qz.id
        WHERE qa.completed_at IS NOT NULL ORDER BY qa.completed_at DESC LIMIT 10
    """).fetchall()
    conn.close()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@app.route("/admin/courses", methods=["GET", "POST"])
@admin_required
def admin_courses():
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            name = request.form.get("name", "").strip()
            code = request.form.get("code", "").strip().upper()
            description = request.form.get("description", "").strip()
            if name and code:
                try:
                    conn.execute("INSERT INTO courses (name, code, description, created_by) VALUES (?,?,?,?)",
                                 (name, code, description, current_user.id))
                    conn.commit()
                    flash("Course created!", "success")
                except Exception:
                    flash("Course code already exists.", "error")
            else:
                flash("Name and code are required.", "error")
        elif action == "delete":
            cid = request.form.get("course_id", type=int)
            conn.execute("DELETE FROM courses WHERE id = ?", (cid,))
            conn.commit()
            flash("Course deleted.", "success")
        conn.close()
        return redirect(url_for("admin_courses"))
    courses = conn.execute("""
        SELECT c.*, u.name as creator_name,
               (SELECT COUNT(*) FROM quizzes WHERE course_id = c.id) as quiz_count,
               (SELECT COUNT(*) FROM faculty_courses WHERE course_id = c.id) as faculty_count
        FROM courses c LEFT JOIN users u ON c.created_by = u.id
        ORDER BY c.name
    """).fetchall()
    conn.close()
    return render_template("admin/courses.html", courses=courses)


@app.route("/admin/faculty", methods=["GET", "POST"])
@admin_required
def admin_faculty():
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            course_ids = request.form.getlist("course_ids")
            if name and email and password:
                existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                if existing:
                    flash("Email already registered.", "error")
                else:
                    cur = conn.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
                                       (name, email, generate_password_hash(password), "faculty"))
                    fid = cur.lastrowid
                    for cid in course_ids:
                        try:
                            conn.execute("INSERT INTO faculty_courses (faculty_id, course_id) VALUES (?,?)", (fid, int(cid)))
                        except Exception:
                            pass
                    conn.commit()
                    flash("Faculty registered!", "success")
            else:
                flash("Name, email and password are required.", "error")
        elif action == "delete":
            fid = request.form.get("faculty_id", type=int)
            conn.execute("DELETE FROM users WHERE id = ? AND role = 'faculty'", (fid,))
            conn.commit()
            flash("Faculty removed.", "success")
        elif action == "assign_course":
            fid = request.form.get("faculty_id", type=int)
            cid = request.form.get("course_id", type=int)
            try:
                conn.execute("INSERT INTO faculty_courses (faculty_id, course_id) VALUES (?,?)", (fid, cid))
                conn.commit()
                flash("Course assigned.", "success")
            except Exception:
                flash("Already assigned.", "error")
        conn.close()
        return redirect(url_for("admin_faculty"))
    faculty = conn.execute("""
        SELECT u.*, GROUP_CONCAT(c.name, ', ') as course_names
        FROM users u LEFT JOIN faculty_courses fc ON u.id = fc.faculty_id
        LEFT JOIN courses c ON fc.course_id = c.id
        WHERE u.role = 'faculty' GROUP BY u.id ORDER BY u.name
    """).fetchall()
    courses = conn.execute("SELECT * FROM courses ORDER BY name").fetchall()
    conn.close()
    return render_template("admin/faculty.html", faculty=faculty, courses=courses)


@app.route("/admin/students")
@admin_required
def admin_students():
    conn = get_db()
    students = conn.execute("""
        SELECT u.*, COUNT(qa.id) as quiz_count,
               ROUND(AVG(qa.percentage), 1) as avg_score
        FROM users u LEFT JOIN quiz_attempts qa ON u.id = qa.user_id AND qa.completed_at IS NOT NULL
        WHERE u.role = 'student' GROUP BY u.id ORDER BY u.name
    """).fetchall()
    conn.close()
    return render_template("admin/students.html", students=students)


@app.route("/admin/results")
@admin_required
def admin_results():
    conn = get_db()
    results = conn.execute("""
        SELECT qa.*, u.name as student_name, qz.title as quiz_title, c.name as course_name
        FROM quiz_attempts qa JOIN users u ON qa.user_id = u.id
        JOIN quizzes qz ON qa.quiz_id = qz.id JOIN courses c ON qz.course_id = c.id
        WHERE qa.completed_at IS NOT NULL ORDER BY qa.completed_at DESC
    """).fetchall()
    conn.close()
    return render_template("admin/results.html", results=results)


# ─── INIT ────────────────────────────────────────────────────

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
