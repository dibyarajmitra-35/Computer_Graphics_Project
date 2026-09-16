from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
from collections import deque


# =====================================================================
# Gravity Maze: Rolling Cube
# CSE423 Computer Graphics - Group Project (Section 03)
#
# Built directly on top of the 3D OpenGL template.
#
# Controls:
#   Arrow keys - roll the cube one cell
#   Space      - jump over a pit
#   G          - Ground Slam
#   V          - Wall Vault
#   L          - Torch
#   N          - Marker
#   K          - Magnet Pulse
#   C          - cycle camera mode
#   T          - toggle rolling trail
#   P          - pause / unpause
#   X          - toggle cheat mode
#   Left click - zoom in
#   Right click - zoom out
#   R          - restart current level
#   Esc        - quit
#
# Allowed extra:
#   glutTimerFunc()
#   glEnable(GL_DEPTH_TEST)
# =====================================================================


# ---------------------------------------------------------------
# Camera variables
# ---------------------------------------------------------------
fovY = 90

camera_mode = "follow"     # "follow", "orbit", "first"

orbit_angle = 0.0
ORBIT_HEIGHT = 500.0
ORBIT_RADIUS = 550.0

camera_zoom = 0.0
ZOOM_MIN = -120.0
ZOOM_MAX = 200.0


# ---------------------------------------------------------------
# Maze / world constants
# ---------------------------------------------------------------
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

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}


# level definitions:
# (columns, rows, extra rotating hazards, patrol length)
LEVELS = [
    (6, 6, 1, 3),
    (8, 8, 2, 4),
    (10, 10, 3, 5),
]


# ---------------------------------------------------------------
# Mutable game state
# ---------------------------------------------------------------
level_index = 0

cols = 0
rows = 0

grid = {}

gates = set()

start_cell = (0, 0)
goal_cell = (0, 0)

key_cell = None
key_collected = False

coins = set()
timebonus_cells = set()
pit_cells = set()

checkpoints = []
checkpoint_cell = None

solve_path = []
solve_dirs = []


# ---------------------------------------------------------------
# Hazards
# ---------------------------------------------------------------
hazards = []


# ---------------------------------------------------------------
# Player state
# ---------------------------------------------------------------
player_cell = (0, 0)

player_x = 0.0
player_y = 0.0
player_z = PLAYER_HALF

moving = False

move_kind = None       # "roll", "vault", "jump"
move_progress = 0.0

move_dir = "N"

move_from_cell = (0, 0)
move_to_cell = (0, 0)

last_dir = "N"

ROLL_TICKS = 10.0
VAULT_TICKS = 12.0
JUMP_TICKS = 14.0


# ---------------------------------------------------------------
# Scoring / state
# ---------------------------------------------------------------
score = 0
coin_count = 0

time_left = 60.0

game_over = False
game_won = False

message = ""

combo_count = 0

best_times = {}


# ---------------------------------------------------------------
# Cheat mode
# ---------------------------------------------------------------
cheat_mode = False
path_index = 0
cheat_cooldown = 0


# ---------------------------------------------------------------
# HUD / camera extras
# ---------------------------------------------------------------
paused = False

trail_enabled = False
trail_points = []

tick_count = 0


# ---------------------------------------------------------------
# Ground Slam
# ---------------------------------------------------------------
SLAM_RADIUS = 130.0
SLAM_STUN_TICKS = 90
SLAM_COOLDOWN = 60

slam_cooldown_ticks = 0


# ---------------------------------------------------------------
# Wall Vault
# ---------------------------------------------------------------
MAX_VAULT_CHARGES = 2
vault_charges = MAX_VAULT_CHARGES


# ---------------------------------------------------------------
# Torch / marker
# ---------------------------------------------------------------
torch_enabled = False

markers = set()


# ---------------------------------------------------------------
# Magnet Pulse
# ---------------------------------------------------------------
MAGNET_RADIUS = 130.0
MAGNET_COOLDOWN = 180

magnet_cooldown_ticks = 0


# ---------------------------------------------------------------
# Ability messages
# ---------------------------------------------------------------
ability_msg = ""
ability_msg_ticks = 0

ABILITY_MSG_DURATION = 90


# ---------------------------------------------------------------
# Effect rings
# ---------------------------------------------------------------
effect_rings = []


# ---------------------------------------------------------------
# Coordinates
# ---------------------------------------------------------------
def cell_to_world(cell):
    c, r = cell

    ox = -cols * CELL / 2.0
    oy = -rows * CELL / 2.0

    return (
        ox + c * CELL + CELL / 2.0,
        oy + r * CELL + CELL / 2.0
    )


# ---------------------------------------------------------------
# Maze generation
# ---------------------------------------------------------------
def generate_maze(c, r):
    g = {}

    for cc in range(c):
        for rr in range(r):
            g[(cc, rr)] = {
                "N": True,
                "S": True,
                "E": True,
                "W": True
            }

    visited = set()

    start = (0, 0)

    visited.add(start)

    stack = [start]

    while stack:

        cur = stack[-1]

        cx, cy = cur

        neighbors = []

        for d, (dx, dy) in DIRS.items():

            nb = (
                cx + dx,
                cy + dy
            )

            if (
                0 <= nb[0] < c
                and 0 <= nb[1] < r
                and nb not in visited
            ):
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


# ---------------------------------------------------------------
# Normal BFS path
# ---------------------------------------------------------------
def bfs_path(g, c, r, src, dst):
    q = deque([src])

    came_from = {
        src: None
    }

    while q:

        cur = q.popleft()

        if cur == dst:
            break

        cx, cy = cur

        for d, (dx, dy) in DIRS.items():

            if g[cur][d]:
                continue

            nb = (
                cx + dx,
                cy + dy
            )

            if nb not in came_from:

                came_from[nb] = (
                    cur,
                    d
                )

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


# ---------------------------------------------------------------
# BFS that also respects locked gates
# Used when cheat mode starts from an unusual position.
# ---------------------------------------------------------------
def bfs_path_with_rules(g, c, r, src, dst):
    q = deque([src])

    came_from = {
        src: None
    }

    while q:

        cur = q.popleft()

        if cur == dst:
            break

        cx, cy = cur

        for d, (dx, dy) in DIRS.items():

            if g[cur][d]:
                continue

            nb = (
                cx + dx,
                cy + dy
            )

            if nb not in g:
                continue

            edge = frozenset({
                cur,
                nb
            })

            if edge in gates and not key_collected:
                continue

            if nb in came_from:
                continue

            came_from[nb] = (
                cur,
                d
            )

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


# ---------------------------------------------------------------
# Find farthest cell
# ---------------------------------------------------------------
def farthest_cell(g, c, r, src):
    q = deque([src])

    dist = {
        src: 0
    }

    far = src

    while q:

        cur = q.popleft()

        cx, cy = cur

        for d, (dx, dy) in DIRS.items():

            if g[cur][d]:
                continue

            nb = (
                cx + dx,
                cy + dy
            )

            if nb not in dist:

                dist[nb] = dist[cur] + 1

                q.append(nb)

                if dist[nb] > dist[far]:
                    far = nb

    return far


# ---------------------------------------------------------------
# Level initialization
# ---------------------------------------------------------------
def init_level(idx):

    global cols, rows
    global grid
    global gates
    global start_cell, goal_cell
    global key_cell, key_collected
    global coins, timebonus_cells, pit_cells
    global checkpoints, checkpoint_cell
    global solve_path, solve_dirs
    global hazards
    global player_cell
    global player_x, player_y, player_z
    global moving, move_progress
    global time_left
    global path_index, cheat_cooldown
    global message
    global combo_count
    global trail_points
    global slam_cooldown_ticks
    global vault_charges
    global torch_enabled
    global markers
    global magnet_cooldown_ticks
    global ability_msg, ability_msg_ticks
    global paused
    global camera_zoom
    global last_dir

    c, r, extra_rotate, patrol_len = LEVELS[idx]

    cols = c
    rows = r

    grid = generate_maze(c, r)

    start_cell = (0, 0)

    goal_cell = farthest_cell(
        grid,
        c,
        r,
        start_cell
    )

    solve_path, solve_dirs = bfs_path(
        grid,
        c,
        r,
        start_cell,
        goal_cell
    )

    solve_path_set = set(solve_path)

    # -----------------------------------------------------------
    # Locked gate
    # -----------------------------------------------------------
    gates = set()

    key_cell = None

    if len(solve_path) > 5:

        gate_idx = int(
            len(solve_path) * 0.6
        )

        gates.add(
            frozenset({
                solve_path[gate_idx - 1],
                solve_path[gate_idx]
            })
        )

        key_idx = max(
            1,
            gate_idx - 3
        )

        key_cell = solve_path[key_idx]

    key_collected = False

    # -----------------------------------------------------------
    # Checkpoints
    # -----------------------------------------------------------
    checkpoints = []

    if len(solve_path) > 6:

        checkpoints.append(
            solve_path[
                len(solve_path) // 3
            ]
        )

        checkpoints.append(
            solve_path[
                (len(solve_path) * 2) // 3
            ]
        )

    checkpoint_cell = start_cell

    # -----------------------------------------------------------
    # Reserve important cells
    # -----------------------------------------------------------
    all_cells = list(grid.keys())

    reserved = {
        start_cell,
        goal_cell,
        key_cell
    }

    reserved.update(checkpoints)

    # -----------------------------------------------------------
    # Off-path cells
    # -----------------------------------------------------------
    free_cells = [
        cell
        for cell in all_cells
        if (
            cell not in reserved
            and cell not in solve_path_set
        )
    ]

    random.shuffle(free_cells)

    # -----------------------------------------------------------
    # Prefer cells adjacent to main path
    # -----------------------------------------------------------
    path_adjacent_set = set()

    for cell in solve_path_set:

        cx, cy = cell

        for d, (dx, dy) in DIRS.items():

            nb = (
                cx + dx,
                cy + dy
            )

            if (
                nb in grid
                and not grid[cell][d]
                and nb not in solve_path_set
                and nb not in reserved
            ):
                path_adjacent_set.add(nb)

    free_cells.sort(
        key=lambda cell:
        cell in path_adjacent_set
    )

    # -----------------------------------------------------------
    # Coins
    # -----------------------------------------------------------
    coins = set()

    for _ in range(
        min(6, len(free_cells))
    ):
        coins.add(
            free_cells.pop()
        )

    # -----------------------------------------------------------
    # Time bonuses
    # -----------------------------------------------------------
    timebonus_cells = set()

    for _ in range(
        min(2, len(free_cells))
    ):
        timebonus_cells.add(
            free_cells.pop()
        )

    # -----------------------------------------------------------
    # Pit
    # -----------------------------------------------------------
    pit_cells = set()

    mid_candidates = []

    for i in range(
        2,
        len(solve_path) - 2
    ):

        cell = solve_path[i]

        if cell in reserved:
            continue

        # Pit must be on a straight section.
        if solve_dirs[i - 1] == solve_dirs[i]:

            mid_candidates.append(cell)

    if mid_candidates:

        pit_cells.add(
            random.choice(
                mid_candidates
            )
        )

    # -----------------------------------------------------------
    # Hazards
    # -----------------------------------------------------------
    hazards = []

    hazard_pool = [
        cell
        for cell in free_cells
    ]

    # -----------------------------------------------------------
    # Rotating hazards
    # -----------------------------------------------------------
    rotate_count = 1 + extra_rotate

    for _ in range(
        min(
            rotate_count,
            len(hazard_pool)
        )
    ):

        hazards.append({
            "type": "rotate",
            "cell": hazard_pool.pop(),
            "angle": 0.0,
            "stun": 0
        })

    # -----------------------------------------------------------
    # Sliding wall
    # Must use two connected off-path cells.
    # -----------------------------------------------------------
    slide_added = False

    for cell in all_cells:

        if (
            cell in solve_path_set
            or cell in reserved
        ):
            continue

        cx, cy = cell

        for d, (dx, dy) in DIRS.items():

            nb = (
                cx + dx,
                cy + dy
            )

            if (
                nb in grid
                and not grid[cell][d]
                and nb not in reserved
                and nb not in solve_path_set
            ):

                hazards.append({
                    "type": "slide",
                    "cellA": cell,
                    "cellB": nb,
                    "t": 0.0,
                    "dir": 1,
                    "stun": 0
                })

                slide_added = True

                break

        if slide_added:
            break

    # -----------------------------------------------------------
    # Patrolling hazard
    # -----------------------------------------------------------
    patrol_start = (
        random.choice(hazard_pool)
        if hazard_pool
        else None
    )

    patrol = []

    if patrol_start is not None:

        patrol = [
            patrol_start
        ]

        cur = patrol_start

        for _ in range(patrol_len):

            if cur is None:
                break

            cx, cy = cur

            options = []

            for d, (dx, dy) in DIRS.items():

                nb = (
                    cx + dx,
                    cy + dy
                )

                if (
                    not grid.get(
                        cur,
                        {}
                    ).get(d, True)
                    and nb not in solve_path_set
                    and nb in grid
                ):
                    options.append(d)

            if not options:
                break

            d = random.choice(options)

            dx, dy = DIRS[d]

            cur = (
                cx + dx,
                cy + dy
            )

            patrol.append(cur)

    if len(patrol) > 1:

        hazards.append({
            "type": "patrol",
            "path": patrol,
            "idx": 0,
            "t": 0.0,
            "dir": 1,
            "stun": 0
        })

    # -----------------------------------------------------------
    # Player reset
    # -----------------------------------------------------------
    player_cell = start_cell

    wx, wy = cell_to_world(
        start_cell
    )

    player_x = wx
    player_y = wy
    player_z = PLAYER_HALF

    moving = False

    move_progress = 0.0

    # Always start facing north on a fresh level.
    last_dir = "N"

    # -----------------------------------------------------------
    # Level timer
    # -----------------------------------------------------------
    time_left = 60.0 + idx * 15.0

    # -----------------------------------------------------------
    # Cheat state
    # -----------------------------------------------------------
    path_index = 0
    cheat_cooldown = 0

    # -----------------------------------------------------------
    # Other state
    # -----------------------------------------------------------
    message = ""

    combo_count = 0

    trail_points = []

    slam_cooldown_ticks = 0

    vault_charges = MAX_VAULT_CHARGES

    torch_enabled = False

    markers = set()

    magnet_cooldown_ticks = 0

    ability_msg = ""
    ability_msg_ticks = 0

    paused = False

    camera_zoom = 0.0

    effect_rings.clear()


# ---------------------------------------------------------------
# Full game reset
# ---------------------------------------------------------------
def reset_game():

    global level_index
    global score, coin_count
    global game_over, game_won
    global cheat_mode
    global best_times
    global paused
    global camera_mode
    global camera_zoom
    global orbit_angle

    level_index = 0

    score = 0
    coin_count = 0

    game_over = False
    game_won = False

    cheat_mode = False

    best_times = {}

    paused = False

    camera_mode = "follow"

    camera_zoom = 0.0

    orbit_angle = 0.0

    init_level(level_index)


# ---------------------------------------------------------------
# Restart current level
# ---------------------------------------------------------------
def restart_current_level():

    global game_over
    global game_won
    global cheat_mode
    global paused

    game_over = False
    game_won = False

    cheat_mode = False

    paused = False

    init_level(level_index)


reset_game()


# ---------------------------------------------------------------
# Text
# Kept based on the template.
# ---------------------------------------------------------------
def draw_text(
    x,
    y,
    text,
    font=GLUT_BITMAP_HELVETICA_18
):

    glColor3f(
        1,
        1,
        1
    )

    glMatrixMode(
        GL_PROJECTION
    )

    glPushMatrix()

    glLoadIdentity()

    gluOrtho2D(
        0,
        1000,
        0,
        800
    )

    glMatrixMode(
        GL_MODELVIEW
    )

    glPushMatrix()

    glLoadIdentity()

    glRasterPos2f(
        x,
        y
    )

    for ch in text:
        glutBitmapCharacter(
            font,
            ord(ch)
        )

    glPopMatrix()

    glMatrixMode(
        GL_PROJECTION
    )

    glPopMatrix()

    glMatrixMode(
        GL_MODELVIEW
    )


# ---------------------------------------------------------------
# Floor
# ---------------------------------------------------------------
def draw_floor():

    glBegin(
        GL_QUADS
    )

    ox = -cols * CELL / 2.0
    oy = -rows * CELL / 2.0

    for c in range(cols):

        for r in range(rows):

            cell = (
                c,
                r
            )

            if cell in pit_cells:

                glColor3f(
                    0.65,
                    0.1,
                    0.05
                )

            elif cell == goal_cell:

                glColor3f(
                    1.0,
                    0.85,
                    0.2
                )

            elif (c + r) % 2 == 0:

                glColor3f(
                    0.85,
                    0.85,
                    0.9
                )

            else:

                glColor3f(
                    0.55,
                    0.4,
                    0.75
                )

            x1 = ox + c * CELL
            y1 = oy + r * CELL

            x2 = x1 + CELL
            y2 = y1 + CELL

            glVertex3f(
                x1,
                y1,
                0
            )

            glVertex3f(
                x2,
                y1,
                0
            )

            glVertex3f(
                x2,
                y2,
                0
            )

            glVertex3f(
                x1,
                y2,
                0
            )

    glEnd()


# ---------------------------------------------------------------
# Wall segment
# ---------------------------------------------------------------
def draw_wall_segment(cell, d):

    cx, cy = cell_to_world(cell)

    dx, dy = DIRS[d]

    glPushMatrix()

    glTranslatef(
        cx + dx * CELL / 2.0,
        cy + dy * CELL / 2.0,
        WALL_HEIGHT / 2.0
    )

    if d in ("N", "S"):

        glScalef(
            CELL,
            WALL_THICK,
            WALL_HEIGHT
        )

    else:

        glScalef(
            WALL_THICK,
            CELL,
            WALL_HEIGHT
        )

    glutSolidCube(
        1.0
    )

    glPopMatrix()


# ---------------------------------------------------------------
# Maze walls
# ---------------------------------------------------------------
def draw_walls():

    glColor3f(
        0.15,
        0.15,
        0.55
    )

    drawn = set()

    for cell in grid:

        for d in (
            "N",
            "S",
            "E",
            "W"
        ):

            if not grid[cell][d]:
                continue

            cx, cy = cell

            dx, dy = DIRS[d]

            nb = (
                cx + dx,
                cy + dy
            )

            if nb in grid:

                key = frozenset({
                    cell,
                    nb
                })

            else:

                key = (
                    cell,
                    d
                )

            if key in drawn:
                continue

            drawn.add(key)

            draw_wall_segment(
                cell,
                d
            )


# ---------------------------------------------------------------
# Gate walls
# ---------------------------------------------------------------
def draw_gate_walls():

    if key_collected:
        return

    glColor3f(
        0.9,
        0.15,
        0.15
    )

    for edge in gates:

        cell_a, cell_b = tuple(edge)

        dx = cell_b[0] - cell_a[0]
        dy = cell_b[1] - cell_a[1]

        for d, (ddx, ddy) in DIRS.items():

            if (
                ddx == dx
                and ddy == dy
            ):

                draw_wall_segment(
                    cell_a,
                    d
                )

                break

    glColor3f(
        0.15,
        0.15,
        0.55
    )


# ---------------------------------------------------------------
# Pickups
# ---------------------------------------------------------------
def draw_pickups():

    # Coins
    for cell in coins:

        wx, wy = cell_to_world(
            cell
        )

        glPushMatrix()

        glColor3f(
            1.0,
            0.85,
            0.1
        )

        glTranslatef(
            wx,
            wy,
            25
        )

        gluSphere(
            gluNewQuadric(),
            10,
            10,
            10
        )

        glPopMatrix()

    # Time bonuses
    for cell in timebonus_cells:

        wx, wy = cell_to_world(
            cell
        )

        glPushMatrix()

        glColor3f(
            0.2,
            0.9,
            1.0
        )

        glTranslatef(
            wx,
            wy,
            25
        )

        gluSphere(
            gluNewQuadric(),
            12,
            10,
            10
        )

        glPopMatrix()

    # Key
    if (
        key_cell is not None
        and not key_collected
    ):

        wx, wy = cell_to_world(
            key_cell
        )

        glPushMatrix()

        glColor3f(
            1.0,
            1.0,
            0.0
        )

        glTranslatef(
            wx,
            wy,
            30
        )

        glRotatef(
            tick_count * 3,
            0,
            0,
            1
        )

        glutSolidCube(
            18
        )

        glPopMatrix()


# ---------------------------------------------------------------
# Goal
# ---------------------------------------------------------------
def draw_goal():

    wx, wy = cell_to_world(
        goal_cell
    )

    glPushMatrix()

    glColor3f(
        0.1,
        1.0,
        0.3
    )

    glTranslatef(
        wx,
        wy,
        40
    )

    glRotatef(
        tick_count * 2,
        0,
        0,
        1
    )

    gluCylinder(
        gluNewQuadric(),
        25,
        0,
        60,
        10,
        10
    )

    glPopMatrix()


# ---------------------------------------------------------------
# Checkpoints
# ---------------------------------------------------------------
def draw_checkpoints():

    for cell in checkpoints:

        wx, wy = cell_to_world(
            cell
        )

        glPushMatrix()

        glColor3f(
            0.6,
            0.6,
            1.0
        )

        glTranslatef(
            wx,
            wy,
            5
        )

        glScalef(
            1,
            1,
            0.1
        )

        glutSolidCube(
            50
        )

        glPopMatrix()


# ---------------------------------------------------------------
# Rolling trail
# ---------------------------------------------------------------
def draw_trail():

    if (
        not trail_enabled
        or not trail_points
    ):
        return

    n = len(
        trail_points
    )

    for i, (
        tx,
        ty,
        tz
    ) in enumerate(
        trail_points
    ):

        fade = (
            i + 1
        ) / n

        glPointSize(
            4 + fade * 4
        )

        glColor3f(
            1.0,
            1.0 - fade * 0.5,
            0.2
        )

        glBegin(
            GL_POINTS
        )

        glVertex3f(
            tx,
            ty,
            tz
        )

        glEnd()


# ---------------------------------------------------------------
# Torch
# ---------------------------------------------------------------
def draw_torch():

    if not torch_enabled:
        return

    cx, cy = player_cell

    glBegin(
        GL_QUADS
    )

    glColor3f(
        1.0,
        0.85,
        0.2
    )

    for d, (dx, dy) in DIRS.items():

        nb = (
            cx + dx,
            cy + dy
        )

        if nb not in grid:
            continue

        wx, wy = cell_to_world(
            nb
        )

        half = CELL / 2.0

        glVertex3f(
            wx - half,
            wy - half,
            1.5
        )

        glVertex3f(
            wx + half,
            wy - half,
            1.5
        )

        glVertex3f(
            wx + half,
            wy + half,
            1.5
        )

        glVertex3f(
            wx - half,
            wy + half,
            1.5
        )

    glEnd()


# ---------------------------------------------------------------
# Ability effect rings
# ---------------------------------------------------------------
def draw_effect_rings():

    for ring in effect_rings:

        elapsed = (
            tick_count
            - ring["start_tick"]
        )

        t = min(
            1.0,
            elapsed / ring["duration"]
        )

        radius = (
            ring["max_radius"] * t
        )

        size = max(
            2.0,
            10.0 * (1.0 - t)
        )

        glPointSize(
            size
        )

        glColor3f(
            *ring["color"]
        )

        glBegin(
            GL_POINTS
        )

        for i in range(16):

            ang = (
                2 * math.pi / 16
            ) * i

            px = (
                ring["x"]
                + radius * math.cos(ang)
            )

            py = (
                ring["y"]
                + radius * math.sin(ang)
            )

            glVertex3f(
                px,
                py,
                6
            )

        glEnd()


def update_effect_rings():

    effect_rings[:] = [
        r
        for r in effect_rings
        if (
            tick_count
            - r["start_tick"]
        ) < r["duration"]
    ]


# ---------------------------------------------------------------
# Markers
# ---------------------------------------------------------------
def draw_markers():

    for cell in markers:

        wx, wy = cell_to_world(
            cell
        )

        # Pole
        glPushMatrix()

        glColor3f(
            0.9,
            0.1,
            0.9
        )

        glTranslatef(
            wx,
            wy,
            60
        )

        glScalef(
            0.35,
            0.35,
            4.5
        )

        glutSolidCube(
            20
        )

        glPopMatrix()

        # Cap
        glPushMatrix()

        glColor3f(
            1.0,
            0.4,
            1.0
        )

        glTranslatef(
            wx,
            wy,
            135
        )

        gluSphere(
            gluNewQuadric(),
            12,
            10,
            10
        )

        glPopMatrix()


# ---------------------------------------------------------------
# Hazard position
# ---------------------------------------------------------------
def hazard_world_pos(hz):

    if hz["type"] == "rotate":

        return cell_to_world(
            hz["cell"]
        )

    if hz["type"] == "slide":

        ax, ay = cell_to_world(
            hz["cellA"]
        )

        bx, by = cell_to_world(
            hz["cellB"]
        )

        t = hz["t"]

        return (
            ax + (bx - ax) * t,
            ay + (by - ay) * t
        )

    if hz["type"] == "patrol":

        path = hz["path"]

        i = hz["idx"]

        direction = hz.get(
            "dir",
            1
        )

        j = i + direction

        # Bounce at both ends instead of
        # teleporting through walls.
        if (
            j < 0
            or j >= len(path)
        ):

            return cell_to_world(
                path[i]
            )

        ax, ay = cell_to_world(
            path[i]
        )

        bx, by = cell_to_world(
            path[j]
        )

        t = hz["t"]

        return (
            ax + (bx - ax) * t,
            ay + (by - ay) * t
        )

    return (
        0,
        0
    )


# ---------------------------------------------------------------
# Hazard drawing
# ---------------------------------------------------------------
def draw_hazards():

    for hz in hazards:

        wx, wy = hazard_world_pos(
            hz
        )

        stunned = (
            hz.get(
                "stun",
                0
            ) > 0
        )

        glPushMatrix()

        # Rotating hazard
        if hz["type"] == "rotate":

            if stunned:

                glColor3f(
                    0.4,
                    0.7,
                    1.0
                )

            else:

                glColor3f(
                    1.0,
                    0.4,
                    0.1
                )

            glTranslatef(
                wx,
                wy,
                0
            )

            glRotatef(
                hz["angle"],
                0,
                0,
                1
            )

            glTranslatef(
                30,
                0,
                0
            )

            gluCylinder(
                gluNewQuadric(),
                15,
                15,
                45,
                8,
                8
            )

        # Sliding wall
        elif hz["type"] == "slide":

            if stunned:

                glColor3f(
                    0.3,
                    0.5,
                    0.9
                )

            else:

                glColor3f(
                    0.7,
                    0.1,
                    0.1
                )

            glTranslatef(
                wx,
                wy,
                WALL_HEIGHT / 2.0
            )

            glScalef(
                CELL * 0.5,
                WALL_THICK,
                WALL_HEIGHT
            )

            glutSolidCube(
                1.0
            )

        # Patrol hazard
        elif hz["type"] == "patrol":

            if stunned:

                glColor3f(
                    0.3,
                    0.6,
                    1.0
                )

            else:

                glColor3f(
                    0.9,
                    0.0,
                    0.6
                )

            glTranslatef(
                wx,
                wy,
                30
            )

            gluSphere(
                gluNewQuadric(),
                18,
                10,
                10
            )

        glPopMatrix()


# ---------------------------------------------------------------
# Hazard update
# ---------------------------------------------------------------
def update_hazards():

    for hz in hazards:

        if hz.get(
            "stun",
            0
        ) > 0:

            hz["stun"] -= 1

            continue

        # Rotating hazard
        if hz["type"] == "rotate":

            hz["angle"] = (
                hz["angle"] + 4
            ) % 360

        # Sliding wall
        elif hz["type"] == "slide":

            hz["t"] += (
                0.02 * hz["dir"]
            )

            if hz["t"] >= 1.0:

                hz["t"] = 1.0

                hz["dir"] = -1

            elif hz["t"] <= 0.0:

                hz["t"] = 0.0

                hz["dir"] = 1

        # Patrolling hazard
        elif hz["type"] == "patrol":

            hz["t"] += 0.02

            if hz["t"] >= 1.0:

                hz["t"] = 0.0

                next_idx = (
                    hz["idx"]
                    + hz.get("dir", 1)
                )

                if (
                    next_idx >= len(
                        hz["path"]
                    ) - 1
                ):

                    hz["idx"] = (
                        len(hz["path"]) - 1
                    )

                    hz["dir"] = -1

                elif next_idx <= 0:

                    hz["idx"] = 0

                    hz["dir"] = 1

                else:

                    hz["idx"] = next_idx


# ---------------------------------------------------------------
# Hazard collision
# ---------------------------------------------------------------
def check_hazard_collision():

    if (
        game_over
        or game_won
    ):
        return

    for hz in hazards:

        if hz.get(
            "stun",
            0
        ) > 0:
            continue

        wx, wy = hazard_world_pos(
            hz
        )

        if (
            math.hypot(
                player_x - wx,
                player_y - wy
            ) < 35
        ):

            respawn_to_checkpoint()

            return


# ---------------------------------------------------------------
# Respawn
# ---------------------------------------------------------------
def respawn_to_checkpoint():

    global player_cell
    global player_x, player_y, player_z
    global moving, move_progress
    global combo_count
    global path_index

    player_cell = checkpoint_cell

    wx, wy = cell_to_world(
        player_cell
    )

    player_x = wx
    player_y = wy
    player_z = PLAYER_HALF

    moving = False

    move_progress = 0.0

    combo_count = 0

    # Keep cheat mode synchronized after respawn.
    if cheat_mode:

        if player_cell in solve_path:

            path_index = solve_path.index(
                player_cell
            )

        else:

            path_index = 0


# ---------------------------------------------------------------
# Ground Slam
# ---------------------------------------------------------------
def ground_slam():

    global slam_cooldown_ticks
    global ability_msg
    global ability_msg_ticks

    if (
        game_over
        or game_won
        or paused
        or moving
    ):
        return

    if slam_cooldown_ticks > 0:

        ability_msg = (
            "Slam is on cooldown!"
        )

        ability_msg_ticks = (
            ABILITY_MSG_DURATION
        )

        return

    hit_any = False

    for hz in hazards:

        wx, wy = hazard_world_pos(
            hz
        )

        if (
            math.hypot(
                player_x - wx,
                player_y - wy
            )
            <= SLAM_RADIUS
        ):

            hz["stun"] = (
                SLAM_STUN_TICKS
            )

            hit_any = True

    if hit_any:

        slam_cooldown_ticks = (
            SLAM_COOLDOWN
        )

        ability_msg = (
            "Ground Slam! Hazard stunned."
        )

        effect_rings.append({
            "x": player_x,
            "y": player_y,
            "start_tick": tick_count,
            "duration": 20,
            "max_radius": SLAM_RADIUS,
            "color": (
                0.3,
                0.8,
                1.0
            )
        })

    else:

        ability_msg = (
            "No hazard nearby to slam."
        )

    ability_msg_ticks = (
        ABILITY_MSG_DURATION
    )


# ---------------------------------------------------------------
# Wall Vault
# ---------------------------------------------------------------
def wall_vault():

    global moving
    global move_kind
    global move_progress
    global move_dir
    global move_from_cell
    global move_to_cell
    global vault_charges
    global ability_msg
    global ability_msg_ticks

    if (
        moving
        or game_over
        or game_won
        or paused
    ):
        return

    ability_msg_ticks = (
        ABILITY_MSG_DURATION
    )

    if vault_charges <= 0:

        ability_msg = (
            "No vault charges left!"
        )

        return

    d = last_dir

    cx, cy = player_cell

    dx, dy = DIRS[d]

    target = (
        cx + dx,
        cy + dy
    )

    if target not in grid:

        ability_msg = (
            "Can't vault the outer boundary!"
        )

        return

    edge = frozenset({
        player_cell,
        target
    })

    if (
        edge in gates
        and not key_collected
    ):

        ability_msg = (
            "That's a locked gate - use the key!"
        )

        return

    if not grid[player_cell][d]:

        ability_msg = (
            "No wall there to vault."
        )

        return

    if target in pit_cells:

        ability_msg = (
            "Can't vault into a pit."
        )

        return

    vault_charges -= 1

    moving = True

    move_kind = "vault"

    move_progress = 0.0

    move_dir = d

    move_from_cell = player_cell

    move_to_cell = target

    ability_msg = (
        "Vaulted through the wall!"
    )


# ---------------------------------------------------------------
# Torch
# ---------------------------------------------------------------
def toggle_torch():

    global torch_enabled
    global ability_msg
    global ability_msg_ticks

    torch_enabled = not torch_enabled

    ability_msg = (
        "Torch ON"
        if torch_enabled
        else "Torch OFF"
    )

    ability_msg_ticks = (
        ABILITY_MSG_DURATION
    )


# ---------------------------------------------------------------
# Marker
# ---------------------------------------------------------------
def toggle_marker():

    global ability_msg
    global ability_msg_ticks

    if player_cell in markers:

        markers.discard(
            player_cell
        )

        ability_msg = (
            "Marker removed."
        )

    else:

        markers.add(
            player_cell
        )

        ability_msg = (
            "Marker placed!"
        )

    ability_msg_ticks = (
        ABILITY_MSG_DURATION
    )


# ---------------------------------------------------------------
# Magnet Pulse
# ---------------------------------------------------------------
def magnet_pulse():

    global magnet_cooldown_ticks
    global score
    global coin_count
    global combo_count
    global time_left
    global ability_msg
    global ability_msg_ticks

    if (
        game_over
        or game_won
        or paused
    ):
        return

    ability_msg_ticks = (
        ABILITY_MSG_DURATION
    )

    if magnet_cooldown_ticks > 0:

        ability_msg = (
            "Magnet is on cooldown!"
        )

        return

    collected_any = False

    # -----------------------------------------------------------
    # Coins
    # -----------------------------------------------------------
    for cell in list(coins):

        wx, wy = cell_to_world(
            cell
        )

        if (
            math.hypot(
                player_x - wx,
                player_y - wy
            )
            <= MAGNET_RADIUS
        ):

            coins.discard(
                cell
            )

            score += 1

            coin_count += 1

            combo_count += 1

            if combo_count % 3 == 0:

                score += 2

            collected_any = True

    # -----------------------------------------------------------
    # Time bonus
    # -----------------------------------------------------------
    for cell in list(
        timebonus_cells
    ):

        wx, wy = cell_to_world(
            cell
        )

        if (
            math.hypot(
                player_x - wx,
                player_y - wy
            )
            <= MAGNET_RADIUS
        ):

            timebonus_cells.discard(
                cell
            )

            time_left += 15.0

            collected_any = True

    if collected_any:

        magnet_cooldown_ticks = (
            MAGNET_COOLDOWN
        )

        ability_msg = (
            "Magnet Pulse! Pickups collected."
        )

        effect_rings.append({
            "x": player_x,
            "y": player_y,
            "start_tick": tick_count,
            "duration": 20,
            "max_radius": MAGNET_RADIUS,
            "color": (
                1.0,
                0.85,
                0.1
            )
        })

    else:

        ability_msg = (
            "No pickups nearby."
        )


# ---------------------------------------------------------------
# Player drawing
# ---------------------------------------------------------------
def draw_player():

    glPushMatrix()

    body_color = (
        0.85,
        0.2,
        0.2
    )

    if moving:

        sx, sy = cell_to_world(
            move_from_cell
        )

        dx, dy = DIRS[
            move_dir
        ]

        # -------------------------------------------------------
        # Roll
        # -------------------------------------------------------
        if move_kind == "roll":

            t = min(
                1.0,
                move_progress
            )

            pivot_x = (
                sx
                + dx * PLAYER_HALF
            )

            pivot_y = (
                sy
                + dy * PLAYER_HALF
            )

            angle = (
                t * 90.0
            )

            axis_x = dy
            axis_y = -dx

            glTranslatef(
                pivot_x,
                pivot_y,
                0
            )

            glRotatef(
                angle,
                axis_x,
                axis_y,
                0
            )

            glTranslatef(
                sx - pivot_x,
                sy - pivot_y,
                PLAYER_HALF
            )

        # -------------------------------------------------------
        # Vault
        # -------------------------------------------------------
        elif move_kind == "vault":

            t = min(
                1.0,
                move_progress
            )

            tx, ty = cell_to_world(
                move_to_cell
            )

            wx = (
                sx
                + (tx - sx) * t
            )

            wy = (
                sy
                + (ty - sy) * t
            )

            wz = (
                PLAYER_HALF
                + 50.0
                * math.sin(
                    math.pi * t
                )
            )

            glTranslatef(
                wx,
                wy,
                wz
            )

            glRotatef(
                t * 360.0,
                dy,
                -dx,
                0
            )

            body_color = (
                0.2,
                0.7,
                1.0
            )

        # -------------------------------------------------------
        # Jump
        # -------------------------------------------------------
        else:

            t = min(
                1.0,
                move_progress
            )

            tx, ty = cell_to_world(
                move_to_cell
            )

            wx = (
                sx
                + (tx - sx) * t
            )

            wy = (
                sy
                + (ty - sy) * t
            )

            wz = (
                PLAYER_HALF
                + 90.0
                * math.sin(
                    math.pi * t
                )
            )

            glTranslatef(
                wx,
                wy,
                wz
            )

            glRotatef(
                t * 360.0,
                0,
                1,
                0
            )

    else:

        glTranslatef(
            player_x,
            player_y,
            player_z
        )

    glColor3f(
        *body_color
    )

    glutSolidCube(
        PLAYER_HALF * 2
    )

    glPopMatrix()


# ---------------------------------------------------------------
# Facing direction
# ---------------------------------------------------------------
def facing_vector():

    dx, dy = DIRS[
        last_dir
    ]

    return dx, dy


# ---------------------------------------------------------------
# Can normal-step
# ---------------------------------------------------------------
def can_step(cell, d):

    if grid[cell][d]:
        return False

    cx, cy = cell

    dx, dy = DIRS[d]

    nb = (
        cx + dx,
        cy + dy
    )

    if nb not in grid:
        return False

    edge = frozenset({
        cell,
        nb
    })

    if (
        edge in gates
        and not key_collected
    ):
        return False

    if nb in pit_cells:
        return False

    return True


# ---------------------------------------------------------------
# Normal roll movement
# Returns True if movement actually started.
# ---------------------------------------------------------------
def try_move(d):

    global moving
    global move_kind
    global move_progress
    global move_dir
    global move_from_cell
    global move_to_cell
    global last_dir

    if (
        moving
        or game_over
        or game_won
        or paused
    ):
        return False

    last_dir = d

    cx, cy = player_cell

    dx, dy = DIRS[d]

    target = (
        cx + dx,
        cy + dy
    )

    if target not in grid:
        return False

    if not can_step(
        player_cell,
        d
    ):
        return False

    moving = True

    move_kind = "roll"

    move_progress = 0.0

    move_dir = d

    move_from_cell = player_cell

    move_to_cell = target

    return True


# ---------------------------------------------------------------
# Jump
#
# IMPORTANT FIX:
# The direction is now explicitly supplied.
# It no longer depends on stale global last_dir.
#
# Returns True if the jump actually started.
# ---------------------------------------------------------------
def try_jump(direction=None):

    global moving
    global move_kind
    global move_progress
    global move_dir
    global move_from_cell
    global move_to_cell
    global last_dir

    if (
        moving
        or game_over
        or game_won
        or paused
    ):
        return False

    if direction is None:
        direction = last_dir
    else:
        last_dir = direction

    d = direction

    cx, cy = player_cell

    dx, dy = DIRS[d]

    # Middle cell: must be the pit.
    mid = (
        cx + dx,
        cy + dy
    )

    # Landing cell: two cells away.
    target = (
        cx + dx * 2,
        cy + dy * 2
    )

    if mid not in pit_cells:
        return False

    if target not in grid:
        return False

    # First edge must be open.
    if grid[player_cell][d]:
        return False

    # Second edge must also be open.
    if grid[mid][d]:
        return False

    # IMPORTANT FIX:
    # Jump cannot bypass a locked gate on either edge.
    first_edge = frozenset({
        player_cell,
        mid
    })

    second_edge = frozenset({
        mid,
        target
    })

    if (
        not key_collected
        and (
            first_edge in gates
            or second_edge in gates
        )
    ):
        return False

    moving = True

    move_kind = "jump"

    move_progress = 0.0

    move_dir = d

    move_from_cell = player_cell

    move_to_cell = target

    return True


# ---------------------------------------------------------------
# Finish movement
# ---------------------------------------------------------------
def finish_move():

    global moving
    global player_cell
    global player_x, player_y, player_z
    global score
    global coin_count
    global time_left
    global key_collected
    global checkpoint_cell
    global game_won
    global message
    global level_index
    global combo_count
    global best_times

    player_cell = move_to_cell

    wx, wy = cell_to_world(
        player_cell
    )

    player_x = wx
    player_y = wy
    player_z = PLAYER_HALF

    moving = False

    # -----------------------------------------------------------
    # Coin pickup
    # -----------------------------------------------------------
    if player_cell in coins:

        coins.discard(
            player_cell
        )

        score += 1

        coin_count += 1

        combo_count += 1

        if combo_count % 3 == 0:

            score += 2

    # -----------------------------------------------------------
    # Time bonus
    # -----------------------------------------------------------
    if (
        player_cell
        in timebonus_cells
    ):

        timebonus_cells.discard(
            player_cell
        )

        time_left += 15.0

    # -----------------------------------------------------------
    # Key
    # -----------------------------------------------------------
    if (
        player_cell == key_cell
        and not key_collected
    ):

        key_collected = True

    # -----------------------------------------------------------
    # Checkpoint
    # -----------------------------------------------------------
    if player_cell in checkpoints:

        checkpoint_cell = (
            player_cell
        )

    # -----------------------------------------------------------
    # Goal
    # -----------------------------------------------------------
    if player_cell == goal_cell:

        prev_level = level_index

        if (
            prev_level not in best_times
            or time_left
            > best_times[prev_level]
        ):

            best_times[
                prev_level
            ] = time_left

        # -------------------------------------------------------
        # Next level
        # -------------------------------------------------------
        if (
            level_index
            < len(LEVELS) - 1
        ):

            level_index += 1

            init_level(
                level_index
            )

            message = "Level Up!"

        # -------------------------------------------------------
        # Final win
        # -------------------------------------------------------
        else:

            game_won = True

            message = (
                "YOU WIN! Press R to restart"
            )


# ---------------------------------------------------------------
# Movement update
# ---------------------------------------------------------------
def update_movement():

    global move_progress

    if not moving:
        return

    if move_kind == "roll":

        total = ROLL_TICKS

    elif move_kind == "vault":

        total = VAULT_TICKS

    else:

        total = JUMP_TICKS

    move_progress += (
        1.0 / total
    )

    if move_progress >= 1.0:

        move_progress = 1.0

        finish_move()


# ---------------------------------------------------------------
# Synchronize cheat path
# ---------------------------------------------------------------
def synchronize_cheat_path():

    global solve_path
    global solve_dirs
    global path_index

    # -----------------------------------------------------------
    # Current position is already on original solve path.
    # -----------------------------------------------------------
    if player_cell in solve_path:

        path_index = (
            solve_path.index(
                player_cell
            )
        )

        return

    # -----------------------------------------------------------
    # Player may have reached a side branch using V.
    # Generate a new valid path from current cell.
    # -----------------------------------------------------------
    new_path, new_dirs = bfs_path_with_rules(
        grid,
        cols,
        rows,
        player_cell,
        goal_cell
    )

    if new_path:

        solve_path = new_path

        solve_dirs = new_dirs

        path_index = 0

    else:

        path_index = 0


# ---------------------------------------------------------------
# Cheat mode update
#
# IMPORTANT FIXES:
#
# 1. Uses the solver's exact direction for jumping.
# 2. A jump consumes TWO path steps.
# 3. path_index only changes when movement actually begins.
# ---------------------------------------------------------------
def update_cheat_mode():

    global path_index
    global cheat_cooldown

    if (
        not cheat_mode
        or moving
        or game_over
        or game_won
        or paused
    ):
        return

    if cheat_cooldown > 0:

        cheat_cooldown -= 1

        return

    if path_index >= len(
        solve_dirs
    ):
        return

    d = solve_dirs[
        path_index
    ]

    cx, cy = player_cell

    dx, dy = DIRS[d]

    target = (
        cx + dx,
        cy + dy
    )

    # -----------------------------------------------------------
    # Pit detected: attempt exact-direction jump.
    # -----------------------------------------------------------
    if target in pit_cells:

        success = try_jump(
            d
        )

        if success:

            # Jump crosses:
            #
            # current -> pit -> landing
            #
            # therefore TWO solution steps are consumed.
            path_index += 2

            cheat_cooldown = 3

        return

    # -----------------------------------------------------------
    # Normal roll.
    # -----------------------------------------------------------
    success = try_move(
        d
    )

    if success:

        path_index += 1

        cheat_cooldown = 3


# ---------------------------------------------------------------
# Timer / countdown
# ---------------------------------------------------------------
def update_timer():

    global time_left
    global game_over
    global message

    if (
        game_over
        or game_won
    ):
        return

    time_left -= (
        1.0 / 60.0
    )

    if time_left <= 0:

        time_left = 0

        game_over = True

        message = (
            "TIME'S UP! Press R to restart"
        )


# ---------------------------------------------------------------
# Keyboard
# ---------------------------------------------------------------
def keyboardListener(
    key,
    x,
    y
):

    global cheat_mode
    global camera_mode
    global paused
    global trail_enabled
    global path_index

    # -----------------------------------------------------------
    # Restart
    # -----------------------------------------------------------
    if key in (
        b'r',
        b'R'
    ):

        restart_current_level()

        return

    # -----------------------------------------------------------
    # Escape
    # -----------------------------------------------------------
    if key == b'\x1b':

        import sys

        sys.exit(0)

    # -----------------------------------------------------------
    # Ignore gameplay keys after win/loss.
    # R above still works.
    # -----------------------------------------------------------
    if (
        game_over
        or game_won
    ):
        return

    # -----------------------------------------------------------
    # Cheat mode
    # -----------------------------------------------------------
    if key in (
        b'x',
        b'X'
    ):

        cheat_mode = not cheat_mode

        if cheat_mode:

            synchronize_cheat_path()

        return

    # -----------------------------------------------------------
    # Camera
    # -----------------------------------------------------------
    if key in (
        b'c',
        b'C'
    ):

        order = [
            "follow",
            "orbit",
            "first"
        ]

        camera_mode = order[
            (
                order.index(
                    camera_mode
                ) + 1
            ) % len(order)
        ]

    # -----------------------------------------------------------
    # Pause
    # -----------------------------------------------------------
    if key in (
        b'p',
        b'P'
    ):

        paused = not paused

    # -----------------------------------------------------------
    # Trail
    # -----------------------------------------------------------
    if key in (
        b't',
        b'T'
    ):

        trail_enabled = (
            not trail_enabled
        )

    # -----------------------------------------------------------
    # Ground Slam
    # -----------------------------------------------------------
    if key in (
        b'g',
        b'G'
    ):

        ground_slam()

    # -----------------------------------------------------------
    # Wall Vault
    # -----------------------------------------------------------
    if key in (
        b'v',
        b'V'
    ):

        wall_vault()

    # -----------------------------------------------------------
    # Torch
    # -----------------------------------------------------------
    if key in (
        b'l',
        b'L'
    ):

        toggle_torch()

    # -----------------------------------------------------------
    # Marker
    # -----------------------------------------------------------
    if key in (
        b'n',
        b'N'
    ):

        toggle_marker()

    # -----------------------------------------------------------
    # Magnet
    # -----------------------------------------------------------
    if key in (
        b'k',
        b'K'
    ):

        magnet_pulse()

    # -----------------------------------------------------------
    # Jump
    # -----------------------------------------------------------
    if key == b' ':

        try_jump()


# ---------------------------------------------------------------
# Special keys
# ---------------------------------------------------------------
def specialKeyListener(
    key,
    x,
    y
):

    if (
        game_over
        or game_won
        or cheat_mode
        or paused
    ):
        return

    if key == GLUT_KEY_UP:

        try_move("N")

    elif key == GLUT_KEY_DOWN:

        try_move("S")

    elif key == GLUT_KEY_LEFT:

        try_move("W")

    elif key == GLUT_KEY_RIGHT:

        try_move("E")


# ---------------------------------------------------------------
# Mouse
# ---------------------------------------------------------------
def mouseListener(
    button,
    state,
    x,
    y
):

    global camera_zoom

    if (
        button == GLUT_LEFT_BUTTON
        and state == GLUT_DOWN
    ):

        # Zoom in
        camera_zoom = max(
            ZOOM_MIN,
            camera_zoom - 30.0
        )

    elif (
        button == GLUT_RIGHT_BUTTON
        and state == GLUT_DOWN
    ):

        # Zoom out
        camera_zoom = min(
            ZOOM_MAX,
            camera_zoom + 30.0
        )


# ---------------------------------------------------------------
# Camera
# ---------------------------------------------------------------
def setupCamera():

    glMatrixMode(
        GL_PROJECTION
    )

    glLoadIdentity()

    gluPerspective(
        fovY,
        1.25,
        0.1,
        2500
    )

    glMatrixMode(
        GL_MODELVIEW
    )

    glLoadIdentity()

    # -----------------------------------------------------------
    # Orbit camera
    # -----------------------------------------------------------
    if camera_mode == "orbit":

        rad = math.radians(
            orbit_angle
        )

        radius = (
            ORBIT_RADIUS
            + camera_zoom
        )

        ex = (
            radius
            * math.sin(rad)
        )

        ey = (
            -radius
            * math.cos(rad)
        )

        gluLookAt(
            ex,
            ey,
            ORBIT_HEIGHT,
            0,
            0,
            0,
            0,
            0,
            1
        )

    # -----------------------------------------------------------
    # First-person camera
    # -----------------------------------------------------------
    elif camera_mode == "first":

        dx, dy = facing_vector()

        eye_x = player_x
        eye_y = player_y
        eye_z = player_z + 20

        gluLookAt(
            eye_x,
            eye_y,
            eye_z,
            eye_x + dx * 150,
            eye_y + dy * 150,
            eye_z,
            0,
            0,
            1
        )

    # -----------------------------------------------------------
    # Follow camera
    # -----------------------------------------------------------
    else:

        dx, dy = facing_vector()

        distance = (
            200
            + camera_zoom
        )

        eye_x = (
            player_x
            - dx * distance
        )

        eye_y = (
            player_y
            - dy * distance
        )

        eye_z = (
            player_z
            + 260
            + camera_zoom * 0.5
        )

        target_x = (
            player_x
            + dx * 40
        )

        target_y = (
            player_y
            + dy * 40
        )

        gluLookAt(
            eye_x,
            eye_y,
            eye_z,
            target_x,
            target_y,
            player_z + 15,
            0,
            0,
            1
        )


# ---------------------------------------------------------------
# Timer callback
# ---------------------------------------------------------------
def timer(value):

    global tick_count
    global orbit_angle
    global slam_cooldown_ticks
    global magnet_cooldown_ticks
    global ability_msg_ticks

    if (
        not game_over
        and not game_won
        and not paused
    ):

        tick_count += 1

        # Player movement
        update_movement()

        # Hazards
        update_hazards()

        # Collision
        check_hazard_collision()

        # Cheat
        update_cheat_mode()

        # Timer
        update_timer()

        # Slam cooldown
        if slam_cooldown_ticks > 0:

            slam_cooldown_ticks -= 1

        # Magnet cooldown
        if magnet_cooldown_ticks > 0:

            magnet_cooldown_ticks -= 1

        # Ability message timer
        if ability_msg_ticks > 0:

            ability_msg_ticks -= 1

        # Effect rings
        update_effect_rings()

        # Trail
        if (
            trail_enabled
            and tick_count % 4 == 0
        ):

            trail_points.append(
                (
                    player_x,
                    player_y,
                    player_z
                )
            )

            if len(
                trail_points
            ) > 25:

                trail_points.pop(0)

        # Orbit camera
        if camera_mode == "orbit":

            orbit_angle += 0.3

            if orbit_angle >= 360.0:

                orbit_angle -= 360.0

    glutTimerFunc(
        16,
        timer,
        0
    )


# ---------------------------------------------------------------
# Idle
# ---------------------------------------------------------------
def idle():

    glutPostRedisplay()


# ---------------------------------------------------------------
# Display
# ---------------------------------------------------------------
def showScreen():

    # -----------------------------------------------------------
    # Clear buffers
    # -----------------------------------------------------------
    glClear(
        GL_COLOR_BUFFER_BIT
        | GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()

    glViewport(
        0,
        0,
        1000,
        800
    )

    setupCamera()

    # -----------------------------------------------------------
    # 3D world
    # -----------------------------------------------------------
    draw_floor()

    draw_walls()

    draw_gate_walls()

    draw_checkpoints()

    draw_markers()

    draw_torch()

    draw_pickups()

    draw_goal()

    draw_hazards()

    draw_trail()

    draw_effect_rings()

    draw_player()

    # -----------------------------------------------------------
    # Clear depth before HUD.
    #
    # glClear() is already present in the original template,
    # so no additional OpenGL function is needed here.
    # -----------------------------------------------------------
    glClear(
        GL_DEPTH_BUFFER_BIT
    )

    # -----------------------------------------------------------
    # HUD
    # -----------------------------------------------------------
    draw_text(
        10,
        770,
        f"Level: {level_index + 1} / {len(LEVELS)}"
    )

    draw_text(
        10,
        745,
        f"Coins: {coin_count}"
    )

    draw_text(
        10,
        720,
        f"Score: {score}"
    )

    draw_text(
        10,
        695,
        f"Time Left: {int(time_left)}"
    )

    draw_text(
        10,
        670,
        f"Key: {'Collected' if key_collected else 'Not Collected'}"
    )

    draw_text(
        10,
        645,
        f"Camera: {camera_mode}"
    )

    draw_text(
        10,
        620,
        f"Combo: {combo_count}"
    )

    draw_text(
        10,
        595,
        f"Vault Charges: {vault_charges}/{MAX_VAULT_CHARGES}"
    )

    draw_text(
        10,
        570,
        f"Torch: {'On' if torch_enabled else 'Off'}"
    )

    # -----------------------------------------------------------
    # Slam
    # -----------------------------------------------------------
    if slam_cooldown_ticks > 0:

        draw_text(
            10,
            545,
            "Slam Cooldown..."
        )

    else:

        draw_text(
            10,
            545,
            "Slam Ready (G)"
        )

    # -----------------------------------------------------------
    # Magnet
    # -----------------------------------------------------------
    if magnet_cooldown_ticks > 0:

        draw_text(
            10,
            520,
            "Magnet Cooldown..."
        )

    else:

        draw_text(
            10,
            520,
            "Magnet Ready (K)"
        )

    # -----------------------------------------------------------
    # Best time
    # -----------------------------------------------------------
    if level_index in best_times:

        draw_text(
            10,
            495,
            f"Best Time Left (this level): "
            f"{int(best_times[level_index])}"
        )

    # -----------------------------------------------------------
    # Cheat
    # -----------------------------------------------------------
    if cheat_mode:

        draw_text(
            10,
            470,
            "CHEAT MODE ON"
        )

    # -----------------------------------------------------------
    # Pause
    # -----------------------------------------------------------
    if paused:

        draw_text(
            450,
            400,
            "PAUSED"
        )

    # -----------------------------------------------------------
    # Main message
    # -----------------------------------------------------------
    if message:

        draw_text(
            370,
            400,
            message
        )

    # -----------------------------------------------------------
    # Ability message
    # -----------------------------------------------------------
    if ability_msg_ticks > 0:

        draw_text(
            300,
            440,
            ability_msg
        )

    # -----------------------------------------------------------
    # Swap buffers
    # -----------------------------------------------------------
    glutSwapBuffers()


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():

    glutInit()

    glutInitDisplayMode(
        GLUT_DOUBLE
        | GLUT_RGB
        | GLUT_DEPTH
    )

    glutInitWindowSize(
        1000,
        800
    )

    glutInitWindowPosition(
        0,
        0
    )

    glutCreateWindow(
        b"Gravity Maze: Rolling Cube"
    )

    # Explicitly allowed by project guideline.
    glEnable(
        GL_DEPTH_TEST
    )

    glutDisplayFunc(
        showScreen
    )

    glutKeyboardFunc(
        keyboardListener
    )

    glutSpecialFunc(
        specialKeyListener
    )

    glutMouseFunc(
        mouseListener
    )

    glutIdleFunc(
        idle
    )

    glutTimerFunc(
        16,
        timer,
        0
    )

    glutMainLoop()


# ---------------------------------------------------------------
# Program start
# ---------------------------------------------------------------
if __name__ == "__main__":
    main()