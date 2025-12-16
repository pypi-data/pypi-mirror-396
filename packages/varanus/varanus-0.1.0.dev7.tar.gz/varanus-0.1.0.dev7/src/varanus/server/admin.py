from django import forms
from django.conf import settings
from django.contrib import admin

from .models import (
    Context,
    ContextIntegration,
    Error,
    Log,
    Metric,
    Node,
    NodePackage,
    NodeUpdate,
    Query,
    Request,
    Site,
    SiteIntegration,
    SiteKey,
    SiteMember,
)


class SaveDefaultModelForm(forms.ModelForm):
    def has_changed(self):
        return self.instance._state.adding or super().has_changed()


class SiteMemberInline(admin.TabularInline):
    model = SiteMember
    extra = 0


class SiteKeyInline(admin.TabularInline):
    model = SiteKey
    form = SaveDefaultModelForm
    extra = 0


class SiteIntegrationInline(admin.StackedInline):
    model = SiteIntegration
    extra = 0


class SiteAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "schema_name"]
    inlines = [SiteMemberInline, SiteKeyInline, SiteIntegrationInline]
    prepopulated_fields = {"slug": ["name"], "schema_name": ["name"]}
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "slug",
                    "schema_name",
                    "module_filter",
                ]
            },
        ),
        (
            "Tabs",
            {
                "fields": [
                    "show_requests",
                    "show_errors",
                    "show_logs",
                    "show_queries",
                    "show_metrics",
                ]
            },
        ),
    ]


class RequestAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "site",
        "environment",
        "method",
        "path",
        "status",
        "ip",
    ]
    list_filter = ["site", "environment", "method", "status"]


class LogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "site", "environment", "message", "level", "context"]
    list_filter = ["site", "environment", "level"]
    raw_id_fields = ["context", "error"]


class ErrorAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "site",
        "environment",
        "module",
        "kind",
        "message",
        "context",
    ]
    list_filter = ["site", "environment", "kind", "module"]
    raw_id_fields = ["context"]


class ContextAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "name", "request", "elapsed_ms"]
    raw_id_fields = ["parent", "request"]


class MetricAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "site",
        "environment",
        "name",
        "agg_count",
        "agg_sum",
        "agg_avg",
        "agg_min",
        "agg_max",
        "context",
    ]
    list_filter = ["site", "environment"]
    raw_id_fields = ["context"]


class QueryAdmin(admin.ModelAdmin):
    list_display = [
        "timestamp",
        "site",
        "environment",
        "sql_summary",
        "elapsed_ms",
        "context",
    ]
    list_filter = ["site", "environment", "db", "success", "command"]
    raw_id_fields = ["context"]


class NodeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "site",
        "environment",
        "platform",
        "language",
        "language_version",
        "framework",
        "framework_version",
        "first_seen",
        "last_seen",
    ]
    list_filter = ["site", "language", "framework"]


class NodePackageAdmin(admin.ModelAdmin):
    list_display = ["node", "node__site", "package", "version"]
    list_filter = ["node__site", "node__environment", "node"]
    ordering = ["node", "package"]


class NodeUpdateAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "node", "node__site"]
    list_filter = ["node", "node__site", "node__environment"]


class ContextIntegrationAdmin(admin.ModelAdmin):
    list_display = ["context", "context__site", "integration", "run_date"]
    list_filter = ["context__site", "integration"]
    raw_id_fields = ["context"]


admin.site.register(Site, SiteAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(NodePackage, NodePackageAdmin)
admin.site.register(NodeUpdate, NodeUpdateAdmin)

if not settings.VARANUS_USE_SCHEMAS:
    admin.site.register(Request, RequestAdmin)
    admin.site.register(Log, LogAdmin)
    admin.site.register(Error, ErrorAdmin)
    admin.site.register(Context, ContextAdmin)
    admin.site.register(Metric, MetricAdmin)
    admin.site.register(Query, QueryAdmin)
    admin.site.register(ContextIntegration, ContextIntegrationAdmin)
