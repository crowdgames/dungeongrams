import argparse, copy, math, pprint, queue, random, sys



class State:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.enemyst = []
        self.switches = []
        self.didwin = False
        self.didlose = False

    def __eq__(self, other):
        return self.player, self.enemies, self.enemyst, self.switches, self.didwin, self.didlose == other.player, other.enemies, other.enemyst, other.switches, other.didwin, other.didlose
    
    def __hash__(self):
        return hash(self.player) + hash(tuple(self.enemies)) + hash(tuple(self.enemyst)) + hash(tuple(self.switches)) + hash(self.didwin) + hash(self.didlose)



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

        if (nr, nc) in state.switches:
            return False

        return (nr, nc)

    @staticmethod
    def enemycollide(level, state):
        for enemy in state.enemies:
            if enemy == state.player:
                return True
        return False

    @staticmethod
    def step(level, state, action):
        newstate = copy.deepcopy(state)

        if newstate.didwin:
            return newstate
        if newstate.didlose:
            return newstate

        if action == 'w':
            dr, dc = -1, 0
        elif action == 's':
            dr, dc = 1, 0
        elif action == 'a':
            dr, dc = 0, -1
        elif action == 'd':
            dr, dc = 0, 1
        else:
            dr, dc = 0, 0

        nrc = Game.validmoveforplayer(level, newstate, newstate.player, dr, dc)
        if nrc:
            newstate.player = nrc

        if Game.enemycollide(level, newstate):
            newstate.didlose = True
            
        elif newstate.player == level.exit:
            newstate.didwin = True

        elif newstate.player in newstate.switches:
            del newstate.switches[newstate.switches.index(newstate.player)]

        for ii in range(len(newstate.enemies)):
            if newstate.enemyst[ii] == 0:
                newstate.enemyst[ii] = 1
            else:
                newstate.enemyst[ii] = 0

                rr, cc = newstate.enemies[ii]
                dr = newstate.player[0] - rr
                dc = newstate.player[1] - cc

                if (dr**2 + dc**2)**0.5 <= 8:
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

        if Game.enemycollide(level, newstate):
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
                elif (rr, cc) in state.switches:
                    sys.stdout.write('~')
                elif (rr, cc) == level.exit:
                    if len(state.switches) == 0:
                        sys.stdout.write('*')
                    else:
                        sys.stdout.write('-')
                elif (rr, cc) in level.blocks:
                    sys.stdout.write('X')
                else:
                    sys.stdout.write('.')
            sys.stdout.write('X')
            sys.stdout.write('\n')

        for cc in range(level.width + 2):
            sys.stdout.write('X')
        sys.stdout.write('\n')

    @staticmethod
    def load(filename):
        level = Level()
        state = State()
        
        with open(filename) as level_file:
            for rr, line in enumerate(level_file.readlines()):
                line = line.strip()

                if level.width == 0:
                    level.width = len(line)
                elif level.width != len(line):
                    raise RuntimeError('lines not all same length')

                level.height += 1

                for cc, char in enumerate(line):
                    if char == '.':
                        pass
                    elif char == 'X':
                        level.blocks.add((rr, cc))
                    elif char == '~':
                        state.switches.append((rr, cc))
                    elif char == '#':
                        state.enemies.append((rr, cc))
                        state.enemyst.append(0)
                    elif char == '@':
                        if state.player != None:
                            raise RuntimeError('multiple players found')
                        state.player = (rr, cc)
                    elif char == '*':
                        if level.exit != None:
                            raise RuntimeError('multiple exits found')
                        level.exit = (rr, cc)

        if state.player == None:
            raise RuntimeError('no player found')
        if level.exit == None:
            raise RuntimeError('no exit found')

        return level, state



    def loadself(self, filename):
        if self.loaded:
            raise RuntimeError('already loaded')

        self.level, self.state = Game.load(filename)
        
        self.loaded = True

    def stepself(self, action):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        self.state = Game.step(self.level, self.state, action)

    def displayself(self):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        Game.display(self.level, self.state)

        

def play(filename):
    g = Game()
    g.loadself(filename)

    while True:
        g.displayself()
        action = input()
        g.stepself(action)

def solve(filename, display):
    g = Game()
    g.loadself(filename)

    # adapted from https://www.redblobgames.com/pathfinding/a-star/implementation.html

    start = copy.deepcopy(g.state)
    tiebreaker = 0

    frontier = queue.PriorityQueue()
    frontier.put((0, tiebreaker, start))
    tiebreaker += 1
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    path_found = None

    while not frontier.empty():
        current = frontier.get()[2]

        if current.player == g.level.exit:
            path_found = current
            break

        neighbors = set()
        for action in ['w', 'a', 's', 'd', '']:
            neighbors.add(Game.step(g.level, current, action))

        for next in neighbors:
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + 0
                frontier.put((priority, tiebreaker, next))
                tiebreaker += 1
                came_from[next] = current

    if display:
        if path_found is None:
            print('No path found.')

        else:
            print('Path found.')

            path = []
            current = path_found
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()

            for state in path:
                print()
                Game.display(g.level, state)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('level', type=str,help='Input level file.')
    parser.add_argument('--play', action='store_true', help='Play level.')
    parser.add_argument('--solve', action='store_true', help='Solve level.')
    args = parser.parse_args()

    if args.play == args.solve:
        raise RuntimeError('exactly one of --play and --solve must be given')

    if args.play:
        play(args.level)

    elif args.solve:
        solve(args.level, True)
