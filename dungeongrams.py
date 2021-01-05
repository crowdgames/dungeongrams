import argparse, copy, math, pprint, random, sys



class State:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.enemyst = []
        self.didwin = False
        self.didlose = False



class Level:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.exit = None
        self.blocks = set()



class Game:
    def __init__(self):
        self.loaded = False

        self.level = Level()
        self.state = State()



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
            return
        if newstate.didlose:
            return

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

        if newstate.player == level.exit:
            newstate.didwin = True

        if Game.enemycollide(level, newstate):
            newstate.didlose = True

        for ii in range(len(newstate.enemies)):
            if newstate.enemyst[ii] == 0:
                newstate.enemyst[ii] = 1
            else:
                newstate.enemyst[ii] = 0

                rr, cc = newstate.enemies[ii]
                dr = newstate.player[0] - rr
                dc = newstate.player[1] - cc

                if abs(dr) > abs(dc):
                    dr = dr / abs(dr) if dr != 0 else 0
                    dc = 0
                else:
                    dr = 0
                    dc = dc / abs(dc) if dc != 0 else 0

                nrc = Game.validmoveforenemy(level, newstate, newstate.enemies[ii], dr, dc)
                if nrc:
                    newstate.enemies[ii] = nrc

        if Game.enemycollide(level, newstate):
            newstate.didlose = True

        return newstate



    def stepself(self, action):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        self.state = Game.step(self.level, self.state, action)

    def load_level(self, filename):
        if self.loaded:
            raise RuntimeError('already loaded')
        
        with open(filename) as level_file:
            for rr, line in enumerate(level_file.readlines()):
                line = line.strip()

                if self.level.width == 0:
                    self.level.width = len(line)
                elif self.level.width != len(line):
                    raise RuntimeError('lines not all same length')

                self.level.height += 1

                for cc, char in enumerate(line):
                    if char == '.':
                        pass
                    elif char == 'X':
                        self.level.blocks.add((rr, cc))
                    elif char == '#':
                        self.state.enemies.append((rr, cc))
                        self.state.enemyst.append(0)
                    elif char == '@':
                        if self.state.player != None:
                            raise RuntimeError('multiple players found')
                        self.state.player = (rr, cc)
                    elif char == '*':
                        if self.level.exit != None:
                            raise RuntimeError('multiple exits found')
                        self.level.exit = (rr, cc)

        if self.state.player == None:
            raise RuntimeError('no player found')
        if self.level.exit == None:
            raise RuntimeError('no exit found')

        self.loaded = True

    def display(self):
        if not self.loaded:
            raise RuntimeError('not loaded')
        
        for cc in range(self.level.width + 2):
            sys.stdout.write('X')
        sys.stdout.write('\n')
        
        for rr in range(self.level.height):
            sys.stdout.write('X')
            for cc in range(self.level.width):
                if (rr, cc) == self.state.player:
                    if self.state.didlose:
                        sys.stdout.write('%')
                    elif self.state.didwin:
                        sys.stdout.write('!')
                    else:
                        sys.stdout.write('@')
                elif (rr, cc) in self.state.enemies:
                    sys.stdout.write('#')
                elif (rr, cc) == self.level.exit:
                    sys.stdout.write('*')
                elif (rr, cc) in self.level.blocks:
                    sys.stdout.write('X')
                else:
                    sys.stdout.write('.')
            sys.stdout.write('X')
            sys.stdout.write('\n')

        for cc in range(self.level.width + 2):
            sys.stdout.write('X')
        sys.stdout.write('\n')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DungeonGrams game.')
    parser.add_argument('level', type=str,help='Input level file.')
    args = parser.parse_args()

    g = Game()
    g.load_level(args.level)
    while True:
        g.display()
        action = input()
        g.stepself(action)
