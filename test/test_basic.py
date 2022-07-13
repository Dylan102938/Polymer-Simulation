from sim_assets.entities.Home import Home
from sim_assets.entities.HomeOwner import HomeOwner
from sim_assets.env.Environment import Environment


def test_ten_years_without_polymer():
    config = {
        'home_appr_rate': 0.06,
        'default_home_price': 800000,
        'default_rent_rate': 0.04,
        'default_income_appr_rate': 0.04,
        'default_equity_contr': 0.5,
        'tax_brackets': [{'max_amount': 1000000000, 'tax': 0.226}],
    }

    env = Environment(config)
    env.add_home(Home("shitty-house", {
        "prop_val": 800000,
        "rent": 36363.63
    }))
    env.add_home(Home("shitty-house-2", {
        "prop_val": 800000,
        "rent": 0
    }))
    env.add_renter(HomeOwner("betty", {
        "income": 0,
        "income_tax": 0,
        "inc_growth_rate": 0,
        "equity_contr": 1,
        "savings": 800000,
        "with_polymer": True
    }))
    env.add_renter(HomeOwner("andy", {
        "income": 90000,
        "income_tax": 0.226,
        "inc_growth_rate": 0.06,
        "equity_contr": 0.5,
        "savings": 40000,
        "with_polymer": False
    }))
    env.add_homeowner(HomeOwner("charlie", {
        "income": 0,
        "income_tax": 0,
        "inc_growth_rate": 0,
        "equity_contr": 1,
        "savings": 800000,
        "with_polymer": True
    }))

    print()

    env.purchase_home(env.homeowners['betty'], env.homes['shitty-house'])
    env.purchase_home(env.homeowners['charlie'], env.homes['shitty-house-2'])
    env.rent(env.renters['andy'], env.homes['shitty-house'])
    env.rent(env.renters['betty'], env.homes['shitty-house-2'])

    for _ in range(10):
        env.progress_one_year()

    env.print_logs()


def test_ten_years_with_polymer_reinvest():
    config = {
        'home_appr_rate': 0.06,
        'default_home_price': 800000,
        'default_rent_rate': 0.04,
        'default_income_appr_rate': 0.04,
        'default_equity_contr': 0.5,
        'tax_brackets': [{'max_amount': 1000000000, 'tax': 0.226}],
    }

    env = Environment(config)
    env.add_home(Home("shitty-house", {
        "prop_val": 800000,
        "rent": 36363.63
    }))
    env.add_home(Home("shitty-house-2", {
        "prop_val": 800000,
        "rent": 0
    }))
    env.add_renter(HomeOwner("betty", {
        "income": 0,
        "income_tax": 0,
        "inc_growth_rate": 0,
        "equity_contr": 1,
        "savings": 800000,
        "with_polymer": True
    }))
    env.add_renter(HomeOwner("andy", {
        "income": 90000,
        "income_tax": 0.226,
        "inc_growth_rate": 0.06,
        "equity_contr": 0.5,
        "savings": 40000,
        "with_polymer": True
    }))
    env.add_homeowner(HomeOwner("charlie", {
        "income": 0,
        "income_tax": 0,
        "inc_growth_rate": 0,
        "equity_contr": 1,
        "savings": 800000,
        "with_polymer": True
    }))

    env.purchase_home(env.homeowners['betty'], env.homes['shitty-house'])
    env.purchase_home(env.homeowners['charlie'], env.homes['shitty-house-2'])
    env.rent(env.renters['andy'], env.homes['shitty-house'])
    env.rent(env.renters['betty'], env.homes['shitty-house-2'])

    for _ in range(10):
        env.progress_one_year()

    env.print_logs()


def main():
    test_ten_years_without_polymer()
    test_ten_years_with_polymer_reinvest()


if __name__ == "__main__":
    main()
