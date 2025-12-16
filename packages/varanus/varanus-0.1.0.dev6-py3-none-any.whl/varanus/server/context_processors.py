def sites(request):
    memberships = None
    if request.user.is_authenticated:
        memberships = request.user.memberships.select_related("site").order_by(
            "site__name"
        )
    return {
        "memberships": memberships,
    }
