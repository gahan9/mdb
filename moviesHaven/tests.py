from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.postgres import fields
from django.test import TestCase

from .models import *
from .utils import *
from faker import Faker
faker = Faker()


class RawDataTests(TestCase):
    def setUp(self):
        self.username = faker.user_name()
        self.first_name, self.last_name = faker.name().split()
        self.email = faker.email()
        self.password = "password@123"
        print("SetUP completed")
        User.objects.create(username=self.username, email=self.email, password=make_password(self.password))

    # def test_create_user(self):
    #     return True
    #     self.username = faker.user_name()
    #     self.first_name, self.last_name = faker.name().split()
    #     self.email = faker.email()
    #     self.password = "password@123"
    #     print("SetUP completed")
    #
    #     _user = User.objects.create(username=self.username, email=self.email, password=self.password)
    #     self.assertEqual(User.objects.count(), 1)
    #     print("Total User count match")
    #     # self.assertEqual(User.objects.last(), _user)
    #     _user.first_name = self.first_name
    #     _user.save()
    #     _user.last_name = self.last_name
    #     self.assertTrue(User.objects.last().first_name == self.first_name)
    #     # self.assertEqual(User.objects.last().first_name, self.first_name)
    #     # self.assertEqual(User.objects.last().last_name, self.last_name)

    def test_login(self):
        self.credentials = {
            'username': self.username,
            'password': self.password}
        self.client.login(**self.credentials)
        print("Credentials---> ", self.credentials)
        response = self.client.get(reverse_lazy('index'))
        # response = self.client.post(reverse_lazy('login'), self.credentials, follow=True)
        # print(dir(response))
        print(response.context['user'])
