from flask import request
from dateutil import parser


def parse_assignee():
    current_assignee = 'None'

    try:
        current_assignee = '@' + request.json['changes']['assignees']['current'][0]['username']
    except KeyError:
        pass
    except IndexError:
        pass

    return current_assignee


def parse_date():
    date = request.json['object_attributes']['updated_at']
    return parser.parse(date).strftime("%-d %b %H:%M")


def parse_action_into_status():
    action = request.json['object_attributes']['action']

    switcher = {
        "open": lambda: "👀 opened 👀",
        "close": lambda: "🪦 closed 🪦",
        "approved": lambda: "👍 approved 👍",
        "unapproved": lambda: "👎 unapproved 👎",
        "merge": lambda: "🚀 merged 🚀",
        "update": lambda: f"🧑‍💻 assigned 🧑‍💻"
    }
    func = switcher.get(action, lambda: 'Invalid')
    return func()


def parse_action_into_message():
    action = request.json['object_attributes']['action']

    switcher = {
        "open": lambda: "opened",
        "close": lambda: "closed",
        "approved": lambda: "approved",
        "unapproved": lambda: "unapproved",
        "merge": lambda: "merged",
        "update": lambda: f"assigned {parse_assignee()} to"
    }
    func = switcher.get(action, lambda: 'Invalid')
    return func()


def parse_action_into_assignee():
    action = request.json['object_attributes']['action']

    switcher = {
        "update": lambda: f"{parse_assignee()}"
    }
    func = switcher.get(action, lambda: 'None')
    return func()