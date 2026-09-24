from flask import Flask, request, redirect, url_for, session, render_template_string, flash, jsonify
import sqlite3
import hashlib
from functools import wraps
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "campusconnect_secret_key_2026"
DATABASE = "campusconnect.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        roll_no TEXT DEFAULT '', branch TEXT DEFAULT '', year TEXT DEFAULT '', phone TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, code TEXT, teacher TEXT,
        attendance INTEGER DEFAULT 0, total_classes INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, subject TEXT, due_date TEXT, description TEXT,
        status TEXT DEFAULT 'Pending'
    );
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, message TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, event_date TEXT, location TEXT, description TEXT
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending', created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT, time TEXT, subject TEXT, room TEXT
    );
    """)

    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cur.execute("""INSERT INTO users(name,email,password,roll_no,branch,year,phone)
        VALUES(?,?,?,?,?,?,?)""", ("Demo Student", "student@campus.com", hash_password("123456"),
        "23A81A0501", "CSE - AIML", "B.Tech 3rd Year", "9876543210"))

    if cur.execute("SELECT COUNT(*) FROM subjects").fetchone()[0] == 0:
        cur.executemany("INSERT INTO subjects(name,code,teacher,attendance,total_classes) VALUES(?,?,?,?,?)", [
            ("Data Structures","CS301","Dr. Ravi",42,50),
            ("Java Programming","CS302","Mrs. Anitha",38,45),
            ("Python Programming","CS303","Mr. Kumar",44,48),
            ("Database Management","CS304","Dr. Suresh",35,42),
            ("Operating Systems","CS305","Mrs. Priya",39,46)])

    if cur.execute("SELECT COUNT(*) FROM assignments").fetchone()[0] == 0:
        cur.executemany("INSERT INTO assignments(title,subject,due_date,description,status) VALUES(?,?,?,?,?)", [
            ("Binary Search Implementation","Data Structures","2026-09-28","Implement binary search using Python.","Pending"),
            ("Java Inheritance Program","Java Programming","2026-09-30","Create a Java program demonstrating inheritance.","Pending"),
            ("SQL Queries","Database Management","2026-10-02","Write SQL queries for student database.","Completed")])

    if cur.execute("SELECT COUNT(*) FROM notices").fetchone()[0] == 0:
        cur.executemany("INSERT INTO notices(title,message,created_at) VALUES(?,?,?)", [
            ("Internal Exams","Internal examinations will begin next month.","2026-09-20"),
            ("Project Submission","Submit your mini project before the deadline.","2026-09-22"),
            ("College Fest","Registrations are open for the annual college fest.","2026-09-23")])

    if cur.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0:
        cur.executemany("INSERT INTO events(title,event_date,location,description) VALUES(?,?,?,?)", [
            ("Technical Fest","2026-10-05","College Auditorium","Technical competitions and project exhibition."),
            ("Hackathon 2026","2026-10-10","Innovation Lab","24-hour coding and innovation challenge."),
            ("Cultural Fest","2026-10-20","College Ground","Music, dance and cultural activities.")])

    if cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.executemany("INSERT INTO tasks(title,priority,status,created_at) VALUES(?,?,?,?)", [
            ("Complete DS Assignment","High","Pending",now),
            ("Practice Java Programs","Medium","Pending",now),
            ("Prepare Project PPT","Low","Completed",now)])

    if cur.execute("SELECT COUNT(*) FROM timetable").fetchone()[0] == 0:
        cur.executemany("INSERT INTO timetable(day,time,subject,room) VALUES(?,?,?,?)", [
            ("Monday","09:00 - 10:00","Data Structures","Room 101"),
            ("Monday","10:00 - 11:00","Java Programming","Room 102"),
            ("Tuesday","09:00 - 10:00","Python Programming","Lab 1"),
            ("Tuesday","11:00 - 12:00","Database Management","Room 203"),
            ("Wednesday","10:00 - 11:00","Operating Systems","Room 105"),
            ("Thursday","09:00 - 10:00","Python Programming","Lab 2"),
            ("Friday","11:00 - 12:00","Data Structures","Room 101")])
    conn.commit(); conn.close()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


BASE = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{{title}} | CampusConnect</title><style>
*{box-sizing:border-box;font-family:Arial,sans-serif}body{margin:0;background:#f4f7fb;color:#1e293b}.nav{height:64px;background:linear-gradient(135deg,#4f46e5,#9333ea,#ec4899);color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 24px}.logo{font-size:22px;font-weight:700}.nav a{color:#fff;text-decoration:none;margin-left:15px}.layout{display:flex;min-height:calc(100vh - 64px)}.side{width:235px;background:#fff;padding:18px 12px;box-shadow:2px 0 12px #00000010}.side a{display:block;color:#475569;text-decoration:none;padding:12px;border-radius:10px;margin:4px 0}.side a:hover{background:#eef2ff;color:#4f46e5}.main{flex:1;padding:28px;max-width:1450px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.card,.box{background:#fff;border-radius:16px;padding:20px;box-shadow:0 5px 20px #0000000d;margin-bottom:20px}.num{font-size:30px;font-weight:700;margin-top:8px}.muted{color:#64748b}.grid{display:grid;grid-template-columns:2fr 1fr;gap:18px}table{width:100%;border-collapse:collapse}th,td{padding:11px;border-bottom:1px solid #e2e8f0;text-align:left}.badge{padding:5px 9px;border-radius:20px;font-size:12px;display:inline-block}.pending{background:#fef3c7;color:#92400e}.completed{background:#dcfce7;color:#166534}.high{background:#fee2e2;color:#991b1b}.medium{background:#fef3c7;color:#92400e}.low{background:#dcfce7;color:#166534}.btn{display:inline-block;border:0;background:#4f46e5;color:#fff;padding:9px 14px;border-radius:9px;text-decoration:none;cursor:pointer}.danger{background:#dc2626}.success{background:#16a34a}input,select,textarea{width:100%;padding:11px;border:1px solid #cbd5e1;border-radius:9px;margin:7px 0 14px}textarea{min-height:90px}.notice{padding:13px;background:#eef2ff;border-left:4px solid #4f46e5;border-radius:8px;margin:10px 0}.progress{height:10px;background:#e2e8f0;border-radius:10px}.bar{height:100%;background:linear-gradient(90deg,#4f46e5,#9333ea);border-radius:10px}.login{min-height:100vh;display:grid;place-items:center;background:linear-gradient(135deg,#4f46e5,#9333ea,#ec4899);padding:20px}.loginbox{width:390px;max-width:100%;background:white;border-radius:22px;padding:32px}.center{text-align:center}.flash{padding:12px;background:#dcfce7;color:#166534;border-radius:9px;margin-bottom:15px}.search{display:flex;gap:8px}.search input{margin:0}.stat{font-size:14px;color:#64748b}@media(max-width:900px){.cards{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}@media(max-width:650px){.side{display:none}.main{padding:15px}.cards{grid-template-columns:1fr}.nav{padding:0 12px}.nav span{display:none}}
</style></head><body>
{% if logged_in %}<div class='nav'><div class='logo'>🎓 CampusConnect</div><div><span>Hi, {{user['name']}}</span> <a href='/logout'>Logout</a></div></div><div class='layout'><aside class='side'>
<a href='/'>🏠 Dashboard</a><a href='/profile'>👤 Profile</a><a href='/attendance'>📊 Attendance</a><a href='/assignments'>📝 Assignments</a><a href='/timetable'>📅 Timetable</a><a href='/notices'>📢 Notices</a><a href='/events'>🎉 Events</a><a href='/tasks'>✅ My Tasks</a><a href='/search'>🔎 Search</a></aside><main class='main'>
{% for m in get_flashed_messages() %}<div class='flash'>{{m}}</div>{% endfor %}{{body|safe}}</main></div>{% else %}{{body|safe}}{% endif %}</body></html>
"""


def page(body, title="CampusConnect", **ctx):
    user = None
    if session.get("user_id"):
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone(); conn.close()
    rendered = render_template_string(body, **ctx)
    return render_template_string(BASE, body=rendered, title=title, logged_in=bool(user), user=user)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email','').strip(); password=hash_password(request.form.get('password',''))
        conn=get_db(); user=conn.execute('SELECT * FROM users WHERE email=? AND password=?',(email,password)).fetchone(); conn.close()
        if user:
            session['user_id']=user['id']; return redirect(url_for('dashboard'))
        flash('Invalid email or password.')
    body="""<div class='login'><div class='loginbox'><div class='center'><h1>🎓 CampusConnect</h1><p class='muted'>Smart College Student Portal</p></div><form method='post'><label>Email</label><input name='email' type='email' required><label>Password</label><input name='password' type='password' required><button class='btn' style='width:100%'>Login</button></form><p class='center muted'>Demo: student@campus.com / 123456</p><p class='center'><a href='/register'>Create account</a></p></div></div>"""
    return page(body,'Login')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip(); password=request.form.get('password','')
        if not name or not email or not password: flash('All fields are required.'); return redirect(url_for('register'))
        try:
            conn=get_db(); conn.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email,hash_password(password))); conn.commit(); conn.close(); flash('Registration successful. Please login.'); return redirect(url_for('login'))
        except sqlite3.IntegrityError: flash('Email already registered.')
    body="""<div class='login'><div class='loginbox'><h1>📝 Create Account</h1><form method='post'><label>Name</label><input name='name' required><label>Email</label><input name='email' type='email' required><label>Password</label><input name='password' type='password' required><button class='btn' style='width:100%'>Register</button></form><p class='center'><a href='/login'>Back to Login</a></p></div></div>"""
    return page(body,'Register')


@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    conn=get_db(); subjects=conn.execute('SELECT * FROM subjects').fetchall(); assignments=conn.execute('SELECT * FROM assignments ORDER BY due_date').fetchall(); notices=conn.execute('SELECT * FROM notices ORDER BY created_at DESC LIMIT 3').fetchall(); events=conn.execute('SELECT * FROM events ORDER BY event_date LIMIT 3').fetchall(); tasks=conn.execute("SELECT * FROM tasks WHERE status='Pending' ORDER BY id DESC LIMIT 5").fetchall(); conn.close()
    total=sum(s['total_classes'] for s in subjects); attended=sum(s['attendance'] for s in subjects); avg=round(attended/total*100,1) if total else 0
    pending=sum(a['status']!='Completed' for a in assignments); completed=len(assignments)-pending
    body="""<h1>Dashboard</h1><p class='muted'>Your academic activity at a glance.</p><div class='cards'>
    <div class='card'><div class='stat'>Attendance</div><div class='num'>{{avg}}%</div></div><div class='card'><div class='stat'>Assignments Pending</div><div class='num'>{{pending}}</div></div><div class='card'><div class='stat'>Completed</div><div class='num'>{{completed}}</div></div><div class='card'><div class='stat'>Tasks Pending</div><div class='num'>{{tasks|length}}</div></div></div>
    <div class='grid'><div><div class='box'><h2>📚 Subjects</h2><table><tr><th>Subject</th><th>Attendance</th></tr>{% for s in subjects %}<tr><td>{{s['name']}}</td><td>{{s['attendance']}} / {{s['total_classes']}}<div class='progress'><div class='bar' style='width:{{(s['attendance']/s['total_classes']*100) if s['total_classes'] else 0}}%'></div></div></td></tr>{% endfor %}</table></div><div class='box'><h2>📝 Upcoming Assignments</h2>{% for a in assignments[:4] %}<p><b>{{a['title']}}</b> — {{a['due_date']}} <span class='badge {{a['status']|lower}}'>{{a['status']}}</span></p>{% endfor %}</div></div><div><div class='box'><h2>📢 Notices</h2>{% for n in notices %}<div class='notice'><b>{{n['title']}}</b><br>{{n['message']}}</div>{% endfor %}</div><div class='box'><h2>🎉 Events</h2>{% for e in events %}<p><b>{{e['title']}}</b><br>{{e['event_date']}} · {{e['location']}}</p>{% endfor %}</div></div></div>"""
    return page(body,'Dashboard',subjects=subjects,assignments=assignments,notices=notices,events=events,tasks=tasks,avg=avg,pending=pending,completed=completed)


@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    conn=get_db(); user=conn.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()
    if request.method=='POST':
        data=(request.form.get('name','').strip(),request.form.get('roll_no','').strip(),request.form.get('branch','').strip(),request.form.get('year','').strip(),request.form.get('phone','').strip(),session['user_id'])
        conn.execute('UPDATE users SET name=?,roll_no=?,branch=?,year=?,phone=? WHERE id=?',data); conn.commit(); user=conn.execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone(); flash('Profile updated successfully.')
    conn.close()
    body="""<h1>👤 Profile</h1><div class='box'><form method='post'><label>Name</label><input name='name' value='{{user["name"]}}' required><label>Email</label><input value='{{user["email"]}}' disabled><label>Roll Number</label><input name='roll_no' value='{{user["roll_no"]}}'><label>Branch</label><input name='branch' value='{{user["branch"]}}'><label>Year</label><input name='year' value='{{user["year"]}}'><label>Phone</label><input name='phone' value='{{user["phone"]}}'><button class='btn'>Save Changes</button></form></div>"""
    return page(body,'Profile',user=user)


@app.route('/attendance')
@login_required
def attendance():
    conn=get_db(); rows=conn.execute('SELECT * FROM subjects').fetchall(); conn.close();
    body="""<h1>📊 Attendance</h1><div class='box'><table><tr><th>Subject</th><th>Code</th><th>Teacher</th><th>Present</th><th>Percentage</th></tr>{% for s in rows %}<tr><td>{{s['name']}}</td><td>{{s['code']}}</td><td>{{s['teacher']}}</td><td>{{s['attendance']}}/{{s['total_classes']}}</td><td>{{((s['attendance']/s['total_classes']*100) if s['total_classes'] else 0)|round(1)}}%</td></tr>{% endfor %}</table></div>"""
    return page(body,'Attendance',rows=rows)


@app.route('/assignments')
@login_required
def assignments():
    q=request.args.get('q','').strip(); conn=get_db()
    if q: rows=conn.execute("SELECT * FROM assignments WHERE title LIKE ? OR subject LIKE ? ORDER BY due_date",(f'%{q}%',f'%{q}%')).fetchall()
    else: rows=conn.execute('SELECT * FROM assignments ORDER BY due_date').fetchall()
    conn.close()
    body="""<h1>📝 Assignments</h1><div class='box'><form class='search'><input name='q' value='{{q}}' placeholder='Search assignments...'><button class='btn'>Search</button></form><table><tr><th>Title</th><th>Subject</th><th>Due</th><th>Status</th><th>Action</th></tr>{% for a in rows %}<tr><td><b>{{a['title']}}</b><br><span class='muted'>{{a['description']}}</span></td><td>{{a['subject']}}</td><td>{{a['due_date']}}</td><td><span class='badge {{a['status']|lower}}'>{{a['status']}}</span></td><td>{% if a['status']!='Completed' %}<a class='btn success' href='/assignments/{{a["id"]}}/complete'>Complete</a>{% else %}✓{% endif %}</td></tr>{% endfor %}</table></div>"""
    return page(body,'Assignments',rows=rows,q=q)


@app.route('/assignments/<int:aid>/complete')
@login_required
def complete_assignment(aid):
    conn=get_db(); conn.execute("UPDATE assignments SET status='Completed' WHERE id=?",(aid,)); conn.commit(); conn.close(); flash('Assignment marked completed.'); return redirect(url_for('assignments'))


@app.route('/timetable')
@login_required
def timetable():
    conn=get_db(); rows=conn.execute("SELECT * FROM timetable ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 ELSE 6 END,time").fetchall(); conn.close()
    body="""<h1>📅 Timetable</h1><div class='box'><table><tr><th>Day</th><th>Time</th><th>Subject</th><th>Room</th></tr>{% for r in rows %}<tr><td>{{r['day']}}</td><td>{{r['time']}}</td><td>{{r['subject']}}</td><td>{{r['room']}}</td></tr>{% endfor %}</table></div>"""
    return page(body,'Timetable',rows=rows)


@app.route('/notices')
@login_required
def notices():
    conn=get_db(); rows=conn.execute('SELECT * FROM notices ORDER BY created_at DESC').fetchall(); conn.close()
    body="""<h1>📢 Notices</h1>{% for n in rows %}<div class='box'><h2>{{n['title']}}</h2><p>{{n['message']}}</p><span class='muted'>{{n['created_at']}}</span></div>{% endfor %}"""
    return page(body,'Notices',rows=rows)


@app.route('/events')
@login_required
def events():
    conn=get_db(); rows=conn.execute('SELECT * FROM events ORDER BY event_date').fetchall(); conn.close()
    body="""<h1>🎉 Events</h1><div class='cards'>{% for e in rows %}<div class='card'><h2>{{e['title']}}</h2><p>📅 {{e['event_date']}}</p><p>📍 {{e['location']}}</p><p>{{e['description']}}</p></div>{% endfor %}</div>"""
    return page(body,'Events',rows=rows)


@app.route('/tasks', methods=['GET','POST'])
@login_required
def tasks():
    conn=get_db()
    if request.method=='POST':
        title=request.form.get('title','').strip(); priority=request.form.get('priority','Medium')
        if title: conn.execute('INSERT INTO tasks(title,priority,status,created_at) VALUES(?,?,?,?)',(title,priority,'Pending',datetime.now().strftime('%Y-%m-%d %H:%M'))); conn.commit(); flash('Task added.')
    rows=conn.execute('SELECT * FROM tasks ORDER BY CASE status WHEN "Pending" THEN 0 ELSE 1 END,id DESC').fetchall(); conn.close()
    body="""<h1>✅ My Tasks</h1><div class='box'><form method='post'><label>New Task</label><input name='title' placeholder='Enter task...' required><select name='priority'><option>High</option><option selected>Medium</option><option>Low</option></select><button class='btn'>Add Task</button></form></div><div class='box'><table><tr><th>Task</th><th>Priority</th><th>Status</th><th>Action</th></tr>{% for t in rows %}<tr><td>{{t['title']}}</td><td><span class='badge {{t['priority']|lower}}'>{{t['priority']}}</span></td><td>{{t['status']}}</td><td>{% if t['status']!='Completed' %}<a class='btn success' href='/tasks/{{t["id"]}}/complete'>Done</a>{% endif %} <a class='btn danger' href='/tasks/{{t["id"]}}/delete'>Delete</a></td></tr>{% endfor %}</table></div>"""
    return page(body,'Tasks',rows=rows)


@app.route('/tasks/<int:tid>/complete')
@login_required
def complete_task(tid):
    conn=get_db(); conn.execute("UPDATE tasks SET status='Completed' WHERE id=?",(tid,)); conn.commit(); conn.close(); return redirect(url_for('tasks'))


@app.route('/tasks/<int:tid>/delete')
@login_required
def delete_task(tid):
    conn=get_db(); conn.execute('DELETE FROM tasks WHERE id=?',(tid,)); conn.commit(); conn.close(); return redirect(url_for('tasks'))


@app.route('/search')
@login_required
def search():
    q=request.args.get('q','').strip(); results=[]
    if q:
        conn=get_db(); like=f'%{q}%'
        results=conn.execute("SELECT 'Assignment' type,title,subject detail FROM assignments WHERE title LIKE ? OR subject LIKE ? UNION ALL SELECT 'Notice',title,message FROM notices WHERE title LIKE ? OR message LIKE ? UNION ALL SELECT 'Event',title,location FROM events WHERE title LIKE ? OR location LIKE ?",(like,like,like,like,like,like)).fetchall(); conn.close()
    body="""<h1>🔎 Global Search</h1><div class='box'><form class='search'><input name='q' value='{{q}}' placeholder='Search assignments, notices, events...'><button class='btn'>Search</button></form>{% if q %}<h3>Results for “{{q}}”</h3>{% for r in results %}<div class='notice'><b>{{r['type']}}:</b> {{r['title']}}<br><span class='muted'>{{r['detail']}}</span></div>{% else %}<p>No results found.</p>{% endfor %}{% endif %}</div>"""
    return page(body,'Search',q=q,results=results)


@app.route('/api/stats')
@login_required
def api_stats():
    conn=get_db(); subjects=conn.execute('SELECT attendance,total_classes FROM subjects').fetchall(); a=conn.execute("SELECT COUNT(*) c FROM assignments WHERE status='Pending'").fetchone()['c']; t=conn.execute("SELECT COUNT(*) c FROM tasks WHERE status='Pending'").fetchone()['c']; conn.close(); total=sum(x['total_classes'] for x in subjects); present=sum(x['attendance'] for x in subjects); return jsonify({'attendance':round(present/total*100,1) if total else 0,'pending_assignments':a,'pending_tasks':t})


init_db()

if __name__ == '__main__':
    print('CampusConnect running at http://127.0.0.1:5000')
    app.run(host='12.0.0.1', port=5000, debug=True, use_reloader=False)
