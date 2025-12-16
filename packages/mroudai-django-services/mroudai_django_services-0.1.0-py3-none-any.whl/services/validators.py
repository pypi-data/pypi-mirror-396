from __future__ import annotations

from datetime import timedelta
from typing import List, Optional

from django.utils import timezone

from .models import Service


def validate_service_time_constraints(
    service: Service,
    start_dt,
    now_dt=None,
) -> List[str]:
    """
    Validate time-based constraints for a service at a proposed start time.
    Returns a list of error messages (empty if valid).
    """
    errors: List[str] = []
    now = now_dt or timezone.now()

    # Minimum notice
    min_notice_delta = timedelta(minutes=service.minimum_notice_minutes)
    if start_dt < now + min_notice_delta:
        errors.append("Booking does not meet the minimum notice period.")

    # Maximum advance
    max_advance_delta = timedelta(days=service.maximum_advance_days)
    if start_dt > now + max_advance_delta:
        errors.append("Booking exceeds the maximum advance window.")

    # Fixed start intervals
    if service.fixed_start_times_only:
        minutes_since_midnight = start_dt.hour * 60 + start_dt.minute
        if minutes_since_midnight % service.start_time_interval_minutes != 0:
            errors.append("Start time is not aligned to the required interval.")

    return errors
