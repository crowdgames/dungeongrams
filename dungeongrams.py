import argparse, heapq, math, pprint, random, sys
from os.path import isfile

ACTIONS = [ ' ', 'w', 'a', 's', 'd' ]

STAMINA_STARTING    = 40
STAMINA_FOOD        = 30

ENEMY_RANGE = 3

CHAR_BLANK          = '-'
CHAR_PLAYER_PLAYING = '@'
CHAR_PLAYER_WON     = '!'
CHAR_PLAYER_LOST    = '%'
CHAR_EXIT_CLOSED    = 'o'
CHAR_EXIT_OPEN      = 'O'
CHAR_ENEMY          = '#'
CHAR_SWITCH         = '*'
CHAR_FOOD           = '&'
CHAR_SPIKE          = '^'
CHAR_BLOCK          = 'X'
CHAR_STRUCTURE_1    = '/'
CHAR_STRUCTURE_2    = '\\'

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



class State:
    def __init__(self):
        self.player = None
        self.stamina = None
        self.exit = None
        self.enemies = []
        self.enemymv = False
        self.switches = []
        self.food = []
        self.didwin = False
        self.didlose = False

    def clone(self):
        ret = State()
        ret.player = self.player
        ret.stamina = self.stamina
        ret.exit = self.exit
        ret.enemies = list(self.enemies)
        ret.enemymv = self.enemymv
        ret.switches = list(self.switches)
        ret.food = list(self.food)
        ret.didwin = self.didwin
        ret.didlose = self.didlose
        return ret

    def totuple(self):
        return (self.player, self.stamina, self.exit, tuple(self.enemies), self.enemymv, tuple(self.switches), tuple(self.food), self.didwin, self.didlose)

    @staticmethod
    def fromtuple(tup):
        ret = State()
        ret.player = tup[0]
        ret.stamina = tup[1]
        ret.exit = tup[2]
        ret.enemies = list(tup[3])
        ret.enemymv = tup[4]
        ret.switches = list(tup[5])
        ret.food = list(tup[6])
        ret.didwin = tup[7]
        ret.didlose = tup[8]
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

        if tup == state.exit and len(state.switches) > 0:
            return False

        return tup

    @staticmethod
    def validmoveforenemy(level, state, rc, dr, dc):
        if not Game.validmoveforplayer(level, state, rc, dr, dc):
            return False

        nr = rc[0] + dr
        nc = rc[1] + dc

        tup = (nr, nc)

        if tup == state.exit:
            return False

        if tup in state.enemies:
            return False

        if tup in level.spikes:
            return False

        if tup in state.switches:
            return False

        if tup in state.food:
            return False

        return tup

    @staticmethod
    def playercollidehazard(level, state):
        if state.player in state.enemies:
            return True
        if state.player in level.spikes:
            return True
        return False

    @staticmethod
    def step(level, state, action):
        newstate = state.clone()

        if newstate.didwin:
            return newstate
        if newstate.didlose:
            return newstate

        if action in [' ']:
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

        elif newstate.player == newstate.exit:
            newstate.didwin = True

        elif newstate.player in newstate.switches:
            del newstate.switches[newstate.switches.index(newstate.player)]

        elif newstate.player in newstate.food:
            newstate.stamina = min(newstate.stamina + STAMINA_FOOD, STAMINA_STARTING)
            del newstate.food[newstate.food.index(newstate.player)]

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
                        enrc = Game.validmoveforenemy(level, newstate, newstate.enemies[ii], edr, edc)
                        if enrc:
                            newstate.enemies[ii] = enrc
                            break

        if Game.playercollidehazard(level, newstate):
            newstate.didlose = True

        newstate.stamina -= 1
        if newstate.stamina < 0:
                raise RuntimeError('negative stamina')
        if newstate.stamina == 0:
            newstate.didlose = True

        return newstate

    @staticmethod
    def display(level, state):
        for cc in range(level.width + 2):
            sys.stdout.write(CHAR_BLOCK)
        sys.stdout.write('\n')

        for rr in range(level.height):
            sys.stdout.write(CHAR_BLOCK)
            for cc in range(level.width):
                if (rr, cc) == state.player:
                    if state.didlose:
                        sys.stdout.write(CHAR_PLAYER_LOST)
                    elif state.didwin:
                        sys.stdout.write(CHAR_PLAYER_WON)
                    else:
                        sys.stdout.write(CHAR_PLAYER_PLAYING)
                elif (rr, cc) in state.enemies:
                    sys.stdout.write(CHAR_ENEMY)
                elif (rr, cc) in level.spikes:
                    sys.stdout.write(CHAR_SPIKE)
                elif (rr, cc) in state.switches:
                    sys.stdout.write(CHAR_SWITCH)
                elif (rr, cc) in state.food:
                    sys.stdout.write(CHAR_FOOD)
                elif (rr, cc) == state.exit:
                    if len(state.switches) == 0:
                        sys.stdout.write(CHAR_EXIT_OPEN)
                    else:
                        sys.stdout.write(CHAR_EXIT_CLOSED)
                elif (rr, cc) in level.blocks:
                    sys.stdout.write(CHAR_BLOCK)
                else:
                    sys.stdout.write('-')
            sys.stdout.write(CHAR_BLOCK)
            sys.stdout.write('\n')

        for cc in range(level.width + 2):
            sys.stdout.write(CHAR_BLOCK)
        sys.stdout.write('\n')

        sys.stdout.write('stamina: %d\n' % state.stamina)
        sys.stdout.write('\n')

    @staticmethod
    def load(filename, is_file, partial):
        level = Level()
        state = State()

        state.stamina = STAMINA_STARTING

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
                pref = (CHAR_PLAYER_PLAYING + CHAR_BLANK) if rr == 0             else (CHAR_BLANK + CHAR_BLANK)
                suff = (CHAR_BLANK + CHAR_EXIT_OPEN)      if rr + 1 == len(rows) else (CHAR_BLANK + CHAR_BLANK)
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
                elif char == CHAR_BLOCK:
                    level.blocks.add((rr, cc))
                elif char == CHAR_STRUCTURE_1:
                    level.blocks.add((rr, cc))
                elif char == CHAR_STRUCTURE_2:
                    level.blocks.add((rr, cc))
                elif char == CHAR_ENEMY:
                    state.enemies.append((rr, cc))
                    level.enemyst.append((rr, cc))
                elif char == CHAR_SPIKE:
                    level.spikes.add((rr, cc))
                elif char == CHAR_SWITCH:
                    state.switches.append((rr, cc))
                    level.switchcount += 1
                elif char == CHAR_FOOD:
                    state.food.append((rr, cc))
                elif char == CHAR_PLAYER_PLAYING:
                    if state.player != None:
                        raise RuntimeError('multiple players found')
                    state.player = (rr, cc)
                elif char == CHAR_EXIT_OPEN:
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

        self.state = Game.step(self.level, self.state, action)

    def displayself(self):
        if not self.loaded:
            raise RuntimeError('not loaded')

        Game.display(self.level, self.state)



def completion(level, best_switches, best_cols):
    return 0.9 * ((best_switches + (best_cols / level.width)) / (level.switchcount + 1.0))

def heur(level, state):
    if len(state.switches) == 0:
        closest_dist_sqr = (state.player[0] - state.exit[0])**2 + (state.player[1] - state.exit[1])**2
        return -state.stamina + closest_dist_sqr**0.5
    else:
        closest_dist_sqr = 1e100
        for switch in state.switches:
            closest_dist_sqr = min(closest_dist_sqr, (state.player[0] - switch[0])**2 + (state.player[1] - switch[1])**2)
        return -state.stamina + closest_dist_sqr**0.5 + len(state.switches) * (level.width + level.height)

def compl_guess(level, state):
    return completion(level, level.switchcount - len(state.switches), state.player[1])

def dosolve(level, state, thorough, slow):
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
    came_from[start_tup] = (None, None)
    cost_so_far[start_tup] = 0

    best_state_guess = 0.0
    best_state_tup = start_tup

    min_switches = len(start.switches)
    state_count = 0

    while len(frontier) > 0:
        current_pri, current_tup, current = heapq.heappop(frontier)

        if not thorough:
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
            actions_available = [' ']

        for action in actions_available:
            nbr = Game.step(level, current, action)
            nbr_tup = nbr.totuple()

            new_cost = cost_so_far[current_tup] + 1
            if nbr_tup not in cost_so_far or new_cost < cost_so_far[nbr_tup]:
                cost_so_far[nbr_tup] = new_cost

                priority = new_cost + heur(level, nbr)

                guess = compl_guess(level, nbr)
                if guess > best_state_guess:
                    best_state_guess = guess
                    best_state_tup = nbr_tup

                heapq.heappush(frontier, (priority, nbr_tup, nbr))
                came_from[nbr_tup] = (action, current_tup)

    actions = []
    path = []

    path_found = State.fromtuple(best_state_tup).didwin

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

    if chk_state.totuple() != best_state_tup:
        raise RuntimeError('actions do not lead to ending state')

    if path_found and not chk_state.didwin:
        raise RuntimeError('actions do not lead to winning state but should')

    if not path_found and chk_state.didwin:
        raise RuntimeError('actions lead to winning state but should not')

    return path_found, actions




def play(levelfile, is_file, partial):
    # https://stackoverflow.com/questions/510357/how-to-read-a-single-character-from-the-user
    def _find_getch():
        try:
            import termios
        except ImportError:
            # Non-POSIX. Return msvcrt's (Windows') getch.
            import msvcrt
            return msvcrt.getch

        # POSIX system. Create and return a getch that manipulates the tty.
        import sys, tty
        def _getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return _getch

    getch = _find_getch()

    g = Game()
    g.loadself(levelfile, is_file, partial)

    while True:
        g.displayself()

        action = getch()

        if action == 'q' or ord(action) == 3:
            break

        if action not in ACTIONS:
            print('Unrecognized input.')
        else:
            g.stepself(action)



def solve_and_run(levelfile, is_file, partial, thorough, flaw, display_states, display_solution):
    g = Game()
    g.loadself(levelfile, is_file, partial)

    solved, actions = solve_for_run(g.level, g.state.clone(), thorough, flaw)
    return run(g.level, g.state.clone(), actions, solved, display_states, display_solution)

def solve_for_run(level, state, thorough, flaw):
    if flaw not in FLAWS:
        raise RuntimeError('unrecognized flaw')

    slow = False
    if flaw == FLAW_NO_SPEED:
        slow = True

    solve_start = state.clone()
    if flaw == FLAW_NO_SPIKE:
        raise RuntimeError('flaw not currently supported')
    elif flaw == FLAW_NO_HAZARD:
        raise RuntimeError('flaw not currently supported')

    # determine reachable tiles
    processing = []
    reachable = set()
    processing.append(solve_start.player)
    while len(processing) > 0:
        curr = processing.pop()
        if curr in reachable:
            continue
        reachable.add(curr)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
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

    return dosolve(level, solve_start, thorough, slow)

def run(level, state, actions, should_solve, display_states, display_solution):
    positions = [state.player]
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
        dsp_state = Game.step(level, dsp_state, action)
        positions.append(dsp_state.player)

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

    return dsp_state.didwin, level, best_switches, best_cols, positions, dsp_state.stamina

def percent_playable(levelfile, is_file, partial, thorough, flaw):
    didwin, level, best_switches, best_cols, _, _ = solve_and_run(levelfile, is_file, partial, thorough, flaw, False, False)

    if didwin:
        return 1.0

    return completion(level, best_switches, best_cols)

def get_path(levelfile, is_file, partial, thorough, flaw):
    didwin, _, _, _, positions = solve_and_run(levelfile, is_file, partial, thorough, flaw, False, False)
    return didwin, positions

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('levelfile', type=str,help='Input level file.')
    parser.add_argument('--play', action='store_true', help='Play level.')
    parser.add_argument('--partial', action='store_true', help='Add player and exit to partial level.')
    parser.add_argument('--solve', action='store_true', help='Solve level.')
    parser.add_argument('--playability', action='store_true', help='Calculate level playability value.')
    parser.add_argument('--thorough', action='store_true', help='Perform a more thorough, but slower, search for a solution.')
    parser.add_argument('--hidestates', action='store_true', help='Hide any solver states that would be displayed.')
    parser.add_argument('--flaw', type=str, help='Flaw for solver: ' + (', '.join(FLAWS)) + '.', default=FLAW_NO_FLAW)
    args = parser.parse_args()

    if int(args.play) + int(args.solve) + int(args.playability) != 1:
        raise RuntimeError('exactly one of --play, --solve, --playability must be given')

    if args.thorough and not (args.solve or args.playability):
        raise RuntimeError('--thorough only works with  --solve or --playability')

    if args.play:
        play(args.levelfile, True, args.partial)

    elif args.solve:
        solve_and_run(args.levelfile, True, args.partial, args.thorough, args.flaw, not args.hidestates, True)

    elif args.playability:
        print(percent_playable(args.levelfile, True, args.partial, args.thorough, args.flaw))

