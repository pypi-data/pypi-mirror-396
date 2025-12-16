from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBase
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from ..models import Site, SiteMember


class SiteView(LoginRequiredMixin, View):
    template_name = ""
    section = ""
    extra_context = None

    site: Site
    member: SiteMember

    def get_context(self) -> dict:
        return {}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.site = get_object_or_404(Site, slug=kwargs["slug"])
        self.member = get_object_or_404(self.site.members, user=request.user)
        if not self.section:
            self.section = self.__class__.__name__.lower()
        with self.site.activated():
            response = super().dispatch(request, *args, **kwargs)
        if isinstance(response, HttpResponseBase):
            return response
        return JsonResponse(response)

    def get(self, request, slug, **kwargs):
        context = {
            "site": self.site,
            "section": self.section,
        }
        if self.extra_context:
            context.update(self.extra_context)
        context.update(self.get_context())
        return render(request, self.template_name, context)
