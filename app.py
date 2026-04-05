from flask import Flask, render_template, request, redirect, g
import sqlite3
import math

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database/main.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

class LogisticsSystem:
    def __init__(self):
        self.truck_capacity = 20 
        self.delivery_days = 2  
        self.warehouse_capacity = 1000
        self.total_drivers = 100  
        self.active_drivers = []
        self.active_deliveries = []
        self.current_warehouses_state = {1: {"stock": 1000}, 2: {"stock": 1000}, 3: {"stock": 1000}}

    def update_demand(self, db, point_id, regular=None, urgent=None):
        if regular is not None:
            db.execute("UPDATE points SET regular_amount = ? WHERE id = ?", (regular, point_id))
        if urgent is not None:
            db.execute("UPDATE points SET urgent_amount = ? WHERE id = ?", (urgent, point_id))
        db.commit()
        self.rebalance_routes(db)

    def rebalance_warehouses(self, db):
        points_db = db.execute("SELECT id, regular_amount, urgent_amount FROM points").fetchall()
        point_loads = [{"id": p[0], "load": p[1] + p[2]} for p in points_db]

        point_loads.sort(key=lambda x: x["load"], reverse=True)
        warehouse_loads = {1: 0, 2: 0, 3: 0}

        for p in point_loads:
            lightest_w = min(warehouse_loads, key=warehouse_loads.get)
            db.execute("UPDATE points SET warehouse_id = ? WHERE id = ?", (lightest_w, p["id"]))
            warehouse_loads[lightest_w] += p["load"]
            
        db.commit()

    def rebalance_routes(self, db):
        self.active_drivers = []
        self.active_deliveries = []
        driver_id_counter = 101

        self.rebalance_warehouses(db)

        warehouses_state = {i: {"stock": self.warehouse_capacity, "outflow": 0} for i in [1, 2, 3]}
        points_db = db.execute("SELECT id, warehouse_id, regular_amount, urgent_amount FROM points").fetchall()
        
        queue = []
        
        for row in points_db:
            p_id, w_id, reg_amt, urg_amt = row

            if urg_amt > 0:
                warehouses_state[w_id]["outflow"] += urg_amt
                trips_month = math.ceil(urg_amt / self.truck_capacity)
                drivers_needed = max(1, math.ceil((trips_month * self.delivery_days) / 30))
                
                for _ in range(drivers_needed):
                    queue.append({"p": p_id, "w": w_id, "type": "Критично", "pri": 1})

            if reg_amt > 0:
                warehouses_state[w_id]["outflow"] += reg_amt
                trips_month = math.ceil(reg_amt / self.truck_capacity)
                drivers_needed = max(1, math.ceil((trips_month * self.delivery_days) / 30))
                
                for _ in range(drivers_needed):
                    queue.append({"p": p_id, "w": w_id, "type": "Регулярно", "pri": 2})

        queue.sort(key=lambda x: x["pri"])
        available_drivers = self.total_drivers

        for trip in queue:
            if available_drivers <= 0: break 
            
            w_id = trip["w"]
            warehouses_state[w_id]["stock"] -= self.truck_capacity
            if warehouses_state[w_id]["stock"] < 0: warehouses_state[w_id]["stock"] = 0
            
            status = f"В дорозі - Критично ({self.delivery_days} дн.)" if trip["type"] == "Критично" else f"В дорозі ({self.delivery_days} дн.)"

            self.active_drivers.append({
                "id": driver_id_counter,
                "from": f"Склад {w_id}",
                "to": f"Точка {trip['p']}",
                "status": status
            })
            driver_id_counter += 1
            available_drivers -= 1

        for w_id in [1, 2, 3]:
            outflow = warehouses_state[w_id]["outflow"]
            
            if outflow > 0:
                sup_trips = math.ceil(outflow / (self.truck_capacity * 5))
                sup_drivers = max(1, math.ceil((sup_trips * self.delivery_days) / 30))
                
                self.active_deliveries.append({
                    "warehouse_id": w_id, 
                    "drivers": sup_drivers, 
                    "amount": outflow
                })
                
                for _ in range(sup_drivers):
                    if available_drivers <= 0: break
                    self.active_drivers.append({
                        "id": driver_id_counter,
                        "from": "Постачальник",
                        "to": f"Склад {w_id}",
                        "status": f"Поповнення ({self.delivery_days} дн.)"
                    })
                    driver_id_counter += 1
                    available_drivers -= 1

        self.current_warehouses_state = warehouses_state

logistics = LogisticsSystem()

@app.route('/')
def home(): return render_template('home.html')

@app.route('/point-log')
def point_log():
    db = get_db()
    points = [r[0] for r in db.execute("SELECT id FROM points ORDER BY id").fetchall()]
    return render_template('point-log.html', points=points)

@app.route('/login-point', methods=["POST"])
def login_point():
    p_id = request.form.get('point_id')
    return redirect(f'/point/{p_id}')

@app.route('/point/<int:p_id>')
def show_point(p_id):
    db = get_db()
    res = db.execute("SELECT regular_amount FROM points WHERE id = ?", (p_id,)).fetchone()
    return render_template('point.html', ID=p_id, number=logistics.truck_capacity, speed=logistics.delivery_days, value=res[0] if res else 0)

@app.route('/set-data/<int:p_id>', methods=["POST"])
def set_data(p_id):
    db = get_db()
    reg = request.form.get('reg')
    term = request.form.get('term')
    if reg: db.execute("UPDATE points SET regular_amount = ? WHERE id = ?", (reg, p_id))
    if term: db.execute("UPDATE points SET urgent_amount = ? WHERE id = ?", (term, p_id))
    db.commit()
    return redirect(f'/point/{p_id}')

@app.route('/admin')
def admin():
    db = get_db()
    logistics.rebalance_routes(db)
    points_info = db.execute("SELECT id, regular_amount, urgent_amount FROM points").fetchall()
    
    warehouses_data = []
    for w_id in [1, 2, 3]:
        pts = [str(r[0]) for r in db.execute("SELECT id FROM points WHERE warehouse_id = ?", (w_id,)).fetchall()]
        warehouses_data.append({
            "id": w_id, "points": ", ".join(pts), 
            "stock": logistics.current_warehouses_state[w_id]["stock"]
        })

    return render_template('manager.html', 
                           warehouses=warehouses_data, drivers=logistics.active_drivers, 
                           deliveries=logistics.active_deliveries, points_info=points_info,
                           amount=logistics.truck_capacity, days=logistics.delivery_days,
                           warehouse_capacity=logistics.warehouse_capacity)

@app.route('/change-amount')
def change_amount():
    logistics.truck_capacity = int(request.args.get('val', 20))
    return redirect('/admin')

@app.route('/change-speed')
def change_speed():
    logistics.delivery_days = int(request.args.get('val', 2))
    return redirect('/admin')

@app.route('/change-warehouse')
def change_warehouse():
    logistics.warehouse_capacity = int(request.args.get('val', 1000))
    return redirect('/admin')

if __name__ == '__main__': app.run(debug=True)