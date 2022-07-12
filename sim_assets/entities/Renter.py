from Home import Home
from HomeOwner import HomeOwnerConfig, HomeOwner


class RenterConfig(HomeOwnerConfig):
    income: float
    inc_growth_rate: float
    equity_contr: float


class Renter(HomeOwner):
    def __init__(self, renter_id: str, config: RenterConfig):
        HomeOwner.__init__(self, renter_id, config)
        self.income = config['income']
        self.residence = None

    def get_income(self) -> None:
        self.savings += self.income

    def rent(self, home: Home, with_polymer=False) -> None:
        assert home.renter is None, f"{self.person_id} cannot rent home {home.home_id} because someone already is " \
                                    f"renting it. "

        self.residence = home
        home.renter = self
        if with_polymer:
            self.homes_owned[home.home_id] = {'equity_owned': 0, 'home_info': home}
            home.other_owners[self.person_id] = self

    def contribute_equity(self, amount: float):
        assert self.residence.home_id in self.homes_owned, f"Cannot contribute equity to house {self.residence} because {self.person_id} does not have equity"

        self.residence.add_equity(self, amount)
