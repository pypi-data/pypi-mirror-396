from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet

from .filters import LookupFilter
from .settings import cs_settings


class BaseModelViewSet(ModelViewSet):
    lookup_field = "id"
    is_singleton = False
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, LookupFilter]

    def __init__(self, *args, **kwargs):
        super(BaseModelViewSet, self).__init__()
        admin_site = cs_settings.ADMIN_SITE

        self.authentication_classes = [
            admin_site.token_backend.active_backend.authentication_class
        ]

    def list(self, request, *args, **kwargs):
        """
        We overwrite the list method to support singletons. If a singleton
        doesn't exist this will raise a NotFound exception.
        """
        if self.is_singleton:
            return super().retrieve(request, *args, **kwargs)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()

        if hasattr(instance, cs_settings.CREATED_BY_ATTR):
            setattr(instance, cs_settings.CREATED_BY_ATTR, self.request.user)
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=ADDITION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_update(self, serializer):
        instance = serializer.save()

        if hasattr(instance, cs_settings.EDITED_BY_ATTR):
            setattr(instance, cs_settings.EDITED_BY_ATTR, self.request.user)
            instance.save()

        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=CHANGE,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

    def perform_destroy(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        LogEntry.objects.create(
            user=self.request.user,
            action_flag=DELETION,
            content_type=content_type,
            object_id=instance.id,
            object_repr=str(instance)[:200],
            change_message="",
        )

        instance.delete()

    def get_object(self):
        """
        We overwrite this method to add support for singletons.
        If a singleton doesn't exist it will raise a NotFound exception.
        """
        if self.is_singleton:
            singleton = self.get_queryset().first()

            if singleton:
                return singleton
            else:
                raise NotFound()

        return super().get_object()
