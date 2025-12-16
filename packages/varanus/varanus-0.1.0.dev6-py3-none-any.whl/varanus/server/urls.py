from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import api, dashboard, site

urlpatterns = [
    path("", dashboard.Dashboard.as_view(), name="dashboard"),
    path(
        "auth/",
        include(
            [
                path("passkey/", include("passkeys.urls")),
                path("", include("django.contrib.auth.urls")),
            ]
        ),
    ),
    path(
        "site/<slug>/",
        include(
            [
                path("", site.Overview.as_view(), name="site-overview"),
                path("errors/", site.Errors.as_view(), name="site-errors"),
                path("logs/", site.Logs.as_view(), name="site-logs"),
                path("requests/", site.Requests.as_view(), name="site-requests"),
                path("queries/", site.Queries.as_view(), name="site-queries"),
                path("metrics/", site.Metrics.as_view(), name="site-metrics"),
                path(
                    "event/<event_id>/<model>/<pk>/",
                    site.Details.as_view(),
                    name="event-details",
                ),
                path(
                    "node/",
                    include(
                        [
                            path(
                                "name/<name>/",
                                site.NodeEnvironments.as_view(),
                                name="node-environments",
                            ),
                            path(
                                "environment/<environment>/",
                                site.EnvironmentNodes.as_view(),
                                name="environment-nodes",
                            ),
                            path(
                                "<pk>/",
                                include(
                                    [
                                        path(
                                            "packages/",
                                            site.NodePackages.as_view(),
                                            name="node-packages",
                                        ),
                                        path(
                                            "settings/",
                                            site.NodeSettings.as_view(),
                                            name="node-settings",
                                        ),
                                        path(
                                            "env/",
                                            site.NodeEnv.as_view(),
                                            name="node-env",
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path(
        "api/",
        include(
            [
                path("ping/", api.NodePingView.as_view(), name="ping"),
                path("ingest/", api.IngestView.as_view(), name="ingest"),
            ]
        ),
    ),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:

    def error_view(request):
        raise ValueError("Kaboom!")

    urlpatterns += [
        path("_error/", error_view),
    ]
