import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy, query
from random import randint

TOP_SECRETE_KEY = "Nayan_2141"

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# #Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# #Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # def to_dict(self):
    #     all_cafes = {
    #         "cafe": {
    #             'id': self.id,
    #             'name': self.name,
    #             'map_url': self.map_url,
    #             'img_url': self.img_url,
    #             'location': self.location,
    #             "amenities": {
    #                 'seats': self.seats,
    #                 'has_toilet': self.has_toilet,
    #                 'has_wifi': self.has_wifi,
    #                 'has_sockets': self.has_sockets,
    #                 'can_take_calls': self.can_take_calls,
    #                 'coffee_price': self.coffee_price
    #             }
    #         }
    #     }
    #     return all_cafes

    # Alternative
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=["GET"])
def get_random_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all_cafes():
    results = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = results.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search", methods=["GET"])
def search_cafe():
    loc = request.args.get('loc')
    try:
        result = db.session.execute(db.select(Cafe).where(Cafe.location == loc))
        cafes = result.scalar()
        return jsonify(cafes.to_dict())
    except AttributeError:
        not_found = {
            "error": {
                "Not Found": "Sorry, we don't have a cafe at that loction."
            }
        }
        return jsonify(not_found)


@app.route("/add", methods=["POST"])
def post_new_cafe():
    try:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    except:
        return jsonify(response={"error": "something went wrong."})


@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    try:
        cafe = db.get_or_404(Cafe, cafe_id)
        cafe.coffee_price = request.form.get("coffee_price")
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the new cafe."})
    except:
        return jsonify({"error": {"Not Found": "Sorry a cafe with that id was not found in the database."}})


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    try:
        cafe = db.get_or_404(Cafe, cafe_id)
        data = request.args.get("api-key")
        print(data)
        if TOP_SECRETE_KEY == data:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the new cafe."})
        else:
            return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct api_key"})
    except:
        return jsonify({"error": {"Not Found": "Sorry a cafe with that id was not found in the database."}})


# # HTTP GET - Read Record

# # HTTP POST - Create Record

# # HTTP PUT/PATCH - Update Record

# # HTTP DELETE - Delete Record

if __name__ == '__main__':
    app.run(debug=True)
