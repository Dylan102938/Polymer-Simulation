from typing import TypedDict, Dict
from sim_assets.entities.Home import Home
from sim_assets.entities.Entity import Entity


class HomeEquity(TypedDict):
    equity_owned: float
    home_info: Home


class HomeOwnerConfig(TypedDict):
    savings: float
    with_polymer: bool


class HomeOwner(Entity):
    def __init__(self, person_id: str, config: HomeOwnerConfig):
        Entity.__init__(self, person_id, config['savings'])
        self.config = config
        self.with_polymer = config['with_polymer']
        self.homes_owned: Dict[str, HomeEquity] = dict()

    def purchase_home(self, home: Home) -> None:
        assert home.prop_val <= self.savings, f"{self.entity_id} does not have enough saved to purchase home {home.entity_id}"

        self.savings -= home.prop_val
        self.homes_owned[home.entity_id] = {'equity_owned': 1, 'home_info': home}
        home.original_owner = self

        print(f"{self.entity_id} buys home {home.entity_id} for {home.prop_val}")

    def collect_rent(self) -> float:
        return sum([home['home_info'].pay(home['equity_owned'] * home['home_info'].rent, self, 'rent') for home in self.homes_owned.values()])

    def purchase_equity(self, home_id: str, seller: 'HomeOwner', amount: float) -> float:
        assert home_id in self.homes_owned, f"{self.entity_id} does not own home {home_id}"
        assert home_id in seller.homes_owned, f"{seller.entity_id} does not own home {home_id}"

        equity = amount / (self.homes_owned[home_id]['home_info'].prop_val * 1.1)

        assert seller.homes_owned[home_id]['equity_owned'] >= equity, f"{seller.entity_id} does not own enough equity " \
                                                                      f"in home {home_id} for this purchase "

        self.pay(amount, seller, f"{equity} equity from home {home_id}")
        self.homes_owned[home_id]['equity_owned'] += equity
        seller.homes_owned[home_id]['equity_owned'] -= equity

        return equity

    def net_worth(self) -> float:
        return self.savings + sum([home['equity_owned'] * home['home_info'].prop_val for home in self.homes_owned.values()])
