from typing import Dict, TypedDict, List
import json

from sim_assets.entities.Individual import Individual
from sim_assets.entities.Home import Home
from sim_assets.entities.Bank import Bank


class TaxBracket(TypedDict):
    max_amount: float
    tax: float


class EnvironmentConfig(TypedDict):
    home_appr_rate: float
    tax_brackets: List[TaxBracket]
    default_home_price: float
    default_rent_rate: float
    default_income_appr_rate: float
    default_equity_contr: float


class HomeLogs(TypedDict):
    prop_val: float
    rent: float


class IndividualLogs(TypedDict):
    net_worth: float
    savings: float


class Log(TypedDict):
    homes: Dict[str, HomeLogs]
    individuals: Dict[str, IndividualLogs]


class Environment:
    def __init__(self, env_id, config: EnvironmentConfig):
        self.env_id = env_id
        self.config = config

        self.homes: Dict[str, Home] = dict()
        self.homeowners: Dict[str, Individual] = dict()
        self.renters: Dict[str, Individual] = dict()
        self.bank: Bank = Bank(self.env_id + "-bank")

        self.home_map: Dict[str, Dict[str, float]] = dict()
        self.rentals_map: Dict[str, Individual] = dict()

        self.logs: List[Log] = []

    @classmethod
    def from_json(cls, env_id: str, filename: str) -> 'Environment':
        with open(filename) as f:
            config: EnvironmentConfig = json.load(f)
            return Environment(env_id, config)

    def add_home(self, home: Home) -> None:
        assert home.entity_id not in self.homes, f"Home {home.entity_id} is already part of this environment"
        self.homes[home.entity_id] = home
        self.home_map[home.entity_id] = dict()

    def add_homeowner(self, owner: Individual) -> None:
        assert owner.entity_id not in self.homes, f"Homeowner {owner.entity_id} is already part of this environment"
        self.homeowners[owner.entity_id] = owner

    def add_renter(self, renter: Individual) -> None:
        assert renter.entity_id not in self.renters, f"Renter {renter.entity_id} is already part of this environment"
        self.renters[renter.entity_id] = renter

        if renter.entity_id not in self.homeowners:
            self.homeowners[renter.entity_id] = renter

    def rent(self, renter: Individual, home: Home) -> None:
        assert renter.entity_id in self.renters, f"Renter {renter.entity_id} is not a part of the environment"
        if home.entity_id not in self.rentals_map:
            self.rentals_map[home.entity_id] = renter

        curr_renter = self.rentals_map[home.entity_id]
        curr_renter.residence = None
        renter.residence = home
        self.rentals_map[home.entity_id] = renter

    def collect_rent(self, renter: Individual, home: Home) -> None:
        assert renter.entity_id in self.renters, f"Renter {renter.entity_id} is not a part of the environment"
        assert home.entity_id in self.homes, f"Home {home.entity_id} is not a part of the environment"
        if renter.residence != home:
            return

        for owner_key in self.home_map[home.entity_id]:
            owner = self.homeowners[owner_key]
            if owner.entity_id == renter.entity_id:
                continue

            equity = self.home_map[home.entity_id][owner_key]
            renter.pay(equity * home.config['rent'], owner, "rent")

    def get_equity_in_home(self, owner: Individual, home: Home) -> float:
        assert owner.entity_id in self.homeowners, f"{owner.entity_id} is not a part of the environment"

        if owner.entity_id not in self.home_map[home.entity_id]:
            return 0

        return self.home_map[home.entity_id][owner.entity_id]

    def purchase_home(self, purchaser: Individual, home: Home) -> None:
        assert purchaser.entity_id in self.homeowners, f"{purchaser.entity_id} is not a part of the environment"

        if len(self.home_map[home.entity_id]) == 0:
            purchaser.pay(home.config['prop_val'], self.bank, f"purchasing home {home}")
            self.home_map[home.entity_id][purchaser.entity_id] = 1
            return

        if purchaser.entity_id not in self.home_map[home.entity_id]:
            self.home_map[home.entity_id][purchaser.entity_id] = 0

        for owner_key in self.home_map[home.entity_id]:
            if owner_key == purchaser.entity_id:
                continue

            owner = self.homeowners[owner_key]
            self.purchase_home_equity(owner, purchaser, home)

    def purchase_home_equity(self, seller: Individual, purchaser: Individual, home: Home, percent_of_equity: float = 1) -> None:
        assert seller.entity_id in self.homeowners, f"{seller.entity_id} is not a part of the environment"
        assert purchaser.entity_id in self.homeowners, f"{purchaser.entity_id} is not a part of the environment"
        assert seller.entity_id in self.home_map[home.entity_id], f"{seller.entity_id} does not own home {home.entity_id}"
        assert percent_of_equity >= 0, f"Must purchase a non-negative amount of equity"

        amount = percent_of_equity * self.home_map[home.entity_id][seller.entity_id] * home.config['prop_val']
        purchaser.pay(amount, seller, f"{percent_of_equity * self.home_map[home.entity_id][seller.entity_id]} equity in home {home.entity_id}")
        if purchaser.entity_id not in self.home_map[home.entity_id]:
            self.home_map[home.entity_id][purchaser.entity_id] = 0

        original_seller_equity = self.home_map[home.entity_id][seller.entity_id]
        self.home_map[home.entity_id][seller.entity_id] -= percent_of_equity * original_seller_equity
        self.home_map[home.entity_id][purchaser.entity_id] += percent_of_equity * original_seller_equity


class EnvironmentOld:
    def __init__(self, env_id: str, config: EnvironmentConfig):
        self.config = config
        self.env_id = env_id
        self.homes: Dict[str, Home] = dict()
        self.homeowners: Dict[str, Individual] = dict()
        self.renters: Dict[str, Individual] = dict()
        self.bank: Bank = Bank(self.env_id + "-bank")
        self.garbage: Bank = Bank("")

        self.home_map: Dict[str, Dict[str, float]] = dict()

        self.logs: List[Log] = []

    def add_home(self, home: Home) -> None:
        assert home.entity_id not in self.homes, f"Home {home.entity_id} is already part of this environment"
        self.homes[home.entity_id] = home

    def add_homeowner(self, owner: Individual) -> None:
        assert owner.entity_id not in self.homes, f"Homeowner {owner.entity_id} is already part of this environment"
        self.homeowners[owner.entity_id] = owner

    def add_renter(self, renter: Individual) -> None:
        assert renter.entity_id not in self.homes, f"Renter {renter.entity_id} is already part of this environment"
        self.renters[renter.entity_id] = renter

        if renter.entity_id not in self.homeowners:
            self.homeowners[renter.entity_id] = renter

    def purchase_home(self, purchaser: Individual, home: Home) -> None:
        assert purchaser.entity_id in self.homeowners and home.entity_id in self.homes, f"Could not complete home " \
                                                                                        f"purchase as entities" \
                                                                                        f" are outside environment "
        assert home.config['prop_val'] <= purchaser.config['savings'], f"{purchaser.entity_id} does not have enough saved to purchase home {home.entity_id} "

        purchaser.config['savings'] -= home.config['prop_val']
        self.home_map[home.entity_id] = {purchaser.entity_id: 1}

        print(f"LOG: {purchaser.entity_id} purchased home {home.entity_id}")

    def sell_home_equity(self, seller: Individual, purchaser: Individual, home: Home) -> None:
        assert seller.entity_id in self.home_map[home.entity_id], f"{seller.entity_id} does not own home {home.entity_id}"

        equity = self.home_map[home.entity_id][seller.entity_id]
        price = equity * home.config['prop_val']
        purchaser.pay(price, seller, f"{equity} in {home.entity_id}")
        self.home_map[home.entity_id][seller.entity_id] -= equity
        if purchaser.entity_id in self.home_map[home.entity_id]:
            self.home_map[home.entity_id][purchaser.entity_id] += equity
        else:
            self.home_map[home.entity_id][purchaser.entity_id] = equity

    def rent(self, renter: Individual, home: Home):
        assert renter.entity_id in self.renters and home.entity_id in self.homes, f"Could not complete home purchase " \
                                                                                  f"as entities are outside " \
                                                                                  f"environment "
        assert home.entity_id in self.home_map, f"Home is not currently being owned by an owner in the environment"
        renter.residence = home
        self.home_map[home.entity_id][renter.entity_id] = 0

        print(f"LOG: {renter.entity_id} is renting at home {home.entity_id}")

    def progress_one_year(self) -> Log:
        for owner in self.homeowners.values():
            owner.get_income()

        self.process_expenses()
        self.process_rent()
        self.appreciate_income()
        self.appreciate_homes()
        self.contribute_equities()

        log: Log = {
            'homes': dict(),
            'individuals': dict(),
        }

        for home in self.homes.values():
            log['homes'][home.entity_id] = {'prop_val': home.config['prop_val'], 'rent': home.config['rent']}
        for homeowner in self.homeowners.values():
            log['individuals'][homeowner.entity_id] = {
                'net_worth': self.get_net_worth(homeowner),
                'savings': homeowner.config['savings']
            }

        self.logs.append(log)
        return log

    def appreciate_homes(self) -> None:
        for home in self.homes.values():
            home.config['prop_val'] += self.config['home_appr_rate'] * home.config['prop_val']
            home.config['rent'] += self.config['home_appr_rate'] * home.config['rent']

    def process_rent(self) -> None:
        for renter in self.renters.values():
            if renter.residence is None:
                continue

            home = renter.residence
            owners_equity = self.home_map[home.entity_id]
            for owner_id in owners_equity:
                owner = self.homeowners[owner_id]
                renter.pay(owners_equity[owner_id] * home.config['rent'], owner, "rent")

    def process_expenses(self) -> None:
        for owner in self.homeowners.values():
            for expense_key in owner.expenses:
                expense = owner.expenses[expense_key]
                if expense['remove_after'] == 0:
                    owner.remove_expense(expense_key)

                owner.pay(expense['amount'] * expense['yearly_payments'], self.garbage, expense_key)
                if expense['remove_after'] > 0:
                    expense['remove_after'] -= 1

    def appreciate_income(self) -> None:
        for owner in self.homeowners.values():
            self.appreciate_ind_income(owner)

    def appreciate_ind_income(self, owner: Individual) -> None:
        owner.config['income'] += owner.config['inc_growth_rate'] * owner.config['income']
        owner.config['income_tax'] = self.get_tax_bracket(owner)

    def get_tax_bracket(self, owner: Individual) -> float:
        for bracket in self.config['tax_brackets']:
            if owner.config['income'] <= bracket['max_amount']:
                return bracket['tax']

    def contribute_equities(self) -> None:
        for renter in self.renters.values():
            home = renter.residence
            if home is None or not renter.config['with_polymer']:
                continue

            owners_equity = self.home_map[home.entity_id]
            amount_to_contr = renter.config['equity_contr'] * renter.config['savings']
            equity_to_contr = amount_to_contr / (home.config['prop_val'] * 1.1)

            for owner_id in owners_equity:
                if owner_id == renter.entity_id:
                    continue

                equity_to_take = equity_to_contr * (owners_equity[owner_id] / (1 - owners_equity[renter.entity_id]))
                renter.pay(
                    equity_to_take * home.config['prop_val'] * 1.1,
                    self.homeowners[owner_id],
                    f"{equity_to_take} equity in home {home.entity_id}"
                )
                owners_equity[owner_id] -= equity_to_take
                owners_equity[renter.entity_id] += equity_to_take

    def print_logs(self) -> None:
        print(json.dumps(self.logs, indent=4))

    def get_net_worth(self, individual: Individual):
        net_worth = individual.config['savings']
        for home_id in self.home_map:
            if individual.entity_id in self.home_map[home_id]:
                net_worth += self.home_map[home_id][individual.entity_id] * self.homes[home_id].config['prop_val']

        return net_worth

    @classmethod
    def from_json(cls, env_id: str, filename: str) -> 'Environment':
        with open(filename) as f:
            config: EnvironmentConfig = json.load(f)
            return Environment(env_id, config)
