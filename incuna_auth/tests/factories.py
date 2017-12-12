import factory
from django.contrib.auth.models import User


class UserFactory(factory.DjangoModelFactory):
    is_active = True
    email = factory.Sequence('user-{}@example.com'.format)
    username = factory.Sequence('user-{}'.format)
    password = factory.PostGenerationMethodCall('set_password', None)

    class Meta:
        model = User
