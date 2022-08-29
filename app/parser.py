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
        "open": "👀 opened 👀",
        "close": "🪦 closed 🪦",
        "approved": "👍 approved 👍",
        "unapproved": "👎 unapproved 👎",
        "merge": "🚀 merged 🚀",
        "update": "🧑‍💻 assigned 🧑‍💻"
    }
    result = switcher.get(action, 'Invalid')
    return result


def parse_action_into_message():
    action = request.json['object_attributes']['action']

    switcher = {
        "open": "opened",
        "close": "closed",
        "approved": "approved",
        "unapproved": "unapproved",
        "merge": "merged",
        "update": f"assigned {parse_assignee()} to"
    }
    result = switcher.get(action, 'Invalid')
    return result


def parse_action_into_assignee():
    action = request.json['object_attributes']['action']

    switcher = {
        "update": f"{parse_assignee()}"
    }
    result = switcher.get(action, 'None')
    return result
