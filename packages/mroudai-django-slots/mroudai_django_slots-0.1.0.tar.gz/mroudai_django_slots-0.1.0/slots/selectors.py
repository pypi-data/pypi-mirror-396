from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from .engine import Slot, generate_slots
from .utils import get_setting


def _resolve_addons(service, addon_ids: Optional[Iterable[int]]):
    if not addon_ids:
        return []
    if hasattr(service, "addons"):
        return list(service.addons.filter(id__in=addon_ids))
    raise ValueError("addon_ids supplied but service does not expose an 'addons' relation.")


def list_available_slots(
    *,
    service,
    provider,
    start_date,
    end_date,
    tenant=None,
    tz=None,
    now_dt=None,
    addon_ids: Optional[Iterable[int]] = None,
) -> Dict:
    addons = _resolve_addons(service, addon_ids)
    return generate_slots(
        service=service,
        provider=provider,
        start_date=start_date,
        end_date=end_date,
        tz=tz,
        now_dt=now_dt,
        addons=addons,
        tenant=tenant,
    )


def _get_provider_queryset(service):
    provider_model_path = get_setting("SLOTS_PROVIDER_MODEL", None)
    if not provider_model_path:
        raise ImproperlyConfigured("SLOTS_PROVIDER_MODEL must be configured to list providers.")
    try:
        provider_model = apps.get_model(provider_model_path)
    except (LookupError, ValueError) as exc:
        raise ImproperlyConfigured(
            "Provider model is not available. Ensure the providers app is installed and "
            "SLOTS_PROVIDER_MODEL points to a valid model."
        ) from exc

    if hasattr(provider_model.objects, "capable_of_service"):
        return provider_model.objects.capable_of_service(service)
    if hasattr(provider_model.objects, "for_service"):
        return provider_model.objects.for_service(service)
    return provider_model.objects.all()


def list_available_slots_for_service(
    *,
    service,
    start_date,
    end_date,
    tenant=None,
    tz=None,
    now_dt=None,
) -> Dict:
    queryset = _get_provider_queryset(service)
    results: Dict = {}
    for provider in queryset:
        results[getattr(provider, "id", getattr(provider, "pk", None))] = list_available_slots(
            service=service,
            provider=provider,
            start_date=start_date,
            end_date=end_date,
            tenant=tenant,
            tz=tz,
            now_dt=now_dt,
        )
    return results
