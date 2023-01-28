from flask import Flask

def create_app():
    app = Flask(__name__)

    from application.views import view_picture
    app.register_blueprint(view_picture.bp)

    return app