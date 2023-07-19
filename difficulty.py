from typing import List, Tuple
from tqdm import tqdm
from math import floor
import json
import os

import dungeongrams

'''
NOTE: Already checked if 
'''

DG_RESOLUTION = 20
SOLIDS = ['X', '^', '/', '\\']

# https://dataaspirant.com/five-most-popular-similarity-measures-implementation-in-python
def jaccard_similarity(a: List[Tuple[int, int]], b: List[Tuple[int, int]]) -> float:
    _a = set(a)
    _b = set(b)

    intersection_cardinality = len(set.intersection(*[_a, _b]))
    union_cardinality = len(set.union(*[_a, _b]))

    return 1.0 - intersection_cardinality/union_cardinality

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
                in_proximity += 1/manhattan_distance(x, y, _x, _y)
            # elif level[_y][_x] == '^':
            #     in_proximity += 0.1*manhattan_distance(x, y, _x, _y)

    return in_proximity / len(path)

def density(level: List[str]) -> float:
    num_tiles = len(level) * len(level[0])
    return sum(sum(1 for t in r if t in SOLIDS) for r in level) / num_tiles

def linearity(level: List[str]) -> float:
    count = 0
    for col in level:
        if '^' in col :
            count += 1/3
        if '#' in col:
            count += 1/3
        if '*' in col:
            count += 1/3

    return count / len(level)

def percent_difference(a: float, b: float) -> float:
    return abs(a-b) / ((a+b)/2)

with open(os.path.join('difficulty', 'output.json'), 'r') as f:
    data = json.load(f)

columns = [
    'level',
    'path-no-enemies',
    'path-nothing',
    'jaccard-no-enemies',
    'jacard-nothing',
    'proximity-to-enemies',
    'stamina-percent-enemies',
    'stamina-percent-nothing',
    'density',
    'leniency'
]

readable_f = open('output.txt', 'w')
computation_f = open('custom_difficulty.csv', 'w')
computation_f.write(','.join(columns))
computation_f.write('\n')

baseline_f = open('baseline_difficulty.csv', 'w')
baseline_f.write('level,difficulty\n')

data_iterator = tqdm(data)
for lvl_key in data_iterator:
    data_iterator.set_description(lvl_key)

    # build levels
    level = data[lvl_key]
    level_no_enemies = [r.replace('#', '-').replace('^', '-') for r in level]
    level_no_nothing = [r.replace('*', '-') for r in level_no_enemies]

    # Find solution for level
    solution_with_enemies = dungeongrams.solve_and_run(level, False, False, True, dungeongrams.FLAW_NO_FLAW, False, False)
    assert(solution_with_enemies[0])
    path_with_enemies = solution_with_enemies[4]
    stamina_with_enemies = solution_with_enemies[5]

    # Find solution for level with no enemies
    solution_no_enemies = dungeongrams.solve_and_run(level_no_enemies, False, False, True, dungeongrams.FLAW_NO_FLAW, False, False)
    assert(solution_no_enemies[0])
    path_no_enemies = solution_no_enemies[4]
    stamina_no_enemies = solution_no_enemies[5]

    # Find solution for level with no enemies or switches
    solution_no_nothing = dungeongrams.solve_and_run(level_no_nothing, False, False, True, dungeongrams.FLAW_NO_FLAW, False, False)
    assert(solution_no_nothing[0])
    path_no_nothing = solution_no_nothing[4]
    stamina_no_nothing = solution_no_nothing[5]

    # Build out the difficulty vector
    V = [ 
        (len(path_with_enemies) - len(path_no_enemies)) / len(path_with_enemies),  # path difference no enemies
        (len(path_with_enemies) - len(path_no_nothing)) / len(path_with_enemies),  # path difference no enemies and switches
        jaccard_similarity(path_with_enemies, path_no_enemies),                    # path similarity no enemies
        jaccard_similarity(path_with_enemies, path_no_nothing),                    # path similarity no enemies and switches
        proximity_to_enemies(level, path_with_enemies),
        percent_difference(stamina_with_enemies, stamina_no_enemies),              # Percent difference of stamina at end no enemies
        percent_difference(stamina_with_enemies, stamina_no_nothing),              # Percent difference of stamina at end no enemies and switches
        density(level),                                                            # Density of the level
        linearity(level),                                                          # linearity of the level
    ]

    # convert to strings for convenience when writing
    V = [str(v) for v in V]
    
    # estimate = min(sum(V)/float(len(V)), 1)
    # likert = floor(estimate * (7 - 1)) + 1

    # Write data to human readable file
    readable_f.write(f'Level: {lvl_key}\n')
    readable_f.write(','.join(V) + '\n')
    readable_f.write('\n'.join(level))
    readable_f.write('\n\n\n')

    # Write difficulty vector to CSV for easier calculation
    computation_f.write(f'{lvl_key},{",".join(d for d in V)}\n')

    # Write data for comparison to a baseline
    D = 1 + (sum(float(x)/DG_RESOLUTION for x in lvl_key.split('_')) / 2.0) * 7.0
    assert(D >= 1)
    assert(D <= 7)
    baseline_f.write(f'{lvl_key},{D}\n')

    # i += 1
    # if i >= 15:
    #     break

readable_f.close()
baseline_f.close()
computation_f.close()
print('output in output.txt')