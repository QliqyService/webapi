import factory

from app.db.models.comments import Comment


class CommentFactory(factory.Factory):
    class Meta:
        model = Comment

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.Faker("random_int", min=100000000, max=999999999999)

    title = factory.Sequence(lambda n: f"Seed Comment #{n}")
    description = factory.Faker("text", max_nb_chars=200)

    user_form_id = None
