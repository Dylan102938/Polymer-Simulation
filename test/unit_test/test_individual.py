import pytest
from sim_assets.entities.Individual import  Individual


def test_income():
    a = Individual.from_json("a", "../configs/new-grad.json")
    a.get_income()

    assert a.savings == (1 - a.config['income_tax']) * 80000 + 10000


def test_add_expense():
    a = Individual.from_json("a", "../configs/new-grad.json")
    a.add_expense('test', 10000, 5, 3)

    assert len(a.expenses) == 1 and a.expenses['test'] == {'amount': 10000, 'yearly_payments': 5, 'remove_after': 3}


def test_remove_expense():
    a = Individual.from_json("a", "../configs/new-grad.json")
    with pytest.raises(Exception) as e_info:
        a.remove_expense("test")
        print(e_info)

    a.add_expense('test', 10000, 5, 3)
    a.remove_expense('test')

    assert len(a.expenses) == 0


def main():
    test_income()
    test_add_expense()
    test_remove_expense()


if __name__ == "__main__":
    main()
