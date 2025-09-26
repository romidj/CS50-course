from constraint import Problem, AllDifferentConstraint

# Define groups
groups = ["G1", "G2", "G3", "G4"]

# Define courses
courses = [
    "Reseau_cours", "Reseau_td", "Reseau_tp",
    "Artificiel_intelligence_cours", "Artificiel_intelligence_td", "Artificiel_intelligence_tp",
    "Cyber_secuity_cours", "Cyber_secuity_td", "Entreprenariat_cours",
    "Recherche_operationel_cours", "Recherche_operationel_td",
    "Methodes_formelles_cours", "Methodes_formelles_td",
    "Analye_numerique_cours", "Analye_numerique_td"
]

# Define time slots
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
time_slots = {
    "Sunday": [1, 2, 3, 4, 5],
    "Monday": [1, 2, 3, 4, 5],
    "Tuesday": [1, 2, 3],
    "Wednesday": [1, 2, 3, 4, 5],
    "Thursday": [1, 2, 3, 4, 5]
}

# Define rooms
rooms = {
    "cours": ["amphi1", "amphi2"],
    "td": ["salle_td1", "salle_td2", "salle_td3", "salle_td4"],
    "tp": ["salle_tp1", "salle_tp2", "salle_tp3", "salle_tp4"]
}

# Initialize the CSP solver
problem = Problem()

# Define the domain for each course session and group
for course in courses:
    course_type = course.split('_')[-1].lower()
    if course_type in rooms:
        if "cours" in course_type:
            domain = [(day, slot, room) for day in days for slot in time_slots[day] for room in rooms["cours"]]
            problem.addVariable(course, domain)
        else:
            for group in groups:
                domain = [(day, slot, room) for day in days for slot in time_slots[day] for room in rooms[course_type]]
                problem.addVariable(f"{course}_{group}", domain)
    else:
        raise ValueError(f"Unknown course type: {course_type}")

# Ensure that each group takes only one course per slot
for group in groups:
    for day in days:
        for slot in time_slots[day]:
            # All courses assigned to a group in a given slot must be different
            slot_courses = [f"{course}_{group}" for course in courses if "_td" in course or "_tp" in course]
            problem.addConstraint(AllDifferentConstraint(), [f"{course}_{group}" for course in courses if f"{day}_{slot}" in course])

# Ensure that "_cours", "_td", "_tp" sessions are scheduled in the correct rooms
def correct_room_assignment(day, slot, room, course):
    if "cours" in course:
        return room in rooms["cours"]
    elif "td" in course:
        return room in rooms["td"]
    elif "tp" in course:
        return room in rooms["tp"]
    return False

for course in courses:
    if "cours" in course:
        problem.addConstraint(lambda assignment, course=course: correct_room_assignment(*assignment, course), [course])
    else:
        for group in groups:
            problem.addConstraint(
                lambda assignment, course=f"{course}_{group}": correct_room_assignment(*assignment, course),
                [f"{course}_{group}"])

# Additional constraints:
# No more than three successive slots for any session
def no_more_than_three_successive(*args):
    times = sorted(args)
    for i in range(len(times) - 2):
        if times[i][1] == times[i + 1][1] - 1 == times[i + 2][1] - 2:
            return False
    return True

for group in groups:
    td_tp_sessions = [f"{course}_{group}" for course in courses if "_td" in course or "_tp" in course]
    problem.addConstraint(no_more_than_three_successive, td_tp_sessions)

# Ensure that different courses of the same group are scheduled in different slots
for group in groups:
    all_group_sessions = [f"{course}_{group}" for course in courses if "_td" in course or "_tp" in course]
    problem.addConstraint(AllDifferentConstraint(), all_group_sessions)

# Ensure that the "_cours" sessions are scheduled without overlapping
cours_sessions = [course for course in courses if "_cours" in course]
problem.addConstraint(AllDifferentConstraint(), cours_sessions)

# Solve the problem
solution = problem.getSolution()

# Display the solution in a readable format
if solution:
    schedule = {}
    for course, (day, slot, room) in solution.items():
        if day not in schedule:
            schedule[day] = {}
        if slot not in schedule[day]:
            schedule[day][slot] = []
        schedule[day][slot].append((course, room))

    for day in days:
        if day in schedule:
            print(f"\n{day}:")
            for slot in sorted(schedule[day]):
                print(f"  Slot {slot}:")
                for course, room in schedule[day][slot]:
                    print(f"    {course} in {room}")
else:
    print("No solution found.")
