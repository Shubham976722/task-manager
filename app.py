# from flask import Flask, render_template, request, redirect, session
# import mysql.connector
# import os
# import time  
# from datetime import date


# app = Flask(__name__)
# app.secret_key = os.environ.get("SECRET_KEY", "mayurbuchkul")
# app.config["SESSION_COOKIE_SECURE"] = False


# # ------- DB CONNECTION -------

# def get_db():
#     for i in range(3):  # retry 3 times
#         try:
#             conn = mysql.connector.connect(
#                 host=os.environ.get("localhost"),
#                 user=os.environ.get("root"),
#                 password=os.environ.get("Shubham@1234"),
#                 database=os.environ.get("task_manager_db"),
#                 port=int(os.environ.get("DB_PORT", 3306)),
#                 connection_timeout=10
#             )
#             return conn
#         except Exception as e:
#             print("Retry DB connection...", e)
#             time.sleep(2)
#     return None


# # ------- HOME / LOGIN PAGE -------
# @app.route("/")
# def index():
#     return render_template("login.html")


# # ------- LOGIN -------
# @app.route("/login", methods=["POST"])
# def login():
#     username = request.form["username"]
#     password = request.form["password"]
#     role = request.form["role"]

#     db = get_db()
#     if db is None:
#         return "Database connection failed"

#     cursor = db.cursor(dictionary=True) 
#     cursor.execute(
#         "SELECT * FROM users WHERE username=%s AND password=%s AND role=%s",
#         (username, password, role)
#     )
#     user = cursor.fetchone()
#     db.close()

#     if user:
#         session["user_id"] = user["id"]
#         session["username"] = user["username"]
#         session["role"] = user["role"]

#         if role == "admin":
#             return redirect("/admin")
#         else:
#             return redirect("/member")
#     else:
#         return render_template("login.html", error="Invalid credentials or wrong role selected.")


# # ------- SIGNUP -------
# @app.route("/signup", methods=["POST"])
# def signup():
#     username = request.form["username"]
#     password = request.form["password"]
#     role = request.form["role"]

#     # basic validation
#     if len(username) < 3:
#         return render_template("login.html", error="Username must be at least 3 characters.")
#     if len(password) < 4:
#         return render_template("login.html", error="Password must be at least 4 characters.")

#     db = get_db()
#     cursor = db.cursor()

#     # check if username already exists
#     cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
#     existing = cursor.fetchone()

#     if existing:
#         db.close()
#         return render_template("login.html", error="Username already taken. Try another.")

#     cursor.execute(
#         "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
#         (username, password, role)
#     )
#     db.commit()
#     db.close()

#     return render_template("login.html", signup_success=True)


# # ------- ADMIN DASHBOARD -------
# @app.route("/admin")
# def admin_dashboard():
#     if session.get("role") != "admin":
#         return redirect("/")

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     # get all members
#     cursor.execute("SELECT id, username FROM users WHERE role='member'")
#     members = cursor.fetchall()

#     # get all projects
#     cursor.execute("SELECT * FROM projects ORDER BY id DESC")
#     projects = cursor.fetchall()

#     # get all tasks with assigned member name and project name
#     cursor.execute("""
#         SELECT tasks.id, tasks.title, tasks.deadline, tasks.status,
#                users.username as assigned_to,
#                projects.name as project_name
#         FROM tasks
#         JOIN users ON tasks.assigned_to = users.id
#         JOIN projects ON tasks.project_id = projects.id
#         ORDER BY tasks.deadline ASC
#     """)
#     tasks = cursor.fetchall()
#     db.close()

#     # check which tasks are overdue
#     today = date.today()
#     for task in tasks:
#         if task["status"] == "pending" and task["deadline"] < today:
#             task["overdue"] = True
#         else:
#             task["overdue"] = False

#     return render_template("admin_dashboard.html",
#                            username=session["username"],
#                            members=members,
#                            projects=projects,
#                            tasks=tasks)


# # ------- CREATE PROJECT (admin only) -------
# @app.route("/create_project", methods=["POST"])
# def create_project():
#     if session.get("role") != "admin":
#         return redirect("/")

#     name = request.form["name"]
#     description = request.form["description"]

#     if not name:
#         return redirect("/admin")

#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute(
#         "INSERT INTO projects (name, description, created_by) VALUES (%s, %s, %s)",
#         (name, description, session["user_id"])
#     )
#     db.commit()
#     db.close()

#     return redirect("/admin")


# # ------- CREATE TASK (admin only) -------
# @app.route("/create_task", methods=["POST"])
# def create_task():
#     if session.get("role") != "admin":
#         return redirect("/")

#     title = request.form["title"]
#     member_id = request.form["member_id"]
#     deadline = request.form["deadline"]
#     project_id = request.form["project_id"]

#     if not title or not member_id or not deadline or not project_id:
#         return redirect("/admin")

#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute(
#         "INSERT INTO tasks (title, assigned_to, deadline, status, project_id) VALUES (%s, %s, %s, 'pending', %s)",
#         (title, member_id, deadline, project_id)
#     )
#     db.commit()
#     db.close()

#     return redirect("/admin")


# # ------- DELETE TASK (admin only) -------
# @app.route("/delete_task/<int:task_id>", methods=["POST"])
# def delete_task(task_id):
#     if session.get("role") != "admin":
#         return redirect("/")

#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
#     db.commit()
#     db.close()

#     return redirect("/admin")


# # ------- DELETE PROJECT (admin only) -------
# @app.route("/delete_project/<int:project_id>", methods=["POST"])
# def delete_project(project_id):
#     if session.get("role") != "admin":
#         return redirect("/")

#     db = get_db()
#     cursor = db.cursor()
#     # tasks will be deleted automatically because of ON DELETE CASCADE
#     cursor.execute("DELETE FROM projects WHERE id=%s", (project_id,))
#     db.commit()
#     db.close()

#     return redirect("/admin")


# # ------- MEMBER DASHBOARD -------
# @app.route("/member")
# def member_dashboard():
#     if session.get("role") != "member":
#         return redirect("/")

#     db = get_db()
#     cursor = db.cursor(dictionary=True)

#     # get tasks for this member, also show project name
#     cursor.execute("""
#         SELECT tasks.id, tasks.title, tasks.deadline, tasks.status,
#                projects.name as project_name
#         FROM tasks
#         JOIN projects ON tasks.project_id = projects.id
#         WHERE tasks.assigned_to=%s
#         ORDER BY tasks.deadline ASC
#     """, (session["user_id"],))
#     tasks = cursor.fetchall()
#     db.close()

#     # check which tasks are overdue
#     today = date.today()
#     for task in tasks:
#         if task["status"] == "pending" and task["deadline"] < today:
#             task["overdue"] = True
#         else:
#             task["overdue"] = False

#     return render_template("member_dashboard.html",
#                            username=session["username"],
#                            tasks=tasks)


# # ------- MARK TASK DONE (member only) -------
# @app.route("/mark_done/<int:task_id>", methods=["POST"])
# def mark_done(task_id):
#     if session.get("role") != "member":
#         return redirect("/")

#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute(
#         "UPDATE tasks SET status='done' WHERE id=%s AND assigned_to=%s",
#         (task_id, session["user_id"])
#     )
#     db.commit()
#     db.close()

#     return redirect("/member")


# # ------- LOGOUT -------
# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")


# if __name__ == "__main__":
#     app.run()   

from flask import Flask, render_template, request, redirect, session
import mysql.connector
import time
from datetime import date

app = Flask(__name__)
app.secret_key = "mayurbuchkul"


# ---------- DB CONNECTION ----------
def get_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shubham@1234",
            database="task_manager_db",
            port=3306
        )
        return conn
    except Exception as e:
        print("DB Error:", e)
        return None


# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("login.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    if db is None:
        return "Database connection failed"

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()
    db.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect("/admin")
        else:
            return redirect("/member")

    return render_template("login.html", error="Invalid username or password")


# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    role = "member"   # 🔒 FORCE MEMBER

    db = get_db()
    if db is None:
        return "Database connection failed"

    cursor = db.cursor()

    # check existing user
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        db.close()
        return render_template("login.html", error="Username already exists")

    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role)
    )

    db.commit()
    db.close()

    return render_template("login.html", signup_success=True)


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, username FROM users WHERE role='member'")
    members = cursor.fetchall()

    cursor.execute("SELECT * FROM projects ORDER BY id DESC")
    projects = cursor.fetchall()

    cursor.execute("""
        SELECT tasks.id, tasks.title, tasks.deadline, tasks.status,
               users.username as assigned_to,
               projects.name as project_name
        FROM tasks
        JOIN users ON tasks.assigned_to = users.id
        JOIN projects ON tasks.project_id = projects.id
        ORDER BY tasks.deadline ASC
    """)
    tasks = cursor.fetchall()
    db.close()

    today = date.today()
    for task in tasks:
        task["overdue"] = task["status"] == "pending" and task["deadline"] < today

    return render_template("admin_dashboard.html",
                           username=session["username"],
                           members=members,
                           projects=projects,
                           tasks=tasks)


# ---------- CREATE PROJECT ----------
@app.route("/create_project", methods=["POST"])
def create_project():
    if session.get("role") != "admin":
        return redirect("/")

    name = request.form["name"]
    description = request.form["description"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO projects (name, description, created_by) VALUES (%s, %s, %s)",
        (name, description, session["user_id"])
    )
    db.commit()
    db.close()

    return redirect("/admin")


# ---------- CREATE TASK ----------
@app.route("/create_task", methods=["POST"])
def create_task():
    if session.get("role") != "admin":
        return redirect("/")

    title = request.form["title"]
    member_id = request.form["member_id"]
    deadline = request.form["deadline"]
    project_id = request.form["project_id"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, assigned_to, deadline, status, project_id) VALUES (%s, %s, %s, 'pending', %s)",
        (title, member_id, deadline, project_id)
    )
    db.commit()
    db.close()

    return redirect("/admin")


# ---------- MEMBER DASHBOARD ----------
@app.route("/member")
def member_dashboard():
    if session.get("role") != "member":
        return redirect("/")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT tasks.id, tasks.title, tasks.deadline, tasks.status,
               projects.name as project_name
        FROM tasks
        JOIN projects ON tasks.project_id = projects.id
        WHERE tasks.assigned_to=%s
    """, (session["user_id"],))

    tasks = cursor.fetchall()
    db.close()

    today = date.today()
    for task in tasks:
        task["overdue"] = task["status"] == "pending" and task["deadline"] < today

    return render_template("member_dashboard.html",
                           username=session["username"],
                           tasks=tasks)


# ---------- MARK DONE ----------
@app.route("/mark_done/<int:task_id>", methods=["POST"])
def mark_done(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET status='done' WHERE id=%s AND assigned_to=%s",
        (task_id, session["user_id"])
    )
    db.commit()
    db.close()

    return redirect("/member")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
