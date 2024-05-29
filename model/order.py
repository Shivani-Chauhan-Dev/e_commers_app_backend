from database.database import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.String(10), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price':self.price,
            'rating': self.rating,
            'product_type': self.product_type,
            'brand ': self.brand,
            'description':self.description
        }