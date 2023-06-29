from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from users.models import User
from blogs.models import Blog
from livechat.models import BlogRoom
from livechat.serializers import BlogRoomCreateSerializer, BlogRoomSerializer, BlogRoomActiceSerializer


class BlogRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, blog_name):
        """블로그 방 정보 가져오기"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        room = get_object_or_404(BlogRoom, room_id=blog[0].id)
        serializer = BlogRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, blog_name):
        """블로그 방 생성"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        serializer = BlogRoomCreateSerializer(data=request.data)
        
        if not BlogRoom.objects.filter(room_id=blog[0].id).exists():
            if serializer.is_valid():
                serializer.save(room_id=blog[0].id)
                return Response({"message": "Live Room 생성 완료"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("이미 개설된 방이 있습니다", status=status.HTTP_400_BAD_REQUEST)


class RoomActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, blog_name):
        """live 활성화 기능"""
        
        blog = Blog.objects.filter(blog_name=blog_name)
        room = get_object_or_404(BlogRoom, room_id=blog[0].id)

        if not room.is_active:
            BlogRoom.objects.filter(room_id=blog[0].id).update(is_active=True)
            return Response("Live 시작!", status=status.HTTP_200_OK)
        else:
            BlogRoom.objects.filter(room_id=blog[0].id).update(is_active=False)
            return Response("Live 종료!", status=status.HTTP_200_OK)
            
