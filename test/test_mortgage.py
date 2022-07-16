from sim_assets.entities.Home import Home
from sim_assets.entities.Individual import Individual
from sim_assets.env.Environment import EnvironmentOld

config = {
    'home_appr_rate': 0.042,
    'default_home_price': 800000,
    'default_rent_rate': 0.04,
    'default_income_appr_rate': 0.04,
    'default_equity_contr': 0.5,
    'tax_brackets': [{'max_amount': 1000000000, 'tax': 0.226}],
}

env = EnvironmentOld("basic", config)
andy = Individual("andy", {
    "income": 50000,
    "income_tax": 0.226,
    "inc_growth_rate": 0.06,
    "equity_contr": 0.5,
    "savings": 10000,
    "with_polymer": False
})
basic_home = Home("basic_home", {
    "prop_val": 800000,
    "rent": 36363.63,
    "savings": 0
})

env.add_home(basic_home)
env.add_renter(andy)
env.add_homeowner(Individual("betty", {
    "income": 0,
    "income_tax": 0.226,
    "inc_growth_rate": 0,
    "equity_contr": 0,
    "savings": 800000,
    "with_polymer": False
}))

env.purchase_home(env.homeowners['betty'], basic_home)
env.rent(andy, basic_home)


def test_mortgage_no_polymer():
    try:
        env.purchase_home(andy, basic_home)
        raise ValueError("Andy should not be able to purchase a house in the beginning")
    except:
        while andy.config['savings'] < 0.2*basic_home.config['prop_val']:
            env.progress_one_year()

        env.bank.issue_mortgage(0.8*basic_home.config['prop_val'], 30, 0.065, andy)
        env.sell_home_equity(env.homeowners['betty'], andy, basic_home)
        del env.renters['andy']

        for _ in range(30):
            env.progress_one_year()

        assert 'mortgage' not in andy.expenses or andy.expenses['mortgage']['remove_after'] == 0

    env.print_logs()


def test_mortgage_polymer():
    andy.with_polymer = True
    test_mortgage_no_polymer()


def main():
    test_mortgage_no_polymer()
    test_mortgage_polymer()


if __name__ == "__main__":
    main()
