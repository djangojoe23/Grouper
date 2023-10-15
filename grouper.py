import pathlib
import math
import random

# if i pick 3 or 4 students randomly, what is their average group score? what is the standard deviation?
# when i go to create all groups, if there is a group more than 1? 0.5? standard deviation below the mean this means there is a group that is a total dud
# start over and try to create groups again

period = "I"

stats_path = pathlib.Path.cwd() / f"Documents/Grouper/Period{period}stats.csv"

student_stats = {}

class_size = 0
for row in stats_path.read_text().split("\n")[1:]:
    if row:
        row_split = row.split(",")
        student_stats[row_split[0]] = {}
        class_size += 1
        student_stats[row_split[0]]["gender"] = row_split[1]
        student_stats[row_split[0]]["race"] = row_split[2]
        student_stats[row_split[0]]["social"] = int(row_split[3])
        student_stats[row_split[0]]["math"] = int(row_split[4])

history_path = pathlib.Path.cwd() / f"Documents/Grouper/Period{period}history.csv"

student_history = {}

for row in history_path.read_text().split("\n")[1:]:
    if row:
        row_split = row.split(",")
        for s in range(0, 4):
            if row_split[s] not in student_history:
                student_history[row_split[s]] = {}
            student_history[row_split[s]][row_split[4]] = {"group": "group{}".format(row_split[5])}
            student_history[row_split[s]][row_split[4]]["members"] = row_split[:4]
            student_history[row_split[s]][row_split[4]]["members"].remove(row_split[s])


# goal of new groups is to get students to work with others they have not worked with before
# and to sit in a different place in the classroom than they have before
# and to be balanced with gender, race, and ability level

# define number of groups
num_groups = math.ceil(class_size / 4)

# define number of 3 person groups
num_trios = 4 - (class_size % 4)

groups = list(range(1, num_groups + 1))
current_iteration = 3
best_groups = []
for trial_count in range(0, 100000):
    student_names = list(student_stats.keys())
    new_groups = {}
    random.shuffle(groups)
    random.shuffle(student_names)
    trios_used = num_trios
    for g in groups:
        group_size = 4
        if trios_used > 0:
            group_size = 3
            trios_used -= 1
        new_groups["group{}".format(g)] = []
        for s in range(0, group_size):
            new_groups["group{}".format(g)].append(student_names[s])
        student_names = student_names[group_size:]

    # score the groupings (less negative scores are better)
    new_groups_score = 0
    social_skills_per_group = []
    math_skills_per_group = []
    skip_groupings = False
    for g in new_groups:
        social_skills_group_sum = 0
        math_skills_group_sum = 0
        for s in new_groups[g]:

            social_skills_group_sum += student_stats[s]["social"]
            math_skills_group_sum += student_stats[s]["math"]

            if student_history:
                for other_s in new_groups[g]:
                    for iteration in student_history[s]:
                        if other_s in student_history[s][iteration]["members"]:
                            new_groups_score -= 1.0 / (current_iteration - int(iteration))

                        if student_stats[s]["gender"] != student_stats[other_s]["gender"]:
                            new_groups_score += 1

                        if student_stats[s]["race"] != student_stats[other_s]["race"]:
                            new_groups_score += 1

                for iteration in student_history[s]:
                    if g in student_history[s][iteration]["group"]:
                        new_groups_score -= 1.0 / (current_iteration - int(iteration))

        if social_skills_group_sum < 3 or math_skills_group_sum < 3:
            skip_groupings = True
            break
        else:
            social_skills_per_group.append(social_skills_group_sum)
            math_skills_per_group.append(math_skills_group_sum)

    if not skip_groupings:
        new_groups_score += sum(social_skills_per_group) / len(social_skills_per_group)
        new_groups_score += sum(math_skills_per_group) / len(math_skills_per_group)

        result = [
            new_groups_score,
        ]
        for i in range(1, num_groups + 1):
            result.append(new_groups["group{}".format(i)])

        if result not in best_groups:
            if len(best_groups) < 10:
                best_groups.append(result)
            else:
                for r in best_groups:
                    if new_groups_score > r[0]:
                        best_groups.remove(r)
                        best_groups.append(result)
                        break

options_path = pathlib.Path.cwd() / f"Documents/Grouper/Period{period}options.csv"

options_path.write_text("")
with options_path.open("a") as f:
    for r in best_groups:
        r_str = str(r)[1:-1]
        f.write(r_str)
        f.write("\n")
