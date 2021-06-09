import argparse, heapq, math, pprint, random, sys
from collections import namedtuple
from os.path import isfile

ACTIONS = [ '', 'w', 'a', 's', 'd' ]

FLAW_NO_FLAW = 'no_flaw'
FLAW_NO_SPIKE = 'no_spike'
FLAW_NO_HAZARD = 'no_hazard'
FLAW_NO_SPEED = 'no_speed'
FLAWS = [
    FLAW_NO_FLAW,
    FLAW_NO_SPIKE,
    FLAW_NO_HAZARD,
    FLAW_NO_SPEED
    ]

ENEMY_RANGE = 3

Position = namedtuple('Position', ['row', 'col'])
Modification = namedtuple('Modification', ['type', 'pos'])
MOD_SPIKE = 0
MOD_BLOCK = 1
MOD_ENEMY = 2

class State:
    def __init__(self):
        self.player = None
        self.exit = None
        self.enemies = []
        self.enemymv = False
        self.switches = []
        self.didwin = False
        self.didlose = False

    def clone(self):
        ret = State()
        ret.player = self.player
        ret.exit = self.exit
        ret.enemies = list(self.enemies)
        ret.enemymv = self.enemymv
        ret.switches = list(self.switches)
        ret.didwin = self.didwin
        ret.didlose = self.didlose
        return ret

    def totuple(self):
        return (self.player, self.exit, tuple(self.enemies), self.enemymv, tuple(self.switches), self.didwin, self.didlose)

    @staticmethod
    def fromtuple(tup):
        ret = State()
        ret.player = tup[0]
        ret.exit = tup[1]
        ret.enemies = list(tup[2])
        ret.enemymv = tup[3]
        ret.switches = list(tup[4])
        ret.didwin = tup[5]
        ret.didlose = tup[6]
        return ret



class Level:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.switchcount = 0
        self.blocks = set()
        self.spikes = set()
        self.enemyst = []



class Game:
    def __init__(self):
        self.loaded = False

        self.level = None
        self.state = None



    @staticmethod
    def validmoveforplayer(level, state, pos):
        if pos.row < 0:
            return False
        if pos.col < 0:
            return False
        if pos.row >= level.height:
            return False
        if pos.col >= level.width:
            return False

        if pos in level.blocks:
            return False

        if pos == state.exit and len(state.switches) > 0:
            return False

        return True

    @staticmethod
    def validmoveforenemy(level, state, pos):
        if not Game.validmoveforplayer(level, state, pos):
            return False

        if pos == state.exit:
            return False

        if pos in state.enemies:
            return False

        if pos in level.spikes:
            return False

        if pos in state.switches:
            return False

        return pos

    @staticmethod
    def playercollidehazard(level, state):
        if state.player in state.enemies:
            return True
        if state.player in level.spikes:
            return True
        return False

    @staticmethod
    def step(level, state, action, allow_mod=False):
        newstate = state.clone()
        mod = None

        if newstate.didwin:
            return newstate, mod
        if newstate.didlose:
            return newstate, mod

        if action in ['']:
            pdr, pdc = 0, 0
        elif action in ['w']:
            pdr, pdc = -1, 0
        elif action in ['s']:
            pdr, pdc = 1, 0
        elif action in ['a']:
            pdr, pdc = 0, -1
        elif action in ['d']:
            pdr, pdc = 0, 1
        else:
            raise RuntimeError('unrecognized action')

            #  and new_player_pos.row >= 0 and new_player_pos.col >= 0 and \
            # new_player_pos.row < level.height and new_player_pos.col < level.width

        new_player_pos = Position(newstate.player[0] + pdr, newstate.player[1] + pdc)
        
        if Game.validmoveforplayer(level, newstate, new_player_pos):
            newstate.player = new_player_pos
        elif allow_mod:
            if new_player_pos in level.blocks:
                mod = Modification(MOD_BLOCK, new_player_pos)
                newstate.player = new_player_pos

            # otherwise, the position is out of bounds and we continue to the rest of the function

        if Game.playercollidehazard(level, newstate):
            if allow_mod:
                if new_player_pos in level.spikes:
                    mod = Modification(MOD_SPIKE, new_player_pos)
                else:
                    try:
                        enemy_index = newstate.enemies.index(new_player_pos)
                        mod = Modification(MOD_ENEMY, level.enemyst[enemy_index])
                    except ValueError:
                        pass
            else:
                newstate.didlose = True
            
        elif newstate.player == newstate.exit:
            newstate.didwin = True

        elif newstate.player in newstate.switches:
            del newstate.switches[newstate.switches.index(newstate.player)]

        if not newstate.enemymv:
            newstate.enemymv = True
        else:
            newstate.enemymv = False
            
            for ii in range(len(newstate.enemies)):
                strr, stcc = level.enemyst[ii]
                stdr = newstate.player[0] - strr
                stdc = newstate.player[1] - stcc

                if (stdr**2 + stdc**2)**0.5 <= ENEMY_RANGE:
                    tgrr = newstate.player[0]
                    tgcc = newstate.player[1]
                else:
                    tgrr = level.enemyst[ii][0]
                    tgcc = level.enemyst[ii][1]
                    
                err, ecc = newstate.enemies[ii]
                edr = tgrr - err
                edc = tgcc - ecc

                if edr == 0 and edc == 0:
                    pass
                else:
                    trymoves = []
                    if abs(edr) > abs(edc):
                        if edr > 0:
                            trymoves.append((1, 0))
                        elif edr < 0:
                            trymoves.append((-1, 0))
                        if edc > 0:
                            trymoves.append((0, 1))
                        elif edc < 0:
                            trymoves.append((0, -1))
                    elif abs(edc) > abs(edr):
                        if edc > 0:
                            trymoves.append((0, 1))
                        elif edc < 0:
                            trymoves.append((0, -1))
                        if edr > 0:
                            trymoves.append((1, 0))
                        elif edr < 0:
                            trymoves.append((-1, 0))
                    elif (err + ecc) % 2 == 0:
                        if edr > 0:
                            trymoves.append((1, 0))
                        elif edr < 0:
                            trymoves.append((-1, 0))
                        if edc > 0:
                            trymoves.append((0, 1))
                        elif edc < 0:
                            trymoves.append((0, -1))
                    else:
                        if edc > 0:
                            trymoves.append((0, 1))
                        elif edc < 0:
                            trymoves.append((0, -1))
                        if edr > 0:
                            trymoves.append((1, 0))
                        elif edr < 0:
                            trymoves.append((-1, 0))

                    for edr, edc in trymoves:
                        new_position = Position(newstate.enemies[ii][0] + edr, newstate.enemies[ii][1] + edc)
                        if Game.validmoveforenemy(level, newstate, new_position):
                            newstate.enemies[ii] = new_position
                            break

        if Game.playercollidehazard(level, newstate):
            newstate.didlose = True

        return newstate, mod

    @staticmethod
    def display(level, state):
        for cc in range(level.width + 2):
            sys.stdout.write('X')
        sys.stdout.write('\n')
        
        for rr in range(level.height):
            sys.stdout.write('X')
            for cc in range(level.width):
                if (rr, cc) == state.player:
                    if state.didlose:
                        sys.stdout.write('%')
                    elif state.didwin:
                        sys.stdout.write('!')
                    else:
                        sys.stdout.write('@')
                elif (rr, cc) in state.enemies:
                    sys.stdout.write('#')
                elif (rr, cc) in level.spikes:
                    sys.stdout.write('^')
                elif (rr, cc) in state.switches:
                    sys.stdout.write('*')
                elif (rr, cc) == state.exit:
                    if len(state.switches) == 0:
                        sys.stdout.write('O')
                    else:
                        sys.stdout.write('o')
                elif (rr, cc) in level.blocks:
                    sys.stdout.write('X')
                else:
                    sys.stdout.write('-')
            sys.stdout.write('X')
            sys.stdout.write('\n')

        for cc in range(level.width + 2):
            sys.stdout.write('X')
        sys.stdout.write('\n')

    @staticmethod
    def load(filename, is_file, partial):
        level = Level()
        state = State()

        if is_file:
            rows = []
            with open(filename) as level_file:
                for line in level_file.readlines():
                    rows.append(line.strip())
        else:
            rows = list(filename)

        if partial:
            newrows = []
            for rr, row in enumerate(rows):
                pref = '@-' if rr == 0 else '--'
                suff = '-O' if rr + 1 == len(rows) else '--'
                newrows.append(pref + row + suff)
            rows = newrows

        for row in rows:
            if level.width == 0:
                level.width = len(row)
            elif level.width != len(row):
                raise RuntimeError('rows not all same length')
        level.height = len(rows)

        for rr, row in enumerate(rows):
            for cc, char in enumerate(row):
                if char == '-':
                    pass
                elif char == 'X':
                    level.blocks.add(Position(rr, cc))
                elif char == '#':
                    state.enemies.append(Position(rr, cc))
                    level.enemyst.append(Position(rr, cc))
                elif char == '^':
                    level.spikes.add(Position(rr, cc))
                elif char == '*':
                    state.switches.append(Position(rr, cc))
                    level.switchcount += 1
                elif char == '@':
                    if state.player != None:
                        raise RuntimeError('multiple players found')
                    state.player = (rr, cc)
                elif char == 'O':
                    if state.exit != None:
                        raise RuntimeError('multiple exits found')
                    state.exit = (rr, cc)
                else:
                    raise RuntimeError(f'unrecognized character: {char}')

        if state.player == None:
            raise RuntimeError('no player found')
        if state.exit == None:
            raise RuntimeError('no exit found')

        return level, state



    def loadself(self, filename, is_file, partial):
        if self.loaded:
            raise RuntimeError('already loaded')

        self.level, self.state = Game.load(filename, is_file, partial)
        self.loaded = True

    def stepself(self, action):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        self.state, _ = Game.step(self.level, self.state, action)

    def displayself(self):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        Game.display(self.level, self.state)



def completion(level, best_switches, best_cols):
    return 0.9 * ((best_switches + (best_cols / level.width)) / (level.switchcount + 1.0))

def heur(level, state):
    if len(state.switches) == 0:
        closest_dist_sqr = (state.player[0] - state.exit[0])**2 + (state.player[1] - state.exit[1])**2
        return closest_dist_sqr**0.5
    else:
        closest_dist_sqr = 1e100
        for switch in state.switches:
            closest_dist_sqr = min(closest_dist_sqr, (state.player[0] - switch[0])**2 + (state.player[1] - switch[1])**2)
        return closest_dist_sqr**0.5 + len(state.switches) * (level.width + level.height)

def compl_guess(level, state):
    return completion(level, level.switchcount - len(state.switches), state.player[1])

def dosolve(level, state, slow, allow_mod=False):
    # adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
    start = state.clone()
    start_tup = start.totuple()

    if start.exit in start.enemies:
        raise RuntimeError('enemy starts on exit')
    if start.exit in level.spikes:
        raise RuntimeError('spike on exit')

    frontier = []
    heapq.heappush(frontier, (0, start_tup, start))

    came_from = {}
    cost_so_far = {}
    came_from[start_tup] = (None, None, None)
    cost_so_far[start_tup] = 0

    best_state_guess = 0.0
    best_state_tup = start_tup

    min_switches = len(start.switches)
    state_count = 0

    while len(frontier) > 0:
        current_pri, current_tup, current = heapq.heappop(frontier)

        # stop after checking too many states
        state_count += 1
        if state_count > 100 * level.width * level.height:
            break

        # don't search states that have too many more remaining switches than the best seen so far
        if len(current.switches) < min_switches:
            min_switches = len(current.switches)
        elif len(current.switches) > min_switches + 1:
            continue
        
        if current.didwin:
            best_state_guess = 1.0
            best_state_tup = current_tup
            break

        actions_available = ACTIONS
        if slow and current.enemymv:
            actions_available = ['']
        
        for action in actions_available:
            nbr, mod = Game.step(level, current, action, allow_mod=allow_mod)
            nbr_tup = nbr.totuple()

            if mod in [None]:
                new_cost = cost_so_far[current_tup] + 1
            else:
                new_cost = cost_so_far[current_tup] + level.width + level.height

            if nbr_tup not in cost_so_far or new_cost < cost_so_far[nbr_tup]:
                cost_so_far[nbr_tup] = new_cost

                priority = new_cost + heur(level, nbr)

                guess = compl_guess(level, nbr)
                if guess > best_state_guess:
                    best_state_guess = guess
                    best_state_tup = nbr_tup

                heapq.heappush(frontier, (priority, nbr_tup, nbr))
                came_from[nbr_tup] = (action, current_tup, mod)

    modifications = []
    actions = []
    path = []

    path_found = State.fromtuple(best_state_tup).didwin

    current_tup = best_state_tup
    while current_tup is not None:
        path.append(State.fromtuple(current_tup))
        action, current_tup, mod = came_from[current_tup]
        actions.append(action)
        if mod not in [None]:
            modifications.append(mod)
    
    actions.reverse()
    actions = actions[1:]
    path.reverse()

    # debug check
    # chk_state = state.clone()
    # for ii in range(len(actions)):
    #     chk_state, _ = Game.step(level, chk_state, actions[ii])
    #     if chk_state.totuple() != path[ii+1].totuple():
    #         raise RuntimeError('actions do not follow path')

    # if chk_state.totuple() != best_state_tup:
    #     raise RuntimeError('actions do not lead to ending state')

    # if path_found and not chk_state.didwin:
    #     raise RuntimeError('actions do not lead to winning state but should')
            
    # if not path_found and chk_state.didwin:
    #     raise RuntimeError('actions lead to winning state but should not')

    return path_found, actions, modifications



def play(levelfile, is_file, partial):
    g = Game()
    g.loadself(levelfile, is_file, partial)

    while True:
        g.displayself()
        action = input()
        g.stepself(action)


def repair(levelfile, is_file, partial, display_states, display_solution):
    g = Game()
    g.loadself(levelfile, is_file, partial)
    modifications = [None]
    while len(modifications) > 0:
        solved, actions, modifications = dosolve(g.level, g.state.clone(), False, allow_mod=True)
        for mod in modifications:
            if mod.type == MOD_BLOCK:
                g.level.blocks.remove(mod.pos)
            elif mod.type == MOD_SPIKE:
                g.level.spikes.remove(mod.pos)
            elif mod.type == MOD_ENEMY:
                g.state.enemies = [pos for pos in g.state.enemies if pos != mod.pos]
                g.level.enemyst = [pos for pos in g.level.enemyst if pos != mod.pos]
            else:
                raise TypeError(f'Unrecognized modification type ({mod.type}) for position {mod.pos}')
    
    if display_states or display_solution:
        run(g.level, g.state.clone(), actions, solved, display_states, display_solution)

    level = [['-' for _ in range(g.level.width)] for _ in range(g.level.height)]
    for enemy in g.level.enemyst:
        level[enemy.row][enemy.col] = '#'

    for block in g.level.blocks:
        level[block.row][block.col] = 'X'

    for spike in g.level.spikes:
        level[spike.row][spike.col] = '^'


    return '\n'.join([''.join(row) for row in level])


def solve_and_run(levelfile, is_file, partial, flaw, display_states, display_solution):
    g = Game()
    g.loadself(levelfile, is_file, partial)

    solved, actions, _ = solve_for_run(g.level, g.state.clone(), flaw,)
    return run(g.level, g.state.clone(), actions, solved, display_states, display_solution)

def solve_for_run(level, state, flaw, allow_mod=False):
    if flaw not in FLAWS:
        raise RuntimeError('unrecognized flaw')

    slow = False
    if flaw == FLAW_NO_SPEED:
        slow = True
    
    solve_start = state.clone()
    if flaw == FLAW_NO_SPIKE:
        raise RuntimeError('floaw not currently supported')
        #solve_start.spikes = set()
    elif flaw == FLAW_NO_HAZARD:
        raise RuntimeError('floaw not currently supported')
        #solve_start.spikes = set()
        #solve_start.enemies = []
        #solve_start.enemyst = []

    # determine reachable tiles
    processing = []
    reachable = set()
    processing.append(solve_start.player)
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while len(processing) > 0:
        curr = processing.pop()
        if curr in reachable:
            continue
        reachable.add(curr)
        for dr, dc in DIRECTIONS:
            rr = curr[0] + dr
            cc = curr[1] + dc
            if 0 <= rr and rr < level.height and 0 <= cc and cc < level.width:
                if (rr, cc) not in level.blocks and (rr, cc) not in level.spikes:
                    processing.append((rr, cc))

    # move the exit if it's not reachable
    if solve_start.exit not in reachable:
        solve_start.exit = solve_start.player
        for rr, cc in reachable:
            if cc > solve_start.exit[1] and (rr, cc) not in solve_start.enemies and (rr, cc) not in solve_start.switches:
                solve_start.exit = (rr, cc)
        if solve_start.exit == solve_start.player:
            solve_start.didwin = True
    
    # remove unreachable switches
    reachable_switches = []
    for switch in solve_start.switches:
        if switch in reachable:
            reachable_switches.append(switch)
    solve_start.switches = reachable_switches

    return dosolve(level, solve_start, slow, allow_mod=allow_mod)

def run(level, state, actions, should_solve, display_states, display_solution):
    best_switches = 0
    best_cols = 0

    dsp_state = state.clone()

    if display_states:
        Game.display(level, dsp_state)

    current_switches = level.switchcount - len(dsp_state.switches)
    best_switches = max(best_switches, current_switches)
    current_cols = dsp_state.player[1] + 1
    best_cols = max(best_cols, current_cols)

    for action in actions:
        dsp_state, _ = Game.step(level, dsp_state, action)

        if display_states:
            print(action)
            Game.display(level, dsp_state)

        if dsp_state.didlose:
            break

        current_switches = level.switchcount - len(dsp_state.switches)
        best_switches = max(best_switches, current_switches)
        current_cols = dsp_state.player[1] + 1
        best_cols = max(best_cols, current_cols)

        if dsp_state.didwin:
            break

    if not should_solve and dsp_state.didwin:
        raise RuntimeError('no path found but still won')

    if display_solution:
        if not should_solve:
            print('No path found!')
        elif dsp_state.didlose:
            print('Lost!')
        elif dsp_state.didwin:
            print('Won!')
        else:
            print('Didn\'t win or lose!')

        print('Best switches: %d / %d.' % (best_switches, level.switchcount))
        print('Best column: %d / %d.' % (best_cols, level.width))

    return dsp_state.didwin, level, best_switches, best_cols

def percent_playable(levelfile, is_file, partial, flaw):
    didwin, level, best_switches, best_cols = solve_and_run(levelfile, is_file, partial, flaw, False, False)

    if didwin:
        return 1.0

    return completion(level, best_switches, best_cols)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('levelfile', type=str,help='Input level file.')
    parser.add_argument('--play', action='store_true', help='Play level.')
    parser.add_argument('--partial', action='store_true', help='Add player and exit to partial level.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--solve', action='store_true', help='Solve level.')
    group.add_argument('--repair', action='store_true', help='Repair level.')
    parser.add_argument('--playability', action='store_true', help='Calculate level playability value.')
    parser.add_argument('--hidestates', action='store_true', help='Hide any solver states that would be displayed.')
    parser.add_argument('--flaw', type=str, help='Flaw for solver: ' + (', '.join(FLAWS)) + '.', default=FLAW_NO_FLAW)
    args = parser.parse_args()

    if args.play:
        play(args.levelfile, True, args.partial)

    elif args.solve:
        solve_and_run(args.levelfile, True, args.partial, args.flaw, not args.hidestates, True)

    elif args.repair:
        repair(args.levelfile, True, args.partial, not args.hidestates, True)
        
    elif args.playability:
        print(percent_playable(args.levelfile, True, args.partial, args.flaw))

    else:
        parser.print_help()


