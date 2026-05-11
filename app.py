from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "quizproject"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")

        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password),
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")

        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=?", (email,))

        user = cur.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect("/dashboard")

        else:
            return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", name=session["user_name"])


@app.route("/add-question", methods=["GET", "POST"])
def add_question():

    if request.method == "POST":

        question = request.form["question"]
        option1 = request.form["option1"]
        option2 = request.form["option2"]
        option3 = request.form["option3"]
        option4 = request.form["option4"]
        answer = request.form["answer"]

        conn = sqlite3.connect("database.db")

        cur = conn.cursor()

        cur.execute(
            """
        INSERT INTO questions
        (question, option1, option2, option3, option4, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (question, option1, option2, option3, option4, answer),
        )

        conn.commit()
        conn.close()

        return "Question Added Successfully"

    return render_template("admin/add_question.html")


@app.route("/quiz")
def quiz():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 5")

    questions = cur.fetchall()

    conn.close()

    return render_template("quiz.html", questions=questions)


@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():

    score = 0

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM questions")

    questions = cur.fetchall()

    for q in questions:

        selected_answer = request.form.get(str(q[0]))

        correct_answer = q[6]

        if selected_answer == correct_answer:
            score += 1

    cur.execute(
        "INSERT INTO results(user_name, score) VALUES(?, ?)",
        (session["user_name"], score),
    )

    conn.commit()
    conn.close()

    percentage = (score / len(questions)) * 100

    return render_template(
        "result.html", score=score, total=len(questions), percentage=percentage
    )


@app.route("/admin")
def admin():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("SELECT * FROM questions")

    questions = cur.fetchall()

    conn.close()

    return render_template("admin/dashboard.html", questions=questions)


@app.route("/delete-question/<int:id>")
def delete_question(id):

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("DELETE FROM questions WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/edit-question/<int:id>", methods=["GET", "POST"])
def edit_question(id):

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    if request.method == "POST":

        question = request.form["question"]

        cur.execute("UPDATE questions SET question=? WHERE id=?", (question, id))

        conn.commit()

        return redirect("/admin")

    cur.execute("SELECT * FROM questions WHERE id=?", (id,))

    question = cur.fetchone()

    conn.close()

    return render_template("admin/edit_question.html", question=question)


@app.route("/leaderboard")
def leaderboard():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM results
    ORDER BY score DESC
    LIMIT 10
    """)

    results = cur.fetchall()

    conn.close()

    return render_template("leaderboard.html", results=results)


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
