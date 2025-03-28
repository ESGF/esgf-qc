import pytest

from compliance_checker.checks.variable_checks.check_variable_existence import check_variable_existence

TEST_CHECK_VARIABLE_EXISTENCE = [
    ("variable_exists", "variable_checks_test_ds", "time", (1, 1), []),
    ("variable_does_not_exist", "variable_checks_test_ds", "novar", (0, 1), ["Variable 'novar' is missing"]),
]


@pytest.mark.parametrize(
    "test_id,ds_fixture_name,var_name,expected_value,expected_msgs",
    TEST_CHECK_VARIABLE_EXISTENCE,
    ids=[t[0] for t in TEST_CHECK_VARIABLE_EXISTENCE],
)
def test_check_variable_existence(request, test_id, ds_fixture_name, var_name, expected_value, expected_msgs):
    # Use pytest built-in 'request' fixture to retrieve dataset fixture.
    ds = request.getfixturevalue(ds_fixture_name)

    # Produce result for current test input.
    # Pass test_id as check_id.
    results = check_variable_existence(ds, var_name, check_id=test_id)

    # Check against expected result.
    assert len(results) == 1
    assert results[0].name.endswith("Variable Existence Check")
    assert results[0].msgs == expected_msgs
    assert results[0].value == expected_value
    if results[0].value[0] != results[0].value[1]:
        # Failed result must have check_id (== test_id) in name
        assert test_id in results[0].name
