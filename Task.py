from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# =========================================================
#                     GLOBAL STATE
# =========================================================

# ---- Camera ----
# Internal orbit parameters (angle around the floor, height, orbit radius).
# These drive camera_pos below, which mirrors the template's own
# camera_pos = (x, y, z) pattern used directly inside setupCamera().
camera_angle = 0.0        # orbit angle around the grid (LEFT/RIGHT arrows)
camera_height = 500.0     # camera height (UP/DOWN arrows)
camera_radius = 700.0     # third-person orbit distance

# camera_pos, exactly like the template: a plain (x, y, z) tuple that
# setupCamera() unpacks and feeds straight into gluLookAt().
camera_pos = (0.0, -camera_radius, camera_height)

first_person = False      # toggled by RIGHT mouse click

# First-person "look" angle. Normally this tracks player_angle (the gun's
# facing direction). While cheat mode is spinning the gun, this angle is
# frozen at whatever it was the instant cheat mode turned on, UNLESS
# cheat_camera_follow (V key) is also on, in which case it keeps tracking
# the spinning gun so the first-person view spins along with it.
view_angle = 0.0

fovY = 120
GRID_LENGTH = 600
TILE = 60                 # size of one checkerboard tile -> grid is built dynamically

# ---- Player ----
player_pos = [0.0, 0.0, 0.0]
player_angle = 0.0        # facing direction in degrees (0 = +Y)
PLAYER_SPEED = 6.0
player_life = 5
player_score = 0
bullets_missed = 0
game_over = False

# ---- Bullets ----
bullets = []               # each: {"pos":[x,y,z], "angle": deg}
BULLET_SPEED = 14.0
BULLET_SIZE = 8

# ---- Enemies ----
enemies = []                # each: {"pos":[x,y,z], "scale":float, "growing":bool}
ENEMY_COUNT = 5
ENEMY_SPEED = 1.6
ENEMY_HIT_RADIUS = 34
PLAYER_HIT_RADIUS = 40

# ---- Cheat modes ----
cheat_mode = False          # C key
cheat_camera_follow = False # V key (only matters in first-person + cheat_mode)
CHEAT_ROTATE_SPEED = 3.0
CHEAT_FOV_TOLERANCE = 6.0   # degrees - how close gun must be to an enemy to "see" it
cheat_fire_cooldown = 0.0

last_time = time.time()

# ---- Frame rate cap (fixes idle() firing thousands of times/sec) ----
FPS = 60
FRAME_TIME = 1.0 / FPS

# Reference frame time that all "per frame" speeds above were tuned for.
# Movement is scaled by (dt / REFERENCE_DT) so behavior stays consistent
# even if the actual frame time drifts a bit on a slower/faster machine.
REFERENCE_DT = 1.0 / 60.0


# =========================================================
#                     SETUP / RESET
# =========================================================

def update_camera_pos():
    """Recompute camera_pos = (x, y, z) from the orbit parameters.
    Called any time camera_angle / camera_height / camera_radius change,
    so setupCamera() can just unpack camera_pos like the template does."""
    global camera_pos
    rad = math.radians(camera_angle)
    cx = camera_radius * math.sin(rad)
    cy = -camera_radius * math.cos(rad)
    cz = camera_height
    camera_pos = (cx, cy, cz)


def spawn_enemy():
    x = random.uniform(-GRID_LENGTH + 80, GRID_LENGTH - 80)
    y = random.uniform(-GRID_LENGTH + 80, GRID_LENGTH - 80)
    return {"pos": [x, y, 0.0], "scale": 1.0, "growing": True}


def init_enemies():
    global enemies
    enemies = [spawn_enemy() for _ in range(ENEMY_COUNT)]


def reset_game():
    global player_pos, player_angle, player_life, player_score
    global bullets_missed, game_over, bullets, cheat_mode, cheat_camera_follow
    global last_time, view_angle
    global camera_angle, camera_height, camera_radius
    player_pos = [0.0, 0.0, 0.0]
    player_angle = 0.0
    view_angle = 0.0
    player_life = 5
    player_score = 0
    bullets_missed = 0
    game_over = False
    bullets = []
    cheat_mode = False
    cheat_camera_follow = False
    camera_angle = 0.0
    camera_height = 500.0
    camera_radius = 700.0
    update_camera_pos()
    last_time = time.time()   # avoid a huge dt on the first frame after reset
    init_enemies()


# =========================================================
#                     TEXT (HUD)
# =========================================================

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


def draw_hud():
    draw_text(10, 770, f"Player Life Remaining: {player_life}")
    draw_text(10, 745, f"Game Score: {player_score}")
    draw_text(10, 720, f"Player Bullet Missed: {bullets_missed}")
    if game_over:
        draw_text(430, 400, "GAME OVER - Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24)


# =========================================================
#                     WORLD (GRID + WALLS)
# =========================================================

def draw_grid():
    """Dynamically built checkerboard floor - NOT hardcoded quad by quad."""
    glBegin(GL_QUADS)
    cols = int((2 * GRID_LENGTH) / TILE)
    for i in range(cols):
        for j in range(cols):
            x1 = -GRID_LENGTH + i * TILE
            y1 = -GRID_LENGTH + j * TILE
            x2 = x1 + TILE
            y2 = y1 + TILE
            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)          # white tile
            else:
                glColor3f(0.7, 0.5, 0.95)   # purple tile
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()


def draw_walls():
    """Four vertical boundary walls around the grid, each a different color."""
    wall_h = 150
    glBegin(GL_QUADS)
    # back wall (+Y) - cyan
    glColor3f(0, 1, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)

    # front wall (-Y) - yellow
    glColor3f(1, 1, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)

    # left wall (-X) - blue
    glColor3f(0, 0, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)

    # right wall (+X) - green
    glColor3f(0, 1, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glEnd()


# =========================================================
#                     PLAYER / ENEMIES / BULLETS
# =========================================================

def draw_player():
    """Sphere head, cylinder gun, cuboid body & legs."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)

    if game_over:
        # lie the player down when the game ends
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -20)

    # Legs (two cuboids)
    glColor3f(0.05, 0.05, 0.5)
    for lx in (-8, 8):
        glPushMatrix()
        glTranslatef(lx, 0, 15)
        glScalef(8, 8, 30)
        glutSolidCube(1)
        glPopMatrix()

    # Body (cuboid)
    glColor3f(0.3, 0.5, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glScalef(30, 20, 30)
    glutSolidCube(1)
    glPopMatrix()

    # Head (sphere)
    glColor3f(0.9, 0.75, 0.6)
    glPushMatrix()
    glTranslatef(0, 0, 70)
    gluSphere(gluNewQuadric(), 12, 10, 10)
    glPopMatrix()

    # Arms (two cylinders at the shoulders, pointing sideways) -
    # matches the two circular shapes at shoulder height in the
    # reference front-view image. This is what makes "Cylinders"
    # plural in the shape list (gun cylinder + these two).
    glColor3f(0.9, 0.75, 0.6)
    for ax in (-1, 1):
        glPushMatrix()
        glTranslatef(ax * 15, 0, 50)
        glRotatef(90, 0, 1, 0) if ax > 0 else glRotatef(-90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 6, 6, 14, 10, 10)
        glPopMatrix()

    # Gun (cylinder pointing forward, +Y)
    glColor3f(0.15, 0.15, 0.15)
    glPushMatrix()
    glTranslatef(0, 10, 50)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 2, 45, 8, 8)
    glPopMatrix()

    glPopMatrix()


def draw_enemies():
    """Each enemy = two spheres (body + smaller 'eye' sphere on top)."""
    for e in enemies:
        glPushMatrix()
        glTranslatef(e["pos"][0], e["pos"][1], e["pos"][2])
        glScalef(e["scale"], e["scale"], e["scale"])

        glColor3f(0.8, 0, 0)
        gluSphere(gluNewQuadric(), 26, 12, 12)

        glColor3f(0, 0, 0)
        glPushMatrix()
        glTranslatef(0, 0, 22)
        gluSphere(gluNewQuadric(), 10, 10, 10)
        glPopMatrix()

        glPopMatrix()


def draw_bullets():
    glColor3f(1, 0.5, 0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b["pos"][0], b["pos"][1], b["pos"][2])
        glutSolidCube(BULLET_SIZE)
        glPopMatrix()


def draw_shapes():
    draw_walls()
    draw_player()
    draw_enemies()
    draw_bullets()


# =========================================================
#                     GAME LOGIC
# =========================================================

def fire_bullet():
    if game_over:
        return
    dx = math.sin(math.radians(player_angle))
    dy = math.cos(math.radians(player_angle))
    start = [player_pos[0] + dx * 40, player_pos[1] + dy * 40, 50.0]
    bullets.append({"pos": start, "angle": player_angle})


def update_bullets(dt):
    global bullets_missed, player_score
    speed_scale = dt / REFERENCE_DT
    remaining = []
    for b in bullets:
        dx = math.sin(math.radians(b["angle"]))
        dy = math.cos(math.radians(b["angle"]))
        b["pos"][0] += dx * BULLET_SPEED * speed_scale
        b["pos"][1] += dy * BULLET_SPEED * speed_scale

        if abs(b["pos"][0]) > GRID_LENGTH or abs(b["pos"][1]) > GRID_LENGTH:
            bullets_missed += 1
            continue

        hit = False
        for e in enemies:
            dist = math.hypot(b["pos"][0] - e["pos"][0], b["pos"][1] - e["pos"][1])
            if dist < ENEMY_HIT_RADIUS:
                player_score += 1
                e["pos"] = spawn_enemy()["pos"]
                hit = True
                break
        if not hit:
            remaining.append(b)
    bullets[:] = remaining


def update_enemies(dt):
    global player_life
    speed_scale = dt / REFERENCE_DT
    for e in enemies:
        # chase the player
        dx = player_pos[0] - e["pos"][0]
        dy = player_pos[1] - e["pos"][1]
        dist = math.hypot(dx, dy)
        if dist > 1e-3:
            e["pos"][0] += (dx / dist) * ENEMY_SPEED * speed_scale
            e["pos"][1] += (dy / dist) * ENEMY_SPEED * speed_scale

        # shrink / expand animation
        if e["growing"]:
            e["scale"] += 0.01 * speed_scale
            if e["scale"] >= 1.3:
                e["growing"] = False
        else:
            e["scale"] -= 0.01 * speed_scale
            if e["scale"] <= 0.7:
                e["growing"] = True

        # collision with player
        if dist < PLAYER_HIT_RADIUS:
            player_life -= 1
            e["pos"] = spawn_enemy()["pos"]


def update_cheat_mode(dt):
    global player_angle, cheat_fire_cooldown, view_angle
    if not cheat_mode or game_over:
        return

    speed_scale = dt / REFERENCE_DT
    player_angle = (player_angle + CHEAT_ROTATE_SPEED * speed_scale) % 360

    # V key: only while cheat mode is spinning the gun does this matter.
    # If ON, the first-person view spins along with the gun.
    # If OFF, view_angle was already frozen when cheat mode started
    # (see keyboardListener), so the camera stays put.
    if cheat_camera_follow:
        view_angle = player_angle

    cheat_fire_cooldown -= dt

    if cheat_fire_cooldown <= 0:
        for e in enemies:
            dx = e["pos"][0] - player_pos[0]
            dy = e["pos"][1] - player_pos[1]
            target_angle = math.degrees(math.atan2(dx, dy)) % 360
            diff = abs((target_angle - player_angle + 180) % 360 - 180)
            if diff <= CHEAT_FOV_TOLERANCE:
                fire_bullet()
                cheat_fire_cooldown = 0.25
                break


def check_game_over():
    global game_over
    if player_life <= 0 or bullets_missed >= 10:
        game_over = True


# =========================================================
#                     INPUT
# =========================================================

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates,
    and cheat mode toggles.
    """
    global player_angle, cheat_mode, cheat_camera_follow, view_angle

    # Reset the game if R key is pressed
    if key == b'r':
        reset_game()
        return

    if game_over:
        return

    dx = math.sin(math.radians(player_angle))
    dy = math.cos(math.radians(player_angle))

    # Move forward (W key)
    if key == b'w':
        player_pos[0] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[0] + dx * PLAYER_SPEED))
        player_pos[1] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[1] + dy * PLAYER_SPEED))

    # Move backward (S key)
    if key == b's':
        player_pos[0] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[0] - dx * PLAYER_SPEED))
        player_pos[1] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[1] - dy * PLAYER_SPEED))

    # Rotate gun left (A key)
    if key == b'a' and not cheat_mode:
        player_angle = (player_angle + 5) % 360
        view_angle = player_angle

    # Rotate gun right (D key)
    if key == b'd' and not cheat_mode:
        player_angle = (player_angle - 5) % 360
        view_angle = player_angle

    # Toggle cheat mode (C key)
    if key == b'c':
        cheat_mode = not cheat_mode
        if cheat_mode:
            # Freeze the first-person look direction at the moment cheat
            # mode starts. It will only keep moving from here if
            # cheat_camera_follow (V) is also turned on.
            view_angle = player_angle
        else:
            # leaving cheat mode: re-sync view to wherever the gun ended up
            view_angle = player_angle

    # Toggle cheat vision / camera follow (V key)
    if key == b'v':
        cheat_camera_follow = not cheat_camera_follow


def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle
    and height. Mirrors the template's approach of updating camera_pos,
    but drives it through the orbit parameters so LEFT/RIGHT actually
    orbit around the floor and UP/DOWN actually change height.
    """
    global camera_height, camera_angle

    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        camera_height = min(1000, camera_height + 10)

    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        camera_height = max(50, camera_height - 10)

    # moving camera left (LEFT arrow key) - orbit around the grid
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 3) % 360

    # moving camera right (RIGHT arrow key) - orbit around the grid
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 3) % 360

    update_camera_pos()


def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling
    camera mode (right click).
    """
    global first_person

    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()

    # Right mouse button toggles camera tracking mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person


# =========================================================
#                     CAMERA
# =========================================================

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at
    the target - same shape as the template's setupCamera(): unpack
    camera_pos into x, y, z and feed it straight into gluLookAt().
    """
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        eye_x = player_pos[0]
        eye_y = player_pos[1]
        eye_z = player_pos[2] + 65

        dx = math.sin(math.radians(view_angle))
        dy = math.cos(math.radians(view_angle))
        center_x = eye_x + dx * 150
        center_y = eye_y + dy * 150
        center_z = eye_z

        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)
    else:
        # Extract camera position from camera_pos, exactly like the template
        x, y, z = camera_pos
        gluLookAt(x, y, z,   # Camera position
                  0, 0, 0,   # Look-at target
                  0, 0, 1)   # Up vector (z-axis)


# =========================================================
#                     MAIN LOOP
# =========================================================

def idle():
    """
    Runs as fast as GLUT will call it (often 1000s of times/sec with no cap),
    which is what was breaking movement speeds and starving input handling.
    We cap it to ~FPS frames/sec using time.sleep (plain Python, not an
    extra OpenGL/GLUT call) so:
      1) Enemies/bullets move at the intended, readable speed.
      2) GLUT actually gets CPU time to process keyboard/mouse events,
         instead of getting starved by an idle() that never yields.
    """
    global last_time

    now = time.time()
    dt = now - last_time
    if dt < FRAME_TIME:
        time.sleep(FRAME_TIME - dt)
        now = time.time()

    dt = now - last_time
    last_time = now

    # Safety clamp: if the window was dragged/minimized and dt spikes huge,
    # don't let a giant dt teleport enemies/bullets across the map in one step.
    dt = min(dt, FRAME_TIME * 3)

    if not game_over:
        update_cheat_mode(dt)
        update_bullets(dt)
        update_enemies(dt)
        check_game_over()

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_grid()
    draw_shapes()
    draw_hud()

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")

    update_camera_pos()
    init_enemies()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()