import socket
import struct
import string
import secrets
import requests
from datetime import timedelta

from flask import request, current_app

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(value):
    return socket.inet_ntoa(struct.pack("!I", value))

def verify_recaptcha(token):
    if not current_app.config["RECAPTCHA_ENABLED"]:
        return True

    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": current_app.config.get("RECAPTCHA_PRIVATE_KEY"),
        "response": token,
        "remoteip": request.remote_addr
    }

    resp = requests.post(recaptcha_url, data=payload)
    data = resp.json()

    return data.get("success", None)

def find_extension(string):
    extension = string.rsplit(".", 1)[-1]

    if len(current_app.config["EXTENSIONS_ALLOWED"]) > 0:
        for _extension in current_app.config["EXTENSIONS_ALLOWED"]:
            if _extension == extension:
                return extension

        return None

    for _extension in current_app.config["EXTENSIONS_TWO"]:
        if string.endswith(_extension):
            return _extension

    if len(extension) > current_app.config["FILE_EXT_MAX_LENGTH"]:
        return extension[:current_app.config["FILE_EXT_MAX_LENGTH"]]

    return extension

def expiry_date(expiration):
    if expiration is None:
        return None
    elif expiration.lower() == "true":
        return timedelta(days=1)
    elif expiration.isdigit():
        return timedelta(hours=int(expiration))
    else:
        return None

def random_string(length):
    return "".join([
        secrets.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    ])
