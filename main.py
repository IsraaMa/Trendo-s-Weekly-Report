from flask import Flask
from flask_restful import Resource, Api
from src.monday_request import monday_connection


app = Flask(__name__)
api = Api(app)

api.add_resource(monday_connection, "/report")


class welcome_message(Resource):
    def get(self):
        return {"message": "Welcome to monday report generator!",
                "version": 1.0}


class authors(Resource):
    def get(self):
        authors_names = ["Israel Mata",
        "Alex de la Torre",
        "Erick Lara"]
        return {"Authors": authors_names,
                "version": 1.0}


api.add_resource(welcome_message, "/")
api.add_resource(authors, "/authors")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3001)
