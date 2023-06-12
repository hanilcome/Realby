from rest_framework.test import APITestCase, APIClient
from users.models import User


# class LoginTestCase(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user_data = {
#             "email": "test@test.com",
#             "username": "test",
#             "age": "20",
#             "password": "test",
#         }
#         cls.user = User.objects.create_user("test@test.com", "test")

# def setUp(self):
# self.access_token = self.client.post(reverse(""))
