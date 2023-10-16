import pathlib
import math
import random

period = "I"
# how many previous seating charts have I used in this class
current_iteration = 1

# read in data on individual students
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

# read in data on who they've worked with and where they've sat before
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


# define number of 3 or 4-person groups
num_groups = math.ceil(class_size / 4)

# define number of 3-person groups I will need to have
num_trios = 4 - (class_size % 4)

# goal of new groups is to get students to work with others they have not worked with before
# and to sit in a different place in the classroom than they have before
# and to be balanced with gender, race, and ability level
groups = list(range(1, num_groups + 1))
best_groups = []
for trial_count in range(0, 100000):

    # shuffle the list of students randomly
    student_names = list(student_stats.keys())
    new_groups = {}
    random.shuffle(groups)
    random.shuffle(student_names)
    trios_used = num_trios

    # split them into groups
    for g in groups:
        group_size = 4
        if trios_used > 0:
            group_size = 3
            trios_used -= 1
        new_groups["group{}".format(g)] = []
        for s in range(0, group_size):
            new_groups["group{}".format(g)].append(student_names[s])
        student_names = student_names[group_size:]

    # score the groupings based on heterogeneity of race, gender, social skills, and math skills,
    desired_score = 3
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
                for other_student in new_groups[g]:
                    for iteration in student_history[s]:
                        if other_student in student_history[s][iteration]["members"]:
                            new_groups_score -= 1.0 / (current_iteration - int(iteration))

                        if student_stats[s]["gender"] != student_stats[other_student]["gender"]:
                            new_groups_score += 1

                        if student_stats[s]["race"] != student_stats[other_student]["race"]:
                            new_groups_score += 1

                for iteration in student_history[s]:
                    if g in student_history[s][iteration]["group"]:
                        new_groups_score -= 1.0 / (current_iteration - int(iteration))

        if social_skills_group_sum < desired_score or math_skills_group_sum < desired_score:
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

# write out the top 10 best group options
options_path = pathlib.Path.cwd() / f"Documents/Grouper/Period{period}options.csv"
options_path.write_text("")
with options_path.open("a") as f:
    for r in best_groups:
        r_str = str(r)[1:-1]
        f.write(r_str)
        f.write("\n")
