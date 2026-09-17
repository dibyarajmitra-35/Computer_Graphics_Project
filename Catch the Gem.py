
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
import random


WIDTH_WIN = 390
HEIGHT_WIN = 590

def midLineZoneZero(x1, y1, x2, y2):
    points = []
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0:
        y = y1
        while y <= y2:
            points.append((x1, y))
            y += 1
        return points

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x = x1
    y = y1

    while x <= x2:
        points.append((x, y))
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE
        x = x + 1
    return points



def zoneFInd(dx, dy):
    if dx >= 0 and dy >= 0:
        return 0 if abs(dx) >= abs(dy) else 1
    if dx <= 0 and dy >= 0:
        return 3 if abs(dx) >= abs(dy) else 2
    if dx <= 0 and dy <= 0:
        return 4 if abs(dx) >= abs(dy) else 5
    return 7 if abs(dx) >= abs(dy) else 6

_TO_ZONE0 = {


    0: lambda dx, dy: (dx, dy),
    1: lambda dx, dy: (dy, dx),
    2: lambda dx, dy: (dy, -dx),
    3: lambda dx, dy: (-dx, dy),
    4: lambda dx, dy: (-dx, -dy),
    5: lambda dx, dy: (-dy, -dx),
    6: lambda dx, dy: (-dy, dx),
    7: lambda dx, dy: (dx, -dy),


}

_FROM_ZONE0 = {



    0: lambda x, y: (x, y),
    1: lambda x, y: (y, x),
    2: lambda x, y: (-y, x),
    3: lambda x, y: (-x, y),
    4: lambda x, y: (-x, -y),
    5: lambda x, y: (-y, -x),
    6: lambda x, y: (y, -x),
    7: lambda x, y: (x, -y),


}



def drawMidLine(x1, y1, x2, y2):



    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)

    if x1 > x2 or (x1 == x2 and y1 > y2):
        x1, y1, x2, y2 = x2, y2, x1, y1

    x1i, y1i, x2i, y2i = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))


    dx = x2i - x1i
    dy = y2i - y1i

    if dx == 0 and dy == 0:

        glBegin(GL_POINTS)
        glVertex2f(x1i, y1i)


        glEnd()


        return

    zone = zoneFInd(dx, dy)
    x0_2, y0_2 = _TO_ZONE0[zone](dx, dy)
    zone0_points = midLineZoneZero(0, 0, x0_2, y0_2)

    glBegin(GL_POINTS)


    for (px, py) in zone0_points:
        rdx, rdy = _FROM_ZONE0[zone](px, py)
        glVertex2f(x1i + rdx, y1i + rdy)


    glEnd()



def colorsSet(rgb):

    red = rgb[0]
    blue = rgb[2]
    gre = rgb[1]
     
    glColor3f(red, gre, blue)



def drawDiamond(x, y, r, color):

    colorsSet(color)

    drawMidLine(x - r, y, x, y + r)
    drawMidLine(x, y + r, x + r, y)

    drawMidLine(x + r, y, x, y - r)
    drawMidLine(x, y - r, x - r, y)

def catchDrawing(cx, cy, half_top, half_bottom, height, color):

    colorsSet(color)


    tl = (cx - half_top, cy + height)
    tr = (cx + half_top, cy + height)


    bl = (cx - half_bottom, cy)
    br = (cx + half_bottom, cy)
    drawMidLine(tl[0], tl[1], bl[0], bl[1])
    drawMidLine(bl[0], bl[1], br[0], br[1])


    drawMidLine(br[0], br[1], tr[0], tr[1])
    drawMidLine(tr[0], tr[1], tl[0], tl[1])

def restartButton(cx, cy, color):
    colorsSet(color)
    drawMidLine(cx - 12, cy, cx + 12, cy)

    drawMidLine(cx - 12, cy, cx - 4, cy + 8)
    drawMidLine(cx - 12, cy, cx - 4, cy - 8)

def drawPause(cx, cy, color):

    colorsSet(color)


    drawMidLine(cx - 6, cy - 9, cx - 6, cy + 9)
    drawMidLine(cx + 6, cy - 9, cx + 6, cy + 9)

def drawPlay(cx, cy, color):
    colorsSet(color)

    drawMidLine(cx - 7, cy - 9, cx - 7, cy + 9)


    drawMidLine(cx - 7, cy + 9, cx + 9, cy)
    drawMidLine(cx + 9, cy, cx - 7, cy - 9)

def drawQuitButton(cx, cy, color):

    colorsSet(color)



    drawMidLine(cx - 9, cy - 9, cx + 9, cy + 9)
    drawMidLine(cx - 9, cy + 9, cx + 9, cy - 9)


TEAL = (0.1, 0.9, 0.8)
AMBER = (1.0, 0.5, 0.1)


RED = (1.0, 0.25, 0.3)
WHITE = (0.9, 0.95, 1.0)

RESTART_BTN = (40, HEIGHT_WIN - 30)
PAUSE_BTN = (WIDTH_WIN // 2, HEIGHT_WIN - 30)


QUIT_BTN = (WIDTH_WIN - 40, HEIGHT_WIN - 30)
BTN_HALF = 17

DIAMONDSIZE = 16


FALLSPEED = 70.5
SPEEDRAISE = 7.0



HALFTOP_CATCHER = 39.5
BOTTOM_CATCHER = 18.5


HEIGHT_C = 27
CATCHER_Y = 42



SPEED_MOVE = 220.5



DIAMONDCOLOR = [

    (1.0, 0.1, 0.3),
    (0.2, 1.0, 0.5),
    (0.2, 0.4, 1.0),
    (1.0, 0.8, 0.0),
    (0.8, 0.2, 1.0),
    (0.0, 0.9, 1.0),
    (1.0, 0.4, 0.0),

]



state = {

    "catchX": WIDTH_WIN/ 2.0,

    "diamondX": WIDTH_WIN / 2.0,
    "diamondY": HEIGHT_WIN - 80.0,
    "diamondColor": random.choice(DIAMONDCOLOR),

    "downSpeed": FALLSPEED,
    "total_score": 0,
    "isPlay": True,
    "gameOver": False,
    "cheat": False,

    "liveTime": 0.0,
    "EndTime": time.time(),

    "leftMove": False,
    "rightMove": False,
}


def new_diamond():

    marg = DIAMONDSIZE + 5
    state["diamondX"] = random.uniform(marg, WIDTH_WIN - marg)
    state["diamond_y"] = HEIGHT_WIN - 60.0
    state["diamondColor"] = random.choice(DIAMONDCOLOR)



def resetGame():
    state["catchX"] = WIDTH_WIN / 2.0
    state["total_score"] = 0
    state["downSpeed"] = FALLSPEED

    state["liveTime"] = 0.0
    state["isPlay"] = True

    state["gameOver"] = False
    state["cheat"] = False

    new_diamond()

    state["EndTime"] = time.time()

    print("Starting Over")


def collisionCheck(ax, ay, aw, ah, bx, by, bw, bh):
    if ax + aw <= bx:
       return False
    if bx + bw <= ax:
        return False
    if ay + ah <= by:
        return False
    if by + bh <= ay:
        return False

    return False 
    

def checkDiamond():
    d = state

    dx0 = d["diamondX"] - DIAMONDSIZE
    dy0 = d["diamond_y"] - DIAMONDSIZE
    dw = dh = DIAMONDSIZE * 2

    cx0 = d["catchX"] - HALFTOP_CATCHER
    cy0 = CATCHER_Y
    cw = HALFTOP_CATCHER * 2
    ch = HEIGHT_C

    if collisionCheck(dx0, dy0, dw, dh, cx0, cy0, cw, ch):
        d["total_score"] += 1
        print("Caught! Score:", d["total_score"])
        new_diamond()
        return

    if d["diamond_y"] - DIAMONDSIZE <= 0:
        d["gameOver"] = True
        d["isPlay"] = False
        print("Game Over. Final Score:", d["total_score"])

def setProjection():
    glViewport(0, 0, WIDTH_WIN, HEIGHT_WIN)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, WIDTH_WIN, 0.0, HEIGHT_WIN, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)



def display():


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    setProjection()

    restartButton(RESTART_BTN[0], RESTART_BTN[1], TEAL)

    if state["isPlay"] and not state["gameOver"]:
        drawPause(PAUSE_BTN[0], PAUSE_BTN[1], AMBER)

    else:
        drawPlay(PAUSE_BTN[0], PAUSE_BTN[1], AMBER)
    drawQuitButton(QUIT_BTN[0], QUIT_BTN[1], RED)


    if not state["gameOver"]:
        drawDiamond(
            state["diamondX"],
            state["diamond_y"],
            DIAMONDSIZE,
            state["diamondColor"]
        )


    catcher_color = RED if state["gameOver"] else WHITE


    catchDrawing(

        state["catchX"],
        CATCHER_Y,
        HALFTOP_CATCHER,
        BOTTOM_CATCHER,
        HEIGHT_C,
        catcher_color

    )

    glutSwapBuffers()


def gameUpdate():


    nw = time.time()

    dt = nw - state["EndTime"]

    state["EndTime"] = nw


    if not state["gameOver"] and state["isPlay"]:

        state["liveTime"] += dt
        state["downSpeed"] = FALLSPEED + state["liveTime"] * SPEEDRAISE


        state["diamond_y"] -= state["downSpeed"] * dt



        if state["cheat"]:
            target = state["diamondX"]
            diff = target - state["catchX"]

            step = SPEED_MOVE * dt

            if abs(diff) <= step:
                state["catchX"] = target

            else:
                state["catchX"] += step if diff > 0 else -step



        else:


            if state["leftMove"]:
                state["catchX"] -= SPEED_MOVE * dt
            if state["rightMove"]:
                state["catchX"] += SPEED_MOVE * dt

        min_x = HALFTOP_CATCHER
        max_x = WIDTH_WIN - HALFTOP_CATCHER



        state["catchX"] = max(min_x, min(max_x, state["catchX"]))



        checkDiamond()



    glutPostRedisplay()




def keyboard_key_Input(key, x, y):




    if key == b'c':

        state["cheat"] = not state["cheat"]
        print("Cheat mode:", "ON" if state["cheat"] else "OFF")


    glutPostRedisplay()



def specialkey_Input(key, x, y):


    if state["gameOver"] or not state["isPlay"] or state["cheat"]:
        return

    if key == GLUT_KEY_LEFT:
        state["leftMove"] = True

    elif key == GLUT_KEY_RIGHT:
        state["rightMove"] = True


    glutPostRedisplay()




def special_key_Out(key, x, y):



    if key == GLUT_KEY_LEFT:
        state["leftMove"] = False


    elif key == GLUT_KEY_RIGHT:
        state["rightMove"] = False




def coordsConvert(x, y):

    nX = x
    nY = HEIGHT_WIN - y


    return nX, nY



def pressButton(x, y, btn):


    return (abs(x - btn[0]) <= BTN_HALF) and (abs(y - btn[1]) <= BTN_HALF)



def mouseInput(button, click_state, x, y):


    if button == GLUT_LEFT_BUTTON and click_state == GLUT_DOWN:


        gx, gy = coordsConvert(x, y)


        if pressButton(gx, gy, RESTART_BTN):
            resetGame()


        elif pressButton(gx, gy, PAUSE_BTN):

            if not state["gameOver"]:
                state["isPlay"] = not state["isPlay"]
                state["EndTime"] = time.time()

                print("Paused" if not state["isPlay"] else "Resumed")



        elif pressButton(gx, gy, QUIT_BTN):
            print("Goodbye. Final Score:", state["total_score"])
            glutLeaveMainLoop()



    glutPostRedisplay()




def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WIDTH_WIN, HEIGHT_WIN)


    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")

    new_diamond()

    glutDisplayFunc(display)
    glutIdleFunc(gameUpdate)


    glutKeyboardFunc(keyboard_key_Input)

    glutSpecialFunc(specialkey_Input)


    glutSpecialUpFunc(special_key_Out)
    glutMouseFunc(mouseInput)


    glutMainLoop()



if __name__ == "__main__":
    main()
