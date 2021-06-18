from flask import Blueprint, request, current_app, url_for
from flask_restful import Api, Resource

tool = Blueprint("tool", __name__, url_prefix="/tool")
tool_api = Api(tool)

class ShareX(Resource):
    def get(self):
        anonymous = request.args.get("anonymous", False)
        apikey = request.args.get("apikey", None)

        if len(str(apikey)) != 32:
            return {
                "success": False,
                "message": "Invalid API key was provided."
            }, 400

        if not apikey:
            anonymous = True

        name = current_app.config["APPLICATION_NAME"]

        if anonymous:
            name += " (anonymous)"

        data = {
            "Version": "13.4.0",
            "Name": name,
            "DestinationType": "ImageUploader, TextUploader, FileUploader",
            "RequestMethod": "PUT",
            "RequestURL": url_for("base.fileinteraction", _external=True),
            "URL": current_app.config["FILE_UPLOAD_BASE"] + "/$json:name$",
            "Body": "MultipartFormData",
            "FileFormName": "file"
        }

        if not anonymous:
            data["Arguments"] = {"apikey": apikey}

        return data

tool_api.add_resource(ShareX, "/sharex")
