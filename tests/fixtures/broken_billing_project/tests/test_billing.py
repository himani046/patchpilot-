from src.billing import apply_discount


def test_discount_calculation():
    assert apply_discount(100, 10) == 90


def test_zero_discount():
    assert apply_discount(100, 0) == 100


def test_full_discount():
    assert apply_discount(100, 100) == 0
