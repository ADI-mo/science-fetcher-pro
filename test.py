import pytest
from calculator_logic import growth_rate, calculate_doubling_time, calculate_cfu_from_plate

TOLERANCE = 1e-4

def test_calculate_cfu_from_plate_standard():
    """Test standard calculation: 50 colonies, 10^4 dilution, 0.1ml plated"""
    # 50 * 10,000 / 0.1 = 5,000,000
    res = calculate_cfu_from_plate(50, 10000, 0.1)
    assert abs(res - 5000000.0) < TOLERANCE

def test_calculate_cfu_from_plate_zero_vol_raises():
    with pytest.raises(ValueError):
        calculate_cfu_from_plate(50, 100, 0)

def test_growth_rate_standard():
    k_result = growth_rate(100000.0, 1000.0, 5.0)
    # log2(100) / 5 = 6.6438 / 5 = 1.3287
    assert abs(k_result - 1.32877) < TOLERANCE

def test_doubling_time():
    assert calculate_doubling_time(1.0) == 1.0
    assert calculate_doubling_time(2.0) == 0.5