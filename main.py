import tkinter as tk
from datetime import datetime, timedelta
import math
from data import digit_0, digit_1, digit_2, digit_3, digit_4, digit_5, digit_6, digit_7, digit_8, digit_9
from settings import rad, dia, line_length, line_width, dot_rad, wn, canvas, canvas_width, canvas_height, x_adj, y_adj, sp, hand_colour
from settings import rotation_speed_hour, rotation_speed_minute, num_rotations_minute, num_rotations_hour, c_shdw_off, b_shdw_off, border, ani_speed
# from test import rotate_line, stop_rotation

# from time_functions import time_values, hand_directions, time_plot
# from animation_functions import animated_hands


current_function = 1
# animation_start_time = None

def grid_centres(): 
    """
    Outputs a tuple of tuple pairs containing centre point of circles and hands
    """
    coord_tuple = ()
    #Calculate start coordindate tuple
    for x in range(8):
        for y in range(3):
            coord_tuple += (((x * dia) + rad + (x * sp) + x_adj, (y * dia) + rad + (y * sp) + y_adj,),) 
    return coord_tuple


def background():
    """
    Draws background
    """
    # Remove canvas outline
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, 
                            fill="white", width=3, outline="white")
    
    # Box shadow
    canvas.create_rectangle(grid[0][0] - rad - border - b_shdw_off, grid[0][1] - rad - border + b_shdw_off, 
                            grid[23][0] + rad + border - b_shdw_off, grid[23][1] + rad + border + b_shdw_off, 
                            outline="light grey", fill="light grey", width=1)
    
    # Box shadow triangles
    canvas.create_polygon(grid[0][0] - rad - border - b_shdw_off, grid[0][1] - rad - border + b_shdw_off,
                          grid[0][0] - rad - border, grid[0][1] - rad - border,
                          grid[0][0] - rad - border, grid[0][1] - rad - border + b_shdw_off, 
                          outline="light grey", fill="light grey", width=1)
    canvas.create_polygon(grid[23][0] + rad + border - b_shdw_off, grid[23][1] + rad + border + b_shdw_off,
                          grid[23][0] + rad + border, grid[23][1] + rad + border,
                          grid[23][0] + rad + border - b_shdw_off, grid[23][1] + rad + border,
                          outline="light grey", fill="light grey", width=1)

    # Box 
    canvas.create_rectangle(grid[0][0] - rad - border, grid[0][1] - rad - border, 
                            grid[23][0] + rad + border, grid[23][1] + rad + border, 
                            outline="light grey", fill="#FAFAFA") 

    # Clock faces
    for x, y in grid_centres():
        x1 = (x + rad) 
        y1 = (y + rad) 
        white_circles = canvas.create_oval(x - rad - c_shdw_off, y - rad + c_shdw_off, 
                                           x1 - c_shdw_off, y1 + c_shdw_off, width= 0.5, 
                                          outline="light grey", fill="#F0F0F0")
        grey_circles = canvas.create_oval(x - rad, y - rad, 
                                         x1, y1, width= 5, 
                                         outline="light grey", fill="light grey")
        # Setting layering order for clock shadow
        canvas.tag_lower(grey_circles, white_circles)
        
    # Centre dots
    for x, y in grid_centres():
        x1 = (x + dot_rad)
        y1 = (y + dot_rad)
        canvas.create_oval(x - dot_rad, y - dot_rad, x1, y1, outline="black", fill=hand_colour)



def time_function():
    """
    Calculates current and future time, outputs a list of 2 lists of 4 elements
    [[c1, c2, c3, c4], [f1, f2, f3, f4]]
    """
    
    # Get the current time
    current_time = datetime.now()
    future_time = current_time + timedelta(minutes=1)
    # print(current_time)
    # print(future_time)

    # Extract the hours and minutes as integers
    hour_current = int(current_time.strftime("%H"))
    minute_current = int(current_time.strftime("%M"))
    hour_future = int(future_time.strftime("%H"))
    minute_future = int(future_time.strftime("%M"))

    # Split hours and minutes into two digits for each, adding a 0 if 9 or lower    
    # Current time
    if hour_current <= 9:
        hour_str_current = '0' + str(hour_current)
    else:
        hour_str_current = str(hour_current)
    if minute_current <= 9:
        minute_str_current = '0' + str(minute_current)
    else:
        minute_str_current = str(minute_current)

    # Future time
    if hour_future <= 9:
        hour_str_future = '0' + str(hour_future)
    else:
        hour_str_future = str(hour_future)
    if minute_future <= 9:
        minute_str_future = '0' + str(minute_future)
    else:
        minute_str_future = str(minute_future)

    hour_digit_1_current = int(hour_str_current[0])
    hour_digit_2_current = int(hour_str_current[1])
    minute_digit_1_current = int(minute_str_current[0])
    minute_digit_2_current = int(minute_str_current[1])

    hour_digit_1_future = int(hour_str_future[0])
    hour_digit_2_future = int(hour_str_future[1])
    minute_digit_1_future = int(minute_str_future[0])
    minute_digit_2_future = int(minute_str_future[1])

    time_digits = [[hour_digit_1_current, hour_digit_2_current, minute_digit_1_current, minute_digit_2_current], 
                   [hour_digit_1_future, hour_digit_2_future, minute_digit_1_future, minute_digit_2_future]]

    return time_digits


def hand_angles(time_values):
    """
    Outputs a list of pairs (hour hand and minute hand) with the angles for each clock
    for current and future time
    """
    
    #tuple to map time digits to angles
    digits = ((0, digit_0), (1, digit_1), (2, digit_2), (3, digit_3), (4, digit_4), (5, digit_5),
              (6, digit_6), (7, digit_7), (8, digit_8), (9, digit_9))

    hours_current_1 = digits[time_values[0][0]]
    hours_current_2 = digits[time_values[0][1]]
    minutes_current_1 = digits[time_values[0][2]]
    minutes_current_2 = digits[time_values[0][3]]

    hours_future_1 = digits[time_values[1][0]]
    hours_future_2 = digits[time_values[1][1]]
    minutes_future_1 = digits[time_values[1][2]]
    minutes_future_2 = digits[time_values[1][3]]

    #Build the tuple
    result_hand_angles_current_tuple = (hours_current_1, hours_current_2, minutes_current_1, minutes_current_2) 
    result_hand_angles_future_tuple = (hours_future_1, hours_future_2, minutes_future_1, minutes_future_2)
    result_hand_angles_tuple = ((result_hand_angles_current_tuple), (result_hand_angles_future_tuple))
    # print(f"This: {result_hand_angles_tuple}")
    # Remove the time digit from the tuple and start list conversion
    result_hand_angles_int = [list(pair[1]) for group in result_hand_angles_tuple for pair in group]
    # print(f"Hello: {result_hand_angles_int}")
    # Fully convert to a list
    result_hand_angles_a = [list(pair) for group in result_hand_angles_int for pair in group]
    global hand_angles_current
    hand_angles_current = result_hand_angles_a[:24]
    global hour_angle_current
    hour_angle_current = [pair[0] for pair in hand_angles_current]
    global minute_angle_current
    minute_angle_current = [pair[1] for pair in hand_angles_current]
    global hand_angles_future
    hand_angles_future = result_hand_angles_a[24:]
    global hour_angle_future
    hour_angle_future = [pair[0] for pair in hand_angles_future]
    global minute_angle_future
    minute_angle_future = [pair[1] for pair in hand_angles_future]
    result_hand_angles = [hand_angles_current,hand_angles_future]

    return result_hand_angles


def plot_current_hour():
    """
    Plots current hour hands
    """
    # canvas.delete("line")  # Clear previous lines
    canvas.delete("line_rotate_hour")
    # start_coordinates = grid_centres()
    combined_list = [[pair[0], pair[1], angle] for pair, angle in zip(grid, hour_angle_current)]
    for a,b,c in combined_list:
        end_hour_x = a + math.sin(math.radians(c)) * line_length
        end_hour_y = b + math.cos(math.radians(c)) * line_length
        canvas.create_line(a, b, end_hour_x, end_hour_y, 
                           tags="line_time_hour", width=line_width, fill=hand_colour)

def plot_current_minute():
    """
    Plots current minute hands
    """
    # canvas.delete("line")  # Clear previous lines
    canvas.delete("line_rotate_minute")
    # start_coordinates = grid_centres()
    combined_list = [[pair[0], pair[1], angle] for pair, angle in zip(grid, minute_angle_current)]
    for a,b,c in combined_list:
        end_hour_x = a + math.sin(math.radians(c)) * line_length
        end_hour_y = b + math.cos(math.radians(c)) * line_length
        canvas.create_line(a, b, end_hour_x, end_hour_y, 
                           tags="line_time_minute", width=line_width, fill=hand_colour)
        


def num_moves():
    """
    Calculate the number of moves each hand must make to get from
    current to future positions
    """
    global num_moves_hour 
    global num_moves_minute
    
    num_moves_hour = [math.floor((((start_angle - end_angle) + (360 * num_rotations_hour)) / rotation_speed_hour) + 1) 
                      for start_angle, end_angle in zip(hour_angle_current, hour_angle_future)]
    
    num_moves_minute = [math.floor((((start_angle - end_angle) + (360 * num_rotations_minute)) / rotation_speed_minute) + 1) 
                    for start_angle, end_angle in zip(minute_angle_current, minute_angle_future)]

    # print(f"num moves hour: {num_moves_hour}")
    # print(f"num moves minute: {num_moves_minute}")

def rotate_hours():
    for i, (start_angle, end_angle) in enumerate(zip(hour_angle_current, hour_angle_future)):
        rotate_hour(start_angle, end_angle, grid[i], 0, num_moves_hour[i], i)

# Function to rotate minute lines
def rotate_minutes():
    for i, (start_angle, end_angle) in enumerate(zip(minute_angle_current, minute_angle_future)):
        rotate_minute(start_angle, end_angle, grid[i], 0, num_moves_minute[i], i)

# Function to rotate hour line
def rotate_hour(start_angle, end_angle, center, count, move_count, index):
    if count < move_count:
        canvas.delete(f"line_rotate_hour_{index}")  # Clear previous line
        end_x = center[0] + math.sin(math.radians(start_angle)) * line_length
        end_y = center[1] + math.cos(math.radians(start_angle)) * line_length
        canvas.create_line(center[0], center[1], end_x, end_y, tags=f"line_rotate_hour_{index}", width=line_width, fill=hand_colour)
        new_angle = (start_angle - rotation_speed_hour) % 360
        wn.after(ani_speed, rotate_hour, new_angle, end_angle, center, count + 1, move_count, index)

# Function to rotate minute line
def rotate_minute(start_angle, end_angle, center, count, move_count, index):
    if count < move_count:
        canvas.delete(f"line_rotate_minute_{index}")  # Clear previous line
        end_x = center[0] + math.sin(math.radians(start_angle)) * line_length
        end_y = center[1] + math.cos(math.radians(start_angle)) * line_length
        canvas.create_line(center[0], center[1], end_x, end_y, tags=f"line_rotate_minute_{index}", width=line_width, fill=hand_colour)
        new_angle = (start_angle - rotation_speed_minute) % 360
        wn.after(ani_speed, rotate_minute, new_angle, end_angle, center, count + 1, move_count, index)

# Start the rotation

def animation():
    # canvas.delete("line_time_hour")
    # canvas.delete("line_time_minute")
    rotate_hours()
    rotate_minutes()
    canvas.after(55000, update_canvas)

def update_time():
    # canvas.delete("line_rotate_hour_{index}")
    # canvas.delete("line_rotate_minute_{index}")
    
    hand_angles(time_function())
    num_moves()
    plot_current_hour()
    plot_current_minute()
    canvas.after(5000, update_canvas)



def update_canvas():
    global current_function
    if current_function == 1: 
        update_time()
        current_function = 2
    else:
        canvas.delete("line_time_hour")
        canvas.delete("line_time_minute")
        animation()
        current_function = 1  



time_function_result = time_function()
hand_angles_result = hand_angles(time_function_result)
grid = grid_centres()
print(f"grid = {grid}")
# print()
# print(time_function())
# print(f"hour_angle_current: {hour_angle_current}")
# print()
# print(f"minute_angle_current: {minute_angle_current}")
# print()
# print(f"hour_angle_future: {hour_angle_future}")
# print()
# print(f"minute_angle_future: {minute_angle_future}")

background()
update_canvas()

wn.mainloop()