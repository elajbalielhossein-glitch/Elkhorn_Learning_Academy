import os, sqlite3, hashlib, secrets, html, urllib.parse, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from datetime import datetime

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,'data','elkhorn_learning.db')
SESSIONS={}
GREEN='#163f2b'; GOLD='#b69145'

def con():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def hp(p,s=None):
    s=s or secrets.token_hex(16); d=hashlib.pbkdf2_hmac('sha256',p.encode(),s.encode(),200000).hex(); return s+'$'+d

def vp(p,stored):
    try:
        s,d=stored.split('$',1); return secrets.compare_digest(hp(p,s).split('$',1)[1],d)
    except: return False

def init_db():
    c=con(); q=c.cursor(); q.executescript('''
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT,full_name TEXT,email TEXT,department TEXT,role TEXT,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY,title TEXT UNIQUE,passing_score INTEGER DEFAULT 80);
    CREATE TABLE IF NOT EXISTS enrollments(id INTEGER PRIMARY KEY,user_id INTEGER,course_id INTEGER,status TEXT DEFAULT 'Not Started',progress INTEGER DEFAULT 0,score INTEGER,completed_at TEXT,certificate_code TEXT,UNIQUE(user_id,course_id));
    ''')
    if not q.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        q.execute('INSERT INTO users(username,password_hash,full_name,email,department,role) VALUES(?,?,?,?,?,?)',('admin',hp('Elkhorn2026!'),'Portal Administrator','admin@elkhornresort.mb.ca','Administration','admin'))
    if not q.execute("SELECT 1 FROM users WHERE username='michelle'").fetchone():
        q.execute('INSERT INTO users(username,password_hash,full_name,email,department,role) VALUES(?,?,?,?,?,?)',('michelle',hp('Welcome2026!'),'Michelle','michelle@elkhornresort.mb.ca','Front Desk','employee'))
    q.execute('INSERT OR IGNORE INTO courses(title,passing_score) VALUES(?,80)',('Conflict Management for Managers',))
    uid=q.execute("SELECT id FROM users WHERE username='michelle'").fetchone()['id']; cid=q.execute("SELECT id FROM courses WHERE title='Conflict Management for Managers'").fetchone()['id']
    q.execute('INSERT OR IGNORE INTO enrollments(user_id,course_id,status,progress,score,completed_at,certificate_code) VALUES(?,?,?,?,?,?,?)',(uid,cid,'Completed',100,92,'2026-07-31','ELK-2026-000124'))
    c.commit(); c.close()

def esc(x): return html.escape(str(x or ''))
def layout(title,body,user=None):
    nav=''
    if user:
        nav='<nav><a href="/dashboard">Dashboard</a>' + ('<a href="/users">Employees</a>' if user['role']=='admin' else '') + '<a href="/logout">Logout</a></nav>'
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>
    *{{box-sizing:border-box}}body{{margin:0;font-family:Arial;background:#f4f6f4;color:#24312a}}header{{background:{GREEN};color:white;display:flex;align-items:center;padding:14px 28px;gap:16px}}header img{{width:78px;height:58px;object-fit:contain;background:white;border-radius:6px;padding:4px}}header h1{{margin:0;font-size:22px}}header p{{margin:3px 0;opacity:.8}}nav{{margin-left:auto;display:flex;gap:18px}}nav a{{color:white;text-decoration:none;font-weight:bold}}main{{max-width:1250px;margin:28px auto;padding:0 20px}}.card,.panel{{background:white;border-radius:14px;padding:24px;box-shadow:0 8px 25px #0001}}.login{{max-width:420px;margin:70px auto}}label{{display:block;font-weight:bold;margin:14px 0}}input,select{{width:100%;padding:11px;border:1px solid #ccd3ce;border-radius:7px;margin-top:6px}}button,.btn{{background:{GREEN};color:white;border:0;border-radius:7px;padding:10px 14px;font-weight:bold;text-decoration:none;cursor:pointer;display:inline-block}}.small{{padding:7px 9px;font-size:12px}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:18px 0}}.cards div{{background:white;border-left:5px solid {GOLD};padding:20px;border-radius:10px}}.cards b{{font-size:30px;display:block;color:{GREEN}}}.table{{overflow:auto;background:white;border-radius:12px;box-shadow:0 5px 18px #0001;margin-top:20px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:13px;border-bottom:1px solid #e8ece9;white-space:nowrap}}th{{background:#f7f3e8;color:{GREEN}}}.completed{{color:#15713e;font-weight:bold}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.msg{{padding:12px;background:#dff3e6;border-radius:8px;margin-bottom:14px}}@media(max-width:800px){{.cards,.two{{grid-template-columns:1fr}}header{{flex-wrap:wrap}}nav{{width:100%;margin-left:0}}}}
    </style></head><body><header><img src="/static/elkhorn_logo.png"><div><h1>Elkhorn Learning Academy</h1><p>Training & Development Portal</p></div>{nav}</header><main>{body}</main></body></html>'''.encode()

def make_pdf(name,course,date,code):
    # Minimal valid one-page landscape PDF using built-in Helvetica fonts.
    def t(s): return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
    ops=f'''q 0.98 0.97 0.92 rg 0 0 842 595 re f Q
0.086 0.247 0.169 RG 12 w 18 18 806 559 re S
0.714 0.569 0.271 RG 2 w 34 34 774 527 re S
BT /F2 26 Tf 0.086 0.247 0.169 rg 235 455 Td (CERTIFICATE OF COMPLETION) Tj ET
BT /F1 13 Tf 0.086 0.247 0.169 rg 300 410 Td (This certificate is proudly presented to) Tj ET
BT /F2 30 Tf 0.086 0.247 0.169 rg 280 360 Td ({t(name)}) Tj ET
BT /F1 13 Tf 0.086 0.247 0.169 rg 330 325 Td (for successfully completing) Tj ET
BT /F2 20 Tf 0.086 0.247 0.169 rg 210 280 Td ({t(course)}) Tj ET
BT /F1 11 Tf 0.086 0.247 0.169 rg 75 82 Td (Completion Date: {t(date)}) Tj ET
BT /F1 11 Tf 0.086 0.247 0.169 rg 610 82 Td (Certificate Code: {t(code)}) Tj ET
BT /F3 18 Tf 0.086 0.247 0.169 rg 355 115 Td (Chris Phillips) Tj ET
BT /F1 10 Tf 0.086 0.247 0.169 rg 385 97 Td (General Manager) Tj ET'''
    objs=[]
    objs.append('1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj')
    objs.append('2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj')
    objs.append('3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 5 0 R /F2 6 0 R /F3 7 0 R >> >> /Contents 4 0 R >> endobj')
    stream=ops.encode('latin-1','replace'); objs.append(f'4 0 obj << /Length {len(stream)} >> stream\n'+stream.decode('latin-1')+'\nendstream endobj')
    objs.append('5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj')
    objs.append('6 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj')
    objs.append('7 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >> endobj')
    out=b'%PDF-1.4\n'; offs=[0]
    for o in objs: offs.append(len(out)); out+=o.encode('latin-1')+b'\n'
    x=len(out); out+=f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()
    for o in offs[1:]: out+=f'{o:010d} 00000 n \n'.encode()
    out+=f'trailer << /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF'.encode(); return out

class H(BaseHTTPRequestHandler):
    def user(self):
        ck=SimpleCookie(self.headers.get('Cookie','')); sid=ck.get('sid'); uid=SESSIONS.get(sid.value) if sid else None
        if not uid:return None
        c=con(); u=c.execute('SELECT * FROM users WHERE id=? AND active=1',(uid,)).fetchone(); c.close(); return u
    def sendb(self,b,status=200,ctype='text/html',headers=None):
        self.send_response(status); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(b)))
        for k,v in (headers or {}).items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(b)
    def redirect(self,p,headers=None): self.sendb(b'',302,headers={'Location':p,**(headers or {})})
    def form(self):
        n=int(self.headers.get('Content-Length','0')); return urllib.parse.parse_qs(self.rfile.read(n).decode())
    def do_GET(self):
        path=urllib.parse.urlparse(self.path).path; u=self.user()
        if path=='/static/elkhorn_logo.png':
            b=open(os.path.join(BASE,'static','elkhorn_logo.png'),'rb').read(); return self.sendb(b,ctype='image/png')
        if path=='/logout':
            return self.redirect('/',{'Set-Cookie':'sid=; Max-Age=0; Path=/'})
        if path=='/' and not u:
            body='''<section class="card login"><h2>Portal Login</h2><form method="post"><label>Username<input name="username" required autofocus></label><label>Password<input name="password" type="password" required></label><button>Login</button></form><p>Administrator: <b>admin</b> / <b>Elkhorn2026!</b></p></section>'''; return self.sendb(layout('Login',body))
        if not u:return self.redirect('/')
        if path=='/' or path=='/dashboard':
            c=con()
            if u['role']=='admin':
                st={'e':c.execute("SELECT COUNT(*) c FROM users WHERE role='employee' AND active=1").fetchone()['c'],'c':c.execute("SELECT COUNT(*) c FROM enrollments WHERE status='Completed'").fetchone()['c'],'i':c.execute("SELECT COUNT(*) c FROM enrollments WHERE status='In Progress'").fetchone()['c']}
                rows=c.execute('''SELECT e.id,u.full_name,u.email,u.department,c.title,e.status,e.progress,e.completed_at FROM enrollments e JOIN users u ON u.id=e.user_id JOIN courses c ON c.id=e.course_id ORDER BY u.full_name''').fetchall(); c.close()
                trs=''.join(f'''<tr><td>{esc(r['full_name'])}</td><td>{esc(r['email'])}</td><td>{esc(r['department'])}</td><td>{esc(r['title'])}</td><td class="{'completed' if r['status']=='Completed' else ''}">{esc(r['status'])}</td><td>{r['progress']}%</td><td>{esc(r['completed_at'] or '—')}</td><td>{f'<a class="btn small" href="/certificate?id={r["id"]}">Download PDF</a>' if r['status']=='Completed' else '—'}</td></tr>''' for r in rows)
                body=f'''<h2>Admin Training Tracker</h2><div class="cards"><div><b>{st['e']}</b>Employees</div><div><b>{st['c']}</b>Completed</div><div><b>{st['i']}</b>In Progress</div></div><div class="table"><table><tr><th>Employee</th><th>Email</th><th>Department</th><th>Course</th><th>Status</th><th>Progress</th><th>Date</th><th>Certificate</th></tr>{trs}</table></div>'''
            else:
                rows=c.execute('''SELECT e.id,c.title,e.status,e.progress,e.completed_at FROM enrollments e JOIN courses c ON c.id=e.course_id WHERE e.user_id=?''',(u['id'],)).fetchall(); c.close()
                trs=''.join(f'''<tr><td>{esc(r['title'])}</td><td class="{'completed' if r['status']=='Completed' else ''}">{esc(r['status'])}</td><td>{r['progress']}%</td><td>{esc(r['completed_at'] or '—')}</td><td>{f'<a class="btn small" href="/certificate?id={r["id"]}">Download PDF</a>' if r['status']=='Completed' else '—'}</td></tr>''' for r in rows)
                body=f'<h2>My Learning</h2><div class="table"><table><tr><th>Course</th><th>Status</th><th>Progress</th><th>Date</th><th>Download</th></tr>{trs}</table></div>'
            return self.sendb(layout('Dashboard',body,u))
        if path=='/users' and u['role']=='admin':
            c=con(); people=c.execute("SELECT * FROM users WHERE role='employee' ORDER BY full_name").fetchall(); courses=c.execute('SELECT * FROM courses').fetchall(); c.close()
            po=''.join(f'<option value="{p["id"]}">{esc(p["full_name"])}</option>' for p in people); co=''.join(f'<option value="{x["id"]}">{esc(x["title"])}</option>' for x in courses)
            body=f'''<h2>Employee Management</h2><div class="two"><section class="panel"><h3>Create Employee</h3><form method="post" action="/create-user"><label>Full name<input name="full_name" required></label><label>Username<input name="username" required></label><label>Temporary password<input name="password" required></label><label>Email<input name="email" type="email"></label><label>Department<input name="department"></label><button>Create User</button></form></section><section class="panel"><h3>Assign Course</h3><form method="post" action="/assign"><label>Employee<select name="user_id">{po}</select></label><label>Course<select name="course_id">{co}</select></label><button>Assign</button></form></section></div>'''; return self.sendb(layout('Employees',body,u))
        if path=='/certificate':
            eid=int(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('id',['0'])[0]); c=con(); r=c.execute('''SELECT e.*,u.full_name,c.title FROM enrollments e JOIN users u ON u.id=e.user_id JOIN courses c ON c.id=e.course_id WHERE e.id=?''',(eid,)).fetchone(); c.close()
            if not r or r['status']!='Completed' or (u['role']!='admin' and r['user_id']!=u['id']): return self.sendb(b'Forbidden',403)
            b=make_pdf(r['full_name'],r['title'],r['completed_at'] or '',r['certificate_code'] or '')
            return self.sendb(b,ctype='application/pdf',headers={'Content-Disposition':f'attachment; filename="certificate_{eid}.pdf"'})
        self.sendb(b'Not found',404)
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path; f=self.form(); u=self.user()
        if path=='/':
            username=f.get('username',[''])[0].strip().lower(); password=f.get('password',[''])[0]; c=con(); x=c.execute('SELECT * FROM users WHERE username=? AND active=1',(username,)).fetchone(); c.close()
            if x and vp(password,x['password_hash']):
                sid=secrets.token_urlsafe(24); SESSIONS[sid]=x['id']; return self.redirect('/dashboard',{'Set-Cookie':f'sid={sid}; HttpOnly; SameSite=Lax; Path=/'})
            return self.sendb(layout('Login','<section class="card login"><h2>Login failed</h2><p>Invalid username or password.</p><a class="btn" href="/">Try again</a></section>'),401)
        if not u or u['role']!='admin': return self.sendb(b'Forbidden',403)
        if path=='/create-user':
            c=con()
            try:c.execute('INSERT INTO users(username,password_hash,full_name,email,department,role) VALUES(?,?,?,?,?,?)',(f['username'][0].strip().lower(),hp(f['password'][0]),f['full_name'][0].strip(),f.get('email',[''])[0],f.get('department',[''])[0],'employee')); c.commit()
            except sqlite3.IntegrityError: pass
            c.close(); return self.redirect('/users')
        if path=='/assign':
            c=con(); c.execute('INSERT OR IGNORE INTO enrollments(user_id,course_id) VALUES(?,?)',(f['user_id'][0],f['course_id'][0])); c.commit(); c.close(); return self.redirect('/dashboard')
        self.sendb(b'Not found',404)
    def log_message(self,fmt,*args): pass

if __name__=='__main__':
    init_db(); threading.Timer(1.0,lambda:webbrowser.open('http://127.0.0.1:8765')).start(); print('Elkhorn Learning Academy running at http://127.0.0.1:8765'); ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
