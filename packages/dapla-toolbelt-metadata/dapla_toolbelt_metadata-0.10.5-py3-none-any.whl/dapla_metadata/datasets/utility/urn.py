"""Validate, parse and render URNs."""

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Literal

from pydantic import AnyUrl

from dapla_metadata._shared.config import get_dapla_environment
from dapla_metadata._shared.enums import DaplaEnvironment
from dapla_metadata.datasets.utility.utils import VariableListType

logger = logging.getLogger(__name__)

URN_ERROR_MESSAGE_BASE = "The URL is not in a supported format"

URN_ERROR_MESSAGE_TEMPLATE = (
    URN_ERROR_MESSAGE_BASE
    + " for field '{field_name}' of variable '{short_name}'. URL: '{value}'. Please contact Team Metadata if this URL should be supported."
)


VARDEF_URL_TEMPLATE = "https://{subdomain}.{domain}/variable-definitions"


class SsbNaisDomains(str, Enum):
    """The available domains on SSBs Nais instance."""

    TEST_EXTERNAL = "test.ssb.no"
    TEST_INTERNAL = "intern.test.ssb.no"
    PROD_EXTERNAL = "ssb.no"
    PROD_INTERNAL = "intern.ssb.no"


class ReferenceUrlTypes(Enum):
    """The general category of the URL.

    This can be useful to refer to when constructing a URL from a URN for a
    specific context.
    """

    API = auto()
    FRONTEND = auto()


UrlVisibility = Literal["public", "internal"]


@dataclass
class UrnConverter:
    """Converts URLs to URNs and vice versa.

    Attributes:
        urn_base: The format for the URN, up to the identifier.
        id_pattern: A capturing group pattern which matches identifiers for this resource.
        url_bases: The list of all the different URL representations for a resource. There
            will typically be a number of URL representations for a particular resource,
            depending on which system or technology they are accessed through and other
            technical factors. This list defines which concrete URLs can be considered
            equivalent to a URN.
    """

    urn_base: str
    id_pattern: str
    url_bases: list[tuple[ReferenceUrlTypes, str]]

    def _extract_id(self, url: str, pattern: re.Pattern[str]) -> str | None:
        if match := pattern.match(url):
            return match.group(1)
        return None

    def _build_pattern(self, url_base: str) -> re.Pattern[str]:
        return re.compile(f"^{url_base}/{self.id_pattern}")

    def get_urn(self, identifier: str) -> str:
        """Build a URN for the given identifier."""
        return f"{self.urn_base}:{identifier}"

    def get_url(
        self,
        identifier: str,
        url_type: ReferenceUrlTypes,
        visibility: Literal["public", "internal"] = "public",
    ) -> str | None:
        """Build concrete URL to reference a resource.

        There are typically multiple URLs used to refer to one resource, this method attempts to support known variations.

        Args:
            identifier (str): The identifier of the resource the URL refers to.
            url_type (ReferenceUrlTypes): The representation type of the URL
            visibility (UrlVisibility, optional): Whether the URL should be that which is publicly available or not. Defaults to "public".

        Returns:
            str | None: The concrete URL. None if we cannot satisfy the supplied requirements.
        """
        candidates = [base[-1] for base in self.url_bases if base[0] == url_type]

        def matches_visibility(url: str, visibility: UrlVisibility):
            return (".intern." in url) is (visibility == "internal")

        def matches_environment(url: str):
            current_environment = get_dapla_environment()
            if current_environment == DaplaEnvironment.TEST:
                return ".test." in url
            return ".test." not in url

        if url := next(
            (
                url
                for url in candidates
                if matches_visibility(url, visibility) and matches_environment(url)
            ),
            None,
        ):
            return url + "/" + identifier
        return None

    def get_id(self, urn_or_url: str | AnyUrl) -> str | None:
        """Get an identifier from a URN or URL.

        Args:
            urn_or_url (str | AnyUrl): The URN or URL refering to a particular resource

        Returns:
            str | None: The identifier for the resource, or None if it cannot be extracted.
        """
        if str(urn_or_url).startswith(self.urn_base):
            return str(urn_or_url).removeprefix(self.urn_base + ":")
        return self._extract_id_from_url(urn_or_url)

    def is_id(self, value: str) -> bool:
        """Check if the value is an identifier for this URN type.

        Args:
            value (str): The value to check.
        """
        if not isinstance(value, str):
            # Mypy thinks it's impossible to reach this branch, but there are no guarantees in Python.
            return False  # type: ignore [unreachable]
        pattern = re.compile(f"^{self.id_pattern}$")
        return bool(pattern.match(value))

    def _extract_id_from_url(self, url: str | AnyUrl) -> str | None:
        patterns = (self._build_pattern(url[-1]) for url in self.url_bases)
        matches = (self._extract_id(str(url), p) for p in patterns)
        return next((m for m in matches if m), None)

    def convert_url_to_urn(self, url: str | AnyUrl) -> AnyUrl | None:
        """Convert a URL to a generalized URN for that same resource.

        Args:
            url (str | AnyUrl): The URL to convert.

        Returns:
            str | None: The URN or None if it can't be converted.
        """
        if str(url).startswith(self.urn_base):
            # In this case the value is already in the expected format and nothing needs to be done.
            return AnyUrl(url)
        if identifier := self._extract_id_from_url(url):
            return AnyUrl(self.get_urn(identifier))

        return None


vardef_urn_converter = UrnConverter(
    urn_base="urn:ssb:variable-definition:vardef",
    id_pattern=r"([a-zA-Z0-9-_]{8})",  # 8 character Nanoid with default alphabet
    url_bases=[
        *[
            (
                ReferenceUrlTypes.API,
                VARDEF_URL_TEMPLATE.format(
                    subdomain="metadata", domain=nais_domain.value
                ),
            )
            for nais_domain in SsbNaisDomains
        ],
        *[
            (
                ReferenceUrlTypes.FRONTEND,
                VARDEF_URL_TEMPLATE.format(
                    subdomain="catalog", domain=nais_domain.value
                ),
            )
            for nais_domain in SsbNaisDomains
        ],
    ],
)

klass_urn_converter = UrnConverter(
    urn_base="urn:ssb:classification:klass",
    id_pattern=r"([0-9]{1,5})",
    url_bases=[
        (ReferenceUrlTypes.FRONTEND, "https://www.ssb.no/klass/klassifikasjoner"),
        (ReferenceUrlTypes.FRONTEND, "https://www.ssb.no/en/klass/klassifikasjoner"),
        (ReferenceUrlTypes.API, "https://data.ssb.no/api/klass/v1/classifications"),
    ],
)


def convert_uris_to_urns(
    variables: VariableListType, field_name: str, converters: Iterable[UrnConverter]
) -> None:
    """Where URIs are recognized URLs, convert them to URNs.

    Where the value is not a known URL we preserve the value as it is and log an
    ERROR level message.

    Args:
        variables (VariableListType): The list of variables.
        field_name (str): The name of the field which has URLs to convert to URNs
        converters (Iterable[UrnConverter]): One or more converters which implement
            conversion of URLs into one specific URN format. These will typically be
            specific to an individual metadata reference system.
    """
    for v in variables:
        field = getattr(v, field_name, None)
        if field:
            if urn := next((c.convert_url_to_urn(field) for c in converters), None):
                setattr(v, field_name, urn)
            else:
                logger.error(
                    URN_ERROR_MESSAGE_TEMPLATE.format(
                        field_name=field_name,
                        short_name=v.short_name,
                        value=field,
                    )
                )
