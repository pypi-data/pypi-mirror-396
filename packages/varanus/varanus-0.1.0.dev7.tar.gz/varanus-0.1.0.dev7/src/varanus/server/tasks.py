import uuid

import msgspec
from django.tasks import task
from django.utils import timezone

from varanus import events

from .integrations import DuplicateIntegration
from .models import Context, Site


@task
def run_integration(site_id: int, integration_id: int, context_id: int):
    site = Site.objects.get(pk=site_id)
    with site.activated():
        integration = site.integrations.get(pk=integration_id)
        context = Context.objects.get(pk=context_id)
        if ident := integration.fingerprint(context):
            # Check to see if this integration has been run for the same identifier
            # within the debounce duration; if so, bail.
            since = timezone.now() - integration.debounce_duration
            if integration.contexts.filter(
                run_date__gt=since, identifier=ident
            ).exists():
                raise DuplicateIntegration(f"{integration.integration_path} - {ident}")
        result = integration.execute(context)
        context.integrations.create(
            integration=integration,
            identifier=ident,
            result=result,
        )


@task(priority=50)
def ingest(
    site_id: int,
    node_name: str,
    environment: str,
    event_json: str,
):
    try:
        # Try to decode a list of events first.
        event_list = msgspec.json.decode(event_json, type=list[events.Context])
    except msgspec.ValidationError:
        # Fall back to single event decoding.
        event_list = [msgspec.json.decode(event_json, type=events.Context)]

    site = Site.objects.get(pk=site_id)
    with site.activated():
        node = site.nodes.filter(name=node_name, environment=environment).get()
        for event in event_list:
            # TODO: modify this to return batches of objects to save?
            context = Context.from_event(
                event,
                event_id=uuid.uuid7(),
                site=site,
                environment=environment,
                node=node,
            )

            for integration in site.integrations.all():
                if integration.is_valid(event):
                    run_integration.enqueue(site_id, integration.pk, context.pk)
