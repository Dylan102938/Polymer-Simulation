from sim_assets.entities.Home import Home
from sim_assets.entities.Renter import Renter
from sim_assets.entities.HomeOwner import HomeOwner


def test_ten_years_rent():
    andy = Renter("andy", {
        "income": 80000,
        "inc_growth_rate": 0.06,
        "equity_contr": 0.5,
        "savings": 10000
    })

    betty = HomeOwner("betty", {
        "savings": 10000
    })

    shitty_home = Home("shitty-house", {
        "prop_val": 800000,
        "rent": 36363.63,
        "other_owners": dict()
    })

    betty.purchase_home(shitty_home)
    andy.rent(shitty_home, with_polymer=True)

    print(andy.net_worth())
    print(betty.net_worth())

    # go through 10 years
    for _ in range(10):
        andy.get_income()
        andy.contribute_equity(0.2 * andy.income + 0.1 * andy.savings)
        shitty_home.collect_rent()

    print(andy.net_worth())
    print(betty.net_worth())


def main():
    test_ten_years_rent()


if __name__ == "__main__":
    main()
