"""
Implement a web server.
"""
import json

from flask import Flask, request
from flask_api import status

from utils import init_azure_client, get_best_most_common_face


def create_app():
    """
    Create the flask web server.
    """
    app = Flask("smiley")

    @app.route("/", methods=["POST"])
    def main():
        """
        Get a group of photos. Get the most detected face, and find the best
        photo of that face. The best photo is defined to be the photo that
        has the biggest face-size to photo-size ratio.

        :return: A string which represents the face's metadata.
        :rtype: str
        """
        init_azure_client()
        uploaded_files = request.files.getlist("files")

        if len(uploaded_files) == 0:
            return "Error! Please send at least 1 picture",\
                   status.HTTP_400_BAD_REQUEST

        face = get_best_most_common_face(uploaded_files)
        return json.dumps(face.attrs)   # Return the face's metadata`

    return app
