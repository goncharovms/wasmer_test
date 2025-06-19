from django.db.models import Model


class BaseRepository:
    model_class: Model = NotImplemented

    @classmethod
    async def get_object(cls, id):
        return await cls.model_class.objects.aget(pk=id)
