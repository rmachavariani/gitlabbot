from flask import current_app as app
from flask import request, make_response
import app.handlers as handlers


@app.route("/mr/notify", methods=["POST"])
def send_message():
    data = request.json
    draft_substr = ["WIP", "Draft"]

    if data['object_attributes']['action'] == 'open' and not any(substr in data['object_attributes']['title'] for substr in draft_substr):
         handlers.send_new_msg(data)
    else:
         handlers.send_upd_msg(data)

    return make_response("", 200)
