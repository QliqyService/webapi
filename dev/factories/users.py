import factory

from app.db.models.users import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"seed.user{n}@example.com")
    phone = factory.Faker("random_int", min=100000000, max=999999999999)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    is_active = True
    is_superuser = False
    is_verified = True
