from django.apps import AppConfig
from django.contrib import admin

from . import VERSION
from .paginators import ContentPagination
from .settings import cs_settings
from .utils import is_runserver


class DjangoContentStudioConfig(AppConfig):
    name = "content_studio"
    label = "content_studio"
    initialized = False

    def ready(self):
        from .utils import log

        if is_runserver() and not self.initialized:
            self.initialized = True

            log("\n")
            log("----------------------------------------")
            log("Django Content Studio")
            log(f"Version {VERSION}")
            log("----------------------------------------")
            log(":rocket:", "Starting Django Content Studio")
            log(":mag:", "Discovering admin models...")
            registered_models = len(admin.site._registry)
            log(
                ":white_check_mark:",
                f"[green]Found {registered_models} admin models[/green]",
            )
            # Set up admin site routes
            admin_site = cs_settings.ADMIN_SITE
            admin_site.setup()

            # Set up content CRUD APIs
            self._create_crud_api()

            log("\n")

    def _create_crud_api(self):
        from .utils import log

        for model, admin_model in admin.site._registry.items():
            self._create_view_set(model, admin_model)

            for inline in admin_model.inlines:
                self._create_view_set(
                    parent=model, model=inline.model, admin_model=inline
                )

        log(
            ":white_check_mark:",
            f"[green]Created CRUD API[/green]",
        )

    def _create_view_set(self, model, admin_model, parent=None):
        from .viewsets import BaseModelViewSet
        from .router import content_studio_router
        from .serializers import ContentSerializer

        class Pagination(ContentPagination):
            page_size = getattr(admin_model, "list_per_page", 10)

        class ViewSet(BaseModelViewSet):
            _model = model
            _admin_model = admin_model
            is_singleton = getattr(admin_model, "is_singleton", False)
            pagination_class = Pagination
            queryset = _model.objects.all()
            search_fields = list(getattr(_admin_model, "search_fields", []))

            def get_serializer_class(self):
                # For list views we include the specified list_display fields.
                if self.action == "list" and not self.is_singleton:
                    available_fields = [
                        "id",
                        "__str__",
                    ] + list(getattr(self._admin_model, "list_display", []))
                # In all other cases we include all fields.
                else:
                    available_fields = "__all__"

                class Serializer(ContentSerializer):

                    class Meta:
                        model = self._model
                        fields = available_fields

                return Serializer

        if parent:
            prefix = f"api/inlines/{parent._meta.label_lower}/{model._meta.label_lower}"
            basename = f"content_studio_api-{parent._meta.label_lower}-{model._meta.label_lower}"
        else:
            prefix = f"api/content/{model._meta.label_lower}"
            basename = f"content_studio_api-{model._meta.label_lower}"

        content_studio_router.register(prefix, ViewSet, basename)
