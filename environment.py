from agents import child
from enum import Enum
import random
from math import floor
from tiles import tile_kind

class tile:
    def __init__(self, kind = tile_kind.normal, dirt = False):
        self.dirt = dirt
        self.kind = kind

class environment:
    def __init__(self, rows:int, cols:int, t:int, childs:int, obstacles_p:float, dirt_p:float, robot_kind, seed=0):
        self.rows = rows
        self.cols = cols
        self.t = t
        self.cur_t = 0
        self.mat = [[tile() for j in range(cols)] for i in range(rows)]
        self.agents = []
        random.seed(seed)
        
        x, y = random.randint(0, rows-1), random.randint(0, cols-1)
        pos = [(abs(x - i) + abs(y - j), i, j) for i in range(rows) for j in range(cols)]
        pos.sort()
        for p in range(childs):
            _, i, j = pos[p]
            self.mat[i][j] = tile(tile_kind.corral)
        pos = pos[childs:]

        random.shuffle(pos)
        
        obstacles = floor(len(pos) * obstacles_p / 100)
        for p in range(obstacles):
            _, i, j = pos[p]
            self.mat[i][j] = tile(tile_kind.obstacle)
        pos = pos[obstacles:]

        for p in range(childs):
            _, i, j = pos[p]
            self.agents.append(child(self, i, j))
        pos = pos[childs:]

        _, i, j = pos[0]
        self.agents.append(robot_kind(self, i, j))

        pos = []
        for i in range(rows):
            for j in range(cols):
                if self.mat[i][j].kind == tile_kind.normal:
                    pos.append((i, j))

        d = floor(len(pos) * dirt_p / 100)
        for p in range(d):
            i, j = pos[p]
            self.mat[i][j].dirt = True
    
    def simulate(self):
        dirt_sum, dirt_tot = 0, 0
        while self.cur_t <= self.t * 100:
            dirt_count = 0
            normal_tiles_count = 0
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.mat[i][j].kind == tile_kind.normal:
                        normal_tiles_count += 1
                    if self.mat[i][j].dirt:
                        dirt_count += 1

            dirt_sum += 100 * dirt_count / normal_tiles_count
            dirt_tot += 1

            corral_count = 0
            for i in self.agents:
                if isinstance(i, child) and self.mat[i.x][i.y].kind == tile_kind.corral:
                    corral_count += 1

            if dirt_count == 0 and corral_count == len(self.agents) - 1:
                #print("Robot contratado")
                return (+1, dirt_sum / dirt_tot)

            if dirt_count > 0 and dirt_count * 100  >= 60 * normal_tiles_count:
                #print("Robot despedido")
                return (-1, dirt_sum / dirt_tot)
            
            self.cur_t += 1

            for i in self.agents:
                if not isinstance(i, child):
                    i.move()
            
            for i in self.agents:
                if isinstance(i, child):
                    i.move()

            # self.print()
            # print(100 * dirt_count / normal_tiles_count)

            if self.cur_t % self.t == 0:
                cur_corral = []
                cur_rest = []
                for i in range(self.rows):
                    for j in range(self.cols):
                        if self.mat[i][j].kind == tile_kind.corral:
                            cur_corral.append((i, j))
                        else:
                            cur_rest.append((i, j))

                x, y = random.randint(0, self.rows-1), random.randint(0, self.cols-1)
                pos = [(abs(x - i) + abs(y - j), i, j) for i in range(self.rows) for j in range(self.cols)]
                pos.sort()

                nxt_corral = pos[:len(cur_corral)]
                nxt_rest = pos[len(cur_corral):]
                random.shuffle(nxt_corral)
                random.shuffle(nxt_rest)

                cur = cur_corral + cur_rest
                nxt = nxt_corral + nxt_rest

                nxt_mat = [[tile() for j in range(self.cols)] for i in range(self.rows)]
                mark = []
                for i in range(len(cur)):
                    ci, cj = cur[i]
                    _, ni, nj = nxt[i]
                    nxt_mat[ni][nj] = self.mat[ci][cj]
                    for a in self.agents:
                        if a.x == ci and a.y == cj and a not in mark:
                            a.x, a.y = ni, nj
                            mark.append(a)
                self.mat = nxt_mat

                # print('relajo')
                # self.print()

        return (0, dirt_sum / dirt_tot)
    
    def valid_pos(self, x, y):
        return x >= 0 and x < self.rows and y >= 0 and y < self.cols

    def empty_tile(self, x, y):
        for i in self.agents:
            if i.x == x and i.y == y:
                return False
        return True
    
    def print(self):
        kd = { tile_kind.normal:'_', tile_kind.corral:'C', tile_kind.obstacle:'X' }
        pm = [['' for i in range(self.cols)] for i in range(self.rows)]
        print('-----------------------------------------------------')
        for i in range(self.rows):
            for j in range(self.cols):
                pm[i][j] += kd[self.mat[i][j].kind] + 'LS'[self.mat[i][j].dirt]
        for a in self.agents:
            if isinstance(a, child):
                pm[a.x][a.y] += 'N'
            else:
                pm[a.x][a.y] += 'R'
        for i in pm:
            print(i)
        print('-----------------------------------------------------')
        print()
