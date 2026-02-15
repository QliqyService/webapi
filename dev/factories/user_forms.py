import factory

from app.db.models.user_forms import UserForm


class UserFormFactory(factory.Factory):
    class Meta:
        model = UserForm

    title = factory.Sequence(lambda n: f"Seed Form #{n}")
    description = factory.Faker("sentence", nb_words=8)
    is_enabled = True
    qrcode = None

    user_id = None
