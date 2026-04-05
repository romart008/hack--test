from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(f'database/main.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

amount_per_delivery = 20
days_per_delivery = 2
max_amount_in_warehouse = 1000

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/point-log')
def point_log():
    return render_template('point-log.html')

@app.route('/login-point', methods=["POST"])
def point():
    return render_template('point.html', number=amount_per_delivery)

@app.route('/admin')
def admin():
    warehouses = [
        {"id": 1, "points": "Точка 1, Точка 2, Точка 3"},
        {"id": 2, "points": "Точка 4, Точка 5"},
        {"id": 3, "points": "Точка 6, Точка 7, Точка 8"}
    ]

    deliveries = [
        {"warehouse_id": 1, "drivers": 2, "amount": 40},
        {"warehouse_id": 2, "drivers": 1, "amount": 20},
        {"warehouse_id": 3, "drivers": 4, "amount": 80}
    ]

    drivers = [
        {"id": 101, "from": "Постачальник", "to": "Склад 1", "status": "В дорозі"},
        {"id": 102, "from": "Склад 2", "to": "Точка 4", "status": "Завантаження"},
        {"id": 103, "from": "Склад 3", "to": "Точка 8", "status": "В дорозі (Критично)"},
        {"id": 104, "from": "Постачальник", "to": "Склад 3", "status": "В дорозі"}
    ]

    return render_template('manager.html', 
                           amount=20, 
                           days=2, 
                           warehouse_capacity=1000,
                           warehouses=warehouses,
                           deliveries=deliveries,
                           drivers=drivers)

if __name__ == '__main__':
    app.run(debug=True)