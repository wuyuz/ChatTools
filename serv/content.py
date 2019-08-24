
import os

from flask import Blueprint, jsonify, send_file
from settings import REG_PATH

content = Blueprint("content", __name__)


@content.route("/get_img/<filename>", methods=['GET'])
def cover_list(filename):

    file_path = os.path.join(REG_PATH, filename)
    # print(file_path)
    return send_file(file_path)
