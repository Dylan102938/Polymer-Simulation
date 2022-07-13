import math


class Entity:
    def __init__(self, entity_id: str, savings: float):
        self.entity_id = entity_id
        self.savings = savings

    def pay(self, amount: float, other: 'Entity', reason: str) -> float:
        amount = math.floor(amount * 100) / 100
        assert amount <= (self.savings + 0.0001), f"{self.entity_id} does not have enough assets to pay {other.entity_id} {amount} for {reason} "

        other.savings += amount
        self.savings -= amount

        print(f"LOG: {self.entity_id} pays {other.entity_id} {amount} for {reason}")

        return amount
