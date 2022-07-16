import pytest
from sim_assets.entities.Home import Home
from sim_assets.entities.Individual import Individual
from sim_assets.env.Environment import Environment

home: Home = None
ind: Individual = None
owner: Individual = None
env: Environment = None


def setup():
    global home, ind, owner, env
    home = Home("home", {"prop_val": 800000, "rent": 36000, "savings": 0})
    ind = Individual.from_json("ind", "../configs/new-grad.json")
    owner = Individual.from_json("owner", "../configs/junior-swe.json")
    env = Environment.from_json("env", "../configs/basic-env.json")

    env.add_home(home)
    env.add_homeowner(ind)
    env.add_homeowner(owner)


def test_single_purchase():
    setup()
    owner.config['savings'] = 800000
    env.purchase_home(owner, home)

    assert owner.config['savings'] == 0
    assert env.get_equity_in_home(owner, home) == 1


def test_purchase_fail():
    setup()
    with pytest.raises(Exception) as e_info:
        env.purchase_home(owner, home)
        print(e_info)


def test_sell_home_equity():
    setup()
    owner.config['savings'] = 800000
    ind.config['savings'] = 800000
    env.purchase_home(owner, home)

    env.purchase_home_equity(owner, ind, home)

    assert owner.config['savings'] == 800000
    assert ind.config['savings'] == 0

    assert env.get_equity_in_home(owner, home) == 0
    assert env.get_equity_in_home(ind, home) == 1


def test_sell_home_equity_fail():
    setup()
    owner.config['savings'] = 800000

    env.purchase_home(owner, home)

    with pytest.raises(Exception) as e_info:
        env.purchase_home_equity(owner, ind, home)
        print(e_info)


def test_sell_home():
    setup()
    owner.config['savings'] = 800000
    env.purchase_home(owner, home)

    ind.config['savings'] = 800000
    env.purchase_home(ind, home)

    assert owner.config['savings'] == 800000
    assert ind.config['savings'] == 0

    assert env.get_equity_in_home(owner, home) == 0
    assert env.get_equity_in_home(ind, home) == 1


def test_sell_partial_equity():
    setup()
    owner.config['savings'] = 800000
    env.purchase_home(owner, home)

    ind.config['savings'] = 400000
    env.purchase_home_equity(owner, ind, home, 0.5)

    assert owner.config['savings'] == 400000
    assert ind.config['savings'] == 0

    assert env.get_equity_in_home(owner, home) == 0.5
    assert env.get_equity_in_home(ind, home) == 0.5


def test_sell_home_with_multiple_owners():
    setup()
    owner.config['savings'] = 800000
    env.purchase_home(owner, home)
    owner2 = Individual.from_json("owner-2", "../configs/junior-swe.json")
    owner2.config['savings'] = 400000
    env.add_homeowner(owner2)
    env.purchase_home_equity(owner, owner2, home, 0.5)

    assert env.get_equity_in_home(owner, home) == 0.5
    assert env.get_equity_in_home(owner2, home) == 0.5

    owner_savings = owner.config['savings']
    owner2_savings = owner2.config['savings']

    ind.config['savings'] = 800000
    env.purchase_home(ind, home)

    assert owner.config['savings'] - owner_savings == 400000
    assert owner2.config['savings'] - owner2_savings == 400000
    assert ind.config['savings'] == 0

    assert env.get_equity_in_home(owner, home) == 0
    assert env.get_equity_in_home(owner2, home) == 0
    assert env.get_equity_in_home(ind, home) == 1


def test_sell_home_with_100_owners():
    setup()
    owner.config['savings'] = 800000
    env.purchase_home(owner, home)
    for i in range(100):
        percentage = 0.01 / env.get_equity_in_home(owner, home)
        env.add_homeowner(Individual.from_json(f"owner-{i}", "../configs/junior-swe.json"))
        env.purchase_home_equity(owner, env.homeowners[f'owner-{i}'], home, percentage)

    ind.config['savings'] = 800000
    for i in range(50):
        env.purchase_home_equity(env.homeowners[f'owner-{i}'], ind, home)

    assert abs(0.5 - env.get_equity_in_home(ind, home)) < 0.001

    env.purchase_home(ind, home)

    assert abs(1 - env.get_equity_in_home(ind, home)) < 0.001
    assert env.get_equity_in_home(owner, home) == 0

    for i in range(100):
        assert env.get_equity_in_home(env.homeowners[f'owner-{i}'], home) == 0


def main():
    test_single_purchase()
    test_purchase_fail()
    test_sell_home_equity()
    test_sell_home_equity_fail()
    test_sell_home()
    test_sell_partial_equity()
    test_sell_home_with_multiple_owners()


if __name__ == "__main__":
    main()
