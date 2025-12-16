from typing import Callable, ClassVar, Iterable, Literal, Self

from django.db.models import QuerySet
from django.http import HttpRequest
from django.template import loader
from django.utils.datastructures import MultiValueDict
from django.utils.functional import Promise
from django.utils.safestring import SafeString

from .utils import Namer, StringValues, string_data


class SkipRender(Exception):
    pass


class SearchField:
    template_name: str
    prefixed = False
    default = False

    def __init__(
        self,
        label=None,
        field_name: str | Iterable[str] | None = None,
        empty_label="NULL",
        # These belong on Facet
        choice_label: Callable[..., str | Promise] | None = None,
        order: Literal["value", "count"] = "value",
        default: bool = False,
    ):
        self.name = ""
        self.label = label or ""
        self.field_name = field_name or ""
        self.prefix = ""
        self.id = ""
        self.empty_label = empty_label
        self.choice_label = choice_label
        self.order = order
        self.default = default

    def __set_name__(self, owner, name: str):
        assert issubclass(owner, Search)
        self.name = name
        self.prefix = f"{name}_" if self.prefixed else ""
        self.id = f"id_{name}"
        if not self.label:
            self.label = name.capitalize().replace("__", " ")
        if not self.field_name:
            self.field_name = name
        if not hasattr(owner, "_fields"):
            owner._fields = []
        owner._fields.append(self)

    def __get__(self, instance: "Search", owner=None) -> StringValues | Self:
        if owner is None:
            return self
        if self.prefixed:
            return {
                key[len(self.prefix) :]: values
                for key, values in instance._data.items()
                if key.startswith(self.prefix)
            }
        else:
            return (
                {self.name: instance._data[self.name]}
                if self.name in instance._data
                else {}
            )

    def __set__(self, instance, value):
        raise AttributeError(f"`{self.name}` is read-only")

    @property
    def named(self):
        """
        Allows for {{ field.named.something }} in templates.
        """
        return Namer(self.prefix)

    def apply(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> QuerySet:
        raise NotImplementedError()

    def has_value(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> bool:
        return any(any(v) for v in field_data.values())

    def get_context(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> dict:
        return {
            "field": self,
        }

    def render(
        self,
        queryset: QuerySet,
        field_data: StringValues,
        request: HttpRequest | None = None,
    ) -> SafeString:
        return loader.render_to_string(
            self.template_name,
            self.get_context(queryset, field_data, request=request),
            request,
        )


class Search:
    _fields: ClassVar[list[SearchField]]
    template_name = "search/search.html"

    def __init__(
        self,
        queryset: QuerySet,
        data: dict | MultiValueDict | None = None,
        request: HttpRequest | None = None,
    ):
        self._queryset = queryset
        self._data = string_data(data)
        self._request = request

    def queryset(self, for_field=None):
        qs = self._queryset
        for field in self._fields:
            if field == for_field:
                continue
            field_data = getattr(self, field.name)
            qs = field.apply(qs, field_data, request=self._request)
        return qs

    def render(self) -> SafeString:
        context = {"fields": []}
        initial = not bool(self._data)
        for field in self._fields:
            qs = self.queryset(for_field=field)
            field_data = getattr(self, field.name)
            try:
                rendered = field.render(qs, field_data, request=self._request)
                default = (initial and field.default) or field.has_value(
                    qs,
                    field_data,
                    request=self._request,
                )
                context["fields"].append((field, default, rendered))
            except SkipRender:
                continue
        return loader.render_to_string(self.template_name, context, self._request)
