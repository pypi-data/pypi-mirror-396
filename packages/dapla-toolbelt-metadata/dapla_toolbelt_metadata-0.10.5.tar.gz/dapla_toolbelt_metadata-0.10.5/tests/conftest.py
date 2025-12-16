import string
import sys
import typing as t

import jwt
import pytest
from faker import Faker

if sys.version_info < (3, 11):
    # dapla_auth_client only supports Python >=3.11
    # We must still support 3.10 for now, but variable definitions never runs on 3.10
    collect_ignore_glob = ["*variable_definitions*"]


@pytest.fixture
def raw_jwt_payload(faker: Faker) -> dict[str, t.Any]:
    user_name = "".join(faker.random_sample(elements=string.ascii_lowercase, length=3))
    email = f"{user_name}@ssb.no"
    first_name = faker.first_name()
    last_name = faker.last_name()
    return {
        "exp": faker.unix_time(),
        "iat": faker.unix_time(),
        "auth_time": faker.unix_time(),
        "jti": faker.uuid4(),
        "iss": faker.url(),
        "aud": [
            faker.word(),
            faker.uuid4(),
            "broker",
            "account",
        ],
        "sub": faker.uuid4(),
        "typ": "Bearer",
        "azp": "onyxia",
        "session_state": faker.uuid4(),
        "allowed-origins": ["*"],
        "realm_access": {
            "roles": [faker.word(), faker.word()],
        },
        "resource_access": {
            "broker": {"roles": [faker.word()]},
            "account": {
                "roles": [faker.word()],
            },
        },
        "scope": "openid email profile",
        "sid": faker.uuid4(),
        "email_verified": True,
        "name": f"{first_name} {last_name}",
        "short_username": f"ssb-{user_name}",
        "preferred_username": email,
        "given_name": first_name,
        "family_name": last_name,
        "email": email,
    }


@pytest.fixture
def fake_jwt(raw_jwt_payload: dict[str, t.Any]) -> str:
    return jwt.encode(raw_jwt_payload, "test secret", algorithm="HS256")


@pytest.fixture
def raw_labid_jwt_payload(faker: Faker) -> dict[str, t.Any]:
    return {
        "aud": ["vardef"],
        "dapla.group": "team-a-developers",
        "dapla.groups": [
            "team-a-data-admins",
            "team-a-developers",
            "team-b-developers",
        ],
        "exp": faker.unix_time(),
        "iat": faker.unix_time(),
        "iss": "https://labid.lab.dapla-external.ssb.no",
        "scope": "all_groups,current_group",
        "sub": "".join(faker.random_sample(elements=string.ascii_lowercase, length=3)),
    }


@pytest.fixture
def fake_labid_jwt(raw_labid_jwt_payload: dict[str, t.Any]) -> str:
    return jwt.encode(raw_labid_jwt_payload, "test secret", algorithm="HS256")
