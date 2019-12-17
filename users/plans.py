# (NAME, DESCRIPTION, PRICE PER MONTH, NUM QUESTIONS)
plans = [
    ('SHY', 'Free Plan', 0, 0),
    ('ASKER', 'Basic Plan', 25, 1),
    ('INQUISITOR', 'Pro Plan', 100, 5),
    ('INTERROGATOR', 'Premium Plan', 400, 25),
]
# name and description
plans_names =  [(p[0], p[1]) for p in plans]

def get_plan_names():
    return plans_names

def get_paid_plans():
    return plans[1:]

def get_num_questions_plans():
    return [p[3] for p in plans]

def get_max_questions(plan_name):
    for plan in plans:
        if plan[0] == plan_name:
            return plan[3]   

def get_plan_by_num_questions(num_questions):
    for plan in plans:
        if float(plan[3]) == num_questions:
            return plan[0]   

def get_plan_by_price(price):
    for plan in plans:
        if float(plan[2]) == price:
            return plan[0]   