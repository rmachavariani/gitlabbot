from app import slack_app, channel
from app.models import *
from app.parser import get_thread_start

def send_new_msg(request):
    message = NewMessage(request)
    return slack_app.client.chat_postMessage(channel=channel,
                                             blocks=message.get_blocks(),
                                             metadata=message.get_metadata(),
                                             unfurl_links=False,
                                             text=message.text)

def send_upd_msg(request):
    history_thread = parser.get_thread_start()
    thread = Thread(history_thread)
    message = UpdateMessage(request)
    slack_app.client.chat_postMessage(channel=channel,
                                        blocks=message.get_blocks(thread),
                                        metadata=message.get_metadata(),
                                        thread_ts=thread.ts,
                                        unfurl_links=False,
                                        text=message.text)

    slack_app.client.chat_update(channel=channel,
                                       ts=thread.ts,
                                       blocks=thread.blocks,
                                       metadata=thread.metadata,
                                       text=thread.text)

# def send_reminder_msg():

