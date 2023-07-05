import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import BlogMessage, User


class LiveChatConsumer(WebsocketConsumer):
    
    # def fetch_messages(self, data):
        
    #     messages = UserMessage.last_30_messages(self)
        
    #     chat = {
    #         'command': 'messages',
    #         'messages': self.messages_to_json(messages)
    #     }
    #     return self.send_message(chat)
        
    def blog_new_message(self, data):
        blog_room = self.room_name
        username = data['username']
        user = User.objects.filter(username=username)[0].id
        
        message = BlogMessage.objects.create(user_id=user, chat=data['message'], room=blog_room)
        chat = {
            'command': 'blog_new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(chat)
    
    # def user_new_message(self, data):
    #     blog_room_id = int(self.room_name)
    #     username = data['username']
    #     user = User.objects.filter(username=username)[0].id
        
    #     message = UserMessage.objects.create(user_id=user, chat=data['message'], blog_room_id=blog_room_id)
    #     chat = {
    #         'command': 'user_new_message',
    #         'message': self.message_to_json(message)
    #     }
    #     return self.send_chat_message(chat)
    
    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result
    
    def message_to_json(self, message):
        return {
            'user': message.user.username,
            'chat': message.chat,
            'created_at': str(message.created_at)
        }
    
    commands = {
        # 'fetch_messages' : fetch_messages,
        'blog_new_message' : blog_new_message,
        # 'user_new_message' : user_new_message
    }
    
    def connect(self):
        # room_name 파라미터를 chat/routing.py URl 에서 얻고, 열러있는 websocket에 접속
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        # Join room group / 그룹에 참여
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # websocket 연결을 수락 / connect() 메서드 내에서 accept()를 호출하지 않으면 연결이 거부되고 닫힌다.
        self.accept()

    # websocket 연결 해제
    def disconnect(self, close_code):
        # Leave room group / 그룹에서 탈퇴
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
        
        
    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))
    
    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))