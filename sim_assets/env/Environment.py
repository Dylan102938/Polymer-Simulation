from typing import Dict, TypedDict, List
import json

from sim_assets.entities.HomeOwner import HomeOwner
from sim_assets.entities.Home import Home
from sim_assets.entities.Renter import Renter


class TaxBracket(TypedDict):
    max_amount: float
    tax: float


class EnvironmentConfig(TypedDict):
    home_appr_rate: float
    default_home_price: float
    default_rent_rate: float
    default_income_appr_rate: float
    default_equity_contr: float
    tax_brackets: List[TaxBracket]
    inflation: float
    savings_appr: float


class HomeLogs(TypedDict):
    prop_val: float
    rent: float


class IndividualLogs(TypedDict):
    net_worth: float
    savings: float


class Log(TypedDict):
    homes: Dict[str, HomeLogs]
    individuals: Dict[str, IndividualLogs]
    inflation: float
    savings_appr: float


class Environment:
    def __init__(self, config: EnvironmentConfig):
        self.homes: Dict[str, Home] = dict()
        self.homeowners: Dict[str, HomeOwner] = dict()
        self.renters: Dict[str, Renter] = dict()
        self.config = config
        self.logs: List[Log] = []
        self.home_map: Dict[str, Dict[str, float]] = dict()

    def add_home(self, home: Home) -> None:
        assert home.entity_id not in self.homes, f"Home {home.entity_id} is already part of this environment"
        self.homes[home.entity_id] = home

    def add_homeowner(self, owner: HomeOwner) -> None:
        assert owner.entity_id not in self.homes, f"Homeowner {owner.entity_id} is already part of this environment"
        self.homeowners[owner.entity_id] = owner

    def add_renter(self, renter: Renter) -> None:
        assert renter.entity_id not in self.homes, f"Renter {renter.entity_id} is already part of this environment"
        self.renters[renter.entity_id] = renter

        if len(renter.homes_owned) != 0 and renter.entity_id not in self.homeowners:
            self.homeowners[renter.entity_id] = renter

    def purchase_home(self, purchaser: HomeOwner, home: Home):
        assert purchaser.entity_id in self.homeowners and home.entity_id in self.homes, f"Could not complete home purchase as entities are outside environment"
        assert home.prop_val <= purchaser.savings, f"{purchaser.entity_id} does not have enough saved to purchase home {home.entity_id}"

        purchaser.savings -= home.prop_val
        purchaser.homes_owned[home.entity_id] = {'equity_owned': 1, 'home_info': home}
        self.home_map[home.entity_id] = {purchaser.entity_id: 1}

    def rent(self, renter: Renter, home: Home):
        assert renter.entity_id in self.renters and home.entity_id in self.homes, f"Could not complete home purchase as entities are outside environment"
        assert home.entity_id in self.home_map, f"Home is not currently being owned by an owner in the environment"
        renter.residence = home
        if renter.config['with_polymer']:
            renter.homes_owned[home.entity_id] = {'equity_onwed': 0, 'home_info': home}
            self.home_map[home.entity_id][renter.entity_id] = 0

    def progress_one_year(self) -> Log:
        for renter in self.renters.values():
            renter.get_income()

        self.process_rent()
        self.contribute_equities()
        self.appreciate_income()
        self.appreciate_homes()
        savings_appr = self.config['savings_appr']
        inflation = self.config['inflation']
        log: Log = {
            'homes': dict(),
            'individuals': dict(),
            'inflation': inflation,
            'savings_appr': savings_appr
        }

        for home in self.homes.values():
            log['homes'][home.entity_id] = {'prop_val': home.prop_val, 'rent': home.rent}
        for homeowner in self.homeowners.values():
            log['individuals'][homeowner.entity_id] = {
                'net_worth': homeowner.net_worth(),
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
            renter.pay_rent()
        for owner in self.homeowners.values():
            owner.collect_rent()

    def appreciate_income(self) -> None:
        for renter in self.renters.values():
            self.appreciate_ind_income(renter)

    def appreciate_ind_income(self, renter: Renter) -> None:
        renter.income += renter.config['inc_growth_rate'] * renter.income
        renter.config['income_tax'] = self.get_tax_bracket(renter)

    def get_tax_bracket(self, renter: Renter) -> float:
        for bracket in self.config['tax_brackets']:
            if renter.income <= bracket['max_amount']:
                return bracket['tax']

    def contribute_equities(self) -> None:
        for renter in self.renters.values():
            if renter.entity_id in self.home_map[renter.residence.entity_id]:
                remaining_equity = 1 - self.home_map[renter.residence.entity_id][renter.entity_id]
                for owner_id in self.home_map[renter.residence.entity_id]:
                    if owner_id == renter.entity_id:
                        continue

                    amount = self.home_map[renter.residence.entity_id][owner_id] / remaining_equity
                    renter.purchase_equity(renter.residence.entity_id, self.homeowners[owner_id], amount)

    def print_logs(self) -> None:
        print(json.dumps(self.logs, indent=4))
