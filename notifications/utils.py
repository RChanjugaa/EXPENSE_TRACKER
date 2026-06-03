from django.contrib.contenttypes.models import ContentType

from .models import Notification


def create_notification(user, message, notification_type, related_object=None):
    data = {
        'user': user,
        'message': message,
        'type': notification_type,
    }
    if related_object is not None:
        data['content_type'] = ContentType.objects.get_for_model(related_object)
        data['object_id'] = related_object.pk
    return Notification.objects.create(**data)
