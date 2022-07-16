import pytest
import random

from sim_assets.entities.Home import Home
from sim_assets.entities.Individual import Individual
from sim_assets.env.Environment import Environment

home: Home = None
owner: Individual = None
renter: Individual = None
env: Environment = None


def setup():
    global home, owner, renter, env
    home = Home.from_json("basic-home", "../configs/basic-home.json")
    owner = Individual.from_json("owner", "../configs/junior-swe.json")
    renter = Individual.from_json("renter", "../configs/new-grad.json")

    env = Environment.from_json("basic-env", "../configs/basic-env.json")
    env.add_home(home)
    env.add_homeowner(owner)
    env.add_renter(renter)

    owner.config['savings'] = 800000
    env.purchase_home(owner, home)
    renter.config['savings'] = 100000


def test_basic_rent():
    setup()
    env.rent(renter, home)

    assert renter.residence == home

    renter_savings = renter.config['savings']
    env.collect_rent(renter, home)
    assert renter_savings - renter.config['savings'] == home.config['rent']


def test_rent_fail():
    setup()
    renter2 = Individual.from_json("renter-2", "../configs/new-grad.json")
    with pytest.raises(Exception) as e_info:
        env.rent(renter2, home)
        print(e_info)


def test_replace_existing_renter():
    setup()
    renter2 = Individual.from_json("renter-2", "../configs/new-grad.json")
    env.rent(renter, home)

    assert renter.residence == home and renter2.residence is None

    renter_savings = renter.config['savings']
    renter2_savings = renter2.config['savings']
    env.collect_rent(renter, home)

    assert renter_savings - renter.config['savings'] == home.config['rent']
    assert renter2.config['savings'] - renter2_savings == 0


def test_renter_purchase_home_equity():
    setup()
    env.rent(renter, home)

    renter.config['savings'] = 800000
    renter_savings = renter.config['savings']

    env.purchase_home_equity(owner, renter, home, 0.1)
    env.collect_rent(renter, home)

    assert env.get_equity_in_home(renter, home) == 0.1
    assert renter_savings - renter.config['savings'] == 0.1 * home.config['prop_val'] + 0.9 * home.config['rent']
    assert env.get_equity_in_home(owner, home) == 0.9


def test_renter_purchase_home():
    setup()
    env.rent(renter, home)

    renter_savings = renter.config['savings']
    env.collect_rent(renter, home)

    assert renter_savings - renter.config['savings'] == home.config['rent']

    renter.config['savings'] = 900000
    env.purchase_home(renter, home)
    env.collect_rent(renter, home)

    assert renter.config['savings'] == 100000


def test_robust_renting():
    setup()
    env.rent(renter, home)

    owner_savings = []
    for i in range(10):
        percentage = random.uniform(0, 1)
        env.add_homeowner(Individual.from_json(f"owner-{i}", "../configs/junior-swe.json"))
        env.homeowners[f"owner-{i}"].config['savings'] = 800000
        env.purchase_home_equity(owner, env.homeowners[f'owner-{i}'], home, percentage)
        owner_savings.append(env.homeowners[f"owner-{i}"].config['savings'])

    renter_savings = renter.config['savings']
    env.collect_rent(renter, home)

    for i in range(10):
        owner_i = env.homeowners[f"owner-{i}"]
        assert abs(owner_i.config['savings'] - owner_savings[i] - env.get_equity_in_home(owner_i, home) * home.config['rent']) < 0.005
        owner_savings[i] = owner_i.config['savings']

    assert abs(renter_savings - renter.config['savings'] - home.config['rent']) < 0.001 * home.config['rent']

    renter.config['savings'] = 1000000
    for i in range(3):
        owner_i = env.homeowners[f"owner-{i}"]
        env.purchase_home_equity(owner_i, renter, home)
        owner_savings[i] = owner_i.config['savings']

    env.collect_rent(renter, home)

    for i in range(3):
        owner_i = env.homeowners[f"owner-{i}"]
        assert abs(owner_i.config['savings'] - owner_savings[i]) < 0.001
        owner_savings[i] = owner_i.config['savings']

    for i in range(3, 10):
        owner_i = env.homeowners[f"owner-{i}"]
        assert abs(owner_i.config['savings'] - owner_savings[i] - env.get_equity_in_home(owner_i, home) * home.config['rent']) < 0.005
        owner_savings[i] = owner_i.config['savings']

    env.purchase_home(renter, home)
    for i in range(10):
        owner_i = env.homeowners[f"owner-{i}"]
        owner_savings[i] = owner_i.config['savings']

    env.collect_rent(renter, home)
    for i in range(10):
        owner_i = env.homeowners[f"owner-{i}"]
        assert abs(owner_i.config['savings'] - owner_savings[i]) < 0.005


def main():
    test_basic_rent()
    test_rent_fail()
    test_replace_existing_renter()
    test_renter_purchase_home_equity()
    test_renter_purchase_home()
    test_robust_renting()


if __name__ == "__main__":
    main()
