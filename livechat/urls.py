from django.urls import path
from livechat import views

urlpatterns = [
    path("active/<str:blog_name>/", views.RoomActiveView.as_view(), name="active_room"),
    path("<str:blog_name>/", views.BlogRoomView.as_view(), name="blog_room"),
    
]