import pytest
from sim_assets.entities.Individual import Individual


def test_sanity():
    new_grad = Individual.from_json("new-grad", "../configs/new-grad.json")
    swe = Individual.from_json("swe", "../configs/junior-swe.json")

    assert new_grad.savings == 10000 and swe.savings == 30000

    new_grad.pay(5000, swe, "test")

    assert new_grad.savings == 5000 and swe.savings == 35000


def test_overpay():
    new_grad = Individual.from_json("new-grad", "../configs/new-grad.json")
    swe = Individual.from_json("swe", "../configs/junior-swe.json")

    with pytest.raises(Exception) as e_info:
        new_grad.pay(10000.01, swe, "test overpay")


def test_pay_negative():
    new_grad = Individual.from_json("new-grad", "../configs/new-grad.json")
    swe = Individual.from_json("swe", "../configs/junior-swe.json")

    with pytest.raises(Exception) as e_info:
        new_grad.pay(-10000, swe, "test negative pay")
        print(e_info)


def test_rounding():
    new_grad = Individual.from_json("new-grad", "../configs/new-grad.json")
    swe = Individual.from_json("swe", "../configs/junior-swe.json")

    new_grad.pay(0.001, swe, "test rounding")

    assert new_grad.savings == 10000 and swe.savings == 30000


def main():
    test_sanity()
    test_overpay()
    test_pay_negative()
    test_rounding()


if __name__ == "__main__":
    main()
