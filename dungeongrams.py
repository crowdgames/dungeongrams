import argparse, math, pprint, queue, random, sys

ACTIONS = [ '', 'w', 'a', 's', 'd' ]
ACTIONS_SLOW = [ 'X', 'wX', 'aX', 'sX', 'dX' ]

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

        if (nr, nc) in level.blocks:
            return False

        if (nr, nc) == level.exit and len(state.switches) > 0:
            return False

        return (nr, nc)

    @staticmethod
    def validmoveforenemy(level, state, rc, dr, dc):
        if not Game.validmoveforplayer(level, state, rc, dr, dc):
            return False

        nr = rc[0] + dr
        nc = rc[1] + dc
        
        if (nr, nc) == level.exit:
            return False

        if (nr, nc) in state.enemies:
            return False

        if (nr, nc) in state.spikes:
            return False

        if (nr, nc) in state.switches:
            return False

        return (nr, nc)

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

        if action in ['', 'X']:
            dr, dc = 0, 0
        elif action in ['w', 'wX']:
            dr, dc = -1, 0
        elif action in ['s', 'sX']:
            dr, dc = 1, 0
        elif action in ['a', 'aX']:
            dr, dc = 0, -1
        elif action in ['d', 'dX']:
            dr, dc = 0, 1
        else:
            raise RuntimeError('unrecognized action')

        nrc = Game.validmoveforplayer(level, newstate, newstate.player, dr, dc)
        if nrc:
            newstate.player = nrc

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
                    
                rr, cc = newstate.enemies[ii]
                dr = tgrr - rr
                dc = tgcc - cc

                if (dr, dc) == (0, 0):
                    pass
                else:
                    trymoves = []
                    if abs(dr) > abs(dc):
                        if dr > 0:
                            trymoves.append((1, 0))
                        elif dr < 0:
                            trymoves.append((-1, 0))
                        if dc > 0:
                            trymoves.append((0, 1))
                        elif dc < 0:
                            trymoves.append((0, -1))
                    elif abs(dc) > abs(dr):
                        if dc > 0:
                            trymoves.append((0, 1))
                        elif dc < 0:
                            trymoves.append((0, -1))
                        if dr > 0:
                            trymoves.append((1, 0))
                        elif dr < 0:
                            trymoves.append((-1, 0))
                    elif (rr + cc) % 2 == 0:
                        if dr > 0:
                            trymoves.append((1, 0))
                        elif dr < 0:
                            trymoves.append((-1, 0))
                        if dc > 0:
                            trymoves.append((0, 1))
                        elif dc < 0:
                            trymoves.append((0, -1))
                    else:
                        if dc > 0:
                            trymoves.append((0, 1))
                        elif dc < 0:
                            trymoves.append((0, -1))
                        if dr > 0:
                            trymoves.append((1, 0))
                        elif dr < 0:
                            trymoves.append((-1, 0))

                    for dr, dc in trymoves:
                        nrc = Game.validmoveforenemy(level, newstate, newstate.enemies[ii], dr, dc)
                        if nrc:
                            newstate.enemies[ii] = nrc
                            break

        if Game.playercollidehazard(level, newstate):
            newstate.didlose = True

        if action in ['X' 'wX', 'sX', 'aX', 'dX']:
            return Game.step(level, newstate, '')
        else:
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
                    sys.stdout.write('~')
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
    def load(filename, partial):
        level = Level()
        state = State()

        rows = []
        with open(filename) as level_file:
            for line in level_file.readlines():
                line = line.strip()

                if level.width == 0:
                    level.width = len(line)
                elif level.width != len(line):
                    raise RuntimeError('lines not all same length')

                level.height += 1

                rows.append(line)

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
                elif char == '~':
                    state.switches.append((rr, cc))
                elif char == '@':
                    if state.player != None:
                        raise RuntimeError('multiple players found')
                    state.player = (rr, cc)
                elif char == 'O':
                    if level.exit != None:
                        raise RuntimeError('multiple exits found')
                    level.exit = (rr, cc)
                else:
                    raise RuntimeError('unrecognized character')

        if state.player == None:
            raise RuntimeError('no player found')
        if level.exit == None:
            raise RuntimeError('no exit found')

        return level, state



    def loadself(self, filename, partial):
        if self.loaded:
            raise RuntimeError('already loaded')

        self.level, self.state = Game.load(filename, partial)
        
        self.loaded = True

    def stepself(self, action):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        self.state = Game.step(self.level, self.state, action)

    def displayself(self):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        Game.display(self.level, self.state)

        

def dosolve(level, state, solve_actions):
    # adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html

    start = state.clone()
    start_tup = start.totuple()
    tiebreaker = 0

    frontier = queue.PriorityQueue()
    frontier.put((0, start_tup))
    came_from = {}
    cost_so_far = {}
    came_from[start_tup] = (None, None)
    cost_so_far[start_tup] = 0

    furthest_col = 0
    path_found = None

    while not frontier.empty():
        current_tup = frontier.get()[1]
        current = State.fromtuple(current_tup)

        furthest_col = max(furthest_col, current.player[1])

        if current.player == level.exit:
            path_found = current_tup
            break

        neighbors = set()
        for action in solve_actions:
            neighbors.add((action, Game.step(level, current, action)))

        for action, nbr in neighbors:
            nbr_tup = nbr.totuple()

            new_cost = cost_so_far[current_tup] + 1
            if nbr_tup not in cost_so_far or new_cost < cost_so_far[nbr_tup]:
                cost_so_far[nbr_tup] = new_cost
                priority = new_cost + 0
                frontier.put((priority, nbr_tup))
                came_from[nbr_tup] = (action, current_tup)

    if path_found is None:
        return False, (furthest_col, level.width)

    else:
        actions = []
        path = []

        current_tup = path_found
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

        if not chk_state.didwin:
            raise RuntimeError('actions do not lead to winning state')
            
        return True, actions




def play(levelfile, partial):
    g = Game()
    g.loadself(levelfile, partial)

    while True:
        g.displayself()
        action = input()
        g.stepself(action)

def solve(levelfile, partial, display, flaw):
    if flaw not in FLAWS:
        raise RuntimeError('unrecognized flaw')

    g = Game()
    g.loadself(levelfile, partial)

    solve_actions = ACTIONS
    if flaw == FLAW_NO_SPEED:
        solve_actions = ACTIONS_SLOW
    
    solve_start = g.state.clone()
    if flaw == FLAW_NO_SPIKE:
        solve_start.spikes = []
    elif flaw == FLAW_NO_HAZARD:
        solve_start.spikes = []
        solve_start.enemies = []
        solve_start.enemyst = []

    solved, info = dosolve(g.level, solve_start, solve_actions)

    if not solved:
        print('No path found.')
        print('Max column: %d / %d.' % info)

    else:
        dsp_state = g.state.clone()
        
        if display:
            Game.display(g.level, dsp_state)

        for action in info:
            dsp_state = Game.step(g.level, dsp_state, action)
            
            if display:
                print(action)
                Game.display(g.level, dsp_state)

            if dsp_state.didlose:
                print('Lost!')
                break
            elif dsp_state.didwin:
                print('Won!')
                break




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('levelfile', type=str,help='Input level file.')
    parser.add_argument('--play', action='store_true', help='Play level.')
    parser.add_argument('--partial', action='store_true', help='Add player and exit to partial level.')
    parser.add_argument('--solve', action='store_true', help='Solve level.')
    parser.add_argument('--flaw', type=str, help='Flaw for solver: ' + (', '.join(FLAWS)) + '.', default=FLAW_NO_FLAW)
    args = parser.parse_args()

    if args.play == args.solve:
        raise RuntimeError('exactly one of --play and --solve must be given')

    if args.play:
        play(args.levelfile, args.partial)

    elif args.solve:
        solve(args.levelfile, args.partial, True, args.flaw)
