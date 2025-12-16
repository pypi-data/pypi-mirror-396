from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from ..models import Node


class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        site_nodes = {}
        for membership in request.user.memberships.select_related("site").order_by(
            "site__name"
        ):
            site_nodes.setdefault(membership.site, [])
        for node in Node.objects.filter(site__in=site_nodes).order_by(
            "environment", "-last_seen"
        ):
            site_nodes[node.site].append(node)
        return render(
            request,
            "dashboard.html",
            {
                "site_nodes": site_nodes,
            },
        )
