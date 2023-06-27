from django.urls import path
from livechat import views

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
    path("<str:room_name>/", views.RoomView.as_view(), name="room"),
    
]