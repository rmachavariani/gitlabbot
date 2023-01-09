from flask import Flask
from slack_bolt import App

from config import Config

slack_app = App(
    token=Config.SLACK_BOT_TOKEN,
    signing_secret=Config.SLACK_SIGNING_SECRET
)
channel = Config.CHANNEL


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False


    with app.app_context():
        from . import routes
        return app