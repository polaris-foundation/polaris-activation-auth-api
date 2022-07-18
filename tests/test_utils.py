from datetime import datetime, timedelta

import pytest

from dhos_activation_auth_api.helpers import utils

# ACTIVATION EXPIRY


def test_ancient_activation_expired() -> None:
    modified_date = datetime(2009, 10, 15, 5, 1, 24)
    days_til_expiry = 7
    assert utils._activation_expired(modified_date, days_til_expiry) is True


def test_yesterday_activation_expired() -> None:
    modified_date = datetime.utcnow() + timedelta(days=-1)
    days_til_expiry = 7
    assert utils._activation_expired(modified_date, days_til_expiry) is False


# GENERATE SECURE RANDOM


def test_generate_secure_random_string_human_readable() -> None:
    # Lol who wrote this test
    length = 4
    for _ in range(1000):
        secure_random_string = utils.generate_secure_human_readable_string(length)
        assert len(secure_random_string) == length
        assert "O" not in secure_random_string
        assert "0" not in secure_random_string
        assert "1" not in secure_random_string
        assert "L" not in secure_random_string


def test_generate_secure_random_string() -> None:
    length = 20
    secure_random_string = utils.generate_secure_random_string(length)
    assert len(secure_random_string) == length


def test_generate_secure_random_string_very_long() -> None:
    length = 200
    secure_random_string = utils.generate_secure_random_string(length)
    assert len(secure_random_string) == length


def test_generate_secure_random_string_too_short() -> None:
    length = -1
    with pytest.raises(ValueError):
        utils.generate_secure_random_string(length)


# AUTHORISATION CODE HASH


def test_hash_authorisation_code_match() -> None:
    code = "12345678901234567890"
    salt = "1234567890987654321123456789098765432"
    assert utils.hash_ascii_with_salt(code, salt) == utils.hash_ascii_with_salt(
        code, salt
    )


# EXPIRY DATE


def test_calculate_end_of_day_expiry() -> None:
    ACTIVATION_EXPIRY_END_OF_NTH_DAY = 20
    from_datetime = datetime(2001, 1, 5, 6, 3, 5, 12)
    correct_expiry_datetime = datetime(2001, 1, 25, 23, 59, 59)

    expiry_datetime = utils.calculate_end_of_day_expiry(
        from_datetime, ACTIVATION_EXPIRY_END_OF_NTH_DAY
    )

    assert expiry_datetime == correct_expiry_datetime
