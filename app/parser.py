from flask import request
from dateutil import parser

mr_attributes = request.json['object_attributes']


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
    date = mr_attributes['updated_at']
    return parser.parse(date).strftime("%-d %b %H:%M")


def parse_action_into_status():
    action = mr_attributes['action']

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


def parse_action_into_message(update_type):
    action = mr_attributes['action']

    switcher = {
        "open": "opened",
        "close": "closed",
        "approved": "approved",
        "unapproved": "unapproved",
        "merge": "merged",
        "update": f"{get_update_message(update_type)}"
    }
    result = switcher.get(action, 'Invalid')
    return result


def parse_action_into_assignee():
    action = mr_attributes['action']

    switcher = {
        "update": f"{parse_assignee()}"
    }
    result = switcher.get(action, 'None')
    return result


def get_assignees():
    assignees = []

    try:
        raw = request.json['assignees']
    except KeyError:
        return assignees

    for i in raw:
        assignees.append('@' + i['username'])

    return assignees


def get_update_message(update_type):
    switcher = {
        "target_change": "has changed the target branch of",
        "new_commit": f"added a new commit <{mr_attributes['last_commit']['url']}|{mr_attributes['last_commit']['id'][:8]}> to",
        "assignee_change": f"assigned {','.join(get_assignees())} to"
    }

    result = switcher.get(update_type, 'None')
    return result
