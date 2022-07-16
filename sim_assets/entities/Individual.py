from typing import TypedDict, Dict
import json
from sim_assets.entities.Home import Home
from sim_assets.entities.Entity import Entity, EntityConfig


class HomeEquity(TypedDict):
    equity_owned: float
    home_info: Home


class Expense(TypedDict):
    amount: float
    yearly_payments: int
    remove_after: int


class IndividualConfig(EntityConfig):
    income: float
    income_tax: float
    inc_growth_rate: float
    with_polymer: bool
    equity_contr: float


class Individual(Entity):
    def __init__(self, person_id: str, config: IndividualConfig):
        Entity.__init__(self, person_id, config)
        self.config = config
        self.residence: Home = None
        self.expenses: Dict[str, Expense] = dict()

    def get_income(self) -> None:
        self.config['savings'] += (1 - self.config['income_tax']) * self.config['income']

    def add_expense(self, name: str, amount: float, yearly_payments: int, remove_after: int) -> None:
        self.expenses[name] = {
            'amount': amount,
            'yearly_payments': yearly_payments,
            'remove_after': remove_after
        }

    def remove_expense(self, name: str):
        assert name in self.expenses, f"{self.entity_id} does not currently pay for expense {name}"

        del self.expenses[name]

    @classmethod
    def from_json(cls, person_id: str, filename: str) -> 'Individual':
        with open(filename) as f:
            config: IndividualConfig = json.load(f)
            return Individual(person_id, config)
