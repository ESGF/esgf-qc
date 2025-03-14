import pytest

from compliance_checker.checks.check_variable_existence import check_variable_existence

TEST_CHECK_VARIABLE_EXISTENCE = [
    ("variable_exists", "checks_test_ds", "time", (1, 1)),
    ("variable_does_not_exist", "checks_test_ds", "novar", (0, 1)),
]


@pytest.mark.parametrize(
    "test_id,ds_fixture,var_name,expected_value",
    TEST_CHECK_VARIABLE_EXISTENCE,
    ids=[t[0] for t in TEST_CHECK_VARIABLE_EXISTENCE],
)
def test_check_variable_existence(request, test_id, ds_fixture, var_name, expected_value):
    ds = request.getfixturevalue(ds_fixture)
    results = check_variable_existence(ds, var_name, check_id=test_id)
    assert len(results) == 1
    assert results[0].name.endswith("Variable Existence Check")
    assert results[0].value == expected_value
    if results[0].value[0] != results[0].value[1]:
        assert test_id in results[0].name
