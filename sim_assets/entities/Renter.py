from sim_assets.entities.HomeOwner import HomeOwnerConfig, HomeOwner
from sim_assets.entities.Home import Home


class RenterConfig(HomeOwnerConfig):
    income: float
    income_tax: float
    inc_growth_rate: float
    equity_contr: float


class Renter(HomeOwner):
    def __init__(self, renter_id: str, config: RenterConfig):
        HomeOwner.__init__(self, renter_id, config)
        self.config = config
        self.income = config['income']
        self.residence: Home = None

    def get_income(self) -> None:
        self.savings += (1 - self.config['income_tax']) * self.income

    def rent(self, home: Home) -> None:
        self.residence = home
        if self.config['with_polymer']:
            self.homes_owned[home.entity_id] = {'equity_owned': 0, 'home_info': home}

    def pay_rent(self) -> float:
        return self.pay(self.residence.rent, self.residence, "rent")

