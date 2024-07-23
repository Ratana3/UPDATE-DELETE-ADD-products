import os

from jinja2 import Template
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import requests
import json
from datetime import date
import sqlite3
from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
import pymysql
import cryptography

app = Flask(__name__)
product_list = [
    {
        'id': '1',
        'title': 'picture',
        'price': '20',
        'description': 'energy drinks',
        'image': 'carabao.png'
    },
    {
        'id': '2',
        'title': 'picture',
        'price': '20',
        'description': 'delicious snack',
        'image': 'twisties.png'
    }
]


@app.route('/testing')
def testing():
    # Fetch a list of items (for simplicity, assuming there are 20 items)
    response = requests.get('https://fakestoreapi.com/products')
    items = response.json()
    return render_template('testing.html', items=items)


@app.route('/item/<int:item_id>')
def item_detail(item_id):
    response = requests.get(f'https://fakestoreapi.com/products/{item_id}')
    if response.status_code == 200:
        data = response.json()
        return render_template('data.html', data=data)
    else:
        return f"Item with ID {item_id} not found", 404


@app.route('/jinja')
def jinja():
    age = 18
    subjects = ['Python', 'C#', 'Laravel', 'HTML', 'Programming', 'Apple']
    student_list = [
        {
            'name': 'user1',
            'age': '18',
            'gender': 'M',
        },
        {
            'name': 'user2',
            'age': '20',
            'gender': 'M',
        },
    ]
    return render_template("jinja20.html", age=age, student_list=student_list, subjects=subjects)


@app.route('/product_detail/<int:id>')
def product_detail(id):
    response = requests.get(f'https://fakestoreapi.com/products/{id}')
    if response.status_code == 200:
        data = response.json()
        return render_template('product_detail.html', data=data)


@app.route('/checkout/<int:id>')
def checkout(id):
    response = requests.get(f'https://fakestoreapi.com/products/{id}')
    if response.status_code == 200:
        data = response.json()
        return render_template('checkout.html', data=data)


@app.route('/submit_order/<int:id>', methods=['POST'])
def submit_order(id):
    response = requests.get(f'https://fakestoreapi.com/products/{id}')
    if response.status_code == 200:
        data = response.json()
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        data_id = request.form.get('item_id')
        response = requests.get(f"https://fakestoreapi.com/products/{data_id}")
        message = f"Data for ID {data_id}:{data}"
        html = (
            "<strong>🧾 Product ID: {inv_no}</strong>\n"
            "<code>សរុប: {grand_total}</code>\n"
            "<code>ប្រាក់ទទួល: {received_amount}</code>\n"
            "<code>ប្រាក់អាប់: {change_amount}</code>\n"
            "<code>📆 {date}</code>\n"
            "<code>=======================</code>\n"
            "<code> -- Product name: {product_name}</code>\n"
            "<code> -- Description: {description}</code>\n"

        ).format(
            description=f"{data['description']}",
            product_name=f"{data['title']}",
            inv_no=f"{data['id']} ",
            grand_total=f"{data['price']} $",
            received_amount=f"{data['price']} $",
            change_amount='0$',
            date=date.today(),
        )

        def send_image_to_telegram_bot(bot_token, chat_id):
            url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            data = {'chat_id': chat_id}
            response = requests.post(url, data=data)
            print(response.json())

        # Replace 'YOUR_BOT_TOKEN' and 'YOUR_CHAT_ID' with your bot's token and your chat ID.
        bot_token = '7043304977:AAH1liq3drA51XyuzQIVlGbpy0Pd3PmpSaU'
        chat_id = '@st34_notify_channel'
        # Replace 'image_path' with the path to the image you want to send.
        send_image_to_telegram_bot(bot_token, chat_id)
        res = requests.get(
            f"https://api.telegram.org/bot7043304977:AAH1liq3drA51XyuzQIVlGbpy0Pd3PmpSaU/sendMessage?chat_id=@st34_notify_channel&text={html}&parse_mode=HTML")
        print(res.status_code)
        #  return render_template("result.html",data=data)
        return render_template("result.html",data=data)


@app.route('/product')
def product():
    response = requests.get('https://fakestoreapi.com/products')
    products = response.json()
    return render_template("product.html",product_list=products)



@app.route('/home')
def home():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/add_product')
def add_product():
    return render_template("add_product.html")


# Connect to mysql
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:

        connection = pymysql.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def execute_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


@app.route('/add_products', methods=['POST'])
def add_products():
    title = request.form['title']
    price = request.form['price']
    category = request.form['category']
    description = request.form['description']
    image = request.files['image']
    connections = create_connection("localhost", "root", "root", "pythonst34")
    # Save the image file temporarily
    image_path = f"static/slider/{image.filename}"
    image.save(image_path)

    # Insert product data into the database
    insert_product_query = """
        INSERT INTO products (title, price, category, description, image)
        VALUES (%s, %s, %s, %s, %s)
        """
    product_data = (title, price, category, description, image_path)
    execute_query(connections, insert_product_query, product_data)
    connections.close()

    return redirect(url_for("dbproduct"))


def fetch_product_by_id(connection, product_id):
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    connections = create_connection("localhost", "root", "root", "pythonst34")
    cursor = connections.cursor()
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    products = cursor.fetchone()
    connections.close()
    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price')
        category = request.form.get('category')
        description = request.form.get('description')
        image = request.files.get('image')
        # Save the image file temporarily
        image_path = f"static/slider/{image.filename}"
        image.save(image_path)
        connections = create_connection("localhost", "root", "root", "pythonst34")
        cursor = connections.cursor()
        cursor.execute('''
                UPDATE products
                SET title = %s, price = %s, category = %s, description = %s, image = %s
                WHERE id = %s
            ''', (title, price, category, description, image_path, product_id))
        connections.commit()
        cursor.close()
        connections.close()
        return redirect(url_for('dbproduct'))

    return render_template('update_product.html',product=products)


@app.route('/delete/<int:id>', methods=['GET'])
def delete_product(id):
    connections = create_connection("localhost", "root", "root", "pythonst34")
    cursor = connections.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    connections.commit()
    connections.close()

    return redirect(url_for('dbproduct'))


def get_product_by_id(connection, product_id):
    cursor = connection.cursor()
    query = "SELECT * FROM products WHERE id = %s"
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    return product


def fetch_all_products(connection):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute("SELECT * FROM products")
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


@app.route('/')
@app.route("/dbproduct")
def dbproduct():
    connections = create_connection("localhost", "root", "root", "pythonst34")
    products = fetch_all_products(connections)
    connections.close()
    return render_template("dbproduct.html", products=products)


if __name__ == '__main__':
    app.run(debug=True)
