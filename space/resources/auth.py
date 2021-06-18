from werkzeug.security import generate_password_hash

from flask import Blueprint, current_app, request
from flask_restful import Api, Resource

from .. import util
from ..models import Invite, User
from ..schema import register_post, login_post
from ..decorators import required_captcha
from ..extensions import db, limiter

auth = Blueprint("auth", __name__, url_prefix="/auth")
auth_api = Api(auth)

limiter.limit("60/hour")(auth)

class AuthRegister(Resource):
    method_decorators = [required_captcha]

    def post(self):
        args = register_post.load(request.form)

        if current_app.config["INVITE_ONLY"] and not args.get("invite"):
            return {
                "success": False,
                "message": "An invite code is necessary."
            }, 400

        user = User.query.filter_by(username=args["username"], active=True).first()
        email = User.query.filter_by(email=args["email"], active=True).first()

        if user:
            return {
                "success": False,
                "message": "Username is already taken."
            }, 400

        if email:
            return {
                "success": False,
                "message": "That email address is already in use."
            }, 400

        entry = User(
            email=args["email"],
            username=args["username"],
            origin=util.ip2int(request.remote_addr),
            password_hash=generate_password_hash(args["password"]),
            api_key=util.random_string(32)
        )

        db.session.add(entry)

        if args.get("invite"):
            invite = Invite.query.filter_by(
                code=args["invite"],
                active=True,
                used=False
            ).first()

            if not invite:
                return {
                    "success": False,
                    "message": "Invalid invite code was provided."
                }, 400

            invite.used = True
            invite.user_id = entry.id

        db.session.commit()

        return {
            "success": True,
            "user": {
                "id": entry.id,
                "apikey": entry.api_key,
                "username": entry.username,
                "email": entry.email,
                "created": entry.created.timestamp()
            }
        }, 200

class AuthLogin(Resource):
    method_decorators = [required_captcha]

    def post(self):
        args = login_post.load(request.form)
        user = User.query.filter_by(username=args["username"], active=True).first()

        if not user:
            return {
                "success": False,
                "message": "User does not exist."
            }, 404

        if not user.check_password(args["password"]):
            return {
                "success": False,
                "message": "Invalid password."
            }, 403

        return {
            "success": True,
            "user": {
                "id": user.id,
                "apikey": user.api_key,
                "username": user.username,
                "email": user.email,
                "created": user.created.timestamp()
            }
        }, 200


auth_api.add_resource(AuthRegister, "/register")
auth_api.add_resource(AuthLogin, "/login")
