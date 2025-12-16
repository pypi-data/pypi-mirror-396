import datetime

import pytest

from dapla_metadata.datasets.utility.utils import calculate_percentage
from dapla_metadata.datasets.utility.utils import get_current_date
from dapla_metadata.datasets.utility.utils import incorrect_date_order
from dapla_metadata.datasets.utility.utils import running_in_notebook


def test_calculate_percentage():
    assert calculate_percentage(1, 3) == 33


@pytest.mark.parametrize(
    ("date_from", "date_until", "expected"),
    [
        (datetime.date(2024, 1, 1), datetime.date(1960, 1, 1), True),
        (datetime.date(1980, 1, 1), datetime.date(2000, 6, 5), False),
        (None, None, False),
        (datetime.date(2024, 1, 1), None, False),
        (None, datetime.date(2024, 1, 1), True),
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 1), False),
    ],
)
def test_incorrect_date_order(date_from, date_until, expected):
    result = incorrect_date_order(date_from, date_until)
    assert result == expected


def test_not_running_in_notebook():
    assert not running_in_notebook()


def test_get_current_date():
    date = get_current_date()
    assert isinstance(date, str)
    datetime.datetime.strptime(date, "%Y-%m-%d").date()  # noqa: DTZ007
