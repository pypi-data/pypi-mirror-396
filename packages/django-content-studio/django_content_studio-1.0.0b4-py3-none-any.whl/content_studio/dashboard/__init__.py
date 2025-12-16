from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from content_studio.settings import cs_settings


class Dashboard:
    """
    The Dashboard class is used to define the structure of the dashboard
    in Django Content Studio.
    """

    widgets = None

    def __init__(self, **kwargs):
        self.widgets = kwargs.get("widgets", [])

    def set_up_router(self):
        from content_studio.router import content_studio_router

        content_studio_router.register(
            "api/dashboard",
            DashboardViewSet,
            basename="content_studio_dashboard",
        )

    def serialize(self):
        return {
            "widgets": [
                {"name": w.__class__.__name__, "col_span": getattr(w, "col_span", 1)}
                for w in self.widgets
            ]
        }


class DashboardViewSet(ViewSet):
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def __init__(self, *args, **kwargs):
        super(ViewSet, self).__init__()
        admin_site = cs_settings.ADMIN_SITE

        self.dashboard = admin_site.dashboard
        self.authentication_classes = [
            admin_site.token_backend.active_backend.authentication_class
        ]

    @action(detail=False, url_path="(?P<name>[^/.]+)")
    def get(self, request, name=None):
        widget = None

        for w in self.dashboard.widgets:
            if name == w.__class__.__name__.lower():
                widget = w

        if not widget:
            raise NotFound()

        return Response(data=widget.get_data(request))
