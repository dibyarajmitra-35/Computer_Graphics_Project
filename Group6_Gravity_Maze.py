from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
from collections import deque

fovY = 90
camera_mode = "follow"
orbit_angle = 0.0


ORBIT_HEIGHT = 500.0
ORBIT_RADIUS = 550.0

CELL = 100.0
WALL_THICK = 10.0


WALL_HEIGHT = 70.0
PLAYER_HALF = 20.0



DIRS = {
    "N": (0, 1),
    "S": (0, -1),
    "E": (1, 0),
    "W": (-1, 0),
}


OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}



LEVELS = [
    (6, 6, 1, 3),
    (8, 8, 2, 4),
    (10, 10, 3, 5),
]

curr_level = 0
cols = rows = 0

grid = {}
gates = set()

start_cell = (0, 0)
goal_exitCell = (0, 0)

key_cell = None
collectedKey = False

coins = set()
timebonus_cells = set()

pits = set()
checkpoints = []


checkpointCell = None
solve_path = []
solve_dirs = []

hazards = []

player_cell = (0, 0)
player_x, player_y, player_z = 0.0, 0.0, PLAYER_HALF


moving = False
move_kind = None


progressing_move = 0.0
move_dir = "N"

move_from_cell = (0, 0)
move_to_cell = (0, 0)


ROLL_TICKS = 10.0
VAULT_TICKS = 12.0


JUMP_TICKS = 14.0
last_dir = "N"

score = 0
time_left = 60.0



gameOver = False
wonGame = False


message = ""

cheat_mode = False
path_index = 0


cheat_cooldown = 0

combo_count = 0
best_times = {}


paused = False
trail_enabled = False


trail_points = []
camera_zoom = 0.0
ZOOM_MIN, ZOOM_MAX = -120.0, 200.0

SLAM_RADIUS = 130.0
SLAM_STUN_TICKS = 90
SLAM_COOLDOWN = 60




slam_cooldown_ticks = 0

MAX_VAULT_CHARGES = 2


vault_charges = MAX_VAULT_CHARGES

onTorch = False

markerCell = set()

MAGNET_RADIUS = 130.0
MAGNET_COOLDOWN = 180


magnet_cooldown_ticks = 0

ability_msg = ""
ability_msg_ticks = 0



ABILITY_MSG_DURATION = 90

effect_rings = []

tickCounter = 0


def cell_to_world(cell):
    c, r = cell


    ox = -cols * CELL / 2.0
    oy = -rows * CELL / 2.0


    return (ox + c * CELL + CELL / 2.0, oy + r * CELL + CELL / 2.0)


def generate_maze(c, r):
    g = {}


    for cc in range(c):
        for rr in range(r):
            g[(cc, rr)] = {"N": True, "S": True, "E": True, "W": True}

    visited = set()
    start = (0, 0)


    visited.add(start)
    stack = [start]

    while stack:
        cur = stack[-1]
        cx, cy = cur


        neighbors = []
        for d, (dx, dy) in DIRS.items():
            nb = (cx + dx, cy + dy)
            if 0 <= nb[0] < c and 0 <= nb[1] < r and nb not in visited:
                neighbors.append((d, nb))



        if not neighbors:
            stack.pop()
            continue

        d, nb = random.choice(neighbors)
        g[cur][d] = False

        g[nb][OPPOSITE[d]] = False


        visited.add(nb)
        stack.append(nb)



    return g


def bfs_path(g, c, r, src, dst):
    q = deque([src])


    came_from = {src: None}
    while q:
        cur = q.popleft()


        if cur == dst:
            break
        cx, cy = cur


        for d, (dx, dy) in DIRS.items():
            if g[cur][d]:
                continue
            nb = (cx + dx, cy + dy)


            if nb not in came_from:
                came_from[nb] = (cur, d)
                q.append(nb)



    if dst not in came_from:
        return [], []

    path = [dst]


    dirs = []
    cur = dst



    while came_from[cur] is not None:
        prev, d = came_from[cur]
        dirs.append(d)
        cur = prev
        path.append(cur)



    path.reverse()
    dirs.reverse()
    return path, dirs


def farthest_cell(g, c, r, src):
    q = deque([src])
    dist = {src: 0}


    far = src
    while q:
        cur = q.popleft()



        cx, cy = cur
        for d, (dx, dy) in DIRS.items():
            if g[cur][d]:


                continue
            nb = (cx + dx, cy + dy)
            if nb not in dist:



                dist[nb] = dist[cur] + 1
                q.append(nb)


                if dist[nb] > dist[far]:
                    far = nb


    return far


def init_level(idx):


    global cols, rows, grid, gates, start_cell, goal_exitCell, key_cell, collectedKey
    global coins, timebonus_cells, pits, checkpoints, checkpointCell


    global solve_path, solve_dirs, hazards
    global player_cell, player_x, player_y, player_z, moving, progressing_move


    global time_left, path_index, cheat_cooldown, message
    global combo_count, trail_points


    global slam_cooldown_ticks, vault_charges, onTorch, markerCell, magnet_cooldown_ticks
    global ability_msg, ability_msg_ticks

    c, r, extra_rotate, patrol_len = LEVELS[idx]
    cols, rows = c, r


    grid = generate_maze(c, r)

    start_cell = (0, 0)


    goal_exitCell = farthest_cell(grid, c, r, start_cell)
    solve_path, solve_dirs = bfs_path(grid, c, r, start_cell, goal_exitCell)


    solve_path_set = set(solve_path)

    gates = set()


    key_cell = None




    if len(solve_path) > 5:
        gate_idx = int(len(solve_path) * 0.6)
        gates.add(frozenset({solve_path[gate_idx - 1], solve_path[gate_idx]}))


        key_idx = max(1, gate_idx - 3)
        key_cell = solve_path[key_idx]


    collectedKey = False

    checkpoints = []



    if len(solve_path) > 6:



        checkpoints.append(solve_path[len(solve_path) // 3])
        checkpoints.append(solve_path[(len(solve_path) * 2) // 3])



    checkpointCell = start_cell

    all_cells = list(grid.keys())


    reserved = {start_cell, goal_exitCell, key_cell}
    reserved.update(checkpoints)

    free_cells = [cell for cell in all_cells if cell not in reserved and cell not in solve_path_set]
    random.shuffle(free_cells)




    path_adjacent_set = set()


    for cell in solve_path_set:


        cx, cy = cell


        for d, (dx, dy) in DIRS.items():


            nb = (cx + dx, cy + dy)


            if nb in grid and not grid[cell][d] and nb not in solve_path_set and nb not in reserved:
                path_adjacent_set.add(nb)


    free_cells.sort(key=lambda c: c in path_adjacent_set)

    coins = set()



    for _ in range(min(6, len(free_cells))):
        coins.add(free_cells.pop())



    timebonus_cells = set()


    for _ in range(min(2, len(free_cells))):
        timebonus_cells.add(free_cells.pop())

    pits = set()


    mid_candidates = []
    gate_adjacent = set()



    for edge in gates:
        gate_adjacent.update(edge)



    for i in range(2, len(solve_path) - 2):
        cell = solve_path[i]
        if cell in reserved or cell in gate_adjacent:
            continue
        if solve_dirs[i - 1] == solve_dirs[i]:
            mid_candidates.append(cell)




    if mid_candidates:
        pits.add(random.choice(mid_candidates))

    hazards = []
    hazard_pool = [cell for cell in free_cells]



    blocked_cells = set(reserved) | solve_path_set | coins | timebonus_cells
    hazard_occupied = set()



    rotate_count = 1 + extra_rotate




    for _ in range(min(rotate_count, len(hazard_pool))):
        cell = hazard_pool.pop()


        hazards.append({"type": "rotate", "cell": cell, "angle": 0.0, "stun": 0})
        hazard_occupied.add(cell)



    for cell in all_cells:


        if cell in blocked_cells or cell in hazard_occupied:
            continue

        cx, cy = cell


        placed = False


        for d, (dx, dy) in DIRS.items():
            nb = (cx + dx, cy + dy)


            if (nb in grid and not grid[cell][d]
                    and nb not in blocked_cells and nb not in hazard_occupied):
                hazards.append({"type": "slide", "cellA": cell, "cellB": nb, "t": 0.0, "dir": 1, "stun": 0})


                hazard_occupied.add(cell)

                hazard_occupied.add(nb)
                placed = True
                break



        if placed:
            break




    patrol_candidates = [c for c in hazard_pool if c not in hazard_occupied]
    patrol_start = random.choice(patrol_candidates) if patrol_candidates else None


    patrol = [patrol_start] if patrol_start is not None else []


    if patrol_start is not None:

        hazard_occupied.add(patrol_start)

    cur = patrol_start



    for _ in range(patrol_len):

        if cur is None:

            break

        cx, cy = cur


        options = [d for d, (dx, dy) in DIRS.items()
                   if not grid.get(cur, {}).get(d, True)
                   and (cx + dx, cy + dy) not in blocked_cells
                   and (cx + dx, cy + dy) not in hazard_occupied]


        if not options:
            break


        d = random.choice(options)


        dx, dy = DIRS[d]
        cur = (cx + dx, cy + dy)
        patrol.append(cur)
        hazard_occupied.add(cur)



    if len(patrol) > 1:
        hazards.append({"type": "patrol", "path": patrol, "idx": 0, "t": 0.0, "stun": 0, "pdir": 1})

    player_cell = start_cell
    wx, wy = cell_to_world(start_cell)

    player_x, player_y, player_z = wx, wy, PLAYER_HALF

    moving = False
    progressing_move = 0.0

    time_left = 60.0 + idx * 15.0
    path_index = 0


    cheat_cooldown = 0
    message = ""




    combo_count = 0
    trail_points = []

    slam_cooldown_ticks = 0
    vault_charges = MAX_VAULT_CHARGES
    onTorch = False

    markerCell = set()

    magnet_cooldown_ticks = 0
    ability_msg = ""


    ability_msg_ticks = 0
    effect_rings.clear()




def reset_game():
    global curr_level, score, gameOver, wonGame, cheat_mode
    curr_level = 0

    score = 0
    gameOver = False

    wonGame = False
    cheat_mode = False


    init_level(curr_level)




def restart_current_level():
    global gameOver, wonGame, paused


    gameOver = False
    wonGame = False
    paused = False


    init_level(curr_level)





reset_game()




def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)


    glMatrixMode(GL_PROJECTION)

    glPushMatrix()


    glLoadIdentity()

    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()


    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)



    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)




def draw_floor():
    glBegin(GL_QUADS)
    ox = -cols * CELL / 2.0


    oy = -rows * CELL / 2.0



    for c in range(cols):


        for r in range(rows):
            if (c, r) in pits:
                glColor3f(0.65, 0.1, 0.05)
            elif (c, r) == goal_exitCell:


                glColor3f(1.0, 0.85, 0.2)
            elif (c + r) % 2 == 0:
                glColor3f(0.85, 0.85, 0.9)
            else:
                glColor3f(0.55, 0.4, 0.75)

            x1 = ox + c * CELL
            y1 = oy + r * CELL
            x2 = x1 + CELL
            y2 = y1 + CELL


            glVertex3f(x1, y1, 0)



            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)


            glVertex3f(x1, y2, 0)
    glEnd()




def draw_wall_segment(cell, d):

    cx, cy = cell_to_world(cell)
    dx, dy = DIRS[d]

    glPushMatrix()


    glTranslatef(cx + dx * CELL / 2.0, cy + dy * CELL / 2.0, WALL_HEIGHT / 2.0)
    if d in ("N", "S"):
        glScalef(CELL, WALL_THICK, WALL_HEIGHT)


    else:
        glScalef(WALL_THICK, CELL, WALL_HEIGHT)
    glutSolidCube(1.0)



    glPopMatrix()





def draw_walls():
    glColor3f(0.15, 0.15, 0.55)
    drawn = set()




    for cell in grid:

        for d in ("N", "S", "E", "W"):


            if not grid[cell][d]:
                continue
            cx, cy = cell


            dx, dy = DIRS[d]
            nb = (cx + dx, cy + dy)


            key = frozenset({cell, nb}) if nb in grid else (cell, d)

            if key in drawn:

                continue


            drawn.add(key)

            draw_wall_segment(cell, d)



def draw_gate_walls():

    if collectedKey:
        return
    glColor3f(0.9, 0.15, 0.15)




    for edge in gates:

        cell_a, cell_b = tuple(edge)
        dx = cell_b[0] - cell_a[0]
        dy = cell_b[1] - cell_a[1]


        for d, (ddx, ddy) in DIRS.items():
            if (ddx, ddy) == (dx, dy):
                draw_wall_segment(cell_a, d)
                break


    glColor3f(0.15, 0.15, 0.55)





def draw_pickups():

    for cell in coins:

        wx, wy = cell_to_world(cell)

        glPushMatrix()


        glColor3f(1.0, 0.85, 0.1)


        glTranslatef(wx, wy, 25)
        gluSphere(gluNewQuadric(), 10, 10, 10)
        glPopMatrix()

    for cell in timebonus_cells:
        wx, wy = cell_to_world(cell)
        glPushMatrix()

        glColor3f(0.2, 0.9, 1.0)
        glTranslatef(wx, wy, 25)


        gluSphere(gluNewQuadric(), 12, 10, 10)
        glPopMatrix()

    if key_cell is not None and not collectedKey:
        wx, wy = cell_to_world(key_cell)
        glPushMatrix()


        glColor3f(1.0, 1.0, 0.0)
        glTranslatef(wx, wy, 30)


        glRotatef(tickCounter * 3, 0, 0, 1)
        glutSolidCube(18)


        glPopMatrix()



def draw_goal():
    wx, wy = cell_to_world(goal_exitCell)
    glPushMatrix()


    glColor3f(0.1, 1.0, 0.3)
    glTranslatef(wx, wy, 40)
    glRotatef(tickCounter * 2, 0, 0, 1)


    gluCylinder(gluNewQuadric(), 25, 0, 60, 10, 10)
    glPopMatrix()



def draw_checkpoints():
    for cell in checkpoints:



        wx, wy = cell_to_world(cell)
        glPushMatrix()


        glColor3f(0.6, 0.6, 1.0)


        glTranslatef(wx, wy, 5)
        glScalef(1, 1, 0.1)


        glutSolidCube(50)
        glPopMatrix()


def draw_trail():


    if not trail_enabled or not trail_points:
        return
    n = len(trail_points)


    for i, (tx, ty, tz) in enumerate(trail_points):
        fade = (i + 1) / n

        glPointSize(4 + fade * 4)
        glColor3f(1.0, 1.0 - fade * 0.5, 0.2)


        glBegin(GL_POINTS)


        glVertex3f(tx, ty, tz)
        glEnd()




def draw_torch():
    if not onTorch:
        return


    cx, cy = player_cell
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.85, 0.2)



    for d, (dx, dy) in DIRS.items():
        nb = (cx + dx, cy + dy)
        if nb not in grid:
            continue
        wx, wy = cell_to_world(nb)
        half = CELL / 2.0
        glVertex3f(wx - half, wy - half, 1.5)
        glVertex3f(wx + half, wy - half, 1.5)


        glVertex3f(wx + half, wy + half, 1.5)
        glVertex3f(wx - half, wy + half, 1.5)


    glEnd()



def draw_effect_rings():


    for ring in effect_rings:
        elapsed = tickCounter - ring["start_tick"]
        t = min(1.0, elapsed / ring["duration"])

        radius = ring["max_radius"] * t
        size = max(2.0, 10.0 * (1.0 - t))
        glPointSize(size)

        glColor3f(*ring["color"])
        glBegin(GL_POINTS)


        for i in range(16):
            ang = (2 * math.pi / 16) * i
            px = ring["x"] + radius * math.cos(ang)

            py = ring["y"] + radius * math.sin(ang)
            glVertex3f(px, py, 6)


        glEnd()


def update_effect_rings():
    effect_rings[:] = [r for r in effect_rings


                        if (tickCounter - r["start_tick"]) < r["duration"]]


def draw_markerCell():


    for cell in markerCell:
        wx, wy = cell_to_world(cell)
        glPushMatrix()
        glColor3f(0.9, 0.1, 0.9)


        glTranslatef(wx, wy, 60)
        glScalef(0.35, 0.35, 4.5)
        glutSolidCube(20)


        glPopMatrix()

        glPushMatrix()
        glColor3f(1.0, 0.4, 1.0)


        glTranslatef(wx, wy, 135)
        gluSphere(gluNewQuadric(), 12, 10, 10)
        glPopMatrix()


def getHazard_pos(hz):


    if hz["type"] == "rotate":
        return cell_to_world(hz["cell"])


    if hz["type"] == "slide":
        ax, ay = cell_to_world(hz["cellA"])
        bx, by = cell_to_world(hz["cellB"])
        t = hz["t"]


        return (ax + (bx - ax) * t, ay + (by - ay) * t)


    if hz["type"] == "patrol":
        path = hz["path"]
        i = hz["idx"]
        pdir = hz.get("pdir", 1)


        j = max(0, min(len(path) - 1, i + pdir))
        ax, ay = cell_to_world(path[i])
        bx, by = cell_to_world(path[j])
        t = hz["t"]



        return (ax + (bx - ax) * t, ay + (by - ay) * t)


    return (0, 0)


def draw_hazards():

    for hz in hazards:
        wx, wy = getHazard_pos(hz)
        stunned = hz.get("stun", 0) > 0
        glPushMatrix()


        if hz["type"] == "rotate":
            glColor3f(0.4, 0.7, 1.0) if stunned else glColor3f(1.0, 0.4, 0.1)
            glTranslatef(wx, wy, 0)


            glRotatef(hz["angle"], 0, 0, 1)

            glTranslatef(30, 0, 0)
            gluCylinder(gluNewQuadric(), 15, 15, 45, 8, 8)


        elif hz["type"] == "slide":
            glColor3f(0.3, 0.5, 0.9) if stunned else glColor3f(0.7, 0.1, 0.1)
            glTranslatef(wx, wy, WALL_HEIGHT / 2.0)


            glScalef(CELL * 0.5, WALL_THICK, WALL_HEIGHT)
            glutSolidCube(1.0)


        elif hz["type"] == "patrol":
            glColor3f(0.3, 0.6, 1.0) if stunned else glColor3f(0.9, 0.0, 0.6)
            glTranslatef(wx, wy, 30)

            gluSphere(gluNewQuadric(), 18, 10, 10)




        glPopMatrix()



def update_hazards():
    for hz in hazards:


        if hz.get("stun", 0) > 0:
            hz["stun"] -= 1
            continue


        if hz["type"] == "rotate":
            hz["angle"] = (hz["angle"] + 4) % 360


        elif hz["type"] == "slide":
            hz["t"] += 0.02 * hz["dir"]


            if hz["t"] >= 1.0:
                hz["t"] = 1.0
                hz["dir"] = -1




            elif hz["t"] <= 0.0:
                hz["t"] = 0.0
                hz["dir"] = 1


        elif hz["type"] == "patrol":
            hz["t"] += 0.02


            if hz["t"] >= 1.0:
                hz["t"] = 0.0
                hz["idx"] += hz.get("pdir", 1)




                if hz["idx"] >= len(hz["path"]) - 1:
                    hz["idx"] = len(hz["path"]) - 1
                    hz["pdir"] = -1



                elif hz["idx"] <= 0:
                    hz["idx"] = 0
                    hz["pdir"] = 1




def check_hazardCol():

    if gameOver or wonGame:
        return


    for hz in hazards:


        if hz.get("stun", 0) > 0:
            continue
        wx, wy = getHazard_pos(hz)


        if math.hypot(player_x - wx, player_y - wy) < 35:
            respawn_player()
            return




def respawn_player():
    global player_cell, player_x, player_y, player_z, moving, progressing_move, combo_count
    player_cell = checkpointCell
    wx, wy = cell_to_world(player_cell)



    player_x, player_y, player_z = wx, wy, PLAYER_HALF
    moving = False
    progressing_move = 0.0
    combo_count = 0


def use_slam():
    global slam_cooldown_ticks, ability_msg, ability_msg_ticks

    if gameOver or wonGame or paused or moving:
        return
    if slam_cooldown_ticks > 0:
        ability_msg = "Slam is on cooldown!"
        ability_msg_ticks = ABILITY_MSG_DURATION
        return

    hit_any = False
    for hz in hazards:
        wx, wy = getHazard_pos(hz)


        if math.hypot(player_x - wx, player_y - wy) <= SLAM_RADIUS:
            hz["stun"] = SLAM_STUN_TICKS
            hit_any = True


    if hit_any:
        slam_cooldown_ticks = SLAM_COOLDOWN
        ability_msg = "Ground Slam! Hazard stunned."
        effect_rings.append({
            "x": player_x, "y": player_y, "start_tick": tickCounter,
            "duration": 20, "max_radius": SLAM_RADIUS, "color": (0.3, 0.8, 1.0)
        })


    else:
        ability_msg = "No hazard nearby to slam."
    ability_msg_ticks = ABILITY_MSG_DURATION


def wall_vault():
    global moving, move_kind, progressing_move, move_dir, move_from_cell, move_to_cell, vault_charges
    global ability_msg, ability_msg_ticks

    if moving or gameOver or wonGame or paused:
        return

    ability_msg_ticks = ABILITY_MSG_DURATION

    if vault_charges <= 0:
        ability_msg = "No vault charges left!"
        return

    d = last_dir
    cx, cy = player_cell
    dx, dy = DIRS[d]


    target = (cx + dx, cy + dy)

    if target not in grid:
        ability_msg = "Can't vault the outer boundary!"
        return

    edge = frozenset({player_cell, target})


    if edge in gates and not collectedKey:
        ability_msg = "That's a locked gate - use the key!"
        return

    if not grid[player_cell][d]:
        ability_msg = "No wall there to vault."
        return

    if target in pits:
        ability_msg = "Can't vault into a pit."
        return

    vault_charges -= 1
    moving = True
    move_kind = "vault"

    progressing_move = 0.0
    move_dir = d
    move_from_cell = player_cell


    move_to_cell = target
    ability_msg = "Vaulted through the wall!"


def toggle_torch():
    global onTorch, ability_msg, ability_msg_ticks
    onTorch = not onTorch

    ability_msg = "Torch ON" if onTorch else "Torch OFF"


    ability_msg_ticks = ABILITY_MSG_DURATION


def toggle_marker():
    global ability_msg, ability_msg_ticks


    if player_cell in markerCell:
        markerCell.discard(player_cell)
        ability_msg = "Marker removed."


    else:
        markerCell.add(player_cell)
        ability_msg = "Marker placed!"
    ability_msg_ticks = ABILITY_MSG_DURATION


def magnet_pulse():
    global magnet_cooldown_ticks, score, combo_count, time_left
    global ability_msg, ability_msg_ticks

    if gameOver or wonGame or paused:

        return

    ability_msg_ticks = ABILITY_MSG_DURATION

    if magnet_cooldown_ticks > 0:
        ability_msg = "Magnet is on cooldown!"
        return

    collected_any = False

    for cell in list(coins):
        wx, wy = cell_to_world(cell)


        if math.hypot(player_x - wx, player_y - wy) <= MAGNET_RADIUS:
            coins.discard(cell)
            score += 1
            combo_count += 1


            if combo_count % 3 == 0:
                score += 2
            collected_any = True


    for cell in list(timebonus_cells):
        wx, wy = cell_to_world(cell)


        if math.hypot(player_x - wx, player_y - wy) <= MAGNET_RADIUS:
            timebonus_cells.discard(cell)
            time_left += 15.0
            collected_any = True



    if collected_any:
        magnet_cooldown_ticks = MAGNET_COOLDOWN
        ability_msg = "Magnet Pulse! Pickups collected."
        effect_rings.append({
            "x": player_x, "y": player_y, "start_tick": tickCounter,
            "duration": 20, "max_radius": MAGNET_RADIUS, "color": (1.0, 0.85, 0.1)
        })


    else:
        ability_msg = "No pickups nearby."


def draw_player():
    glPushMatrix()

    body_color = (0.85, 0.2, 0.2)

    if moving:
        sx, sy = cell_to_world(move_from_cell)
        dx, dy = DIRS[move_dir]

        if move_kind == "roll":
            t = min(1.0, progressing_move)
            pivot_x = sx + dx * PLAYER_HALF
            pivot_y = sy + dy * PLAYER_HALF
            angle = t * 90.0
            axis_x, axis_y = dy, -dx

            glTranslatef(pivot_x, pivot_y, 0)
            glRotatef(angle, axis_x, axis_y, 0)
            glTranslatef(sx - pivot_x, sy - pivot_y, PLAYER_HALF)



        elif move_kind == "vault":
            t = min(1.0, progressing_move)
            tx, ty = cell_to_world(move_to_cell)

            wx = sx + (tx - sx) * t


            wy = sy + (ty - sy) * t
            wz = PLAYER_HALF + 50.0 * math.sin(math.pi * t)


            glTranslatef(wx, wy, wz)

            glRotatef(t * 360.0, dy, -dx, 0)
            body_color = (0.2, 0.7, 1.0)

        else:
            t = min(1.0, progressing_move)
            tx, ty = cell_to_world(move_to_cell)


            wx = sx + (tx - sx) * t
            wy = sy + (ty - sy) * t
            wz = PLAYER_HALF + 90.0 * math.sin(math.pi * t)


            glTranslatef(wx, wy, wz)
            glRotatef(t * 360.0, 0, 1, 0)
    else:

        glTranslatef(player_x, player_y, player_z)

    glColor3f(*body_color)
    glutSolidCube(PLAYER_HALF * 2)

    glPopMatrix()


def facing_vector():

    dx, dy = DIRS[last_dir]
    return dx, dy


def can_step(cell, d):


    if grid[cell][d]:
        return False
    cx, cy = cell
    dx, dy = DIRS[d]
    nb = (cx + dx, cy + dy)


    if nb not in grid:
        return False
    edge = frozenset({cell, nb})


    if edge in gates and not collectedKey:
        return False


    if nb in pits:
        return False
    return True


def startMove(d):
    global moving, move_kind, progressing_move, move_dir, move_from_cell, move_to_cell, last_dir

    if moving or gameOver or wonGame or paused:
        return False

    last_dir = d


    cx, cy = player_cell
    dx, dy = DIRS[d]


    target = (cx + dx, cy + dy)

    if target not in grid:
        return False


    if can_step(player_cell, d):
        moving = True
        move_kind = "roll"

        progressing_move = 0.0
        move_dir = d
        move_from_cell = player_cell



        move_to_cell = target
        return True

    return False


def start_jump():
    global moving, move_kind, progressing_move, move_dir, move_from_cell, move_to_cell

    if moving or gameOver or wonGame or paused:
        return False

    cx, cy = player_cell
    dx, dy = DIRS[last_dir]


    mid = (cx + dx, cy + dy)
    target = (cx + dx * 2, cy + dy * 2)

    if mid not in pits:
        return False


    if target not in grid:
        return False

    edge_in = frozenset({player_cell, mid})
    edge_out = frozenset({mid, target})



    if (edge_in in gates or edge_out in gates) and not collectedKey:
        return False

    moving = True
    move_kind = "jump"


    progressing_move = 0.0


    move_dir = last_dir
    move_from_cell = player_cell
    move_to_cell = target
    return True


def move_finished():

    global moving, player_cell, player_x, player_y, player_z, score, time_left
    global collectedKey, checkpointCell, wonGame, message, curr_level

    global combo_count, best_times

    player_cell = move_to_cell
    wx, wy = cell_to_world(player_cell)


    player_x, player_y, player_z = wx, wy, PLAYER_HALF
    moving = False

    if player_cell in coins:
        coins.discard(player_cell)
        score += 1
        combo_count += 1
        if combo_count % 3 == 0:
            score += 2

    if player_cell in timebonus_cells:
        timebonus_cells.discard(player_cell)
        time_left += 15.0



    if player_cell == key_cell and not collectedKey:
        collectedKey = True


    if player_cell in checkpoints:
        checkpointCell = player_cell


    if player_cell == goal_exitCell:
        prev_level = curr_level
        if prev_level not in best_times or time_left > best_times[prev_level]:
            best_times[prev_level] = time_left





        if curr_level < len(LEVELS) - 1:
            curr_level += 1
            init_level(curr_level)
            message = "Level Up!"


        else:
            wonGame = True
            message = "YOU WIN! Press R to play again"


def move_player():
    global progressing_move
    if not moving:
        return

    if move_kind == "roll":
        total = ROLL_TICKS


    elif move_kind == "vault":
        total = VAULT_TICKS


    else:
        total = JUMP_TICKS

    progressing_move += 1.0 / total

    if progressing_move >= 1.0:
        move_finished()


def runCheat_mode():
    global path_index, cheat_cooldown, last_dir

    if not cheat_mode or moving or gameOver or wonGame:
        return

    if cheat_cooldown > 0:
        cheat_cooldown -= 1
        return

    if path_index < len(solve_dirs):
        d = solve_dirs[path_index]



        cx, cy = player_cell
        dx, dy = DIRS[d]
        target = (cx + dx, cy + dy)



        if target in pits:
            last_dir = d
            jumped = start_jump()


            if jumped:
                path_index += 2
                cheat_cooldown = 3
        else:
            moved = startMove(d)
            if moved:
                path_index += 1
                cheat_cooldown = 3


def update_timer():
    global time_left, gameOver, message


    if gameOver or wonGame:
        return
    time_left -= 1.0 / 60.0



    if time_left <= 0:
        time_left = 0
        gameOver = True
        message = "TIME'S UP! Press R to restart"


def keyboardListener(key, x, y):


    global cheat_mode, camera_mode, paused, trail_enabled

    if key in (b'r', b'R'):
        restart_current_level()
        return



    if key == b'\x1b':
        import sys
        sys.exit(0)


    if gameOver or wonGame:
        return




    if key in (b'x', b'X'):
        cheat_mode = not cheat_mode

    if key in (b'c', b'C'):
        order = ["follow", "orbit", "first"]
        camera_mode = order[(order.index(camera_mode) + 1) % len(order)]



    if key in (b'p', b'P'):
        paused = not paused

    if key in (b't', b'T'):
        trail_enabled = not trail_enabled

    if key in (b'g', b'G'):
        use_slam()



    if key in (b'v', b'V'):
        wall_vault()



    if key in (b'l', b'L'):
        toggle_torch()

    if key in (b'n', b'N'):
        toggle_marker()



    if key in (b'k', b'K'):
        magnet_pulse()

    if key == b' ':
        start_jump()


def specialKeyListener(key, x, y):
    if gameOver or wonGame or cheat_mode or paused:
        return

    if key == GLUT_KEY_UP:
        startMove("N")


    if key == GLUT_KEY_DOWN:
        startMove("S")


    if key == GLUT_KEY_LEFT:
        startMove("W")
    if key == GLUT_KEY_RIGHT:
        startMove("E")


def mouseListener(button, state, x, y):
    global camera_zoom

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        camera_zoom = max(ZOOM_MIN, camera_zoom - 30.0)

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_zoom = min(ZOOM_MAX, camera_zoom + 30.0)


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()


    gluPerspective(fovY, 1.25, 0.1, 2500)
    glMatrixMode(GL_MODELVIEW)


    glLoadIdentity()

    if camera_mode == "orbit":
        rad = math.radians(orbit_angle)


        radius = ORBIT_RADIUS + camera_zoom



        cam_x = radius * math.sin(rad)

        cam_y = -radius * math.cos(rad)



        gluLookAt(cam_x, cam_y, ORBIT_HEIGHT,

                  0, 0, 0,
                  0, 0, 1)

    elif camera_mode == "first":


        dx, dy = facing_vector()
        eye_x, eye_y, eye_z = player_x, player_y, player_z + 20



        gluLookAt(eye_x, eye_y, eye_z,

                  eye_x + dx * 150, eye_y + dy * 150, eye_z,
                  0, 0, 1)

    else:
        dx, dy = facing_vector()
        distance = 200 + camera_zoom


        eye_x = player_x - dx * distance
        eye_y = player_y - dy * distance
        eye_z = player_z + 260 + camera_zoom * 0.5


        target_x = player_x + dx * 40
        target_y = player_y + dy * 40


        gluLookAt(eye_x, eye_y, eye_z,
                  target_x, target_y, player_z + 15,
                  0, 0, 1)


def timer(value):
    global tickCounter, orbit_angle, slam_cooldown_ticks, magnet_cooldown_ticks, ability_msg_ticks

    if not (gameOver or wonGame) and not paused:
        tickCounter += 1
        move_player()
        update_hazards()


        check_hazardCol()
        runCheat_mode()


        update_timer()

        if slam_cooldown_ticks > 0:
            slam_cooldown_ticks -= 1

        if magnet_cooldown_ticks > 0:
            magnet_cooldown_ticks -= 1

        if ability_msg_ticks > 0:
            ability_msg_ticks -= 1

        update_effect_rings()


        if trail_enabled and tickCounter % 4 == 0:
            trail_points.append((player_x, player_y, player_z))

            if len(trail_points) > 25:
                trail_points.pop(0)


        if camera_mode == "orbit":
            orbit_angle += 0.3

    glutTimerFunc(16, timer, 0)


def idle():
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_floor()
    draw_walls()

    draw_gate_walls()
    draw_checkpoints()
    draw_markerCell()

    draw_torch()
    draw_pickups()
    draw_goal()

    draw_hazards()
    draw_trail()

    draw_effect_rings()
    draw_player()

    glClear(GL_DEPTH_BUFFER_BIT)

    draw_text(10, 770, f"Level: {curr_level + 1} / {len(LEVELS)}")
    draw_text(10, 745, f"Coins: {score}")


    draw_text(10, 720, f"Time Left: {int(time_left)}")
    draw_text(10, 695, f"Key: {'Collected' if collectedKey else 'Not Collected'}")
    draw_text(10, 670, f"Camera: {camera_mode}")

    draw_text(10, 645, f"Combo: {combo_count}")
    draw_text(10, 620, f"Vault Charges: {vault_charges}/{MAX_VAULT_CHARGES}")
    draw_text(10, 595, f"Torch: {'On' if onTorch else 'Off'}")

    if slam_cooldown_ticks > 0:
        draw_text(10, 570, "Slam Cooldown...")
    else:
        draw_text(10, 570, "Slam Ready (G)")


    if magnet_cooldown_ticks > 0:
        draw_text(10, 545, "Magnet Cooldown...")

    else:
        draw_text(10, 545, "Magnet Ready (K)")


    if curr_level in best_times:
        draw_text(10, 520, f"Best Time Left (this level): {int(best_times[curr_level])}")

    if cheat_mode:
        draw_text(10, 495, "CHEAT MODE ON")



    if paused:
        draw_text(450, 400, "PAUSED")

    if message:
        draw_text(370, 400, message)

    if ability_msg_ticks > 0:
        draw_text(330, 440, ability_msg)

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)


    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)


    glutCreateWindow(b"Gravity Maze: Rolling Cube")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)


    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)

    glutIdleFunc(idle)
    glutTimerFunc(16, timer, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()