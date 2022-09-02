from slack_bolt import App
from flask import Flask, request
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
    def __init__(self, mr_request):
        self.channel = environ.get('CHANNEL')
        self.client = slack_app.client
        self.mr_attributes = mr_request['object_attributes']
        self.assignees = get_assignees()
        self.thread_start = {}
        self.unfurl_links = False
        self.metadata = {}
        self.message = []
        self.text = ''
        self.update_type = ''

    def send_message(self):
        self.set_metadata()

        if self.metadata['event_type'] == 'mr_updated':
            self.set_thread_start()
            if self.mr_attributes['action'] == 'update':
                self.which_update_action()
                if len(self.update_type) == 0:
                    return 'Do not send anything'

            self.send_thread_start_update()
            self.set_message('__update__')
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
        custom_blocks = get_blocks_to_change(self.thread_start, self.update_type)
        return self.client.chat_update(channel=self.channel,
                                       ts=self.thread_start['ts'],
                                       blocks=custom_blocks,
                                       metadata=self.thread_start['metadata'],
                                       text=self.text)

    def get_message_history(self):
        history = self.client.conversations_history(channel=self.channel,
                                                    limit=100,
                                                    include_all_metadata=True)
        return history['messages']

    def set_message(self, message_type):
        message = Message(self.mr_attributes, self.update_type)
        self.message = getattr(message, message_type)

    def set_thread_start(self):
        for message in self.get_message_history():
            try:
                if message['metadata']['event_type'] == 'mr_created' and message['metadata']['event_payload'][
                    'mr_id'] == self.mr_attributes['id']:
                    self.thread_start = message
            except KeyError:
                pass
        return 'Thread start not found'

    def set_metadata(self):
        if self.mr_attributes['action'] == 'open':
            metadata = {'event_type': "mr_created", 'event_payload': {'mr_id': self.mr_attributes['id'],
                                                                      'target_branch': self.mr_attributes[
                                                                          'target_branch'],
                                                                      'assignees': self.assignees}}
        else:
            metadata = {'event_type': "mr_updated", 'event_payload': {'mr_id': self.mr_attributes['id']}}

        self.metadata = metadata

    def which_update_action(self):
        if self.thread_start['metadata']['event_payload']['target_branch'] != self.mr_attributes['target_branch']:
            self.update_type = 'target_change'
            self.thread_start['metadata']['event_payload']['target_branch'] = self.mr_attributes['target_branch']
            self.thread_start['blocks'][1]['text'][
                'text'] = f"`{self.mr_attributes['source_branch']}` → `{self.mr_attributes['target_branch']}`"
        elif 'oldrev' in request.json['object_attributes']:
            self.update_type = 'new_commit'
        elif self.thread_start['metadata']['event_payload']['assignees'] != self.assignees:
            self.update_type = 'assignee_change'
            self.thread_start['metadata']['event_payload']['assignees'] = self.assignees
            self.thread_start['blocks'][3]['fields'][3]['text'] = f"*Assignees:*\n{','.join(self.assignees)}"


def get_blocks_to_change(target_message, update_type):
    blocks = target_message['blocks']
    blocks[3]['fields'][2]['text'] = f"*Last Update:*\n{parse_date()}"
    if request.json['object_attributes']['action'] != 'update':
        blocks[3]['fields'][1]['text'] = f"*Status:*\n{parse_action_into_status()}"

    return blocks


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/gitlab", methods=["POST"])
def send_message():
    bot = MagentologyBot(request.json)
    return bot.send_message()


@flask_app.route("/api/health")
def health():
    return "OK"

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", debug=True)