# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["AndroidInstance", "Metadata", "Spec", "Status", "StatusSandbox", "StatusSandboxPlaywrightAndroid"]


class Metadata(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")

    organization_id: str = FieldInfo(alias="organizationId")

    display_name: Optional[str] = FieldInfo(alias="displayName", default=None)

    labels: Optional[Dict[str, str]] = None

    terminated_at: Optional[datetime] = FieldInfo(alias="terminatedAt", default=None)


class Spec(BaseModel):
    inactivity_timeout: str = FieldInfo(alias="inactivityTimeout")
    """
    After how many minutes of inactivity should the instance be terminated. Example
    values 1m, 10m, 3h. Default is 3m. Providing "0" disables inactivity checks
    altogether.
    """

    region: str
    """The region where the instance will be created.

    If not given, will be decided based on scheduling clues and availability.
    """

    hard_timeout: Optional[str] = FieldInfo(alias="hardTimeout", default=None)
    """
    After how many minutes should the instance be terminated. Example values 1m,
    10m, 3h. Default is "0" which means no hard timeout.
    """


class StatusSandboxPlaywrightAndroid(BaseModel):
    url: Optional[str] = None


class StatusSandbox(BaseModel):
    playwright_android: Optional[StatusSandboxPlaywrightAndroid] = FieldInfo(alias="playwrightAndroid", default=None)


class Status(BaseModel):
    token: str

    state: Literal["unknown", "creating", "assigned", "ready", "terminated"]

    adb_web_socket_url: Optional[str] = FieldInfo(alias="adbWebSocketUrl", default=None)

    endpoint_web_socket_url: Optional[str] = FieldInfo(alias="endpointWebSocketUrl", default=None)

    error_message: Optional[str] = FieldInfo(alias="errorMessage", default=None)

    sandbox: Optional[StatusSandbox] = None

    target_http_port_url_prefix: Optional[str] = FieldInfo(alias="targetHttpPortUrlPrefix", default=None)


class AndroidInstance(BaseModel):
    metadata: Metadata

    spec: Spec

    status: Status
