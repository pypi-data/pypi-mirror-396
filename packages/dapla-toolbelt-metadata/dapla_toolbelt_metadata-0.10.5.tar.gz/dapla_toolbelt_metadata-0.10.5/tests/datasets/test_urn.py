import logging

import datadoc_model.all_optional.model as all_optional_model
import pytest
from pydantic import AnyUrl
from typeguard import suppress_type_checks

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.utility.urn import URN_ERROR_MESSAGE_BASE
from dapla_metadata.datasets.utility.urn import ReferenceUrlTypes
from dapla_metadata.datasets.utility.urn import SsbNaisDomains
from dapla_metadata.datasets.utility.urn import UrlVisibility
from dapla_metadata.datasets.utility.urn import klass_urn_converter
from dapla_metadata.datasets.utility.urn import vardef_urn_converter

EXAMPLE_KLASS_ID = "91"
EXAMPLE_KLASS_URN = AnyUrl(klass_urn_converter.get_urn(EXAMPLE_KLASS_ID))
EXAMPLE_VARDEF_ID = "hd8_Ks-9"
EXAMPLE_VARDEF_URN = AnyUrl(vardef_urn_converter.get_urn(EXAMPLE_VARDEF_ID))

VARIABLE_DEFINITION_URN_TEST_CASES = [
    *[
        (
            f"https://metadata.{domain.value}/variable-definitions/{EXAMPLE_VARDEF_ID}",
            EXAMPLE_VARDEF_URN,
            False,
        )
        for domain in SsbNaisDomains
    ],
    *[
        (
            f"https://catalog.{domain.value}/variable-definitions/{EXAMPLE_VARDEF_ID}",
            EXAMPLE_VARDEF_URN,
            False,
        )
        for domain in SsbNaisDomains
    ],
    (
        EXAMPLE_VARDEF_URN,
        EXAMPLE_VARDEF_URN,
        False,
    ),
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", None, True),
    ],
)
def test_convert_to_vardef_urn(
    case: str,
    expected_result: AnyUrl | None,
    expect_warning: bool,  # noqa: ARG001
):
    assert vardef_urn_converter.convert_url_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *VARIABLE_DEFINITION_URN_TEST_CASES,
        ("https://www.vg.no", AnyUrl("https://www.vg.no/"), True),
        (None, None, False),
    ],
)
def test_convert_to_vardef_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[
                all_optional_model.Variable(
                    short_name="my_variable", definition_uri=case
                )
            ],
        )
    )
    if not expected_result:
        assert meta.variables[0].definition_uri is None
    else:
        assert meta.variables[0].definition_uri == expected_result
    assert (URN_ERROR_MESSAGE_BASE in caplog.text) is expect_warning


@pytest.mark.parametrize("identifier", [EXAMPLE_VARDEF_ID])
@pytest.mark.parametrize("visibility", ["internal", "public"])
@pytest.mark.parametrize(
    "url_type", [ReferenceUrlTypes.API, ReferenceUrlTypes.FRONTEND]
)
def test_vardef_get_url(
    url_type: ReferenceUrlTypes, visibility: UrlVisibility, identifier: str
):
    url = vardef_urn_converter.get_url(identifier, url_type, visibility)
    assert url is not None
    assert url.endswith("/" + identifier)
    if url_type == ReferenceUrlTypes.API:
        assert url.startswith("https://metadata.")
    else:
        assert url.startswith("https://catalog.")
    if visibility == "internal":
        assert ".intern." in url
    else:
        assert ".intern." not in url


@pytest.mark.parametrize(
    ("urn_or_url", "identifier"),
    [
        ("https://www.vg.no", None),
        (EXAMPLE_VARDEF_URN, EXAMPLE_VARDEF_ID),
        (
            f"https://catalog.ssb.no/variable-definitions/{EXAMPLE_VARDEF_ID}",
            EXAMPLE_VARDEF_ID,
        ),
        (
            AnyUrl(
                f"https://metadata.intern.test.ssb.no/variable-definitions/{EXAMPLE_VARDEF_ID}"
            ),
            EXAMPLE_VARDEF_ID,
        ),
    ],
)
def test_vardef_get_id(urn_or_url: str | AnyUrl, identifier: str | None):
    assert vardef_urn_converter.get_id(urn_or_url) == identifier


@pytest.mark.parametrize(
    ("identifier", "expected"),
    [
        (EXAMPLE_VARDEF_ID, True),
        ("invalid-id", False),
        ("123", False),
        ("12345678", True),
        ("123456789", False),
        ("abc$EFGH", False),
        ("", False),
        (None, False),
    ],
)
@suppress_type_checks
def test_vardef_is_id(identifier: str, expected: bool):
    assert vardef_urn_converter.is_id(identifier) is expected


CLASSIFICATION_URN_TEST_CASES = [
    (
        f"https://www.ssb.no/klass/klassifikasjoner/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://www.ssb.no/en/klass/klassifikasjoner/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://data.ssb.no/api/klass/v1/classifications/{EXAMPLE_KLASS_ID}",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        f"https://data.ssb.no/api/klass/v1/classifications/{EXAMPLE_KLASS_ID}.json",
        EXAMPLE_KLASS_URN,
        False,
    ),
    (
        EXAMPLE_KLASS_URN,
        EXAMPLE_KLASS_URN,
        False,
    ),
]


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    CLASSIFICATION_URN_TEST_CASES,
)
def test_convert_to_klass_urn(
    case: str,
    expected_result: str,
    expect_warning: bool,  # noqa: ARG001
):
    assert klass_urn_converter.convert_url_to_urn(case) == expected_result


@pytest.mark.parametrize(
    ("case", "expected_result", "expect_warning"),
    [
        *CLASSIFICATION_URN_TEST_CASES,
        ("https://www.vg.no", AnyUrl("https://www.vg.no/"), True),
        (None, None, False),
    ],
)
def test_convert_to_klass_urn_end_to_end(
    case: str | None,
    expected_result: str | None,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    meta = Datadoc()
    meta._set_metadata(  # noqa: SLF001
        all_optional_model.DatadocMetadata(
            dataset=all_optional_model.Dataset(),
            variables=[
                all_optional_model.Variable(
                    short_name="my_variable", classification_uri=case
                )
            ],
        )
    )
    if not expected_result:
        assert meta.variables[0].classification_uri is None
    else:
        assert meta.variables[0].classification_uri == expected_result
    assert (URN_ERROR_MESSAGE_BASE in caplog.text) is expect_warning


@pytest.mark.parametrize("identifier", [EXAMPLE_KLASS_ID])
@pytest.mark.parametrize("visibility", ["internal", "public"])
@pytest.mark.parametrize(
    "url_type", [ReferenceUrlTypes.API, ReferenceUrlTypes.FRONTEND]
)
def test_klass_get_url(
    url_type: ReferenceUrlTypes, visibility: UrlVisibility, identifier: str
):
    url = klass_urn_converter.get_url(identifier, url_type, visibility)
    if visibility == "internal":
        # Klass doesn't have an internal representation
        assert url is None
    else:
        assert url is not None
        assert url.endswith("/" + identifier)
        if url_type == ReferenceUrlTypes.API:
            assert url.startswith("https://data.")
        else:
            assert url.startswith("https://www.ssb.")


@pytest.mark.parametrize(
    ("urn_or_url", "identifier"),
    [
        ("https://www.vg.no", None),
        (EXAMPLE_KLASS_URN, EXAMPLE_KLASS_ID),
        (
            f"https://www.ssb.no/klass/klassifikasjoner/{EXAMPLE_KLASS_ID}",
            EXAMPLE_KLASS_ID,
        ),
        (
            AnyUrl(
                f"https://data.ssb.no/api/klass/v1/classifications/{EXAMPLE_KLASS_ID}"
            ),
            EXAMPLE_KLASS_ID,
        ),
    ],
)
def test_klass_get_id(urn_or_url: str | AnyUrl, identifier: str | None):
    assert klass_urn_converter.get_id(urn_or_url) == identifier


@pytest.mark.parametrize(
    ("identifier", "expected"),
    [
        (EXAMPLE_KLASS_ID, True),
        ("invalid-id", False),
        ("123", True),
        ("1", True),
        ("123456789", False),
        ("abcdEFGH", False),
        ("", False),
        (None, False),
    ],
)
@suppress_type_checks
def test_klass_is_id(identifier: str, expected: bool):
    assert klass_urn_converter.is_id(identifier) is expected
