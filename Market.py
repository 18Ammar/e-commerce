
# importing the need it library

from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float 
# import flask_whooshalchemy as ws
import sqlite3




SQLAlchemy._ModelClassMarker = object()


app = Flask(__name__, template_folder='template')
app.secret_key = "hello"

app.permanent_session_lifetime = timedelta(days=5)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'amar2003895@gmail.com'
app.config['MAIL_PASSWORD'] = '********'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['WHOOSH_BASE'] = 'whoosh'


mail = Mail(app)
db = SQLAlchemy(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
    



class Product(db.Model):
    __searchable__ = ['name', 'dis','path','price']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=True)
    dis = db.Column(db.String(100), nullable=True)
    path = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer,nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


# ws.whoosh_index(app,Product)

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")


@app.route("/addItem", methods=["POST", "GET"])
def addItem():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            dis = request.form.get("dis")
            path = request.form.get("path")
            price = request.form.get("price")
            pro = Product(name=name, dis=dis,path=path,price=price)
            db.session.add(pro)
            db.session.commit()
    return render_template("addItem.html")


def get_product_by_id(product_id):
    engine = create_engine('sqlite:///C:/Users/Lenovo/digitalMarkting/instance/product.sqlite3')
    metadata = MetaData()
    products = Table('product', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('dis', String),
        Column('price', Float),
        Column('path', String)
    )
    conn = engine.connect()
    query = products.select().where(products.c.id == product_id)
    result = conn.execute(query).fetchone()
    conn.close()
    if result:
        product = {
            'id': result[0],
            'name': result[1],
            'dis': result[2],
            'price': result[3],
            'path': result[4]
        }
    else:
        product = None
    return product



@app.route('/SHOP', methods=['POST', 'GET'])
def SHOP():
    products = Product.query.all()
    if request.method == 'POST':
        search = request.form.get('qq')
        if search:
            results = Product.query.filter(Product.name.ilike('%{}%'.format(search))).all()
            return render_template('shop.html', products=results, search=search)
    return render_template('shop.html', products=products)


@app.route('/join')
def join():
    return 'hello from join us page'

@app.route('/contact', methods=["POST", "GET"])
def contact_form():
    return render_template("countact.html")

def send_email(name, email, message):
    msg = Message('New message from your website', sender='<your_email_address>', recipients=['<recipient_email_address>'])
    msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"
    mail.send(msg)

@app.route('/send-message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    send_email(name, email, message)
    return 'Message sent!'


@app.route("/chackout",methods=["POST", "GET"])
def checkout():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        session["email"] = email
        session["password"] = password

        # create a new user
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("register", email=email, password=password))
    else:
        return render_template("chackout.html")


@app.route('/place-order', methods=['POST'])
def place_order():
    # Get the form data
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        session["email"] = email
        session["password"] = password

        # create a new user
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("register", email=email, password=password))
    
    
    return 'thank-you'


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register")
def register(): 
    email = request.args.get('email')
    password = request.args.get('password')
    return f"Registered user with email: {email} and password: {password}"

@app.route('/view/<index>')
def view(index):
    product = get_product_by_id(index)
    return render_template('view.html',product=product)



with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
