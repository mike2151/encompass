from channels.generic.websocket import AsyncWebsocketConsumer
import json
from interview_q_instance.models import InterviewQuestionInstance

class InterviewConsumer(AsyncWebsocketConsumer):
    room_name_to_num_users = {}
    async def connect(self):
        self.live_interview_id = self.scope['url_route']['kwargs']['live_interview_id']
        self.instance_id = self.scope['url_route']['kwargs']['instance_id']
        self.interview_session_name = 'interview_' + str(self.instance_id) + "_" + str(self.live_interview_id)

        connecting_user = self.scope["user"]
        if not connecting_user or not connecting_user.is_authenticated:
            self.close()

        connecting_user_email = connecting_user.email
        question_instance = InterviewQuestionInstance.objects.get(pk=self.instance_id)
        if connecting_user_email != question_instance.interviewee_email and connecting_user_email != question_instance.creator_email:
            self.close()

        await self.channel_layer.group_add(
            self.interview_session_name,
            self.channel_name
        )

        if self.interview_session_name not in InterviewConsumer.room_name_to_num_users:
            InterviewConsumer.room_name_to_num_users[self.interview_session_name] = 1
        else:
            InterviewConsumer.room_name_to_num_users[self.interview_session_name] += 1
        await self.accept()

    async def disconnect(self, close_code):
        if self.interview_session_name in InterviewConsumer.room_name_to_num_users:
            InterviewConsumer.room_name_to_num_users[self.interview_session_name] -= 1
            if InterviewConsumer.room_name_to_num_users[self.interview_session_name] == 0:
                # empty so remove 
                del InterviewConsumer.room_name_to_num_users[self.interview_session_name]
        await self.channel_layer.group_discard(
            self.interview_session_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if (InterviewConsumer.room_name_to_num_users[self.interview_session_name] > 1):
            update_data_json = json.loads(text_data)
            file_to_update = update_data_json['file']
            new_content = update_data_json['content']

            is_test_body = update_data_json['is_test_body']
            is_test_results = update_data_json['is_test_results']

            sending_user = self.scope["user"]

            
            await self.channel_layer.group_send(
                self.interview_session_name,
                {
                    'type': 'update_file_content',
                    'content': new_content,
                    'file': file_to_update,
                    'sending_user': sending_user.username,
                    'is_test_body': is_test_body,
                    'is_test_results': is_test_results
                }
            )

    async def update_file_content(self, event):
        file_to_update = event['file']
        new_content = event['content']
        is_test_body = event['is_test_body']
        is_test_results = event['is_test_results']
        sending_user = event['sending_user']

        await self.send(text_data=json.dumps({
            'content': new_content,
            'file': file_to_update,
            'sending_user': sending_user,
            'is_test_body': is_test_body,
            'is_test_results': is_test_results
        }))