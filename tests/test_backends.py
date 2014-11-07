from unittest import TestCase

from incuna_auth.backends import CustomUserModelBackend

from .factories import UserFactory


class TestCustomUserModelBackend(TestCase):
    backend = CustomUserModelBackend()

    def test_nonexistent_user(self):
        result = self.backend.authenticate('fake-user', 'fake-password')
        self.assertEqual(result, None)

    def test_user_by_username(self):
        username = 'user'
        password = 'pass'
        user = UserFactory.create(username=username)
        user.set_password(password)
        user.save()
        result = self.backend.authenticate(username, password)
        self.assertEqual(result, user)

    def test_user_by_email(self):
        email = 'user2@name.com'
        password = 'pass'
        user = UserFactory.create(email=email)
        user.set_password(password)
        user.save()
        result = self.backend.authenticate(email, password)
        self.assertEqual(result, user)

    def test_user_wrong_password(self):
        username = 'user3'
        password = 'pass'
        user = UserFactory.create(username=username)
        user.set_password(password)
        user.save()
        result = self.backend.authenticate(username, 'wrong_password')
        self.assertEqual(result, None)
