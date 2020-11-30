import random
from tiles import tile_kind

class agent:
    def __init__(self, env, x:int, y:int):
        self.env = env
        self.x = x
        self.y = y
    
    def move(self):
        pass

dx = [0, 1, -1, 0, 1, -1, -1, 1]
dy = [1, 0, 0, -1, 1, 1, -1, -1]

class child(agent):
    def move(self):
        if self.env.mat[self.x][self.y].kind == tile_kind.corral:
            return

        for i in self.env.agents:
            if not isinstance(i, child) and i.ch == self:
                return

        if random.random() < 0.5:
            return

        pos = []
        ch_count = 1
        prev_pos = [(self.x, self.y)]
        for x, y in zip(dx, dy):
            nx, ny = self.x + x, self.y + y
            if self.env.valid_pos(nx, ny):
                prev_pos.append((nx, ny))
                for i in self.env.agents:
                    if isinstance(i, child) and i.x == nx and i.y == ny:
                        ch_count += 1
                m = [(nx, ny)]
                px, py = nx, ny
                while self.env.valid_pos(px, py) and self.env.mat[px][py].kind == tile_kind.obstacle:
                    px, py = px + x, py + y
                    m.append((px, py))
                if self.env.valid_pos(px, py) and self.env.mat[px][py].kind == tile_kind.normal \
                        and not self.env.mat[px][py].dirt and self.env.empty_tile(px, py):
                    pos.append(m)
        
        to_d = 1
        if ch_count == 2:
            to_d = 3
        if ch_count >= 3:
            to_d = 6
        
        if len(pos) == 0:
            return
        
        random.shuffle(pos)
        random.shuffle(prev_pos)

        m = pos[0]
        px, py = m[-1]
        self.env.mat[px][py].kind == tile_kind.obstacle
        px, py = m[0]
        self.env.mat[px][py].kind == tile_kind.normal
        self.x, self.y = px, py

        to_d = random.randint(0, to_d)
        for px, py in prev_pos:
            if self.env.empty_tile(px, py) and to_d > 0 and not self.env.mat[px][py].dirt and self.env.mat[px][py].kind == tile_kind.normal:
                to_d -= 1
                self.env.mat[px][py].dirt = True

class robot(agent):
    def __init__(self, env, x:int, y:int):
        super().__init__(env, x, y)
        self.ch = None
    
    def can_clean(self):
        return self.env.mat[self.x][self.y].dirt

    def clean(self):
        self.env.mat[self.x][self.y].dirt = False
    
    def can_drop(self):
        return not self.env.mat[self.x][self.y].dirt

    def pick(self):
        for a in self.env.agents:
            if a.x == self.x and a.y == self.y and isinstance(a, child):
                self.ch = a

    def move_drop(self, nx, ny):
        self.x, self.y = nx, ny
        self.ch = None
        self.pick()
    
    def move_with(self, nx, ny):
        if not self.env.empty_tile(nx, ny):
            self.move_drop(nx, ny)
            return
        self.x, self.y = nx, ny
        if self.ch is not None:
            self.ch.x, self.ch.y = self.x, self.y
        self.pick()

    def get_inf_dist(self):
        return self.env.rows * self.env.cols + 5

    def get_dist_to(self, pi, pj):
        dist = [[self.get_inf_dist() for j in range(self.env.cols)] for i in range(self.env.rows)]
        dist[pi][pj] = 0
        p = 0
        q = [(pi, pj)]
        while p < len(q):
            px, py = q[p]
            p += 1
            for x, y in zip(dx, dy):
                nx, ny = px + x, py + y
                if self.env.valid_pos(nx, ny) and self.env.mat[nx][ny].kind != tile_kind.obstacle  \
                        and (self.ch is None or self.env.empty_tile(nx, ny) or not self.env.mat[self.x][self.y].dirt) \
                            and dist[nx][ny] == self.get_inf_dist():
                    dist[nx][ny] = dist[px][py] + 1
                    q.append((nx, ny))
        return dist
    
    def target(self, func):
        min_dist = self.get_inf_dist()
        pi, pj = -1, -1
        dist = self.get_dist_to(self.x, self.y)
        for i in range(self.env.rows):
            for j in range(self.env.cols):
                if func(i, j):
                    if dist[i][j] < min_dist:
                        min_dist = dist[i][j]
                        pi, pj = i, j
        return (min_dist, pi, pj)

    def is_dirt(self, i, j):
        return self.env.mat[i][j].dirt
    
    def is_corral(self, i, j):
        return self.env.mat[i][j].kind == tile_kind.corral and self.env.empty_tile(i, j)

    def is_child(self, i, j):
        return [a.x == i and a.y == j and isinstance(a, child) for a in self.env.agents].count(True) \
            and self.env.mat[i][j].kind != tile_kind.corral
    
    def go(self, min_dist, pi, pj):
        dist = self.get_dist_to(pi, pj)
        for x, y in zip(dx, dy):
            nx, ny = self.x + x, self.y + y
            if self.env.valid_pos(nx, ny) and dist[nx][ny] == min_dist - 1:
                if self.env.mat[self.x][self.y].kind == tile_kind.corral:
                    self.move_drop(nx, ny)
                else:
                    self.move_with(nx, ny)
                break
    
    def go_clean(self):
        if self.can_clean():
            self.clean()
            return True
        return False
    
    def go_dirt(self):
        ok = False
        it = 1 if self.ch is None else 2
        for _ in range(it):
            if _ > 0 and self.ch is None:
                break

            min_dist, pi, pj = self.target(self.is_dirt)
            
            if pi == -1:
                break
            
            ok = True
            self.go(min_dist, pi, pj)
        
        return ok
    
    def go_deliver(self):
        if self.ch is not None:
            min_dist, pi, pj = self.target(self.is_corral)
            if pi != -1:
                self.go(min_dist, pi, pj)
                return True
        return False
    
    def go_find_ch(self):
        if self.ch is None:
            min_dist, pi, pj = self.target(self.is_child)
            if pi != -1:
                self.go(min_dist, pi, pj)
                return True
        return False

class robot_proactive(robot):
    def move(self):
        if self.go_clean():
            return

        if self.go_find_ch():
            return
        
        if self.go_deliver():
            return
        
        if self.go_dirt():
            return

class robot_reactive(robot):
    def move(self):
        if self.go_clean():
            return

        dirt_min_dist, _, _ = self.target(self.is_dirt)
        deliver_min_dist, _, _ = self.target(self.is_corral)
        find_ch_min_dist, _, _ = self.target(self.is_child)

        if 4 * dirt_min_dist <= find_ch_min_dist:
            if self.go_dirt():
                return
        
        if 3 * dirt_min_dist <= deliver_min_dist:
            if self.go_dirt():
                return

        if self.go_find_ch():
            return
        
        if self.go_deliver():
            return
        
        if self.go_dirt():
            return
