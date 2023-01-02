from app.parser import *
from dataclasses import dataclass


@dataclass
class Message:

    def __init__(self, mr_object, update_type):
        self.username = request.json['user']['username']
        self.mr_url = mr_object['url']
        self.mr_iid = mr_object['iid']
        self.mr_title = mr_object['title']
        self.source = mr_object['source_branch']
        self.target = mr_object['target_branch']
        self.target_url = mr_object['target']['web_url']
        self.target_name = mr_object['target']['name']
        self.update_type = update_type

    @property
    def __open__(self):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{self.username} has created a new merge request: <{self.mr_url}|!{self.mr_iid}>: {self.mr_title}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"`{self.source}` → `{self.target}`"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:*\n<{self.target_url}|{self.target_name}>"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Status:*\n:weewoo: new :weewoo:"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Last Update:*\n{parse_date()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Assignees:*\nNone"
                    }
                ]
            }
        ]

    @property
    def __update__(self):
        return [{

                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{self.username} has {parse_action_into_message(self.update_type)} this merge request"
                }
        }]
