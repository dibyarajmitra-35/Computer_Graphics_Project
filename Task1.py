from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math


WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

windTransfer = 0.0
WIND_STEP = 2.0
WIND_MAX = 45.0



rainSp = 7.5
NUM_DROPS = 180
raindropping = []



skyColor = 0.25
BRIGHTNESS_STEP = 0.02

rain_angle = 90.0



def init_createRain():
    global raindropping
    raindropping = []
    
    for _ in range(NUM_DROPS):
        x = random.uniform(0, WINDOW_WIDTH)
        y = random.uniform(0, WINDOW_HEIGHT)
        
        leng = random.uniform(10, 16)
        raindropping.append([x, y, leng])



def set_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()


def show_house():
    glColor3f(0.60, 0.45, 0.10)
    glBegin(GL_TRIANGLES)

    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, 360)

    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 360)
    glVertex2f(0, 360)
    
    glEnd()

    show_tree()

    hx_axis, hy_axis = 230, 200
    hWidth, hHeigth = 370, 128

    glColor3f(0.97, 0.94, 0.90)
    glBegin(GL_TRIANGLES)
    glVertex2f(hx_axis, hy_axis)
    glVertex2f(hx_axis + hWidth, hy_axis)
    glVertex2f(hx_axis + hWidth, hy_axis + hHeigth)

    glVertex2f(hx_axis, hy_axis)
    glVertex2f(hx_axis + hWidth, hy_axis + hHeigth)
    glVertex2f(hx_axis, hy_axis + hHeigth)
    glEnd()

    glColor3f(0.33, 0.10, 0.65)
    glBegin(GL_TRIANGLES)

    glVertex2f(hx_axis - 45, hy_axis + hHeigth)
    glVertex2f(hx_axis + hWidth + 45, hy_axis + hHeigth)
    glVertex2f(hx_axis + hWidth / 2, hy_axis + hHeigth + 96)
    glEnd()

   
    draw_width, draw_height = 70, 110
    dx_axis, dy_axis = hx_axis + hWidth / 2 - draw_width / 2, hy_axis
    
    glColor3f(0.20, 0.55, 0.95)
    
    glBegin(GL_TRIANGLES)
    
    glVertex2f(dx_axis, dy_axis)
    glVertex2f(dx_axis + draw_width, dy_axis)
    glVertex2f(dx_axis + draw_width, dy_axis + draw_height)

    glVertex2f(dx_axis, dy_axis)
    glVertex2f(dx_axis + draw_width, dy_axis + draw_height)
    glVertex2f(dx_axis, dy_axis + draw_height)
    
    glEnd()

    glColor3f(1.0, 1.0, 0.0)
    
    glPointSize(5)
    glBegin(GL_POINTS)
    
    glVertex2f(dx_axis + draw_width - 8, dy_axis + draw_height / 2)
    
    glEnd()

    glColor3f(0.20, 0.60, 0.95)
    glLineWidth(2)
   
    for windowx_axis in (hx_axis + 40, hx_axis + hWidth - 100):
        windowy_axis = hy_axis + 50
        windowwidth, windowheight = 50, 50

       
        glColor3f(0.20, 0.50, 0.95)
        glBegin(GL_TRIANGLES)
        glVertex2f(windowx_axis, windowy_axis)
        glVertex2f(windowx_axis + windowwidth, windowy_axis)
        glVertex2f(windowx_axis + windowwidth, windowy_axis + windowheight)

        glVertex2f(windowx_axis, windowy_axis)
        glVertex2f(windowx_axis + windowwidth, windowy_axis + windowheight)
        glVertex2f(windowx_axis, windowy_axis + windowheight)
        glEnd()

       
        glColor3f(0.1, 0.1, 0.1)
        glLineWidth(2)


        glBegin(GL_LINES)
        glVertex2f(windowx_axis + windowwidth / 2, windowy_axis)
        glVertex2f(windowx_axis + windowwidth / 2, windowy_axis + windowheight)

        glVertex2f(windowx_axis, windowy_axis + windowheight / 2)
        glVertex2f(windowx_axis + windowwidth, windowy_axis + windowheight / 2)
        glEnd()

       

def show_tree():
    glColor3f(0.18, 0.85, 0.08)

    for x in range(-10, WINDOW_WIDTH, 40):
       
       if 250 <= x <= 570:
         continue
       
       y = 300

       glBegin(GL_TRIANGLES)
       glVertex2f(x , y)
       glVertex2f(x + 16, y + 70)
       glVertex2f(x + 31, y)

       glEnd()


def show_rain():
    if skyColor > 0.55:
        glColor3f(0.25, 0.35, 0.85)
    else:
        glColor3f(0.65, 0.78, 1.0)

    glLineWidth(1.5)
    rad = math.radians(rain_angle)
    value = math.tan(rad)
    
    
    glBegin(GL_LINES)
    

    for x, y, length in raindropping:
        dx_axis = length / value if abs(value) > 1e-4 else 0.0  
           
        glVertex2f(x, y)
        glVertex2f(x + dx_axis, y - length)
    glEnd()


def shift_rain():
    for dropping in raindropping:
        dropping[1] -= rainSp
        dropping[0] += windTransfer * 0.08      

        if dropping[1] < 0:
            dropping[1] = WINDOW_HEIGHT + random.uniform(0, 60)
            dropping[0] = random.uniform(0, WINDOW_WIDTH)

        if dropping[0] < -20:
            dropping[0] = WINDOW_WIDTH + 20
        elif dropping[0] > WINDOW_WIDTH + 20:
            dropping[0] = -20


def show_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    set_projection()

    red = 0.02 + skyColor * 0.55
    green = 0.02 + skyColor * 0.65
    blue = 0.15 + skyColor * 0.65

    glClearColor(red, green, blue, 1.0)



    show_house()
    show_rain()

    glutSwapBuffers()



def update_animation():
    move_rain()
    shift_rain()

    glutPostRedisplay()

def move_rain():
    global rain_angle
    changeTime = glutGet(GLUT_ELAPSED_TIME) / 1000.0

    if changeTime < 2:
        rain_angle = 90
    elif changeTime < 5:
        rain_angle = 45
    else:
        rain_angle = -45            


def keyboard_listener(key, x, y):
    global skyColor

    if key == b'a':
        skyColor = min(1.0, skyColor + BRIGHTNESS_STEP)
        print("Turning towards day, brightness =", round(skyColor, 2))

    elif key == b'z':
        skyColor = max(0.0, skyColor - BRIGHTNESS_STEP)
        print("Turning towards night, brightness =", round(skyColor, 2))

    glutPostRedisplay()


def special_key_listener(key, x, y):
    global windTransfer

    if key == GLUT_KEY_LEFT:
        windTransfer = max(-WIND_MAX, windTransfer - WIND_STEP)
        print("Bending rain left, offset =", round(windTransfer, 2))

    elif key == GLUT_KEY_RIGHT:
        windTransfer = min(WIND_MAX, windTransfer + WIND_STEP)
        print("Bending rain right, offset =", round(windTransfer, 2))

    glutPostRedisplay()





def main_task1():
    glutInit()
    
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    
    glutInitWindowPosition(100, 100)
    
    
    glutCreateWindow(b"Task 1: House in Rainfall - CSE423")

    init_createRain()

    glutDisplayFunc(show_display)
    glutIdleFunc(update_animation)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)

    glutMainLoop()




if __name__ == "__main__task1":
    main_task1()