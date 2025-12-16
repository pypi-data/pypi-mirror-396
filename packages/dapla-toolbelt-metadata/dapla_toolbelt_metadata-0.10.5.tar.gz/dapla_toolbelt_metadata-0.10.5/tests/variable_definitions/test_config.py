import pytest
from pytest_mock import MockType

from dapla_metadata._shared.config import DAPLA_ENVIRONMENT
from dapla_metadata._shared.enums import DaplaEnvironment
from dapla_metadata.variable_definitions._utils.config import VARDEF_HOST_PROD
from dapla_metadata.variable_definitions._utils.config import VARDEF_HOST_TEST
from dapla_metadata.variable_definitions._utils.config import WORKSPACE_DIR
from dapla_metadata.variable_definitions._utils.config import (
    get_vardef_client_configuration,
)
from dapla_metadata.variable_definitions._utils.config import get_vardef_host
from dapla_metadata.variable_definitions._utils.config import get_workspace_dir
from dapla_metadata.variable_definitions.vardef import Vardef


@pytest.mark.parametrize(
    "env",
    [DaplaEnvironment.PROD.value],
)
def test_vardef_host_prod(monkeypatch: pytest.MonkeyPatch, env: str):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, env)
    assert get_vardef_host() == VARDEF_HOST_PROD


@pytest.mark.parametrize(
    "env",
    [
        DaplaEnvironment.TEST.value,
        DaplaEnvironment.DEV.value,
    ],
)
def test_vardef_host_test(monkeypatch: pytest.MonkeyPatch, env: str):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, env)
    assert get_vardef_host() == VARDEF_HOST_TEST


def test_vardef_host_default(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DAPLA_ENVIRONMENT, raising=False)
    monkeypatch.delenv("VARDEF_HOST", raising=False)
    assert get_vardef_host() == "http://localhost:8080"


def test_vardef_host_specified(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(DAPLA_ENVIRONMENT, raising=False)
    monkeypatch.setenv("VARDEF_HOST", "my-host")
    assert get_vardef_host() == "my-host"


def test_get_vardef_client_configuration(
    monkeypatch: pytest.MonkeyPatch, fake_labid_jwt: str
):
    monkeypatch.setenv(DAPLA_ENVIRONMENT, DaplaEnvironment.TEST.value)
    config = get_vardef_client_configuration()
    assert config.host == get_vardef_host()
    assert config.access_token == fake_labid_jwt


def test_workspace_dir_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(WORKSPACE_DIR, "home/work")
    assert get_workspace_dir() == "home/work"


@pytest.mark.parametrize("number_of_calls", [0, 3, 10])
def test_access_token_refreshed_for_each_request(
    mock_auth_client_fetch_personal_token: MockType, number_of_calls: int
):
    for _ in range(number_of_calls):
        Vardef.list_variable_definitions()
    assert mock_auth_client_fetch_personal_token.call_count == number_of_calls
    if number_of_calls:
        mock_auth_client_fetch_personal_token.assert_called_with(
            scopes=["all_groups", "current_group"], audiences=["vardef"]
        )
