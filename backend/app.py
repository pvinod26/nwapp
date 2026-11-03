import os, sqlite3, calendar, csv, io
from datetime import date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "replace-with-a-long-random-secret")
DB_PATH = os.getenv("DATABASE_PATH", "cabledesk.db")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
COMPANIES = ["SSC", "ZEE", "SDV / Spandana", "AP Fiber", "GTPL", "JKC"]

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def month_keys():
    today = date.today()
    out = []
    for off in range(3, -1, -1):
        y, m = today.year, today.month - off
        while m < 1:
            y -= 1
            m += 12
        out.append((f"{y:04d}-{m:02d}", calendar.month_abbr[m]))
    return out

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS customers(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT DEFAULT '',
      connection_id TEXT DEFAULT '', company TEXT NOT NULL, area TEXT DEFAULT '',
      monthly_amount REAL DEFAULT 0, pack_expiry TEXT DEFAULT '', notes TEXT DEFAULT '',
      recharged INTEGER DEFAULT 0, recharge_previous_expiry TEXT DEFAULT NULL, active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS payments(
      id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, month_key TEXT NOT NULL,
      paid INTEGER NOT NULL DEFAULT 0, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(customer_id,month_key), FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS admin_users(username TEXT PRIMARY KEY,password_hash TEXT NOT NULL);
    """)
    # Safe migration for an older demo database.
    cols = [r["name"] for r in c.execute("PRAGMA table_info(customers)").fetchall()]
    if "recharged" not in cols:
        c.execute("ALTER TABLE customers ADD COLUMN recharged INTEGER DEFAULT 0")
    if "recharge_previous_expiry" not in cols:
        c.execute("ALTER TABLE customers ADD COLUMN recharge_previous_expiry TEXT DEFAULT NULL")
    user = c.execute("SELECT username FROM admin_users WHERE username=?", (ADMIN_USERNAME,)).fetchone()
    if not user:
        c.execute("INSERT INTO admin_users VALUES(?,?)",
                  (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD)))
    if c.execute("SELECT COUNT(*) n FROM customers").fetchone()["n"] == 0:
        seed(c)
    c.commit()
    c.close()

def seed(c):
    data = {
      "SSC": [
        ("Bamidi Laxmi","23122380178835",""),("D. Raju / Renuka","23122380178868",""),
        ("Durga Prasad","6030637011008323",""),("Boolakamma","23122380178785",""),
        ("Hari Amma","6030637010666048",""),("Nageswara Rao","6030637010643120",""),
        ("Tedha","23122380139928",""),("Padma (Raju S)","6030637010416147",""),
        ("Satyanarayana","6030637010452787",""),("M. Pallavi / Chakali KD","6030637010621340",""),
        ("Venkat","6030637010640571",""),("Durgarao / Raju","6030637010837627",""),
        ("Prasanna Laxmi","23122380140892",""),("P. V. Ramana Murthy","6030637010806370",""),
        ("Potnuru Trinadharao","6030637010640589",""),("Papa Rao","6030637010959957",""),
        ("Putta Venkateswara Rao","231223801289779",""),("Y. Jagadeeswara Rao","6030637010643666",""),
        ("Ramesh / Pedda Siochi","6030637010813095",""),("Krishna Rao","6030637010659068",""),
        ("P. Suresh","6030637010654572",""),("K. Adhi Laxmi","6030637010031299",""),
        ("Jaya Laxmi","60306370106660188",""),("Rama Rao / Mango","23122380140975",""),
        ("Peruri Venkataramana","6030637010442416",""),("Jaya Sister","6030637010864007",""),
        ("Srinivas G","6030637010009942",""),("Shk. Manju","23122380139829",""),
        ("RTC Conductor","6030637009423369",""),("Sri Rama Murthy","6030637010456556",""),
        ("Gaddayya","6030637010658981","")
      ],
      "ZEE": [
        ("G. Krishna","02748834750",""),("Ganapathi / Tailor","02748834758",""),
        ("Sarayini / Injirapu","02748834760",""),("Annamma / Kishore","02748834756",""),
        ("Nandipilli Satyam","02748834723",""),("R. Chinna Rao","02748834625",""),
        ("Teki Chandra Mohan","02748834743",""),("Pitta Bala Krishna","02748834776",""),
        ("Rati Rama Rao","02748834749",""),("Karthik","02748834757",""),
        ("Injirapu Mallesh","02748834759",""),("China Raju P","02748834739",""),
        ("Doogana Laxmi","02748834733",""),("G. Rama Rao","02748834780",""),
        ("Mungati Parvathi","02748834183",""),("Revathi","02748834793",""),
        ("Ratnaalu","02748834769",""),("I. Mallamma","02748834754",""),
        ("Gopi / Rukshana","02748834738",""),("Kistnada Thirupathirao","02748834768",""),
        ("P. Adhinarayana","02748834744","")
      ],
      "SDV / Spandana": [
        ("Pydithalli","VCCSID4JH56692",""),("Zarina Begum","VCCSID3EH02603",""),
        ("Ruva Satyam","VCCSID10E11980",""),("Bodd","VCCSID4JH56743",""),
        ("E. Rajeswara Rao","VCCSID10E13165",""),("Thathayya","VCCSID4JH56754",""),
        ("S. Venkateswara Rao","VCCSID10E9451",""),("Jucce Son","VCCSID34008154",""),
        ("Mahesh Gold Smith","VCCSID34002659",""),("Rambabu","VCCSID34001300",""),
        ("M. Pallavi","VCCSID4JH550119",""),("Purni","VCCSID10E9451",""),
        ("Santhulu / Rambabu","VCCSID34013010",""),("Ravi","VCCSID4JH550151",""),
        ("Laxmi","VCCSID34002602",""),("Haria","VCCSID4JH550284",""),
        ("K. Laxmi","VCCSID4JH550970","")
      ],
      "AP Fiber": [
        ("K. Chinnammadu","103251803","8328402231"),("Anantha","103661882","9440319997"),
        ("Ganeswara Rao","102786640","7893123790"),("Bodayya","200264176","7995117068"),
        ("Chinavenkata Reddy","103251755",""),("Ram Mohana Rao","103171503","9440121463"),
        ("Bheri Chinna Rao","200267975","9959118524"),("Chinavenkata Reddy","200264177","9959007367"),
        ("Hameed Khan","103251809","8978760122"),("House","200317122","9440417300"),
        ("Balaji Jyothi Prakash","200318289","9493986641"),("D. Siva Kumar","200156147","7875090959"),
        ("Malleswara Rao","103251584","9440149496"),("Ravi Kiran","103251766","8019548802"),
        ("Santhosh Kumar","103251746","7386155433"),("Sadasivuni Narendra","200163546","9182512216"),
        ("D. T. R. Patnaik","200092912","9110753006"),("N. Shekar","103166254","7008608966"),
        ("Ravi Potnuru","200232398","9962411585"),("I. Satish","103598215","")
      ]
    }
    keys = month_keys()
    for company, rows in data.items():
        for name, cid, phone in rows:
            cur = c.execute("INSERT INTO customers(name,phone,connection_id,company) VALUES(?,?,?,?)",
                            (name, phone, cid, company))
            for i,(key,label) in enumerate(keys):
                c.execute("INSERT INTO payments(customer_id,month_key,paid) VALUES(?,?,?)",
                          (cur.lastrowid,key,1 if i < 3 else 0))

def auth(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not session.get("username"): return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrapped

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        c=connect(); u=c.execute("SELECT * FROM admin_users WHERE username=?",(request.form.get("username",""),)).fetchone(); c.close()
        if u and check_password_hash(u["password_hash"],request.form.get("password","")):
            session["username"]=u["username"]; return redirect(url_for("home"))
        flash("Incorrect username or password.","error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/")
@auth
def home():
    return render_template("index.html", companies=COMPANIES, months=month_keys(), username=session["username"])

@app.route("/api/customers")
@auth
def customers():
    company=request.args.get("company","All"); q=request.args.get("q","").strip()
    sort=request.args.get("sort","name"); payment=request.args.get("payment","all"); expiry_filter=request.args.get("expiry","all")
    c=connect(); sql="SELECT * FROM customers WHERE active=1"; args=[]
    if company!="All": sql+=" AND company=?"; args.append(company)
    if q:
        sql+=" AND (name LIKE ? OR phone LIKE ? OR connection_id LIKE ? OR area LIKE ?)"
        args += [f"%{q}%"]*4
    order={"name":"name COLLATE NOCASE","expiry":"CASE WHEN pack_expiry='' THEN '9999-12-31' ELSE pack_expiry END",
           "company":"company,name COLLATE NOCASE","amount":"monthly_amount DESC"}.get(sort,"name COLLATE NOCASE")
    sql+=" ORDER BY "+order
    rows=c.execute(sql,args).fetchall(); keys=month_keys(); today=date.today(); out=[]
    for r in rows:
        ps=c.execute("SELECT month_key,paid FROM payments WHERE customer_id=?",(r["id"],)).fetchall()
        pm={p["month_key"]:bool(p["paid"]) for p in ps}
        pays=[{"key":k,"label":lab,"paid":pm.get(k,False)} for k,lab in keys]
        if payment=="pending" and pays[-1]["paid"]: continue
        if payment=="paid" and not pays[-1]["paid"]: continue
        pending=0
        for p in reversed(pays):
            if not p["paid"]: pending+=1
            else: break
        days=None
        if r["pack_expiry"]:
            try: days=(date.fromisoformat(r["pack_expiry"])-today).days
            except ValueError: pass
        if expiry_filter=="today" and days != 0: continue
        if expiry_filter=="expired" and not (days is not None and days < 0 and not bool(r["recharged"])): continue
        if expiry_filter=="tomorrow" and days != 1: continue
        if expiry_filter=="week" and not (days is not None and 0 <= days <= 7): continue
        out.append(dict(id=r["id"],name=r["name"],phone=r["phone"],connection_id=r["connection_id"],
          company=r["company"],area=r["area"],monthly_amount=r["monthly_amount"],pack_expiry=r["pack_expiry"],
          notes=r["notes"],recharged=bool(r["recharged"]),payments=pays,pending_months=pending,days_to_expiry=days))
    c.close(); return jsonify(out)

@app.route("/api/customers",methods=["POST"])
@auth
def add_customer():
    d=request.get_json(force=True); name=(d.get("name") or "").strip(); company=d.get("company","")
    if not name or company not in COMPANIES: return jsonify(error="Name and valid service provider are required."),400
    c=connect()
    cur=c.execute("""INSERT INTO customers(name,phone,connection_id,company,area,monthly_amount,pack_expiry,notes,recharged)
      VALUES(?,?,?,?,?,?,?,?,?)""",(name,d.get("phone",""),d.get("connection_id",""),company,d.get("area",""),
      float(d.get("monthly_amount") or 0),d.get("pack_expiry",""),d.get("notes",""),0))
    for i,(k,l) in enumerate(month_keys()):
        c.execute("INSERT INTO payments(customer_id,month_key,paid) VALUES(?,?,?)",(cur.lastrowid,k,1 if i<3 else 0))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/customers/<int:cid>",methods=["PUT","DELETE"])
@auth
def edit_customer(cid):
    c=connect()
    if request.method=="DELETE":
        c.execute("UPDATE customers SET active=0 WHERE id=?",(cid,)); c.commit(); c.close(); return jsonify(ok=True)
    d=request.get_json(force=True); name=(d.get("name") or "").strip(); company=d.get("company","")
    if not name or company not in COMPANIES: c.close(); return jsonify(error="Name and provider required."),400
    c.execute("""UPDATE customers SET name=?,phone=?,connection_id=?,company=?,area=?,monthly_amount=?,pack_expiry=?,notes=?
      WHERE id=?""",(name,d.get("phone",""),d.get("connection_id",""),company,d.get("area",""),
      float(d.get("monthly_amount") or 0),d.get("pack_expiry",""),d.get("notes",""),cid))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/payment",methods=["POST"])
@auth
def payment():
    d=request.get_json(force=True); c=connect()
    c.execute("""INSERT INTO payments(customer_id,month_key,paid) VALUES(?,?,?)
      ON CONFLICT(customer_id,month_key) DO UPDATE SET paid=excluded.paid,updated_at=CURRENT_TIMESTAMP""",
      (int(d["customer_id"]),d["month_key"],1 if d["paid"] else 0))
    c.commit(); c.close(); return jsonify(ok=True)

@app.route("/api/recharge",methods=["POST"])
@auth
def recharge():
    d=request.get_json(force=True); cid=int(d["customer_id"]); c=connect()
    r=c.execute("SELECT pack_expiry FROM customers WHERE id=? AND active=1",(cid,)).fetchone()
    if not r: c.close(); return jsonify(error="Customer not found."),404
    today=date.today()
    try: old=date.fromisoformat(r["pack_expiry"]) if r["pack_expiry"] else today
    except ValueError: old=today
    # Extend from the later of today or the existing expiry date.
    new_expiry=max(today,old)+timedelta(days=30)
    c.execute("UPDATE customers SET recharge_previous_expiry=pack_expiry,pack_expiry=?,recharged=1 WHERE id=?",(new_expiry.isoformat(),cid))
    c.commit(); c.close()
    return jsonify(ok=True,pack_expiry=new_expiry.isoformat(),message="Recharge recorded; expiry extended by 30 days.")

@app.route("/api/recharge/reset",methods=["POST"])
@auth
def reset_recharge():
    d=request.get_json(force=True); c=connect()
    cid=int(d["customer_id"])
    row=c.execute("SELECT recharge_previous_expiry,recharged FROM customers WHERE id=? AND active=1",(cid,)).fetchone()
    if not row:
        c.close(); return jsonify(error="Customer not found."),404
    if not row["recharged"]:
        c.close(); return jsonify(error="This customer is not currently marked as recharged."),400
    previous=row["recharge_previous_expiry"]
    if previous is None:
        c.close()
        return jsonify(error="This recharge was made in an older app version, so its previous expiry date was not saved. Its date has been left unchanged to protect your data. New recharges can be rolled back fully."),409
    c.execute("UPDATE customers SET pack_expiry=?,recharged=0,recharge_previous_expiry=NULL WHERE id=?",
              (previous,cid))
    c.commit(); c.close()
    return jsonify(ok=True,pack_expiry=previous or "",message="Recharge rolled back and original expiry restored.")

@app.route("/api/reminders")
@auth
def reminders():
    c=connect(); rows=c.execute("SELECT * FROM customers WHERE active=1").fetchall(); keys=month_keys()
    result={"expiring_tomorrow":[],"long_pending":[]}; tomorrow=(date.today()+timedelta(days=1)).isoformat()
    for r in rows:
        ps=c.execute("SELECT month_key,paid FROM payments WHERE customer_id=?",(r["id"],)).fetchall()
        pm={p["month_key"]:bool(p["paid"]) for p in ps}; n=0
        for k,l in reversed(keys):
            if not pm.get(k,False): n+=1
            else: break
        item=dict(id=r["id"],name=r["name"],phone=r["phone"],company=r["company"],connection_id=r["connection_id"])
        if r["pack_expiry"]==tomorrow: result["expiring_tomorrow"].append(item)
        if n>=3: result["long_pending"].append({**item,"pending_months":n})
    c.close(); return jsonify(result)

@app.route("/api/summary")
@auth
def summary():
    c=connect(); keys=month_keys(); total=c.execute("SELECT COUNT(*) n FROM customers WHERE active=1").fetchone()["n"]
    pending=c.execute("""SELECT COUNT(*) n FROM customers x LEFT JOIN payments p ON p.customer_id=x.id AND p.month_key=?
      WHERE x.active=1 AND COALESCE(p.paid,0)=0""",(keys[-1][0],)).fetchone()["n"]
    tomorrow=(date.today()+timedelta(days=1)).isoformat()
    exp=c.execute("SELECT COUNT(*) n FROM customers WHERE active=1 AND pack_expiry=?",(tomorrow,)).fetchone()["n"]
    allrows=c.execute("SELECT pack_expiry,recharged FROM customers WHERE active=1").fetchall()
    today=date.today()
    counts={"today":0,"expired":0,"tomorrow":0,"week":0}
    for row in allrows:
        if not row["pack_expiry"]: continue
        try: days=(date.fromisoformat(row["pack_expiry"])-today).days
        except ValueError: continue
        if days==0: counts["today"]+=1
        if days<0 and not row["recharged"]: counts["expired"]+=1
        if days==1: counts["tomorrow"]+=1
        if 0<=days<=7: counts["week"]+=1
    c.close(); return jsonify(total=total,pending=pending,expiring_tomorrow=exp,expiry_counts=counts)

@app.route("/export.csv")
@auth
def export_csv():
    c=connect(); rows=c.execute("SELECT * FROM customers WHERE active=1 ORDER BY company,name").fetchall(); keys=month_keys()
    s=io.StringIO(); w=csv.writer(s); w.writerow(["Name","Phone","Connection ID","Company","Area","Monthly amount","Pack expiry","Recharged"]+[l for k,l in keys])
    for r in rows:
        pm={p["month_key"]:p["paid"] for p in c.execute("SELECT month_key,paid FROM payments WHERE customer_id=?",(r["id"],))}
        w.writerow([r["name"],r["phone"],r["connection_id"],r["company"],r["area"],r["monthly_amount"],r["pack_expiry"],"Yes" if r["recharged"] else "No"]+["Paid" if pm.get(k,0) else "Pending" for k,l in keys])
    c.close(); return Response(s.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=cabledesk-customers.csv"})

@app.route("/change-password",methods=["POST"])
@auth
def change_password():
    old=request.form.get("old_password",""); new=request.form.get("new_password","")
    c=connect(); r=c.execute("SELECT password_hash FROM admin_users WHERE username=?",(session["username"],)).fetchone()
    if not r or not check_password_hash(r["password_hash"],old) or len(new)<10:
        flash("Current password incorrect or new password must be at least 10 characters.","error")
    else:
        c.execute("UPDATE admin_users SET password_hash=? WHERE username=?",(generate_password_hash(new),session["username"]))
        c.commit(); flash("Password changed successfully.","success")
    c.close(); return redirect(url_for("home"))

init_db()
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",5000)),debug=True)
