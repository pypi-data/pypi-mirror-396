import datetime
import functools
import operator
from typing import Any, ClassVar

from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _

from .base import SearchField, SkipRender
from .utils import StringValues, date_value


class Choice:
    id: str
    value: str
    label: str | Promise
    count: int

    def __init__(self, field: SearchField, value: Any, count: int):
        self.value = self.stringify(value)
        if callable(field.choice_label):
            self.label = field.choice_label(value)
        else:
            self.label = self.value or field.empty_label
        self.id = field.id + "_" + self.value.replace(" ", "")
        self.count = count

    @classmethod
    def stringify(cls, value):
        return str(value) if value is not None else ""


class Facet(SearchField):
    choice_class: ClassVar[type[Choice]] = Choice

    def get_choices(self, queryset, request: HttpRequest | None = None):
        choice_qs = queryset.values_list(self.field_name).annotate(num=Count("*"))
        match self.order:
            case "value":
                choice_qs = choice_qs.order_by(self.field_name)
            case "count":
                choice_qs = choice_qs.order_by("-num")
        return [self.choice_class(self, c, num) for c, num in choice_qs]


class MultiFacet(Facet):
    template_name = "search/multifacet.html"

    def apply(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> QuerySet:
        filters = []
        if selected := set(field_data.get(self.name, [])):
            if "" in selected:
                selected.discard("")
                filters.append(Q(**{f"{self.field_name}__isnull": True}))
            if selected:
                filters.append(Q(**{f"{self.field_name}__in": selected}))
        if filters:
            queryset = queryset.filter(functools.reduce(operator.or_, filters))
        return queryset

    def get_context(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> dict:
        return {
            **super().get_context(queryset, field_data, request=request),
            "choices": self.get_choices(queryset, request=request),
            "selected": field_data.get(self.name, []),
        }


class DateRange(SearchField):
    template_name = "search/daterange.html"
    prefixed = True

    def apply(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> QuerySet:
        filters = {}
        if start := date_value(field_data, "start"):
            filters[f"{self.field_name}__date__gte"] = start
        if end := date_value(field_data, "end"):
            filters[f"{self.field_name}__date__lte"] = end
        return queryset.filter(**filters)

    def get_context(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> dict:
        today = datetime.date.today()
        buttons = [
            (_("Today"), today - datetime.timedelta(days=0)),
            (_("Last 7 Days"), today - datetime.timedelta(days=7)),
            (_("Last 30 Days"), today - datetime.timedelta(days=30)),
        ]
        return {
            **super().get_context(queryset, field_data, request=request),
            "start": date_value(field_data, "start"),
            "end": date_value(field_data, "end"),
            "today": today,
            "buttons": buttons,
        }


class Filter(SearchField):
    template_name = "search/filter.html"

    def apply(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> QuerySet:
        for term in field_data.get(self.name, []):
            if not term.strip():
                continue
            if isinstance(self.field_name, str):
                queryset = queryset.filter(**{f"{self.field_name}__icontains": term})
            else:
                filters = [
                    Q(**{f"{name}__icontains": term}) for name in self.field_name
                ]
                queryset = queryset.filter(functools.reduce(operator.or_, filters))
        return queryset

    def get_context(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> dict:
        return {
            **super().get_context(queryset, field_data, request=request),
            "terms": field_data.get(self.name, []),
        }


class Hidden(SearchField):
    template_name = "search/hidden.html"

    def apply(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> QuerySet:
        values = field_data.get(self.name, [])
        if not values:
            return queryset
        filters = {f"{self.field_name}__in": values}
        return queryset.filter(**filters)

    def get_context(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> dict:
        values = field_data.get(self.name, [])
        if not values:
            raise SkipRender()
        filtered = self.apply(queryset, field_data)
        clear_link = ""
        if request:
            query = request.GET.copy()
            query.pop(self.name, None)
            clear_link = request.path
            if qs := query.urlencode():
                clear_link += "?" + qs
        return {
            **super().get_context(queryset, field_data, request=request),
            "count": filtered.count(),
            "values": values,
            "clear_link": clear_link,
        }
