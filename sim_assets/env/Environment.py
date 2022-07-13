from typing import Dict, TypedDict, List
import json

from sim_assets.entities.HomeOwner import HomeOwner
from sim_assets.entities.Home import Home


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
    def __init__(self, config: EnvironmentConfig):
        self.config = config
        self.homes: Dict[str, Home] = dict()
        self.homeowners: Dict[str, HomeOwner] = dict()
        self.renters: Dict[str, HomeOwner] = dict()

        self.home_map: Dict[str, Dict[str, float]] = dict()

        self.logs: List[Log] = []

    def add_home(self, home: Home) -> None:
        assert home.entity_id not in self.homes, f"Home {home.entity_id} is already part of this environment"
        self.homes[home.entity_id] = home

    def add_homeowner(self, owner: HomeOwner) -> None:
        assert owner.entity_id not in self.homes, f"Homeowner {owner.entity_id} is already part of this environment"
        self.homeowners[owner.entity_id] = owner

    def add_renter(self, renter: HomeOwner) -> None:
        assert renter.entity_id not in self.homes, f"Renter {renter.entity_id} is already part of this environment"
        self.renters[renter.entity_id] = renter

        if renter.with_polymer and renter.entity_id not in self.homeowners:
            self.homeowners[renter.entity_id] = renter

    def purchase_home(self, purchaser: HomeOwner, home: Home) -> None:
        assert purchaser.entity_id in self.homeowners and home.entity_id in self.homes, f"Could not complete home " \
                                                                                        f"purchase as entities" \
                                                                                        f" are outside environment "
        assert home.prop_val <= purchaser.savings, f"{purchaser.entity_id} does not have enough saved to purchase home {home.entity_id} "

        purchaser.savings -= home.prop_val
        self.home_map[home.entity_id] = {purchaser.entity_id: 1}

        print(f"LOG: {purchaser.entity_id} purchased home {home.entity_id}")

    def rent(self, renter: HomeOwner, home: Home):
        assert renter.entity_id in self.renters and home.entity_id in self.homes, f"Could not complete home purchase " \
                                                                                  f"as entities are outside " \
                                                                                  f"environment "
        assert home.entity_id in self.home_map, f"Home is not currently being owned by an owner in the environment"
        renter.residence = home
        if renter.with_polymer:
            self.home_map[home.entity_id][renter.entity_id] = 0

        print(f"LOG: {renter.entity_id} is renting at home {home.entity_id}")

    def progress_one_year(self) -> Log:
        for renter in self.renters.values():
            renter.get_income()

        self.process_rent()
        self.contribute_equities()
        self.appreciate_income()
        self.appreciate_homes()

        log: Log = {
            'homes': dict(),
            'individuals': dict(),
        }

        for home in self.homes.values():
            log['homes'][home.entity_id] = {'prop_val': home.prop_val, 'rent': home.rent}
        for homeowner in self.homeowners.values():
            log['individuals'][homeowner.entity_id] = {
                'net_worth': self.get_net_worth(homeowner),
                'savings': homeowner.savings
            }

        self.logs.append(log)
        return log

    def appreciate_homes(self) -> None:
        for home in self.homes.values():
            home.prop_val += self.config['home_appr_rate'] * home.prop_val
            home.rent += self.config['home_appr_rate'] * home.rent

    def process_rent(self) -> None:
        for renter in self.renters.values():
            if renter.residence is None:
                continue

            home = renter.residence
            owners_equity = self.home_map[home.entity_id]
            for owner_id in owners_equity:
                owner = self.homeowners[owner_id]
                renter.pay(owners_equity[owner_id] * home.rent, owner, "rent")

    def appreciate_income(self) -> None:
        for owner in self.homeowners.values():
            self.appreciate_ind_income(owner)

    def appreciate_ind_income(self, owner: HomeOwner) -> None:
        owner.income += owner.config['inc_growth_rate'] * owner.income
        owner.config['income_tax'] = self.get_tax_bracket(owner)

    def get_tax_bracket(self, owner: HomeOwner) -> float:
        for bracket in self.config['tax_brackets']:
            if owner.income <= bracket['max_amount']:
                return bracket['tax']

    def contribute_equities(self) -> None:
        for renter in self.renters.values():
            home = renter.residence
            if home is None or not renter.with_polymer:
                continue

            owners_equity = self.home_map[home.entity_id]
            amount_to_contr = renter.config['equity_contr'] * renter.savings
            equity_to_contr = amount_to_contr / (home.prop_val * 1.1)

            for owner_id in owners_equity:
                if owner_id == renter.entity_id:
                    continue

                equity_to_take = equity_to_contr * (owners_equity[owner_id] / (1 - owners_equity[renter.entity_id]))
                renter.pay(
                    equity_to_take * home.prop_val,
                    self.homeowners[owner_id],
                    f"{equity_to_take} equity in home {home.entity_id}"
                )
                owners_equity[owner_id] -= equity_to_take
                owners_equity[renter.entity_id] += equity_to_take

    def print_logs(self) -> None:
        print(json.dumps(self.logs, indent=4))

    def write_logs(self) -> None:

    def get_net_worth(self, individual: HomeOwner):
        net_worth = individual.savings
        for home_id in self.home_map:
            if individual.entity_id in self.home_map[home_id]:
                net_worth += self.home_map[home_id][individual.entity_id] * self.homes[home_id].prop_val

        return net_worth
