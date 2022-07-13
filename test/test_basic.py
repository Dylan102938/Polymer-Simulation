from sim_assets.entities.Home import Home
from sim_assets.entities.Renter import Renter
from sim_assets.entities.HomeOwner import HomeOwner
from sim_assets.env.Environment import Environment


def test_ten_years_rent():
    andy = Renter("andy", {
        "income": 80000,
        "income_tax": 0.3,
        "inc_growth_rate": 0.06,
        "equity_contr": 0.5,
        "savings": 10000,
        "with_polymer": True
    })

    betty = HomeOwner("betty", {
        "savings": 800000,
        "with_polymer": True
    })

    shitty_home = Home("shitty-house", {
        "prop_val": 800000,
        "rent": 36363.63
    })

    betty.purchase_home(shitty_home)
    andy.rent(shitty_home, with_polymer=True)

    print(andy.net_worth())
    print(betty.net_worth())

    # go through 10 years
    for _ in range(10):
        andy.get_income()
        andy.pay_rent()
        andy.purchase_equity('shitty-house', betty, 0.2 * andy.income + 0.1 * andy.savings)
        andy.collect_rent()
        betty.collect_rent()

    print(andy.net_worth())
    print(betty.net_worth())


def test_ten_years_with_env():
    config = {
        'home_appr_rate': 0,
        'default_home_price': 800000,
        'default_rent_rate': 0.04,
        'default_income_appr_rate': 0.04,
        'default_equity_contr': 0.5,
        'tax_brackets': [{'max_amount': 1000000000, 'tax': 0.37}],
        'inflation': 0.025,
        'savings_appr': 0.007,
    }

    env = Environment(config)
    env.add_home(Home("shitty-house", {
        "prop_val": 800000,
        "rent": 36363.63
    }))
    env.add_homeowner(HomeOwner("betty", {
        "savings": 800000,
        "with_polymer": True
    }))
    env.add_renter(Renter("andy", {
        "income": 80000,
        "income_tax": 0.3,
        "inc_growth_rate": 0.06,
        "equity_contr": 0.5,
        "savings": 10000,
        "with_polymer": True
    }))

    env.purchase_home(env.homeowners['betty'], env.homes['shitty-house'])
    env.rent(env.renters['andy'], env.homes['shitty-house'])

    for _ in range(10):
        env.progress_one_year()

    env.print_logs()


def main():
    test_ten_years_with_env()


if __name__ == "__main__":
    main()
