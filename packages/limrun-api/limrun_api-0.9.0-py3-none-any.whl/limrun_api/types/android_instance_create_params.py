# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "AndroidInstanceCreateParams",
    "Metadata",
    "Spec",
    "SpecClue",
    "SpecInitialAsset",
    "SpecInitialAssetConfiguration",
    "SpecSandbox",
    "SpecSandboxPlaywrightAndroid",
]


class AndroidInstanceCreateParams(TypedDict, total=False):
    reuse_if_exists: Annotated[bool, PropertyInfo(alias="reuseIfExists")]
    """
    If there is another instance with given labels and region, return that one
    instead of creating a new instance.
    """

    wait: bool
    """Return after the instance is ready to connect."""

    metadata: Metadata

    spec: Spec


class Metadata(TypedDict, total=False):
    display_name: Annotated[str, PropertyInfo(alias="displayName")]

    labels: Dict[str, str]


class SpecClue(TypedDict, total=False):
    kind: Required[Literal["ClientIP", "OSVersion"]]

    client_ip: Annotated[str, PropertyInfo(alias="clientIp")]

    os_version: Annotated[str, PropertyInfo(alias="osVersion")]
    """The major version of Android, e.g. "13", "14" or "15"."""


class SpecInitialAssetConfiguration(TypedDict, total=False):
    kind: Required[Literal["ChromeFlag"]]

    chrome_flag: Annotated[Literal["enable-command-line-on-non-rooted-devices@1"], PropertyInfo(alias="chromeFlag")]


class SpecInitialAsset(TypedDict, total=False):
    kind: Required[Literal["App", "Configuration"]]

    asset_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="assetIds")]

    asset_name: Annotated[str, PropertyInfo(alias="assetName")]

    asset_names: Annotated[SequenceNotStr[str], PropertyInfo(alias="assetNames")]

    configuration: SpecInitialAssetConfiguration

    source: Literal["URL", "URLs", "AssetName", "AssetNames", "AssetIDs"]

    url: str

    urls: SequenceNotStr[str]


class SpecSandboxPlaywrightAndroid(TypedDict, total=False):
    enabled: bool


class SpecSandbox(TypedDict, total=False):
    playwright_android: Annotated[SpecSandboxPlaywrightAndroid, PropertyInfo(alias="playwrightAndroid")]


class Spec(TypedDict, total=False):
    clues: Iterable[SpecClue]

    hard_timeout: Annotated[str, PropertyInfo(alias="hardTimeout")]
    """
    After how many minutes should the instance be terminated. Example values 1m,
    10m, 3h. Default is "0" which means no hard timeout.
    """

    inactivity_timeout: Annotated[str, PropertyInfo(alias="inactivityTimeout")]
    """
    After how many minutes of inactivity should the instance be terminated. Example
    values 1m, 10m, 3h. Default is 3m. Providing "0" disables inactivity checks
    altogether.
    """

    initial_assets: Annotated[Iterable[SpecInitialAsset], PropertyInfo(alias="initialAssets")]

    region: str
    """The region where the instance will be created.

    If not given, will be decided based on scheduling clues and availability.
    """

    sandbox: SpecSandbox
