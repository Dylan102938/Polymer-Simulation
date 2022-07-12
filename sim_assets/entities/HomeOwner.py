from typing import TypedDict, Dict
from Home import Home


class HomeEquity(TypedDict):
    equity_owned: float
    home_info: Home


class HomeOwnerConfig(TypedDict):
    savings: float


class HomeOwner:
    def __init__(self, person_id: str, config: HomeOwnerConfig):
        self.config = config
        self.person_id = person_id
        self.savings = config['savings']
        self.homes_owned = dict()

    def pay(self, amount: float, recipient: 'HomeOwner', reason: str) -> None:
        assert amount <= self.savings, f"{self.person_id} does not have enough saved to pay {recipient.person_id} for {reason}"

        self.savings -= amount
        recipient.savings += amount

        print(f"{self.person_id} pays {recipient.person_id} {amount} for {reason}")

    def purchase_home(self, home: Home) -> None:
        assert home.prop_val <= self.savings, f"{self.person_id} does not have enough saved to purchase home f{home.home_id}"
        assert home.original_owner is None, f"{self.person_id} cannot purchase home because the home is already owned"

        self.savings -= home.prop_val
        self.homes_owned[home.home_id] = {'equity_owned': 1, 'home_info': home}
        home.original_owner = self

        print(f"{self.person_id} buys home f{home.home_id} for {home.prop_val}")

    def net_worth(self) -> float:
        return self.savings + sum([home['equity_owned'] * home['home_info'].prop_value for home in self.homes_owned])
