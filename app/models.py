import app.parser as parser


class NewMessage:
    def __init__(self, request):
        self.request = request
        self.text = ''

    def get_assignees(self):
        assignees = []

        try:
            raw = self.request['assignees']
        except KeyError:
            return assignees

        for i in raw:
            assignees.append('@' + i['username'])

        return assignees

    def get_metadata(self):
         metadata = {'event_type': "mr_created", 'event_payload': {'mr_id': self.request['object_attributes']['id'], 'target_branch': self.request['object_attributes']['target_branch'],'assignees': self.get_assignees()}}
         return metadata

    def get_blocks(self):
        blocks = Blocks(self.request, '')
        return blocks.generate_new_message()


class UpdateMessage:
    def __init__(self, request):
        self.request = request
        self.text = ''

    def get_metadata(self):
         metadata = {'event_type': "mr_updated", 'event_payload': {'mr_id': self.request['object_attributes']['id']}}
         return metadata

    def get_blocks(self, thread):
        blocks = Blocks(self.request, self.get_update_type(thread))
        return blocks.generate_update_message()

    def get_update_type(self, thread):
        assignees = parser.parse_assignee()
        target_branch = self.request['object_attributes']['target_branch']
        source_branch = self.request['object_attributes']['source_branch']

        if thread.target_branch != target_branch:
            thread.set_target_branch(target_branch)
            thread.set_target_branch_text(f"`{source_branch}` → `{target_branch}`")
            return 'target_change'
        elif 'oldrev' in self.request['object_attributes']:
            return 'new_commit'
        elif thread.assignees != assignees:
            thread.set_assignees(assignees)
            thread.set_assignee_text(f"*Assignees:*\n{assignees}")
            return 'assignee_change'
        else:
            return ''

class Blocks:
    def __init__(self, request, update_type):
        self.username = request['user']['username']
        self.mr_url = request['object_attributes']['url']
        self.mr_iid = request['object_attributes']['iid']
        self.mr_title = request['object_attributes']['title']
        self.source = request['object_attributes']['source_branch']
        self.target = request['object_attributes']['target_branch']
        self.target_url = request['object_attributes']['target']['web_url']
        self.target_name = request['object_attributes']['target']['name']
        self.update_type = update_type

    def generate_new_message(self):
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
                        "text": f"*Last Update:*\n{parser.parse_date()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Assignees:*\nNone"
                    }
                ]
            }
        ]

    def generate_update_message(self):
        return [{

                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{self.username} has {parser.parse_action_into_message(self.update_type)} this merge request"
                }
        }]

class Thread:
    def __init__(self, thread):
        self.thread = thread
        self.target_branch = self.thread['metadata']['event_payload']['target_branch']
        self.assignees = self.thread['metadata']['event_payload']['assignees']
        self.assignee_text = self.thread['blocks'][3]['fields'][3]['text']
        self.target_branch_text = self.thread['blocks'][1]['text']['text']
        self.blocks = self.thread['blocks']
        self.ts = self.thread['ts']
        self.metadata  = self.thread['metadata']
        self.text = ''

        self.set_last_update()
        self.set_new_status()

    def set_target_branch(self, new_target):
        self.thread['metadata']['event_payload']['target_branch'] = new_target

    def set_assignees(self, new_assignees):
        self.thread['metadata']['event_payload']['assignees'] = new_assignees

    def set_assignee_text(self, new_assignee_text):
        self.blocks[3]['fields'][3]['text'] = new_assignee_text

    def set_target_branch_text(self, new_target_branch_text):
        self.blocks[1]['text']['text'] = new_target_branch_text

    def set_last_update(self):
        self.blocks[3]['fields'][2]['text'] = f"*Last Update:*\n{parser.parse_date()}"

    def set_new_status(self):
        self.blocks[3]['fields'][1]['text'] = f"*Status:*\n{parser.parse_action_into_status()}"