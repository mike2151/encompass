# (NAME, DESCRIPTION, PRICE PER MONTH, NUM QUESTIONS)
plans = [
    ('SHY', 'Free Plan', 0, 0),
    ('ASKER', 'Basic Plan', 35, 1),
    ('INQUISITOR', 'Pro Plan', 100, 10),
    ('INTERROGATOR', 'Premium Plan', 300, 50),
]
# name and description
plans_names =  [(p[0], p[1]) for p in plans]

def get_plan_names():
    return plans_names

def get_paid_plans():
    return plans[1:]

def get_max_questions(plan_name):
    for plan in plans:
        if plan[0] == plan_name:
            return plan[3]   

def get_plan_by_price(price):
    for plan in plans:
        if float(plan[2]) == price:
            return plan[0]   