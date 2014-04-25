from unittest import TestCase

from incuna_auth.backends import CustomUserModelBackend


class TestCustomUserModelBackend(TestCase):
    backend = CustomUserModelBackend()

    def test_nonexistent_user(self):
        result = self.backend.authenticate('fake-user', 'fake-password')
        self.assertEqual(result, None)
