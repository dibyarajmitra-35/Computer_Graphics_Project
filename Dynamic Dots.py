from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
BOX_LIMIT = 250

dots = []

crr_spd= 1.0
SPEED_STEP = 0.5
MIN_SPEED = 0.2
MAX_SPEED = 6.0

frezz = False
blinkShow = True
blinking = False


BG_COLOR = (0.0, 0.0, 0.0)


def convert_coordinate(x, y):
    ox = x - (WINDOW_WIDTH / 2)
    oy = (WINDOW_HEIGHT / 2) - y
    return ox, oy


def setup_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-WINDOW_WIDTH / 2, WINDOW_WIDTH / 2,
            -WINDOW_HEIGHT / 2, WINDOW_HEIGHT / 2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()





def draw_points():
    POINT_SIZE = 7

    glPointSize(POINT_SIZE)
    glBegin(GL_POINTS)
    
    for point in dots:
        
        p, z, dx_axis, dy_axis, red, gre, blue = point
        
        if blinking and not blinkShow:
            glColor3f(*BG_COLOR)
        
        else:
            glColor3f(red, gre, blue)
        glVertex2f(p, z)
    
    glEnd()



def update_points():
    if frezz:
        return

    for pointer in dots:
        pointer[0] += pointer[2] * crr_spd
        pointer[1] += pointer[3] * crr_spd

        
        if pointer[0] > BOX_LIMIT:
            
            pointer[0] = BOX_LIMIT
            pointer[2] *= -1
        
        
        elif pointer[0] < -BOX_LIMIT:
            
            pointer[0] = -BOX_LIMIT
            pointer[2] = -pointer[2]

        if pointer[1] > BOX_LIMIT:
            
            pointer[1] = BOX_LIMIT
            pointer[3] = -pointer[3]
        
        
        elif pointer[1] < -BOX_LIMIT:
            
            pointer[1] = -BOX_LIMIT
            pointer[3] = -pointer[3]




def display_dots():
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_projection()
    
    glClearColor(*BG_COLOR, 1.0)

    

    draw_points()

    
    glutSwapBuffers()


def show_animation():
    update_points()
    glutPostRedisplay()


def timeBlink(value):
    global blinkShow

    
    if blinking and not frezz:
        blinkShow = not blinkShow
        glutPostRedisplay()

    glutTimerFunc(500, timeBlink, 0)


def mouse_clicker(button, state, x, y):
    global blinking

    if frezz:
        return

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        gx_axis, gy_axis = convert_coordinate(x, y)

        if -BOX_LIMIT <= gx_axis <= BOX_LIMIT and -BOX_LIMIT <= gy_axis <= BOX_LIMIT:
            
            dx_axis = random.uniform(-1, 1)
            dy_axis = random.uniform(-1, 1)
            def randomColor():
                return(random.random(), random.random(), random.random())
            
            red, gre, blue = randomColor()
            dots.append([gx_axis, gy_axis, dx_axis, dy_axis, red, gre, blue])

            print(f"Spawned point at ({gx_axis:.1f}, {gy_axis:.1f}) dir=({dx_axis},{dy_axis}) color=({red:.2f},{gre:.2f},{blue:.2f})")

    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        
        blinking = not blinking

        print("Blinking:", "ON" if blinking else "OFF")


def keyboard_clicker(key, x, y):
    global frezz

    if key == b' ':
        frezz = not frezz
        
        if frezz:
            print("Animation Stop")

        else:
            print("Animation Working")    

    glutPostRedisplay()



def special_key_clicker(key, x, y):
    global crr_spd

    
    if frezz:
        return

    if key == GLUT_KEY_UP:
        crr_spd = min(MAX_SPEED, crr_spd + SPEED_STEP)
        print("Speed increased ->", crr_spd)

    elif key == GLUT_KEY_DOWN:
        crr_spd = max(MIN_SPEED, crr_spd - SPEED_STEP)
        print("Speed decreased ->", crr_spd)

    glutPostRedisplay()




def main_task2():
    
    glutInit()
    
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    
    
    glutCreateWindow(b"Task 2: The Amazing Box - CSE423")

    glutDisplayFunc(display_dots)
    glutIdleFunc(show_animation)
    
    glutMouseFunc(mouse_clicker)
    glutKeyboardFunc(keyboard_clicker)
    
    glutSpecialFunc(special_key_clicker)
    glutTimerFunc(500, timeBlink, 0)

    
    glutMainLoop()




if __name__ == "__main__":
    main_task2()    