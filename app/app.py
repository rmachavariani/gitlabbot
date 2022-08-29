from slack_bolt import App
from flask import Flask
from slack_bolt.adapter.flask import SlackRequestHandler
from os import environ
from app.message import Message
from app.parser import *
from dotenv import load_dotenv

load_dotenv()

slack_app = App(
    token=environ.get("SLACK_BOT_TOKEN"),
    signing_secret=environ.get("SLACK_SIGNING_SECRET")
)

flask_app = Flask(__name__)
flask_app.url_map.strict_slashes = False
handler = SlackRequestHandler(slack_app)


class MagentologyBot:
    def __init__(self):
        self.channel = environ.get('CHANNEL')
        self.client = slack_app.client
        self.mr_id = request.json['object_attributes']['id']
        self.thread_start = {}
        self.unfurl_links = False
        self.metadata = {}
        self.message = []
        self.text = ''

    def send_message(self):
        self.set_metadata()
        if self.metadata['event_type'] == 'mr_updated':
            self.set_message('__update__')
            self.set_thread_start()
            self.send_thread_start_update()
            return self.client.chat_postMessage(channel=self.channel,
                                                blocks=self.message,
                                                metadata=self.metadata,
                                                thread_ts=self.thread_start['ts'],
                                                unfurl_links=self.unfurl_links,
                                                text=self.text)
        elif self.metadata['event_type'] == 'mr_created':
            self.set_message('__open__')
            return self.client.chat_postMessage(channel=self.channel,
                                                blocks=self.message,
                                                metadata=self.metadata,
                                                unfurl_links=self.unfurl_links,
                                                text=self.text)

    def send_thread_start_update(self):
        custom_blocks = get_blocks_to_change(self.thread_start)
        return self.client.chat_update(channel=self.channel,
                                       ts=self.thread_start['ts'],
                                       blocks=custom_blocks,
                                       text='')

    def get_message_history(self):
        history = self.client.conversations_history(channel=self.channel,
                                                    limit=100,
                                                    include_all_metadata=True)
        return history['messages']

    def set_message(self, message_type):
        message = Message()
        self.message = getattr(message, message_type)

    def set_thread_start(self):
        for message in self.get_message_history():
            try:
                if message['metadata']['event_type'] == 'mr_created' and message['metadata']['event_payload'][
                    'mr_id'] == self.mr_id:
                    self.thread_start = message
            except KeyError:
                pass
        return 'Thread start not found'

    def set_metadata(self):
        if request.json['object_attributes']['action'] == 'open':
            metadata = {'event_type': "mr_created", 'event_payload': {'mr_id': self.mr_id}}
        else:
            metadata = {'event_type': "mr_updated", 'event_payload': {'mr_id': self.mr_id}}

        self.metadata = metadata


def get_blocks_to_change(target_message):
    blocks = target_message['blocks']
    blocks[2]['fields'][2]['text'] = f"*Last Update:*\n{parse_date()}"
    if request.json['object_attributes']['action'] == 'update':
        blocks[2]['fields'][3]['text'] = f"*Assignee:*\n{parse_action_into_assignee()}"
        if parse_action_into_assignee() != "None":
            blocks[2]['fields'][1]['text'] = f"*Status:*\n{parse_action_into_status()}"
    else:
        blocks[2]['fields'][1]['text'] = f"*Status:*\n{parse_action_into_status()}"

    return blocks


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/gitlab", methods=["POST"])
def send_message():
    bot = MagentologyBot()
    return bot.send_message()

@flask_app.route("/api/health")
def health():
    return "OK"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", debug=True)