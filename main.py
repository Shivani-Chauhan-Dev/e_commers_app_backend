from flask import Flask, request, jsonify
import json
from database.database import db
from model.user import User
from model.product import Product
from model.order import Order
import jwt
import datetime
import bcrypt



app = Flask(__name__)
app.config['secret_key'] = "this is secret"


def create_app():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()



def token_required(f):
    def decorated(*args, **kwargs):
        # token = request.args.get('token')
        token = request.headers['Authorization'].split()[1]
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            jwt.decode(token, app.config['secret_key'], algorithms="HS256")
        except Exception as error:
            return jsonify({'error': 'token is invalid/expired'})
        return f(*args, **kwargs)
    return decorated
 


# rejistration form
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if data:

        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if email and password and first_name and last_name:
            # Check if the email already exists in the database
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({"message": "User already exists"}), 400
            else:
                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                )
                # Create the new user
                if User.create_user(
                    {
                        "email": email,
                        "password": hashed_password,
                        "first_name": first_name,
                        "last_name": last_name,
                    }
                ):
                    return jsonify({"message": "User created successfully"}), 201
                else:
                    return jsonify({"message": "Failed to create user"}), 500
        else:
            return jsonify({"message": "Missing fields"}), 400
    else:
        return jsonify({"message": "No data provided"}), 400


# loginform
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if data:
        email = data.get("email")
        password = data.get("password")
        if email and password:
            # Retrieve user from the database by email
            user = User.query.filter_by(email=email).first()
            print(user.email)
            if user:
                # Check if the provided password matches the hashed password stored in the database

                if bcrypt.checkpw(password.encode("utf-8"), user.password):
                    token = jwt.encode({'user': user.email, 'exp': datetime.datetime.utcnow(
                ) + datetime.timedelta(seconds=120)}, app.config['secret_key'])
                    return jsonify(token)

                    # return jsonify({"message": "Login successful"}), 200
                else:
                    return jsonify({"message": "Invalid email or password"}), 401
            else:
                return jsonify({"message": "Invalid email or password"}), 401
        else:
            return jsonify({"message": "Missing email or password"}), 400
    else:
        return jsonify({"message": "No data provided"}), 400

@app.route("/productlist", methods=["POST"])

def create_wish():
    try:
        order_data = request.json
        print(order_data)
        entry = Product(**order_data)
        
        db.session.add(entry)
        db.session.commit()

        return jsonify(entry.to_dict()), 201
    except Exception as e:
        return jsonify({"status": "Failed", "message": str(e)}), 500


@app.route("/productlist", methods=["GET"])
@token_required
def get_wishlist():
    # Filter parameters
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    min_rating = request.args.get("min_rating")
    product_type = request.args.get("product_type")
    brand = request.args.get("brand")

    query = Product.query

    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))
    if min_rating:
        query = query.filter(Product.rating >= min_rating)
    if product_type:
        query = query.filter(Product.product_type == product_type)
    if brand:
        query = query.filter(Product.brand == brand)
    products = query.all()
    product_list = [product.to_dict() for product in products]

    return jsonify(product_list), 200


@app.route("/productlist/<product_id>", methods=["DELETE"])
@token_required
def delete_wish(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return "", 204


@app.route("/orders", methods=["POST"])
@token_required
def create_order():
    try:
        order_data = json.loads(request.data)
        id = order_data.get("id")
        name = order_data.get("name")
        price = order_data.get("price")
        rating = order_data.get("rating")
        product_type = order_data.get("product_type")
        brand = order_data.get("brand")
        description = order_data.get("description")

        entry = Order(
            id=id,
            name=name,
            price=price,
            rating=rating,
            product_type=product_type,
            brand=brand,
            description=description,
        )
        db.session.add(entry)
        db.session.commit()

        return jsonify(entry.to_dict()), 201
    except Exception as e:
        return jsonify({"status": "Failed", "message": str(e)}), 500


@app.route("/orders", methods=["GET"])
@token_required
def get_orders():
    orders = Order.query.all()
    order_list = []
    for get_order in orders:
        order_list.append(
            {
                "id": get_order.id,
                "name": get_order.name,
                "price": get_order.price,
                "rating": get_order.rating,
                "product_type": get_order.product_type,
                "brand": get_order.brand,
                "description": get_order.description,
            }
        )
    return jsonify(order_list), 200


@app.route("/orders/<order_id>", methods=["DELETE"])
@token_required
def delete_order(order_id):
    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    create_app()
    app.run(debug=True)
