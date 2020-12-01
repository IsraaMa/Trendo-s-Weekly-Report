from flask import request
from flask_restful import Resource
from src.monday_api_connection import monday_admin_info


def authenticate(token):
    if token == 'mOnd4y!REPORT':
        return True
    else:
        return False


class monday_connection(Resource):
    def get(self):
        arguments = request.args
        api_key = arguments.get('api_key')
        token = arguments.get('token')
        allowed = authenticate(token)
        if allowed is False:
            return {"Error": "Authentication failed."}, 422
        if api_key is None:
            return {"Error": "api_key needed!"}, 422

        monday_info = monday_admin_info(api_key)
        output = {'data': monday_info}
        return output
