import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
    GITLAB_GROUP = os.environ.get("GITLAB_GROUP")
    CHANNEL = os.environ.get("CHANNEL")
