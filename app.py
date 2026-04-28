from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

DELIVERIES = [
    {"id":"DEL-001","driver":"Ravi Kumar","driverId":"DRV-14","color":"#2563EB","destination":"Gandhipuram, Coimbatore","status":"on-time","eta":"11:40 AM","delay":0,"weight":"320 kg"},
    {"id":"DEL-002","driver":"Priya Sharma","driverId":"DRV-07","color":"#0D9488","destination":"RS Puram, Coimbatore","status":"delayed","eta":"2:15 PM","delay":35,"weight":"180 kg"},
    {"id":"DEL-003","driver":"Arun Patel","driverId":"DRV-22","color":"#7C3AED","destination":"Peelamedu, Coimbatore","status":"in-transit","eta":"3:30 PM","delay":0,"weight":"450 kg"},
    {"id":"DEL-004","driver":"Meena Raj","driverId":"DRV-05","color":"#D97706","destination":"Saibaba Colony, CBE","status":"completed","eta":"10:00 AM","delay":0,"weight":"95 kg"},
    {"id":"DEL-005","driver":"Karthik S","driverId":"DRV-31","color":"#DC2626","destination":"Ukkadam, Coimbatore","status":"critical","eta":"4:00 PM","delay":65,"weight":"270 kg"},
    {"id":"DEL-006","driver":"Divya Nair","driverId":"DRV-18","color":"#059669","destination":"Singanallur, Coimbatore","status":"pending","eta":"5:00 PM","delay":0,"weight":"130 kg"},
    {"id":"DEL-007","driver":"Suresh M","driverId":"DRV-09","color":"#2563EB","destination":"Tidel Park, Chennai","status":"on-time","eta":"6:30 PM","delay":0,"weight":"510 kg"},
    {"id":"DEL-008","driver":"Lakshmi V","driverId":"DRV-27","color":"#7C3AED","destination":"Anna Nagar, Chennai","status":"delayed","eta":"7:00 PM","delay":20,"weight":"215 kg"},
    {"id":"DEL-009","driver":"Venkat R","driverId":"DRV-33","color":"#0D9488","destination":"T Nagar, Chennai","status":"in-transit","eta":"8:15 PM","delay":0,"weight":"340 kg"},
    {"id":"DEL-010","driver":"Anitha K","driverId":"DRV-41","color":"#D97706","destination":"Madurai North","status":"on-time","eta":"9:00 AM","delay":0,"weight":"680 kg"},
]

ORDERS = {
    "ORD-2847": {"id":"ORD-2847","customer":"TechCorp India","product":"Server Rack Components x4","weight":"320 kg","driver":"Ravi Kumar","from":"NexaChain Warehouse, Coimbatore","to":"TechCorp, Tidel Park, Chennai","eta":"Today, 3:40 PM","progress":65,"status":"in-transit","delayReason":None,"steps":[{"label":"Order Placed","time":"Jan 15, 9:00 AM","done":True},{"label":"Packed","time":"Jan 15, 10:30 AM","done":True},{"label":"Dispatched","time":"Jan 15, 11:00 AM","done":True},{"label":"In Transit","time":"Jan 15, 12:00 PM","done":True},{"label":"Out for Delivery","time":"Expected 3:00 PM","done":False},{"label":"Delivered","time":"Expected 3:40 PM","done":False}]},
    "ORD-2851": {"id":"ORD-2851","customer":"FreshMart","product":"Perishable Goods - Vegetables","weight":"180 kg","driver":"Priya Sharma","from":"NexaChain Cold Storage, Coimbatore","to":"FreshMart Store, RS Puram","eta":"Today, 2:15 PM (35 min delay)","progress":40,"status":"delayed","delayReason":"Heavy traffic near Avinashi Road junction","steps":[{"label":"Order Placed","time":"Jan 15, 8:00 AM","done":True},{"label":"Packed","time":"Jan 15, 9:00 AM","done":True},{"label":"Dispatched","time":"Jan 15, 9:30 AM","done":True},{"label":"In Transit","time":"Delayed - traffic","done":False},{"label":"Delivered","time":"Expected 2:15 PM","done":False}]},
    "ORD-2863": {"id":"ORD-2863","customer":"AutoParts Hub","product":"Engine Components Batch #7","weight":"450 kg","driver":"Arun Patel","from":"NexaChain Warehouse, Coimbatore","to":"AutoParts Hub, Peelamedu","eta":"Today, 3:30 PM","progress":20,"status":"pending","delayReason":None,"steps":[{"label":"Order Placed","time":"Jan 15, 10:00 AM","done":True},{"label":"Packed","time":"Jan 15, 11:00 AM","done":True},{"label":"Dispatched","time":"Expected 12:00 PM","done":False},{"label":"In Transit","time":"Expected 1:00 PM","done":False},{"label":"Delivered","time":"Expected 3:30 PM","done":False}]},
}

WEEKLY_CHART = [
    {"day":"Mon","on":32,"delayed":8},{"day":"Tue","on":28,"delayed":5},
    {"day":"Wed","on":40,"delayed":12},{"day":"Thu","on":35,"delayed":7},
    {"day":"Fri","on":42,"delayed":9},{"day":"Sat","on":25,"delayed":4},
    {"day":"Sun","on":18,"delayed":3},
]

ADMIN_STATS = {"total_deliveries":248,"on_time_rate":87,"delayed":31,"failed":8,"active_drivers":14}
DRIVER_STATS = {"today_deliveries":3,"completed":1,"distance_km":47.2,"eta_accuracy":94}
TASKS = [
    {"num":1,"id":"DEL-001","done":True,"address":"Gandhipuram, Near Town Hall","weight":"320 kg","time":"10:00-11:40 AM"},
    {"num":2,"id":"DEL-002","done":False,"address":"RS Puram, 3rd Street","weight":"180 kg","time":"12:00-2:15 PM"},
    {"num":3,"id":"DEL-003","done":False,"address":"Peelamedu, KGISL Campus","weight":"450 kg","time":"3:00-4:30 PM"},
]
ALERTS = [
    {"type":"danger","title":"Critical Delay - DEL-005","desc":"Karthik S is 65 min behind schedule.","time":"2 min ago"},
    {"type":"warning","title":"Traffic Alert - Avinashi Road","desc":"Heavy congestion affecting 3 routes.","time":"8 min ago"},
    {"type":"success","title":"DEL-004 Delivered","desc":"Meena Raj completed delivery on time.","time":"22 min ago"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/driver/stats")
def driver_stats():
    return jsonify(DRIVER_STATS)

@app.route("/api/driver/tasks")
def driver_tasks():
    return jsonify(TASKS)

@app.route("/api/driver/status", methods=["POST"])
def set_driver_status():
    data = request.get_json()
    return jsonify({"ok":True,"status":data.get("status"),"message":f"Status set to {data.get('status')}"})

@app.route("/api/driver/complete/<task_id>", methods=["POST"])
def complete_task(task_id):
    for t in TASKS:
        if t["id"] == task_id:
            t["done"] = True
            return jsonify({"ok":True,"task":t})
    return jsonify({"ok":False,"error":"Not found"}), 404

@app.route("/api/track/<order_id>")
def track_order(order_id):
    order = ORDERS.get(order_id.upper())
    if not order:
        return jsonify({"ok":False,"error":f"Order {order_id} not found"}), 404
    return jsonify({"ok":True,"order":order})

@app.route("/api/admin/stats")
def admin_stats():
    return jsonify(ADMIN_STATS)

@app.route("/api/admin/deliveries")
def admin_deliveries():
    search = request.args.get("search","").lower()
    status = request.args.get("status","")
    driver = request.args.get("driver","")
    page = int(request.args.get("page",1))
    per_page = 8
    data = DELIVERIES[:]
    if search:
        data = [d for d in data if search in d["id"].lower() or search in d["driver"].lower() or search in d["destination"].lower()]
    if status:
        data = [d for d in data if d["status"] == status]
    if driver:
        data = [d for d in data if d["driver"] == driver]
    total = len(data)
    start = (page-1)*per_page
    return jsonify({"ok":True,"data":data[start:start+per_page],"total":total,"page":page,"per_page":per_page})

@app.route("/api/admin/chart")
def admin_chart():
    return jsonify(WEEKLY_CHART)

@app.route("/api/admin/alerts")
def admin_alerts():
    return jsonify(ALERTS)

@app.route("/api/admin/delivery/<del_id>", methods=["PATCH"])
def update_delivery(del_id):
    data = request.get_json()
    for d in DELIVERIES:
        if d["id"] == del_id:
            d.update({k:v for k,v in data.items() if k in d})
            return jsonify({"ok":True,"delivery":d})
    return jsonify({"ok":False,"error":"Not found"}), 404

@app.route("/api/admin/export")
def export_data():
    lines = ["id,driver,driverId,destination,status,eta,delay,weight"]
    for d in DELIVERIES:
        lines.append(f"{d['id']},{d['driver']},{d['driverId']},{d['destination']},{d['status']},{d['eta']},{d['delay']},{d['weight']}")
    return app.response_class("\n".join(lines), mimetype="text/csv",
        headers={"Content-Disposition":"attachment;filename=deliveries.csv"})

port = int(os.environ.get("PORT", 5000))
app.run(debug=False, host="0.0.0.0", port=port)
