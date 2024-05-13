# Create main window
import tkinter as tk
wn = tk.Tk()
wn.title("ClockClock24")
wn.configure(bg="white")
# wn.state('zoomed')
wn.attributes('-fullscreen', True)


# Set screen dimensions
screen_width = 1600
screen_height = 1200

# Set window size
window_width = screen_width
window_height = screen_height 

# Set window position to center
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set window size and position
wn.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Set the canvas dimensions
canvas_width = (1 * window_width)
canvas_height = (1 * window_height)

# Create a canvas 
canvas = tk.Canvas(wn, width=canvas_width, height=canvas_height)
canvas.place(relx = 0.5, rely = 0.5, anchor=tk.CENTER)
canvas.configure(bg="white")

# Define clock radius:
rad = 70
# Define clock diameter
dia = rad * 2
# Define spacing between clocks
sp = 0.15 * rad
# Define length of clock hand
line_length = rad * 0.99
line_width = 10

# Define hand colour
hand_colour = "#282828"

# Border around clock grid
border = 0.5 * rad

# Box shadow offset
b_shdw_off = 0.5 * rad

# Circle shadow offset
c_shdw_off = 0.06 * rad

#Center clocks on canvas
x_adj = (canvas_width - (8 * dia + 7 * sp)) / 2
y_adj = (canvas_height - (3 * dia + 2 * sp)) / 2

# Define dot radius
dot_rad = 4

# Define the rotation speed
rotation_speed_hour = 1  # Adjust the speed as needed
rotation_speed_minute = 0.5  # Adjust the speed as needed

# Set animate speed
ani_speed = 20 # lower is faster

# Define the number of rotations
num_rotations_hour = 1
num_rotations_minute = 1





