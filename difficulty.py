from typing import List, Tuple
from tqdm import tqdm
from math import floor
import json
import os

import dungeongrams

'''
NOTE: Already checked if 
'''

# https://dataaspirant.com/five-most-popular-similarity-measures-implementation-in-python
def jaccard_similarity(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> float:
    _a = set(a)
    _b = set(b)

    intersection_cardinality = len(set.intersection(*[_a, _b]))
    union_cardinality = len(set.union(*[_a, _b]))

    return 1.0 - intersection_cardinality/float(union_cardinality)

def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x2-x1) + abs(y2-y1)


ENEMY_RADIUS =[
    (x,y) for x in range(-dungeongrams.ENEMY_RANGE, dungeongrams.ENEMY_RANGE) 
          for y in range(-dungeongrams.ENEMY_RANGE, dungeongrams.ENEMY_RANGE) 
          if x != 0 and y != 0
]

def proximity_to_enemies(level: List[str], path: List[Tuple[int, int]]) -> float:
    in_proximity = 0
    for (y, x) in path:
        for (x_mod, y_mod) in ENEMY_RADIUS:
            _x = x + x_mod
            _y = y + y_mod

            if _x < 0 or _y < 0 or _x >= len(level[0]) or _y >= len(level):
                continue

            if level[_y][_x] == '#':
                in_proximity += manhattan_distance(x, y, _x, _y)
            elif level[_y][_x] == '^':
                in_proximity += 0.1*manhattan_distance(x, y, _x, _y)

    return in_proximity / len(path)

with open(os.path.join('difficulty', 'output.json'), 'r') as f:
    data = json.load(f)

f = open('output.txt', 'w')

data_iterator = tqdm(data)
for lvl_key in data_iterator:
    data_iterator.set_description(lvl_key)
    level = data[lvl_key]
    level_no_enemies = [r.replace('#', '-').replace('^', '-') for r in level]


    solution_with_enemies = dungeongrams.solve_and_run(level, False, False, True, dungeongrams.FLAW_NO_FLAW, False, False)
    assert(solution_with_enemies[0])
    
    solution_no_enemies = dungeongrams.solve_and_run(level_no_enemies, False, False, True, dungeongrams.FLAW_NO_FLAW, False, False)
    assert(solution_no_enemies[0])

    path_with_enemies = solution_with_enemies[4]
    path_no_enemies = solution_no_enemies[4]

    stamina_with_enemies = solution_with_enemies[5]
    stamina_no_enemies = solution_no_enemies[5]

    path_length_difference = (len(path_with_enemies) - len(path_no_enemies)) / len(path_with_enemies)
    difficulty = [
        # (len(path_with_enemies) - len(path_no_enemies)) / len(path_with_enemies),
        jaccard_similarity(path_with_enemies, path_no_enemies),
        proximity_to_enemies(level, path_with_enemies),
        1.0 - (stamina_with_enemies/dungeongrams.STAMINA_STARTING)
    ]
    estimate = min(sum(difficulty)/float(len(difficulty)), 1)

    f.write(f'Level: {lvl_key}\n')
    # f.write(f'Path: {difficulty[0]}\n'\n')
    f.write(f'Estimate: {estimate}\n')
    f.write(f'7-Likert: {floor(estimate * (7 - 1)) + 1}\n')
    f.write('\n'.join(level))
    f.write('\n\n\n')

f.close()
print('output in output.txt')