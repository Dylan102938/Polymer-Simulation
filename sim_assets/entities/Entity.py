from typing import TypedDict


class EntityConfig(TypedDict):
    savings: float


class Entity:
    def __init__(self, entity_id: str, config: EntityConfig):
        self.entity_id = entity_id
        self.config = config

    def pay(self, amount: float, other: 'Entity', reason: str) -> float:
        amount = round(amount * 100) / 100
        assert amount <= round(self.config['savings']), f"{self.entity_id} only has {self.config['savings']}, not " \
                                                        f"enough assets to pay {other.entity_id} {amount} for {reason} "
        assert amount >= 0, f"{self.entity_id} cannot pay a negative amount of money"

        other.config['savings'] += amount
        self.config['savings'] -= amount

        print(f"LOG: {self.entity_id} pays {other.entity_id} {amount} for {reason}")

        return amount
