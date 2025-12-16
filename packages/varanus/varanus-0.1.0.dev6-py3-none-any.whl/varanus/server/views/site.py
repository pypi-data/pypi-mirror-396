from typing import ClassVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    Avg,
    Count,
    Max,
    Min,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
)
from django.shortcuts import get_object_or_404

from varanus.search import DateRange, Filter, Hidden, MultiFacet, Search

from ..models import Context, Log
from .base import SiteView


class Overview(SiteView):
    template_name = "site/overview.html"

    def get_context(self):
        nodes = self.site.nodes.annotate(
            last_event=Subquery(
                Context.objects.filter(node_id=OuterRef("id"))
                .order_by("-timestamp")
                .values("timestamp")[:1]
            ),
            num_packages=Count("packages"),
        )
        return {
            "host": self.request.get_host(),
            "scheme": self.request.scheme,
            "nodes": nodes,
        }


class SearchView(SiteView):
    search_class: ClassVar[type[Search]]

    def get_queryset(self, grouped: bool) -> QuerySet:
        raise NotImplementedError()

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        raise NotImplementedError()

    def get_context(self):
        grouped = "grouped" in self.request.GET
        search = self.search_class(
            self.get_queryset(grouped),
            self.request.GET,
            request=self.request,
        )
        results = search.queryset()
        if grouped:
            results = self.aggregate(results)
        return {
            "search": search,
            "results": results[:50],
            "grouped": grouped,
        }


class Logs(SearchView):
    template_name = "site/logs.html"

    class search_class(Search):
        fingerprint = Hidden()
        search = Filter(default=True, field_name=("context__name", "message"))
        timeframe = DateRange(default=True, field_name="timestamp")
        name = MultiFacet()
        level = MultiFacet(choice_label=Log.level_name)
        environment = MultiFacet()
        node__name = MultiFacet()

    def get_queryset(self, grouped: bool) -> QuerySet:
        return self.site.logs.select_related("context")

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        return queryset.values(
            "fingerprint", "message", "level", "name", "file", "lineno"
        ).annotate(
            num=Count("*"),
            timestamp=Max("timestamp"),
        )


class Errors(SearchView):
    template_name = "site/errors.html"

    class search_class(Search):
        fingerprint = Hidden()
        search = Filter(default=True, field_name=("context__name", "message"))
        timeframe = DateRange(default=True, field_name="timestamp")
        kind = MultiFacet()
        module = MultiFacet()
        environment = MultiFacet()
        node__name = MultiFacet()

    def get_queryset(self, grouped: bool) -> QuerySet:
        return self.site.errors.select_related("context")

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        return queryset.values("fingerprint", "message", "kind", "module").annotate(
            num=Count("*"),
            timestamp=Max("timestamp"),
        )


class Requests(SearchView):
    template_name = "site/requests.html"

    class search_class(Search):
        fingerprint = Hidden()
        search = Filter(default=True, field_name=("path", "query", "ip"))
        timeframe = DateRange(default=True, field_name="timestamp")
        host = MultiFacet()
        method = MultiFacet()
        status = MultiFacet()
        environment = MultiFacet()
        node__name = MultiFacet()

    def get_queryset(self, grouped: bool) -> QuerySet:
        return self.site.requests.select_related("context").defer("headers")

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        return queryset.values("fingerprint", "host", "method", "path").annotate(
            num=Count("*"),
            timestamp=Max("timestamp"),
            elapsed_min=Min("context__elapsed_ms"),
            elapsed_max=Max("context__elapsed_ms"),
            elapsed_avg=Avg("context__elapsed_ms"),
            # num_ips=Count("ip", distinct=True),
            # statuses=StringAgg(Cast("status", TextField()), ", "),
        )


class Queries(SearchView):
    template_name = "site/queries.html"

    class search_class(Search):
        fingerprint = Hidden()
        search = Filter(default=True, field_name=("context__name", "sql"))
        timeframe = DateRange(default=True, field_name="timestamp")
        type = MultiFacet(field_name="command")
        db = MultiFacet(label="Database")
        environment = MultiFacet()
        node__name = MultiFacet(label="Node")

    def get_queryset(self, grouped: bool) -> QuerySet:
        return self.site.queries.select_related("context")

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        return queryset.values("fingerprint", "sql_summary").annotate(
            num=Count("*"),
            timestamp=Max("timestamp"),
            elapsed_min=Min("elapsed_ms"),
            elapsed_max=Max("elapsed_ms"),
            elapsed_avg=Avg("elapsed_ms"),
        )


class Metrics(SearchView):
    template_name = "site/metrics.html"

    class search_class(Search):
        search = Filter(default=True, field_name="context__name")
        timeframe = DateRange(default=True, field_name="timestamp")
        name = MultiFacet()
        environment = MultiFacet()
        node__name = MultiFacet()

    def get_queryset(self, grouped: bool) -> QuerySet:
        return self.site.metrics.select_related("context")

    def aggregate(self, queryset: QuerySet) -> QuerySet:
        return queryset.values("name").annotate(
            agg_avg=Sum("agg_sum") / Sum("agg_count"),
            agg_count=Sum("agg_count"),
            agg_sum=Sum("agg_sum"),
            agg_min=Min("agg_min"),
            agg_max=Max("agg_max"),
            timestamp=Max("timestamp"),
        )


class Details(SiteView):
    @property
    def template_name(self):
        model = self.kwargs["model"]
        return f"site/details/{model}.html"

    def get_context(self):
        ct = ContentType.objects.get_by_natural_key("varanus", self.kwargs["model"])
        obj = ct.get_object_for_this_type(pk=self.kwargs["pk"])
        return {
            "object": obj,
            "context": getattr(obj, "context", None),
        }


class NodePackages(SiteView):
    template_name = "site/details/node_packages.html"

    def get_context(self):
        node = get_object_or_404(self.site.nodes, pk=self.kwargs["pk"])
        return {
            "node": node,
        }


class NodeSettings(SiteView):
    template_name = "site/details/node_settings.html"

    def get_context(self):
        node = get_object_or_404(self.site.nodes, pk=self.kwargs["pk"])
        return {
            "node": node,
        }


class NodeEnv(SiteView):
    template_name = "site/details/node_env.html"

    def get_context(self):
        node = get_object_or_404(self.site.nodes, pk=self.kwargs["pk"])
        return {
            "node": node,
        }


class NodeEnvironments(SiteView):
    template_name = "site/details/node_environments.html"

    def get_context(self):
        return {
            "name": self.kwargs["name"],
            "nodes": self.site.nodes.filter(name__iexact=self.kwargs["name"]),
        }


class EnvironmentNodes(SiteView):
    template_name = "site/details/environment_nodes.html"

    def get_context(self):
        return {
            "environment": self.kwargs["environment"],
            "nodes": self.site.nodes.filter(
                environment__iexact=self.kwargs["environment"]
            ),
        }
