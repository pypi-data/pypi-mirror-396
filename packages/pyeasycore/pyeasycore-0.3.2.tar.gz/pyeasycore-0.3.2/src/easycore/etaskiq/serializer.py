# -*- coding: utf-8 -*-
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from taskiq.abc.serializer import TaskiqSerializer


def _json_default(value: Any):
    """Make datetime (and friends) JSON serializable."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (UUID,)):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


class DateTimeSafeJsonSerializer(TaskiqSerializer):
    """Json serializer that encodes datetime instances as ISO strings."""

    def dumpb(self, message: Any) -> bytes:
        return json.dumps(
            message,
            default=_json_default,
            separators=(",", ":"),
        ).encode("utf-8")

    def loadb(self, data: bytes) -> Any:
        return json.loads(data.decode("utf-8"))
