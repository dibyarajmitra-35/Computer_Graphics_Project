from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math, random, time


fovY, GRID_LENGTH, TILE = 120, 600, 60
camera_pos = (0.0, -700.0, 500.0)

camera_angle, camera_height, camera_radius = 0.0, 500.0, 700.0
fpp_screen, view_angle = False, 0.0

playerPosition = [0.0, 0.0, 0.0]
player_ang, PLAYER_SPEED = 0.0, 6.0

player_energy, playerPoint, missingShots = 5, 0, 0

game_end = False

bullets, SHOT_SPEED, BULLET_SIZE = [], 14.0, 8
enemyList, ENEMY_COUNT = [], 5

ENEMY_SPEED, ENEMY_HIT_RADIUS, PLAYER_HIT_RADIUS = 1.6, 34, 40

cheat_method, cheat_camera_follow = False, False
CHEAT_ROTATE_SPEED, CHEAT_FOV_TOLERANCE = 3.0, 6.0

cheat_fire_cooldown = 0.0
last_time = time.time()


def revise_cameraPos():
    global camera_pos

    r = math.radians(camera_angle)

    camera_pos = (
        camera_radius * math.sin(r),
        -camera_radius * math.cos(r),
        camera_height
    )


def land_enemy():
    return {
        "pos": [
            random.uniform(-GRID_LENGTH + 80, GRID_LENGTH - 80),
            random.uniform(-GRID_LENGTH + 80, GRID_LENGTH - 80),
            0.0
        ],
        "scale": 1.0,
        "growing": True
    }


def init_enemyList():
    global enemyList
    enemyList = [land_enemy() for _ in range(ENEMY_COUNT)]


def reboot_play():
    global playerPosition, player_ang, player_energy, playerPoint, missingShots
    global game_end, bullets, cheat_method, cheat_camera_follow, view_angle
    global camera_angle, camera_height, camera_radius, last_time

    playerPosition = [0.0, 0.0, 0.0]
    player_ang = 0.0
    player_energy = 5
    playerPoint = 0
    missingShots = 0

    game_end = False
    bullets = []

    cheat_method = False
    cheat_camera_follow = False
    view_angle = 0.0

    camera_angle = 0.0
    camera_height = 500.0
    camera_radius = 700.0

    last_time = time.time()

    revise_cameraPos()
    init_enemyList()


def draw_text(dx, dy, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(dx, dy)

    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)


def drawGrid():
    glBegin(GL_QUADS)

    nm = int(2 * GRID_LENGTH / TILE)

    for i in range(nm):
        for j in range(nm):
            x1 = -GRID_LENGTH + i * TILE
            y1 = -GRID_LENGTH + j * TILE
            x2 = x1 + TILE
            y2 = y1 + TILE

            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(.7, .5, .95)

            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)

    glEnd()


def draw_divider():
    h = 150

    glBegin(GL_QUADS)

    walls = [
        (
            (0, 1, 1),
            [
                (-GRID_LENGTH, GRID_LENGTH, 0),
                (GRID_LENGTH, GRID_LENGTH, 0),
                (GRID_LENGTH, GRID_LENGTH, h),
                (-GRID_LENGTH, GRID_LENGTH, h)
            ]
        ),
        (
            (1, 1, 0),
            [
                (-GRID_LENGTH, -GRID_LENGTH, 0),
                (GRID_LENGTH, -GRID_LENGTH, 0),
                (GRID_LENGTH, -GRID_LENGTH, h),
                (-GRID_LENGTH, -GRID_LENGTH, h)
            ]
        ),
        (
            (0, 0, 1),
            [
                (-GRID_LENGTH, -GRID_LENGTH, 0),
                (-GRID_LENGTH, GRID_LENGTH, 0),
                (-GRID_LENGTH, GRID_LENGTH, h),
                (-GRID_LENGTH, -GRID_LENGTH, h)
            ]
        ),
        (
            (0, 1, 0),
            [
                (GRID_LENGTH, -GRID_LENGTH, 0),
                (GRID_LENGTH, GRID_LENGTH, 0),
                (GRID_LENGTH, GRID_LENGTH, h),
                (GRID_LENGTH, -GRID_LENGTH, h)
            ]
        )
    ]

    for color, verts in walls:
        glColor3f(*color)

        for v in verts:
            glVertex3f(*v)

    glEnd()


def brick(dx, dy, dz, sx, sy, sz):
    glPushMatrix()

    glTranslatef(dx, dy, dz)
    glScalef(sx, sy, sz)
    glutSolidCube(1)

    glPopMatrix()


def make_cyl(dx, dy, dz, rx, ry, rz, r1, r2, h):
    glPushMatrix()

    glTranslatef(dx, dy, dz)
    glRotatef(rx, 1, 0, 0)
    glRotatef(ry, 0, 1, 0)
    glRotatef(rz, 0, 0, 1)

    gluCylinder(gluNewQuadric(), r1, r2, h, 10, 10)

    glPopMatrix()


def make_sphere(x, y, z, r):
    glPushMatrix()

    glTranslatef(x, y, z)
    gluSphere(gluNewQuadric(), r, 10, 10)

    glPopMatrix()


def render_player():
    glPushMatrix()

    glTranslatef(*playerPosition)
    glRotatef(player_ang, 0, 0, 1)

    if game_end:
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -20)

    glColor3f(.05, .05, .5)
    brick(-8, 0, 15, 8, 8, 30)
    brick(8, 0, 15, 8, 8, 30)

    glColor3f(.3, .5, .3)
    brick(0, 0, 45, 30, 20, 30)

    glColor3f(.9, .75, .6)
    make_sphere(0, 0, 70, 12)

    glColor3f(.9, .75, .6)
    make_cyl(-15, 0, 50, 0, -90, 0, 6, 6, 14)
    make_cyl(15, 0, 50, 0, 90, 0, 6, 6, 14)

    glColor3f(.15, .15, .15)
    make_cyl(0, 10, 50, -90, 0, 0, 4, 2, 45)

    glPopMatrix()


def draw_enemyList():
    for e in enemyList:
        x, y, z = e["pos"]

        glPushMatrix()

        glTranslatef(x, y, z)
        glScalef(e["scale"], e["scale"], e["scale"])

        glColor3f(.8, 0, 0)
        gluSphere(gluNewQuadric(), 26, 12, 12)

        glColor3f(0, 0, 0)
        glTranslatef(0, 0, 22)

        gluSphere(gluNewQuadric(), 10, 10, 10)

        glPopMatrix()


def renderingBullets():
    glColor3f(1, .5, 0)

    for b in bullets:
        glPushMatrix()

        glTranslatef(*b["pos"])
        glutSolidCube(BULLET_SIZE)

        glPopMatrix()


def draw_shapes():
    draw_divider()

    if not fpp_screen:
        render_player()

    draw_enemyList()
    renderingBullets()


def shooting_bullets():
    if game_end:
        return

    a = math.radians(player_ang)

    bullets.append({
        "pos": [
            playerPosition[0] + math.sin(a) * 40,
            playerPosition[1] + math.cos(a) * 40,
            50.0
        ],
        "angle": player_ang
    })


def moveEnemy(dt):
    global missingShots, playerPoint

    k = dt / (1 / 60)
    keep = []

    for b in bullets:
        a = math.radians(b["angle"])

        b["pos"][0] += math.sin(a) * SHOT_SPEED * k
        b["pos"][1] += math.cos(a) * SHOT_SPEED * k

        if abs(b["pos"][0]) > GRID_LENGTH or abs(b["pos"][1]) > GRID_LENGTH:
            missingShots += 1
            continue

        hit = False

        for e in enemyList:
            if math.hypot(
                b["pos"][0] - e["pos"][0],
                b["pos"][1] - e["pos"][1]
            ) < ENEMY_HIT_RADIUS:

                playerPoint += 1
                e["pos"] = land_enemy()["pos"]

                hit = True
                break

        if not hit:
            keep.append(b)

    bullets[:] = keep


def update_enemyList(dt):
    global player_energy

    k = dt / (1 / 60)

    for e in enemyList:
        dx = playerPosition[0] - e["pos"][0]
        dy = playerPosition[1] - e["pos"][1]

        d = math.hypot(dx, dy)

        if d > 1e-3:
            e["pos"][0] += dx / d * ENEMY_SPEED * k
            e["pos"][1] += dy / d * ENEMY_SPEED * k

        e["scale"] += (.01 if e["growing"] else -.01) * k

        if e["scale"] >= 1.3:
            e["scale"] = 1.3
            e["growing"] = False

        if e["scale"] <= .7:
            e["scale"] = .7
            e["growing"] = True

        d2 = math.hypot(
            playerPosition[0] - e["pos"][0],
            playerPosition[1] - e["pos"][1]
        )

        if d2 < PLAYER_HIT_RADIUS:
            player_energy -= 1
            e["pos"] = land_enemy()["pos"]


def enter_cheat(dt):
    global player_ang, cheat_fire_cooldown, view_angle

    if not cheat_method or game_end:
        return

    k = dt / (1 / 60)

    player_ang = (player_ang + CHEAT_ROTATE_SPEED * k) % 360

    if cheat_camera_follow:
        view_angle = player_ang

    cheat_fire_cooldown -= dt

    if cheat_fire_cooldown <= 0:
        for e in enemyList:
            dx = e["pos"][0] - playerPosition[0]
            dy = e["pos"][1] - playerPosition[1]

            tar = math.degrees(math.atan2(dx, dy)) % 360
            diff = abs((tar - player_ang + 180) % 360 - 180)

            if diff <= CHEAT_FOV_TOLERANCE:
                shooting_bullets()
                cheat_fire_cooldown = .25
                break


def verify_game_over():
    global game_end

    game_end = player_energy <= 0 or missingShots >= 10


def keyboardListener(key, x, y):
    global player_ang, cheat_method, cheat_camera_follow, view_angle

    if key == b'r':
        reboot_play()
        return

    if game_end:
        return

    a = math.radians(player_ang)
    dx, dy = math.sin(a), math.cos(a)

    if key == b'w':
        playerPosition[0] = max(
            -GRID_LENGTH,
            min(GRID_LENGTH, playerPosition[0] + dx * PLAYER_SPEED)
        )

        playerPosition[1] = max(
            -GRID_LENGTH,
            min(GRID_LENGTH, playerPosition[1] + dy * PLAYER_SPEED)
        )

    elif key == b's':
        playerPosition[0] = max(
            -GRID_LENGTH,
            min(GRID_LENGTH, playerPosition[0] - dx * PLAYER_SPEED)
        )

        playerPosition[1] = max(
            -GRID_LENGTH,
            min(GRID_LENGTH, playerPosition[1] - dy * PLAYER_SPEED)
        )

    elif key == b'a' and not cheat_method:
        player_ang = (player_ang + 5) % 360

    elif key == b'd' and not cheat_method:
        player_ang = (player_ang - 5) % 360

    elif key == b'c':
        cheat_method = not cheat_method
        view_angle = player_ang

    elif key == b'v':
        cheat_camera_follow = not cheat_camera_follow


def specialKeyListener(key, x, y):
    global camera_height, camera_angle

    if key == GLUT_KEY_UP:
        camera_height = min(1000, camera_height + 10)

    elif key == GLUT_KEY_DOWN:
        camera_height = max(50, camera_height - 10)

    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 3) % 360

    elif key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 3) % 360

    revise_cameraPos()


def mouseListener(button, state, x, y):
    global fpp_screen

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shooting_bullets()

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        fpp_screen = not fpp_screen


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(fovY, 1.25, .1, 1500)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if fpp_screen:
        ex = playerPosition[0]
        ey = playerPosition[1]
        ez = playerPosition[2] + 65

        a = math.radians(player_ang)

        gluLookAt(
            ex,
            ey,
            ez,
            ex + math.sin(a) * 300,
            ey + math.cos(a) * 300,
            ez,
            0,
            0,
            1
        )

    else:
        x, y, z = camera_pos

        gluLookAt(
            x,
            y,
            z,
            0,
            0,
            0,
            0,
            0,
            1
        )


def idle():
    global last_time

    now = time.time()
    dt = min(now - last_time, .05)
    last_time = now

    if not game_end:
        enter_cheat(dt)
        moveEnemy(dt)
        update_enemyList(dt)
        verify_game_over()

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glViewport(0, 0, 1000, 800)

    setupCamera()
    drawGrid()
    draw_shapes()

    draw_text(
        10,
        770,
        f"Player Life Remaining: {player_energy}"
    )

    draw_text(
        10,
        745,
        f"Game Score: {playerPoint}"
    )

    draw_text(
        10,
        720,
        f"Player Bullet Missed: {missingShots}"
    )

    if game_end:
        draw_text(
            380,
            400,
            "GAME OVER - Press R to restart",
            GLUT_BITMAP_TIMES_ROMAN_24
        )

    glutSwapBuffers()


def main():
    global last_time

    glutInit()

    glutInitDisplayMode(
        GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH
    )

    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)

    glutCreateWindow(b"Bullet Frenzy")

    glEnable(GL_DEPTH_TEST)

    revise_cameraPos()
    init_enemyList()
    last_time = time.time()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()