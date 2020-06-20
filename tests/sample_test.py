import pytest


@pytest.mark.run(order=4)
def test_dummy():
    assert True


@pytest.mark.run(order=1)
def test_dummy_sec():
    assert True


@pytest.mark.run(order=2)
def test_dummy_tw():
    assert True


@pytest.mark.run(order=6)
def test_dummy_six():
    assert True
