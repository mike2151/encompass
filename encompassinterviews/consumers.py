from channels.generic.websocket import AsyncWebsocketConsumer
import json

class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.interview = self.scope['url_route']['kwargs']['live_interview_id']
        self.interview_session_name = 'interview_%s' % self.interview

        await self.channel_layer.group_add(
            self.interview_session_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.interview_session_name,
            self.channel_name
        )

    async def receive(self, text_data):
        update_data_json = json.loads(text_data)
        file_to_update = update_data_json['file']
        new_content = update_data_json['content']
        sending_user = self.scope["user"]

        
        await self.channel_layer.group_send(
            self.interview_session_name,
            {
                'type': 'update_file_content',
                'content': new_content,
                'file': file_to_update,
                'sending_user': sending_user.username
            }
        )

    async def update_file_content(self, event):
        file_to_update = event['file']
        new_content = event['content']
        sending_user = event['sending_user']

        await self.send(text_data=json.dumps({
            'content': new_content,
            'file': file_to_update,
            'sending_user': sending_user
        }))