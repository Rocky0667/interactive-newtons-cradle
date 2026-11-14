from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import sys

# --- Window & Simulation Constants ---
WIDTH = 500
HEIGHT = 500

num_balls = 5
ball_radius = 18.0
string_length = 230.0 
pivot_y = 425.0
spacing = 38.0
start_x = 171.0    

# Store angles and angular velocities for each pendulum
angles = [0.0, 0.0, 0.0, 0.0, 0.0]
velocities = [0.0, 0.0, 0.0, 0.0, 0.0]

# Mouse interaction state
dragging_ball_index = -1

def get_ball_positions():
    positions = []
    for i in range(num_balls):
        pivot_x = start_x + (i * spacing)
        angle = angles[i]
        x = pivot_x + string_length * math.sin(angle)
        y = pivot_y - string_length * math.cos(angle)
        positions.append((x, y))
    return positions

def draw_circle(x, y, radius, r, g, b):
    # Main ball body
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    segments = 30
    for i in range(segments + 1):
        theta = 2.0 * math.pi * float(i) / float(segments)
        dx = radius * math.cos(theta)
        dy = radius * math.sin(theta)
        glVertex2f(x + dx, y + dy)
    glEnd()

    # Simple highlight overlay for basic shading effect
    glColor3f(min(r + 0.3, 1.0), min(g + 0.3, 1.0), min(b + 0.3, 1.0))
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x - 4, y + 4)
    highlight_radius = radius * 0.3
    for i in range(15):
        theta = math.pi * float(i) / 14.0
        dx = highlight_radius * math.cos(theta)
        dy = highlight_radius * math.sin(theta)
        glVertex2f(x - 4 + dx, y + 4 + dy)
    glEnd()

def draw_rounded_box(x1, y1, x2, y2, r, g, b):
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()

def draw_arch_frame():
    # Left & Right Metallic Pillars (with basic lighting highlight effect)
    draw_rounded_box(100, 110, 120, 440, 0.6, 0.6, 0.65)
    draw_rounded_box(103, 110, 108, 440, 0.8, 0.8, 0.85) # Highlight line
    
    draw_rounded_box(380, 110, 400, 440, 0.6, 0.6, 0.65)
    draw_rounded_box(383, 110, 388, 440, 0.8, 0.8, 0.85) # Highlight line
    
    # Top Horizontal Bar
    draw_rounded_box(90, 430, 410, 455, 0.7, 0.7, 0.75)
    draw_rounded_box(90, 445, 410, 452, 0.85, 0.85, 0.9) # Top reflection

def draw_wooden_base():
    # Bottom dark shadow block
    draw_rounded_box(60, 60, 440, 85, 0.35, 0.18, 0.08)
    # Main wooden block
    draw_rounded_box(50, 85, 450, 115, 0.55, 0.32, 0.15)
    # Top wood surface grain/highlight
    draw_rounded_box(55, 105, 445, 111, 0.65, 0.40, 0.20)

def update_physics():
    global angles, velocities, dragging_ball_index
    
    g = 0.5  # Gravity factor
    dt = 0.2 # Time step
    damping = 0.995 # Air resistance

    for i in range(num_balls):
        if i == dragging_ball_index:
            continue
        
        # Simple pendulum formula acceleration
        acceleration = -(g / (string_length / 20.0)) * math.sin(angles[i])
        velocities[i] += acceleration * dt
        velocities[i] *= damping
        angles[i] += velocities[i] * dt

    # Handle collisions between adjacent balls (Momentum transfer)
    positions = get_ball_positions()
    for i in range(num_balls - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i+1]
        
        dist = math.hypot(x2 - x1, y2 - y1)
        min_dist = ball_radius * 2.0
        
        if dist < min_dist:
            v_temp = velocities[i]
            velocities[i] = velocities[i+1] * 0.95
            velocities[i+1] = v_temp * 0.95
            
            overlap = 0.5 * (min_dist - dist)
            if i != dragging_ball_index:
                angles[i] -= overlap * 0.01
            if i + 1 != dragging_ball_index:
                angles[i+1] += overlap * 0.01

def display():
    # Set background color to Black
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_wooden_base()
    draw_arch_frame()

    positions = get_ball_positions()
    for i in range(num_balls):
        pivot_x = start_x + (i * spacing)
        ball_x, ball_y = positions[i]

        # Draw clean parallel strings (single vertical line for each side or clean double line)
        glLineWidth(1.5)
        glBegin(GL_LINES)
        glColor3f(0.8, 0.8, 0.8) 
        
        # Ekhane amra duita line ekdom smooth parallel kore diyechi (jorh laga lagbe na)
        glVertex2f(pivot_x - 2, pivot_y)
        glVertex2f(ball_x - 2, ball_y)
        
        glVertex2f(pivot_x + 2, pivot_y)
        glVertex2f(ball_x + 2, ball_y)
        glEnd()

        # Draw ball with basic shading
        draw_circle(ball_x, ball_y, ball_radius, 0.75, 0.8, 0.85)

    glutSwapBuffers()

def idle():
    update_physics()
    glutPostRedisplay()

def mouse(button, state, x, y):
    global dragging_ball_index
    y_gl = HEIGHT - y
    
    positions = get_ball_positions()
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            for i in range(num_balls):
                bx, by = positions[i]
                if math.hypot(x - bx, y_gl - by) < ball_radius + 12:
                    dragging_ball_index = i
                    velocities[i] = 0.0
                    break
        elif state == GLUT_UP:
            dragging_ball_index = -1

def motion(x, y):
    global angles, dragging_ball_index
    if dragging_ball_index != -1:
        y_gl = HEIGHT - y
        pivot_x = start_x + (dragging_ball_index * spacing)
        
        dx = x - pivot_x
        dy = pivot_y - y_gl
        
        new_angle = math.atan2(dx, dy)
        angles[dragging_ball_index] = max(-1.2, min(1.2, new_angle))
        velocities[dragging_ball_index] = 0.0

def init():
    glViewport(0, 0, WIDTH, HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WIDTH, 0, HEIGHT, 0, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Blending enabled as taught in basic graphics
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# --- Main Program Execution ---
glutInit()

glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(WIDTH, HEIGHT)
glutInitWindowPosition(200, 30)
glutCreateWindow(b"Interactive 2D Newton Cradle")

init()

glutDisplayFunc(display)

glutMouseFunc(mouse)
glutMotionFunc(motion)
glutIdleFunc(idle)

glutMainLoop()