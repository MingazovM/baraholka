from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    orders = db.relationship('Order', backref='game', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(20))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, completed, cancelled
    total_price = db.Column(db.Float)

@app.route('/')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form

            game = Game(
                title=data.get('title'),
                condition=data.get('condition'),
                purchase_price=float(data.get('purchase_price')),
                selling_price=float(data.get('selling_price')),
                notes=data.get('notes')
            )
            db.session.add(game)
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': 'Игра успешно добавлена'}), 200
            return redirect(url_for('index'))

        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 400
            return redirect(url_for('index'))

    return render_template('add_game.html')

@app.route('/create_order', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        game_id = int(request.form['game_id'])
        game = Game.query.get(game_id)
        
        if game and game.status == 'available':
            order = Order(
                game_id=game_id,
                customer_name=request.form['customer_name'],
                customer_phone=request.form['customer_phone'],
                status='new',
                total_price=float(request.form['total_price'])
            )
            
            game.status = 'reserved'
            db.session.add(order)
            db.session.commit()
            return redirect(url_for('orders'))
            
    games = Game.query.filter_by(status='available').all()
    return render_template('create_order.html', games=games)

@app.route('/orders')
def orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)