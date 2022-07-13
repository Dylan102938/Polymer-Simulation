from typing import TypedDict
from sim_assets.entities.Home import Home
from sim_assets.entities.Entity import Entity


class HomeEquity(TypedDict):
    equity_owned: float
    home_info: Home


class HomeOwnerConfig(TypedDict):
    income: float
    income_tax: float
    inc_growth_rate: float
    savings: float
    with_polymer: bool
    equity_contr: float


class HomeOwner(Entity):
    def __init__(self, person_id: str, config: HomeOwnerConfig):
        Entity.__init__(self, person_id, config['savings'])
        self.config = config
        self.income = config['income']
        self.residence: Home = None
        self.with_polymer = config['with_polymer']

    def get_income(self) -> None:
        self.savings += (1 - self.config['income_tax']) * self.income
