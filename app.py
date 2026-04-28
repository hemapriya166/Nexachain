"""
NexaChain — AI Supply Chain Platform
Flask Backend with SQLite Database
Run with: python app.py
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "nexachain.db"

# ─────────────────────────────────────────────
#  Database Setup
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

def init_db():
    """Create tables and seed with initial data if DB doesn't exist."""
    if os.path.exists(DB_PATH):
        return  # already initialized

    conn = get_db()
    c = conn.cursor()

    # --- Deliveries table ---
    c.execute("""
        CREATE TABLE deliveries (
            id          TEXT PRIMARY KEY,
            driver      TEXT,
            driverId    TEXT,
            color       TEXT,
            destination TEXT,
            status      TEXT,
            eta         TEXT,
            delay       INTEGER DEFAULT 0,
            weight      TEXT
        )
    """)

    # --- Orders table ---
    c.execute("""
        CREATE TABLE orders (
            id          TEXT PRIMARY KEY,
            customer    TEXT,
            product     TEXT,
            weight      TEXT,
            driver      TEXT,
            origin      TEXT,
            destination TEXT,
            eta         TEXT,
            progress    INTEGER DEFAULT 0,
            status      TEXT,
            delayReason TEXT
        )
    """)

    # --- Order steps table ---
    c.execute("""
        CREATE TABLE order_steps (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            label    TEXT,
            time     TEXT,
            done     INTEGER DEFAULT 0
        )
    """)

    # --- Alerts table ---
    c.execute("""
        CREATE TABLE alerts (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            type  TEXT,
            title TEXT,
            desc  TEXT,
            time  TEXT
        )
    """)

    # --- Tasks table ---
    c.execute("""
        CREATE TABLE tasks (
            id      TEXT PRIMARY KEY,
            num     INTEGER,
            address TEXT,
            weight  TEXT,
            time    TEXT,
            done    INTEGER DEFAULT 0
        )
    """)

    # --- Driver stats table ---
    c.execute("""
        CREATE TABLE driver_stats (
            id                INTEGER PRIMARY KEY,
            today_deliveries  INTEGER,
            completed         INTEGER,
            distance_km       REAL,
            eta_accuracy      INTEGER
        )
    """)

    # ── Seed Data ──────────────────────────────

    deliveries = [
        ("DEL-001","Ravi Kumar",   "DRV-14","#2563EB","Gandhipuram, Coimbatore",  "on-time",  "11:40 AM", 0,  "320 kg"),
        ("DEL-002","Priya Sharma", "DRV-07","#0D9488","RS Puram, Coimbatore",     "delayed",  "2:15 PM",  35, "180 kg"),
        ("DEL-003","Arun Patel",   "DRV-22","#7C3AED","Peelamedu, Coimbatore",    "in-transit","3:30 PM", 0,  "450 kg"),
        ("DEL-004","Meena Raj",    "DRV-05","#D97706","Saibaba Colony, CBE",      "completed","10:00 AM", 0,  "95 kg"),
        ("DEL-005","Karthik S",    "DRV-31","#DC2626","Ukkadam, Coimbatore",      "critical", "4:00 PM",  65, "270 kg"),
        ("DEL-006","Divya Nair",   "DRV-18","#059669","Singanallur, Coimbatore",  "pending",  "5:00 PM",  0,  "130 kg"),
        ("DEL-007","Suresh M",     "DRV-09","#2563EB","Tidel Park, Chennai",      "on-time",  "6:30 PM",  0,  "510 kg"),
        ("DEL-008","Lakshmi V",    "DRV-27","#7C3AED","Anna Nagar, Chennai",      "delayed",  "7:00 PM",  20, "215 kg"),
        ("DEL-009","Venkat R",     "DRV-33","#0D9488","T Nagar, Chennai",         "in-transit","8:15 PM", 0,  "340 kg"),
        ("DEL-010","Anitha K",     "DRV-41","#D97706","Madurai North",            "on-time",  "9:00 AM",  0,  "680 kg"),
    ]
    c.executemany("INSERT INTO deliveries VALUES (?,?,?,?,?,?,?,?,?)", deliveries)

    orders = [
        ("ORD-2847","TechCorp India","Server Rack Components × 4","320 kg","Ravi Kumar",
         "NexaChain Warehouse, Coimbatore","TechCorp, Tidel Park, Chennai","Today, 3:40 PM",65,"in-transit",None),
        ("ORD-2851","FreshMart","Perishable Goods — Vegetables","180 kg","Priya Sharma",
         "NexaChain Cold Storage, Coimbatore","FreshMart Store, RS Puram","Today, 2:15 PM (35 min delay)",40,"delayed",
         "Heavy traffic near Avinashi Road junction"),
        ("ORD-2863","AutoParts Hub","Engine Components Batch #7","450 kg","Arun Patel",
         "NexaChain Warehouse, Coimbatore","AutoParts Hub, Peelamedu","Today, 3:30 PM",20,"pending",None),
    ]
    c.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?)", orders)

    order_steps = [
        ("ORD-2847","Order Placed",    "Jan 15, 9:00 AM",  1),
        ("ORD-2847","Packed",          "Jan 15, 10:30 AM", 1),
        ("ORD-2847","Dispatched",      "Jan 15, 11:00 AM", 1),
        ("ORD-2847","In Transit",      "Jan 15, 12:00 PM", 1),
        ("ORD-2847","Out for Delivery","Expected 3:00 PM", 0),
        ("ORD-2847","Delivered",       "Expected 3:40 PM", 0),
        ("ORD-2851","Order Placed",    "Jan 15, 8:00 AM",  1),
        ("ORD-2851","Packed",          "Jan 15, 9:00 AM",  1),
        ("ORD-2851","Dispatched",      "Jan 15, 9:30 AM",  1),
        ("ORD-2851","In Transit",      "Delayed — traffic",0),
        ("ORD-2851","Delivered",       "Expected 2:15 PM", 0),
        ("ORD-2863","Order Placed",    "Jan 15, 10:00 AM", 1),
        ("ORD-2863","Packed",          "Jan 15, 11:00 AM", 1),
        ("ORD-2863","Dispatched",      "Expected 12:00 PM",0),
        ("ORD-2863","In Transit",      "Expected 1:00 PM", 0),
        ("ORD-2863","Delivered",       "Expected 3:30 PM", 0),
    ]
    c.executemany("INSERT INTO order_steps (order_id,label,time,done) VALUES (?,?,?,?)", order_steps)

    alerts = [
        ("danger",  "Critical Delay — DEL-005",    "Karthik S is 65 min behind schedule. Customer notified.",         "2 min ago"),
        ("warning", "Traffic Alert — Avinashi Road","Heavy congestion affecting 3 active routes. Rerouting in progress.","8 min ago"),
        ("success", "DEL-004 Delivered",            "Meena Raj completed delivery to Saibaba Colony on time.",          "22 min ago"),
    ]
    c.executemany("INSERT INTO alerts (type,title,desc,time) VALUES (?,?,?,?)", alerts)

    tasks = [
        ("DEL-001", 1, "Gandhipuram, Near Town Hall", "320 kg", "10:00–11:40 AM", 1),
        ("DEL-002", 2, "RS Puram, 3rd Street",        "180 kg", "12:00–2:15 PM",  0),
        ("DEL-003", 3, "Peelamedu, KGISL Campus",     "450 kg", "3:00–4:30 PM",   0),
    ]
    c.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?)", tasks)

    c.execute("INSERT INTO driver_stats VALUES (1, 3, 1, 47.2, 94)")

    conn.commit()
    conn.close()
    print("✅ Database created and seeded!")

# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ----- Driver -----

@app.route("/api/driver/stats")
def driver_stats():
    conn = get_db()
    row = conn.execute("SELECT * FROM driver_stats WHERE id=1").fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/driver/tasks")
def driver_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks ORDER BY num").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/driver/status", methods=["POST"])
def set_driver_status():
    data = request.get_json()
    status = data.get("status", "active")
    return jsonify({"ok": True, "status": status, "message": f"Status set to {status}"})

@app.route("/api/driver/complete/<task_id>", methods=["POST"])
def complete_task(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    # update driver completed count
    conn.execute("UPDATE driver_stats SET completed = completed + 1 WHERE id=1")
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    if row:
        return jsonify({"ok": True, "task": dict(row)})
    return jsonify({"ok": False, "error": "Task not found"}), 404


# ----- Tracking -----

@app.route("/api/track/<order_id>")
def track_order(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id.upper(),)).fetchone()
    if not order:
        conn.close()
        return jsonify({"ok": False, "error": f"Order {order_id} not found"}), 404

    steps = conn.execute(
        "SELECT label, time, done FROM order_steps WHERE order_id=? ORDER BY id",
        (order_id.upper(),)
    ).fetchall()
    conn.close()

    result = dict(order)
    result["from"] = result.pop("origin")
    result["to"]   = result.pop("destination")
    result["steps"] = [dict(s) for s in steps]
    return jsonify({"ok": True, "order": result})


# ----- Admin -----

@app.route("/api/admin/stats")
def admin_stats():
    conn = get_db()
    total     = conn.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]
    delayed   = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='delayed' OR status='critical'").fetchone()[0]
    failed    = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='failed'").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='completed'").fetchone()[0]
    in_transit= conn.execute("SELECT COUNT(*) FROM deliveries WHERE status='in-transit'").fetchone()[0]
    on_time   = total - delayed - failed
    on_time_rate = round((on_time / total * 100)) if total else 0
    conn.close()
    return jsonify({
        "total_deliveries": total,
        "on_time_rate": on_time_rate,
        "delayed": delayed,
        "failed": failed,
        "active_drivers": 14,
        "donut": {"completed": completed, "delayed": delayed, "failed": failed, "in_transit": in_transit}
    })

@app.route("/api/admin/deliveries")
def admin_deliveries():
    search   = request.args.get("search", "").lower()
    status   = request.args.get("status", "")
    driver   = request.args.get("driver", "")
    page     = int(request.args.get("page", 1))
    per_page = 8

    query  = "SELECT * FROM deliveries WHERE 1=1"
    params = []
    if search:
        query += " AND (LOWER(id) LIKE ? OR LOWER(driver) LIKE ? OR LOWER(destination) LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if status:
        query += " AND status=?"
        params.append(status)
    if driver:
        query += " AND driver=?"
        params.append(driver)

    conn  = get_db()
    total = conn.execute(f"SELECT COUNT(*) FROM ({query})", params).fetchone()[0]
    rows  = conn.execute(query + f" LIMIT {per_page} OFFSET {(page-1)*per_page}", params).fetchall()
    conn.close()
    return jsonify({"ok": True, "data": [dict(r) for r in rows], "total": total, "page": page, "per_page": per_page})

@app.route("/api/admin/chart")
def admin_chart():
    return jsonify([
        {"day": "Mon", "on": 32, "delayed": 8},
        {"day": "Tue", "on": 28, "delayed": 5},
        {"day": "Wed", "on": 40, "delayed": 12},
        {"day": "Thu", "on": 35, "delayed": 7},
        {"day": "Fri", "on": 42, "delayed": 9},
        {"day": "Sat", "on": 25, "delayed": 4},
        {"day": "Sun", "on": 18, "delayed": 3},
    ])

@app.route("/api/admin/alerts")
def admin_alerts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/delivery/<del_id>", methods=["PATCH"])
def update_delivery(del_id):
    data = request.get_json()
    allowed = {"status", "eta", "delay", "driver", "destination", "weight"}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"ok": False, "error": "Nothing to update"}), 400

    set_clause = ", ".join(f"{k}=?" for k in updates)
    values     = list(updates.values()) + [del_id]
    conn = get_db()
    conn.execute(f"UPDATE deliveries SET {set_clause} WHERE id=?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM deliveries WHERE id=?", (del_id,)).fetchone()
    conn.close()
    if row:
        return jsonify({"ok": True, "delivery": dict(row)})
    return jsonify({"ok": False, "error": "Not found"}), 404

@app.route("/api/admin/export")
def export_data():
    conn  = get_db()
    rows  = conn.execute("SELECT * FROM deliveries").fetchall()
    conn.close()
    lines = ["id,driver,driverId,destination,status,eta,delay,weight"]
    for r in rows:
        d = dict(r)
        lines.append(f"{d['id']},{d['driver']},{d['driverId']},{d['destination']},"
                     f"{d['status']},{d['eta']},{d['delay']},{d['weight']}")
    csv_text = "\n".join(lines)
    return app.response_class(csv_text, mimetype="text/csv",
                              headers={"Content-Disposition": "attachment;filename=deliveries.csv"})


# ─────────────────────────────────────────────
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
