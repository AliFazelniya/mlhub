def create_set(input_ls):
    a = set(input_ls)
    return a

def union(first_set, second_set):
    union_set = create_set([])
    for i in first_set:
        union_set.add(i)
    for i in second_set:
        union_set.add(i)
    return union_set

def intersection(first_set, second_set):
    intersection_set = create_set([])
    for i in first_set:
        if i in second_set:
            intersection_set.add(i)
    return intersection_set

def difference(first_set, second_set):
    difference_set = create_set([])
    for i in first_set:
        if not i in second_set:
            difference_set.add(i)
    return difference_set

def complement(universal_set, first_set):
    complement_set = create_set([])
    for i in universal_set:
        if not i in first_set:
            complement_set.add(i)
    return complement_set

def is_empty(the_set):
    if len(the_set) != 0:
        return False
    return True

def is_subset(first_set, second_set):
    for i in first_set:
        if not i in second_set:
            return False
    return True

def is_member(the_set, element):
    if element in the_set:
        return True
    return False

def power_set_number(the_set):
    return 2**len(the_set)

def probability_of_event(events, sample_space) -> float:
    return len(events) / len(sample_space)

def conditional_probability(events, sample_space) -> float:
    return len(intersection(events, sample_space)) / len(sample_space)

def are_independent(events1, events2, sample_space) -> bool:
    if probability_of_event(intersection(events1 , events2), sample_space) == (probability_of_event(events1 , sample_space) * probability_of_event(events2, sample_space)):
        return True
    return False

def bayes_theorem(events1, events2, sample_space) -> float:
    return (conditional_probability(events2, events1) * probability_of_event(events1, sample_space)) / probability_of_event(events1, sample_space)
