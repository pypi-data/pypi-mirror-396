import ipaddress

from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from ..events import Request
from .client import client, resolve_include_exclude


def get_ip(request: HttpRequest):
    ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").strip()
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    if not ip_address:
        ip_address = request.META.get("REMOTE_ADDR", "127.0.0.1").strip()
    try:
        # Validate and normalize the IP address.
        return str(ipaddress.ip_address(ip_address))
    except ValueError:
        return ""


def request_headers(request: HttpRequest):
    headers = {}
    include_headers = resolve_include_exclude(
        [name.lower() for name in request.headers],
        client.include_headers,
        client.exclude_headers,
    )
    for name in include_headers:
        value = request.headers.get(name)
        if value is not None:
            headers[name] = value
    return headers


class VaranusMiddleware:
    def __init__(self, get_response):
        if not client.configured:
            # TODO: warning
            print("VaranusClient is not configured -- disabling middleware.")
            raise MiddlewareNotUsed()
        self.last_ping = None
        self.get_response = get_response

    def process_exception(self, request, exception):
        # Any value in using request.varanus instead of current context here?
        client.raw_exception(exception)

    def __call__(self, request: HttpRequest):
        if self.last_ping is None:
            self.last_ping = timezone.now()
            try:
                client.ping()
            except Exception:
                pass

        with client.context(request.path) as varanus:
            setattr(request, client.request_attr, varanus)
            response = self.get_response(request)
            # TODO: any need for request tags separate from context tags?
            varanus.request = Request(
                host=request.get_host(),
                method=request.method or "",
                path=request.path,
                query=request.META.get("QUERY_STRING", ""),
                status=response.status_code,
                headers=request_headers(request),
                size=(
                    len(response.content)
                    if isinstance(response, HttpResponse)
                    else None
                ),
                ip=get_ip(request),
                user=(
                    request.user.get_username()
                    if hasattr(request, "user")
                    and request.user
                    and request.user.is_authenticated
                    else None
                ),
            )
        return response
