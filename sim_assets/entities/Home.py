from typing import TypedDict
from sim_assets.entities.Entity import Entity


class HomeConfig(TypedDict):
    prop_val: float
    rent: float


class Home(Entity):
    def __init__(self, home_id: str, config: HomeConfig):
        Entity.__init__(self, home_id, 0)
        self.prop_val = config['prop_val']
        self.rent = config['rent']
        self.config = config
