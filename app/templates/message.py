from flask import request
from .parser import *
from dataclasses import dataclass


@dataclass
class Message:

    def __init__(self):
        self.username = request.json['user']['username']
        self.mr_url = request.json['object_attributes']['url']
        self.mr_iid = request.json['object_attributes']['iid']
        self.mr_title = request.json['object_attributes']['title']
        self.source = request.json['object_attributes']['source_branch']
        self.target = request.json['object_attributes']['target_branch']
        self.target_url = request.json['object_attributes']['target']['web_url']
        self.target_name = request.json['object_attributes']['target']['name']

    @property
    def __open__(self):
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{self.username} has created a new merge request: <{self.mr_url}|{self.mr_iid}: {self.mr_title}>"
                            f"\n \n`{self.source}` → `{self.target}`"
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
                        "text": f"*Assignee:*\nNone"
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
                    "text": f"@{self.username} has {parse_action_into_message()} this merge request"
                }

        }]
