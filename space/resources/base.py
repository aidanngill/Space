import os
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Blueprint, request, current_app
from flask_restful import Api, Resource

from .. import util
from ..models import File, Invite
from ..decorators import api_key_required
from ..extensions import db, limiter

base = Blueprint("base", __name__, url_prefix="/")
base_api = Api(base)

class FileInteraction(Resource):
    @limiter.limit("10/minute")
    @api_key_required(allow_anonymous="ANONYMOUS_UPLOADS")
    def put(self, user):
        expires = util.expiry_date(request.form.get("expires", None))

        if expires and expires.days > 7:
            return {
                "success": False,
                "message": "Files must expire in less than one week (7 days)."
            }, 400

        if "file" not in request.files:
            return {
                "success": False,
                "message": "No file was given."
            }, 400

        file = request.files["file"]

        if file.filename == "" or not file:
            return {
                "success": False,
                "message": "No file was selected."
            }, 400

        extension = util.find_extension(file.filename)
        blacklist = current_app.config["EXTENSIONS_DISALLOWED"]

        if not extension or extension in blacklist:
            return {
                "success": False,
                "message": "Disallowed file extension."
            }, 400

        file_length = current_app.config["FILE_NAME_LENGTH"]

        name = f"{util.random_string(file_length)}.{extension}"
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)

        file.save(path)

        expiry_date = None

        if expires:
            expiry_date = datetime.now() + expires

        data = {
            "name": name,
            "parent_id": None,
            "size": os.stat(path).st_size,
            "origin": util.ip2int(request.remote_addr),
            "expires": expiry_date
        }

        if user is not None:
            data.update({
                "anonymous": False,
                "parent_id": user.id
            })

        entry = File(**data)

        db.session.add(entry)
        db.session.commit()

        return {
            "success": True,
            "name": entry.name,
            "user": entry.parent_id,
            "size": entry.size,
            "expires": entry.expires
        }, 200

    @api_key_required()
    def delete(self, user):
        file_name = request.json.get("file", None)

        if file_name is None:
            return {
                "success": False,
                "message": "No file was provided."
            }, 400

        safe_name = secure_filename(file_name)

        file = File.query.filter_by(name=safe_name, active=True).first()
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)

        if not file:
            return {
                "success": False,
                "message": "File does not exist."
            }, 400

        if file.parent_id != user.id:
            return {
                "success": False,
                "message": "You do not own that file."
            }, 403

        if not os.path.isfile(path):
            file.active = False
            db.session.commit()

            return {
                "success": False,
                "message": "File does not exist anymore."
            }, 410

        os.remove(path)
        file.active = False

        db.session.commit()

        return {}, 204

class InviteInteraction(Resource):
    @limiter.limit("10/minute")
    def get(self, code):
        invite = Invite.query.filter_by(code=code, active=True).first()

        if not invite:
            return {
                "success": False,
                "message": "Invite code does not exist."
            }, 404

        return {
            "success": True,
            "invite": {
                "created": invite.created.timestamp(),
                "creator": invite.parent.username,
                "code": invite.code,
                "used": invite.used
            }
        }

    @limiter.limit("10/minute")
    @api_key_required()
    def delete(self, user, code):
        invite = Invite.query.filter_by(code=code, active=True).first()

        if not invite:
            return {
                "success": False,
                "message": "Invite code does not exist."
            }, 404

        if invite.parent != user:
            return {
                "success": False,
                "message": "You do not own that invite."
            }, 403

        invite.active = False
        db.session.commit()

        return {}, 204

class Server(Resource):
    def get(self):
        return {
            "name": current_app.config["APPLICATION_NAME"],
            "open": current_app.config["INVITE_ONLY"],
            "captcha": current_app.config["RECAPTCHA_PUBLIC_KEY"],
            "urls": {
                "return": current_app.config["FILE_UPLOAD_BASE"],
                "api": current_app.config["API_URL_BASE"]
            }
        }

base_api.add_resource(FileInteraction, "/file")
base_api.add_resource(InviteInteraction, "/invite/<string:code>")
base_api.add_resource(Server, "/server")
