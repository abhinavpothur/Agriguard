import os
from qpiai_opt.opt_modeller import Binary, Model
from qpiai_opt.opt_solvers import Client, solve

# Sample farms: higher scores mean greater urgency.

farms = {
"Farm_A": {"priority": 10, "visit_hours": 2},
"Farm_B": {"priority": 8, "visit_hours": 2},
"Farm_C": {"priority": 5, "visit_hours": 1},
}

# Sample agronomists and their available hours.

agronomists = {
"Agronomist_1": {"available_hours": 4},
"Agronomist_2": {"available_hours": 3},
}

# Maximum number of farms we can visit today.

daily_visit_capacity = 2

model = Model("agronomist_assignment")

# selected[i] = 1 when farm i is selected for a visit.

selected = {
farm: Binary(f"selected_{farm}")
for farm in farms
}

# assigned[i, j] = 1 when agronomist j visits farm i.

assigned = {
(farm, agronomist): Binary(f"assigned_{farm}_{agronomist}")
for farm in farms
for agronomist in agronomists
}

# Reward selecting high-priority farms.

model.maximize(
sum(
farms[farm]["priority"] * selected[farm]
for farm in farms
)
)

# Every selected farm must have exactly one assigned agronomist.

for farm in farms:
    model.add_constraint(
sum(assigned[farm, agronomist] for agronomist in agronomists)
== selected[farm],
label=f"one_agronomist_{farm}",
)

# Each agronomist must remain within available working hours.

for agronomist in agronomists:
    model.add_constraint(
sum(
farms[farm]["visit_hours"] * assigned[farm, agronomist]
for farm in farms
)
<= agronomists[agronomist]["available_hours"],
label=f"working_hours_{agronomist}",
)

# Respect the daily visit limit.

model.add_constraint(
sum(selected[farm] for farm in farms) <= daily_visit_capacity,
label="daily_visit_capacity",
)

# Validate the model before solving.

print("Problem type:", model.validate())
print("Objective:", model.objective_as_string())
print("Model summary:")
print(model.summary())
client = Client(api_key=os.environ["QPIAI_OPT_API_KEY"])

result = solve(model, client=client, mode="local")

print("\n--- OPTIMIZATION RESULT ---")
print("Problem type:", result.problem_class)
print("Execution mode:", result.execution_mode)
print("Solution:", result.solution)
print("Objective score:", result.objective)