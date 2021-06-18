from functools import wraps

from flask import request, current_app
from flask_restful import abort

from . import util
from .models import User
from .extensions import db

def api_key_required(allow_anonymous=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _allow_anonymous = False

            args = list(args)
            self = args.pop(0)

            if isinstance(allow_anonymous, str):
                _allow_anonymous = current_app.config[allow_anonymous]

            if request.method == "GET":
                apikey = request.args.get("apikey", None)
            elif request.method == "DELETE":
                if not request.json:
                    return {
                        "success": False,
                        "message": "No API key was given."
                    }, 401

                apikey = request.json.get("apikey", None)
            else:
                apikey = request.form.get("apikey", None)

            if apikey in ("", None):
                if _allow_anonymous:
                    return func(self, None, *args, **kwargs)

                return {
                    "success": False,
                    "message": "No API key was given."
                }, 401

            user = User.query.filter_by(api_key=apikey).first()

            if not user:
                if _allow_anonymous:
                    return func(self, None, *args, **kwargs)

                return {
                    "success": False,
                    "message": "User does not exist."
                }, 401

            if user.origin is None:
                user.origin = util.ip2int(request.remote_addr)
                db.session.commit()

            return func(self, user, *args, **kwargs)

        return wrapper

    return decorator

def required_captcha(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not util.verify_recaptcha(request.form.get("captcha")):
            abort(401, description="Invalid Google reCAPTCHA token was provided.")

        return f(*args, **kwargs)

    return wrapper
