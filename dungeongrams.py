import argparse, heapq, math, pprint, random, sys
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



class State:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.enemyst = []
        self.enemymv = False
        self.spikes = []
        self.switches = []
        self.didwin = False
        self.didlose = False

    def clone(self):
        return State.fromtuple(self.totuple())

    def totuple(self):
        return (self.player, tuple(self.enemies), tuple(self.enemyst), self.enemymv, tuple(self.spikes), tuple(self.switches), self.didwin, self.didlose)

    @staticmethod
    def fromtuple(tup):
        ret = State()
        ret.player = tup[0]
        ret.enemies = list(tup[1])
        ret.enemyst = list(tup[2])
        ret.enemymv = tup[3]
        ret.spikes = list(tup[4])
        ret.switches = list(tup[5])
        ret.didwin = tup[6]
        ret.didlose = tup[7]
        return ret



class Level:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.switchcount = 0
        self.exit = None
        self.blocks = set()



class Game:
    def __init__(self):
        self.loaded = False

        self.level = None
        self.state = None



    @staticmethod
    def validmoveforplayer(level, state, rc, dr, dc):
        nr = rc[0] + dr
        nc = rc[1] + dc
        if nr < 0:
            return False
        if nc < 0:
            return False
        if nr >= level.height:
            return False
        if nc >= level.width:
            return False

        tup = (nr, nc)
        if tup in level.blocks:
            return False

        if tup == level.exit and len(state.switches) > 0:
            return False

        return tup

    @staticmethod
    def validmoveforenemy(level, state, rc, dr, dc):
        if not Game.validmoveforplayer(level, state, rc, dr, dc):
            return False

        nr = rc[0] + dr
        nc = rc[1] + dc

        tup = (nr, nc)
        
        if tup == level.exit:
            return False

        if tup in state.enemies:
            return False

        if tup in state.spikes:
            return False

        if tup in state.switches:
            return False

        return tup

    @staticmethod
    def playercollidehazard(level, state):
        if state.player in state.enemies:
            return True
        if state.player in state.spikes:
            return True
        return False

    @staticmethod
    def step(level, state, action):
        newstate = state.clone()

        if newstate.didwin:
            return newstate
        if newstate.didlose:
            return newstate

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

        pnrc = Game.validmoveforplayer(level, newstate, newstate.player, pdr, pdc)
        if pnrc:
            newstate.player = pnrc

        if Game.playercollidehazard(level, newstate):
            newstate.didlose = True
            
        elif newstate.player == level.exit:
            newstate.didwin = True

        elif newstate.player in newstate.switches:
            del newstate.switches[newstate.switches.index(newstate.player)]

        
        if not newstate.enemymv:
            newstate.enemymv = True
        else:
            newstate.enemymv = False
            
            for ii in range(len(newstate.enemies)):
                strr, stcc = newstate.enemyst[ii]
                stdr = newstate.player[0] - strr
                stdc = newstate.player[1] - stcc

                if (stdr**2 + stdc**2)**0.5 <= ENEMY_RANGE:
                    tgrr = newstate.player[0]
                    tgcc = newstate.player[1]
                else:
                    tgrr = newstate.enemyst[ii][0]
                    tgcc = newstate.enemyst[ii][1]
                    
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
                        enrc = Game.validmoveforenemy(level, newstate, newstate.enemies[ii], edr, edc)
                        if enrc:
                            newstate.enemies[ii] = enrc
                            break

        if Game.playercollidehazard(level, newstate):
            newstate.didlose = True

        return newstate

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
                elif (rr, cc) in state.spikes:
                    sys.stdout.write('^')
                elif (rr, cc) in state.switches:
                    sys.stdout.write('*')
                elif (rr, cc) == level.exit:
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

        rows = []
        if is_file:
            with open(filename) as level_file:
                for line in level_file.readlines():
                    line = line.strip()

                    if level.width == 0:
                        level.width = len(line)
                    elif level.width != len(line):
                        raise RuntimeError('lines not all same length')

                    level.height += 1

                    rows.append(line)
        else:
            rows = filename
            level.width = len(rows[0])
            level.height = len(rows)

        if partial:
            level.width += 4
            
            newrows = []
            for rr, row in enumerate(rows):
                pref = '@-' if rr == 0 else '--'
                suff = '-O' if rr + 1 == len(rows) else '--'
                newrows.append(pref + row + suff)
            rows = newrows

        for rr, row in enumerate(rows):
            for cc, char in enumerate(row):
                if char == '-':
                    pass
                elif char == 'X':
                    level.blocks.add((rr, cc))
                elif char == '#':
                    state.enemies.append((rr, cc))
                    state.enemyst.append((rr, cc))
                elif char == '^':
                    state.spikes.append((rr, cc))
                elif char == '*':
                    state.switches.append((rr, cc))
                    level.switchcount += 1
                elif char == '@':
                    if state.player != None:
                        raise RuntimeError('multiple players found')
                    state.player = (rr, cc)
                elif char == 'O':
                    if level.exit != None:
                        raise RuntimeError('multiple exits found')
                    level.exit = (rr, cc)
                else:
                    raise RuntimeError(f'unrecognized character: {char}')

        if state.player == None:
            raise RuntimeError('no player found')
        if level.exit == None:
            raise RuntimeError('no exit found')

        # sort switches from low to high column, for solve order
        state.switches = sorted(state.switches, key=lambda x: x[1])

        return level, state



    def loadself(self, filename, is_file, partial):
        if self.loaded:
            raise RuntimeError('already loaded')

        self.level, self.state = Game.load(filename, is_file, partial)
        self.loaded = True

    def stepself(self, action):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        self.state = Game.step(self.level, self.state, action)

    def displayself(self):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        Game.display(self.level, self.state)



def completion(level, best_switches, best_cols):
    return 0.9 * ((best_switches + (best_cols / level.width)) / (level.switchcount + 1.0))

def heur(level, state):
    if len(state.switches) == 0:
        dist_sqr = (state.player[0] - level.exit[0])**2 + (state.player[1] - level.exit[1])**2
        return dist_sqr**0.5
    else:
        dist_sqr = (state.player[0] - state.switches[0][0])**2 + (state.player[1] - state.switches[0][1])**2
        return dist_sqr**0.5 + len(state.switches) * (level.width + level.height)

def compl_guess(level, state):
    return completion(level, level.switchcount - len(state.switches), state.player[1])

def dosolve(level, state, slow):
    # adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html
    start = state.clone()
    start_tup = start.totuple()

    frontier = []
    heapq.heappush(frontier, (0, start_tup))

    came_from = {}
    cost_so_far = {}
    came_from[start_tup] = (None, None)
    cost_so_far[start_tup] = 0

    path_found = False
    best_state_guess = 0.0
    best_state_tup = start_tup

    while len(frontier) > 0:
        current_tup = heapq.heappop(frontier)[1]
        current = State.fromtuple(current_tup)

        if current.player == level.exit:
            path_found = True
            best_state_guess = 1.0
            best_state_tup = current_tup
            break

        actions_available = ACTIONS
        if slow and current.enemymv:
            actions_available = ['']
        
        for action in actions_available:
            nbr = Game.step(level, current, action)

            # only try getting switches in order
            if len(nbr.switches) != len(current.switches):
                if nbr.switches != current.switches[1:]:
                    continue
            
            nbr_tup = nbr.totuple()

            new_cost = cost_so_far[current_tup] + 1
            if nbr_tup not in cost_so_far or new_cost < cost_so_far[nbr_tup]:
                cost_so_far[nbr_tup] = new_cost

                priority = new_cost + heur(level, nbr)

                guess = compl_guess(level, nbr)
                if guess > best_state_guess:
                    best_state_guess = guess
                    best_state_tup = nbr_tup

                heapq.heappush(frontier, (priority, nbr_tup))
                came_from[nbr_tup] = (action, current_tup)

    actions = []
    path = []

    current_tup = best_state_tup
    while current_tup is not None:
        path.append(State.fromtuple(current_tup))
        action, current_tup = came_from[current_tup]
        actions.append(action)
    actions.reverse()
    actions = actions[1:]
    path.reverse()

    # debug check
    chk_state = state.clone()
    for ii in range(len(actions)):
        chk_state = Game.step(level, chk_state, actions[ii])
        if chk_state.totuple() != path[ii+1].totuple():
            raise RuntimeError('actions do not follow path')

    if path_found and not chk_state.didwin:
        raise RuntimeError('actions do not lead to winning state but should')
            
    if not path_found and chk_state.didwin:
        raise RuntimeError('actions lead to winning state but should not')

    return path_found, actions




def play(levelfile, is_file, partial):
    g = Game()
    g.loadself(levelfile, is_file, partial)

    while True:
        g.displayself()
        action = input()
        g.stepself(action)

def solve_and_play(levelfile, is_file, partial, flaw, display):
    if flaw not in FLAWS:
        raise RuntimeError('unrecognized flaw')

    g = Game()
    g.loadself(levelfile, is_file, partial)

    slow = False
    if flaw == FLAW_NO_SPEED:
        slow = True
    
    solve_start = g.state.clone()
    if flaw == FLAW_NO_SPIKE:
        solve_start.spikes = []
    elif flaw == FLAW_NO_HAZARD:
        solve_start.spikes = []
        solve_start.enemies = []
        solve_start.enemyst = []

    solved, actions = dosolve(g.level, solve_start, slow)

    best_switches = 0
    best_cols = 0

    dsp_state = g.state.clone()

    if display:
        Game.display(g.level, dsp_state)

    current_switches = g.level.switchcount - len(dsp_state.switches)
    best_switches = max(best_switches, current_switches)
    current_cols = dsp_state.player[1] + 1
    best_cols = max(best_cols, current_cols)

    for action in actions:
        dsp_state = Game.step(g.level, dsp_state, action)

        if display:
            print(action)
            Game.display(g.level, dsp_state)

        if dsp_state.didlose:
            break

        current_switches = g.level.switchcount - len(dsp_state.switches)
        best_switches = max(best_switches, current_switches)
        current_cols = dsp_state.player[1] + 1
        best_cols = max(best_cols, current_cols)

        if dsp_state.didwin:
            break

    if not solved and dsp_state.didwin:
        raise RuntimeError('no path found but still won')

    if display:
        if not solved:
            print('No path found!')
        elif dsp_state.didlose:
            print('Lost!')
        elif dsp_state.didwin:
            print('Won!')

        print('Best switches: %d / %d.' % (best_switches, g.level.switchcount))
        print('Best column: %d / %d.' % (best_cols, g.level.width))

    return dsp_state.didwin, g.level, best_switches, best_cols

def percent_playable(levelfile, is_file, partial, flaw):
    didwin, level, best_switches, best_cols = solve_and_play(levelfile, is_file, partial, flaw, False)

    if didwin:
        return 1.0

    return completion(level, best_switches, best_cols)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('levelfile', type=str,help='Input level file.')
    parser.add_argument('--play', action='store_true', help='Play level.')
    parser.add_argument('--partial', action='store_true', help='Add player and exit to partial level.')
    parser.add_argument('--solve', action='store_true', help='Solve level.')
    parser.add_argument('--playability', action='store_true', help='Calculate level playability value.')
    parser.add_argument('--flaw', type=str, help='Flaw for solver: ' + (', '.join(FLAWS)) + '.', default=FLAW_NO_FLAW)
    args = parser.parse_args()

    if int(args.play) + int(args.solve) + int(args.playability) != 1:
        raise RuntimeError('exactly one of --play, --solve, --playability must be given')

    if args.play:
        play(args.levelfile, True, args.partial)

    elif args.solve:
        solve_and_play(args.levelfile, True, args.partial, args.flaw, True)

    elif args.playability:
        print(percent_playable(args.levelfile, True, args.partial, args.flaw))
