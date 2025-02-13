from lkr.load_test.utils import (
    check_random_int_format,
    format_attributes,
    get_user_id,
)


def test_check_random_int_format_valid():
    # Test valid random.randint format
    is_valid, value = check_random_int_format("random.randint(0,100)")
    assert is_valid is True
    assert value.isdigit()
    assert 0 <= int(value) <= 100

    is_valid, value = check_random_int_format("random.randint(1000,2000)")
    assert is_valid is True
    assert value.isdigit()
    assert 1000 <= int(value) <= 2000

    is_valid, value = check_random_int_format("random.randint(0.2,1000000)")
    assert is_valid is False
    assert value is None


def test_check_random_int_format_invalid():
    # Test invalid formats
    test_cases = [
        "random.randint(a,100)",  # Non-integer arguments
        "random.randint(0,b)",  # Non-integer arguments
        "random.randint(0,100",  # Missing closing parenthesis
        "random.randint(0)",  # Missing second argument
        "random.randint",  # Missing arguments
        "random.randint()",  # Empty arguments
        "something_else",  # Completely different format
        "random.randint(0, 100)",  # Extra spaces (not matching exact format)
    ]

    for test_case in test_cases:
        is_valid, value = check_random_int_format(test_case)
        assert is_valid is False
        assert value is None


def test_format_attributes():
    # Test with valid random.randint attributes
    attributes = ["key1:random.randint(0,100)", "key2:random.randint(1000,2000)"]
    formatted = format_attributes(attributes)
    print(formatted)
    assert len(formatted) == 2
    assert int(formatted["key1"]) >= 0 and int(formatted["key1"]) <= 100
    assert int(formatted["key2"]) >= 1000 and int(formatted["key2"]) <= 2000

    # Test with empty list
    assert format_attributes([]) == {}

    # Test with invalid attributes
    invalid_attributes = [
        "key1",  # Missing value
        "key2:",  # Empty value
        ":value",  # Missing key
        ":",  # Empty key and value
    ]
    formatted = format_attributes(invalid_attributes)
    assert formatted == {}


def test_get_user_id():
    user_id = get_user_id()
    assert user_id.startswith("embed-")
    assert len(user_id) == 16  # "embed-" + 10 digits
    assert user_id[6:].isdigit()  # Check if the part after "embed-" is all digits

    # Test uniqueness
    user_ids = [get_user_id() for _ in range(100)]
    assert len(set(user_ids)) == 100  # All IDs should be unique
