import sqlalchemy

from flask import Blueprint, request
from flask_restful import Api, Resource

from .. import util
from ..models import File, Invite
from ..schema import info_post
from ..decorators import api_key_required
from ..extensions import db, limiter

user = Blueprint("user", __name__, url_prefix="/user")
user_api = Api(user)

class Info(Resource):
    @api_key_required()
    def get(self, user):
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

    @limiter.limit("2/minute")
    @api_key_required()
    def post(self, user):
        args = info_post.dump(request.form)

        if args.get("email"):
            user.email = args["email"]

        if args.get("username"):
            user.username = args["username"]

        db.session.commit()

        return {
            "success": True,
            "user": {
                "id": user.id,
                "apikey": user.api_key,
                "username": user.username,
                "email": user.email,
                "created": user.created.timestamp()
            }
        }

class Files(Resource):
    @api_key_required()
    def get(self, user):
        return {
            "success": True,
            "files": File.query.filter_by(parent_id=user.id, active=True).count()
        }

class FilesPage(Resource):
    @limiter.limit("10/minute")
    @api_key_required()
    def get(self, user, page):
        if page < 1:
            return {
                "success": False,
                "message": "Page count must be a number greater than zero."
            }, 400

        order_type = request.args.get("order", "desc")

        if not order_type in ("asc", "desc"):
            return {
                "success": False,
                "message": "Invalid order type was given."
            }

        order = getattr(sqlalchemy, order_type)
        files = File.query \
            .filter_by(parent_id=user.id, active=True) \
            .order_by(order(File.date)) \
            .offset((page - 1) * 25) \
            .limit(25)

        return {
            "success": True,
            "files": [{
                "id": file.id,
                "name": file.name,
                "date": file.date.timestamp(),
                "expires": file.expires.timestamp() if file.expires else None,
                "size": file.size
            } for file in files]
        }, 200

class Invites(Resource):
    @api_key_required()
    def get(self, user):
        return {
            "success": True,
            "invites": Invite.query.filter_by(parent_id=user.id, active=True).count()
        }

    @limiter.limit("5/minute")
    @api_key_required()
    def put(self, user):
        invites = Invite.query.filter_by(parent_id=user.id, active=True).count()

        if invites > 5:
            return {
                "success": False,
                "message": "You may have only 5 active invite codes."
            }, 403

        invite_code = util.random_string(32)
        entry = Invite(
            origin=util.ip2int(request.remote_addr),
            parent_id=user.id,
            code=invite_code
        )

        db.session.add(entry)
        db.session.commit()

        return {
            "success": True,
            "invite": {
                "id": entry.id,
                "code": entry.code,
                "created": entry.created.timestamp(),
                "used": entry.used
            }
        }, 200

class InvitesPage(Resource):
    @limiter.limit("10/minute")
    @api_key_required()
    def get(self, user, page):
        if page < 1:
            return {
                "success": False,
                "message": "Page count must be a number greater than zero."
            }, 400

        order_type = request.args.get("order", "desc")

        if not order_type in ("asc", "desc"):
            return {
                "success": False,
                "message": "Invalid order type was given."
            }

        order = getattr(sqlalchemy, order_type)
        invites = Invite.query \
            .filter_by(parent_id=user.id, active=True) \
            .order_by(order(Invite.created)) \
            .offset((page - 1) * 25) \
            .limit(25)

        return {
            "success": True,
            "invites": [{
                "id": invite.id,
                "code": invite.code,
                "created": invite.created.timestamp(),
                "used": invite.used
            } for invite in invites]
        }, 200

user_api.add_resource(Info, "/info")
user_api.add_resource(Invites, "/invites")
user_api.add_resource(InvitesPage, "/invites/<int:page>")
user_api.add_resource(Files, "/files")
user_api.add_resource(FilesPage, "/files/<int:page>")
