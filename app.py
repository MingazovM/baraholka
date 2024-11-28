from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(50))  # состояние игры
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='available')  # available, sold, reserved
    notes = db.Column(db.Text)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # new, completed, cancelled
    total_price = db.Column(db.Float)

@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        game = Game(
            title=request.form['title'],
            condition=request.form['condition'],
            purchase_price=float(request.form['purchase_price']),
            selling_price=float(request.form['selling_price']),
            notes=request.form['notes']
        )
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_game.html')

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        order = Order(
            game_id=request.form['game_id'],
            customer_name=request.form['customer_name'],
            customer_phone=request.form['customer_phone'],
            status='new',
            total_price=float(request.form['total_price'])
        )
        game = Game.query.get(request.form['game_id'])
        game.status = 'reserved'
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('orders'))
    games = Game.query.filter_by(status='available').all()
    return render_template('create_order.html', games=games)

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
