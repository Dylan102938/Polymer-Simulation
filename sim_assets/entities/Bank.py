from sim_assets.entities.Entity import Entity
from sim_assets.entities.Individual import Individual


class Bank(Entity):
    def __init__(self, bank_id: str):
        Entity.__init__(self, bank_id, {'savings': 10000000000})

    def issue_mortgage(self, amount: float, loan_term: int, interest: float, recipient: Individual) -> None:
        monthly_interest = interest / 12
        loan_term_months = loan_term * 12
        monthly_payment = amount * (monthly_interest / (1 - (1 + monthly_interest)**(-loan_term_months)))

        self.pay(amount, recipient, f"{amount} loan over {loan_term} years with {interest} interest")
        recipient.add_expense("mortgage", monthly_payment, 12, loan_term)
