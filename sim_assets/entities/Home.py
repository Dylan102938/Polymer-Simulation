import json
from sim_assets.entities.Entity import Entity, EntityConfig


class HomeConfig(EntityConfig):
    prop_val: float
    rent: float


class Home(Entity):
    def __init__(self, home_id: str, config: HomeConfig):
        Entity.__init__(self, home_id, config)
        self.config = config

    @classmethod
    def from_json(cls, home_id: str, filename: str) -> 'Home':
        with open(filename) as f:
            config: HomeConfig = json.load(f)
            return Home(home_id, config)
