from typing import TypedDict, Dict
from HomeOwner import HomeOwner
from Renter import Renter


class HomeConfig(TypedDict):
    prop_val: float
    rent: float
    other_owners: Dict[str, HomeOwner]


class Home:
    def __init__(self, home_id: str, config: HomeConfig):
        self.prop_val = config['prop_val']
        self.rent = config['rent']
        self.home_id = home_id
        self.other_owners = config['other_owners']
        self.renter = None
        self.original_owner = None
        self.config = config

    def collect_rent(self) -> None:
        self.renter.pay(self.rent, self.original_owner, "rent")

        for owner in self.other_owners.values():
            self.original_owner.pay(owner.homes_owned[self.home_id]['equity_owned'] * self.rent, owner, "equity")

    def add_equity(self, renter: Renter, amount: float) -> None:
        equity_to_add = amount / (self.prop_val * 1.1)
        total_equity = 0
        for owner in self.other_owners.values():
            total_equity += owner.homes_owned['equity_owned']

        assert total_equity + equity_to_add < 1, f"{renter.person_id} cannot add more equity because there is not " \
                                                 f"enough equity remaining in the property "

        renter.pay(amount, self.original_owner, "house equity")
        renter.homes_owned[self.home_id]['equity_owned'] += equity_to_add
