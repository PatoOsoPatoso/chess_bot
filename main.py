from selenium.webdriver.common.by import By
from stockfish import Stockfish
from selenium import webdriver
from PIL import ImageTk, Image
from getpass import getuser
import threading
import chess.svg
import tkinter
import chess
import os

# Here we define some variables that are different in windows and linux
if os.name == 'nt':
    # Dirty fix to use cairo in windows, you can modify your enviroment variables as usual and import it at the top
    os.environ['path'] += r';C:\Program Files\UniConvertor-2.0rc5\dlls'
    separator = "\\"
    user_data_dir = rf'--user-data-dir=C:\Users\{getuser()}\AppData\Local\Google\Chrome\User Data'
else:
    separator = "/"
    user_data_dir = f"--user-data-dir=/home/{getuser()}/.config/google-chrome"

# We import cairosvg here because we needed to set the enviroment variable for the dlls path
from cairosvg import svg2png

# We define the stockfish path to our current working directory
stockfish_path = separator.join(__file__.split(separator)[:-1]) + f'{separator}stockfish'

# Create Stockfish type element
stockfish = Stockfish(path=stockfish_path)

# Create our control variable to stop the thread
keep_going = bool

img = ''

# A function that recives a svg image as code and updates the tkinter label to show it
def update_image(svgcode):
    global img
    # Here we convert our svg code into a png image for tkinter
    svg2png(bytestring=svgcode, write_to='current.png')
    img = Image.open("current.png")
    resized = img.resize((root.winfo_width(), root.winfo_height() - 50), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(resized)

    canvas.create_image(0, 50, image=img, anchor='nw')

# A function that removes the image from the label
def remove_image():
    try:
        canvas.delete(img)
        img = ''
        canvas.create_image(0, 50, image=img, anchor='nw')
    except:
        pass

# A class named web with a threading type to execute selenium into a thread
class web(threading.Thread):
    # A control variable to stop the thread

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global keep_going

        # This is a variable to flip the board in case we are playing as black
        flip = False

        # Set our control variable as True
        keep_going = True

        options = webdriver.ChromeOptions()

        # Now we set the Chrome user data dir to have persistence and don't have to log in every time
        options.add_argument(user_data_dir)

        driver = webdriver.Chrome(options=options)

        # Those XPATHs go to the white and black moves into the scoreboard
        white_xpath = '//*[@id="move-list"]/vertical-move-list/div[{}]/div[1]'
        black_xpath = '//*[@id="move-list"]/vertical-move-list/div[{}]/div[3]'

        # Now we define some variables to keep information about the moves and the board
        board = chess.Board()
        old_num_moves = 0
        old_moves = []

        # while loop with our control variable
        while keep_going:
            # Auxiliar vairables for the moves
            white_moves = []
            black_moves = []
            new_moves = []

            # This checks everytime if the game has ended
            end_check1 = driver.find_elements(By.CLASS_NAME, 'game-over-modal-content')
            end_check2 = driver.find_elements(By.CLASS_NAME, 'game-review-overlay-overlay')

            # If there is an element inside end_check we reset everything and remove our image
            if end_check1 or end_check2:
                board = chess.Board()
                old_num_moves = 0
                old_moves = []
                remove_image()
                continue

            # We select now all the moves, inside every move there is a white move and a black move
            moves = driver.find_elements(By.CLASS_NAME, 'move')

            # If we don't find moves is because there is no game, so we go to the next iteration and reset everything just in case
            if not moves:
                board = chess.Board()
                old_num_moves = 0
                old_moves = []
                remove_image()
                continue

            # We try to access the lower clock and we check if it's white or black to flip the board in case we are black
            side = driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div[4]')
            if 'black' in side.get_attribute("class"):
                flip = True

            # Now we iterate every move to get the white and black ones
            for i in range(len(moves)):
                # We use this try except to catch the possible error in case the white player has made his move but the black one hasn't
                try:
                    white_moves.append(driver.find_element(By.XPATH, white_xpath.format(i+1)).text)
                    black_moves.append(driver.find_element(By.XPATH, black_xpath.format(i+1)).text)
                except:
                    pass
            
            # This is the count of the total moves in the game so far
            new_num_moves = len(white_moves) + len(black_moves)

            # If the new count is equal or lower(just in case) we continue with the next iteration
            if new_num_moves <= old_num_moves:
                continue

            # If there are new moves we update our old moves
            old_num_moves = new_num_moves

            # Now we add one white move and one black move one after the other inside new_moves
            new_moves = white_moves
            for i, j in enumerate(black_moves):
                new_moves.insert(2 * i + 1, j)
            
            # The actual new moves that happened since the last iteration are the real_new_moves
            real_new_moves = new_moves[len(old_moves):]

            # If there are not new moves we continue with the next iteration (shouldn't happend, but in case I'm wrong)
            if not real_new_moves:
                continue

            # Now we update our old_moves
            old_moves = new_moves

            # We iterate every real move to push it as san into our board object
            for move in real_new_moves:
                # Sometimes an empty string slides into the list, didn't figure this out yet, but this prevents it
                if move:
                    try:
                        board.push_san(move)
                    except:
                        board = chess.Board()
                        old_num_moves = 0
                        old_moves = []
                        remove_image()
                        continue

            # Now we get the fen
            fen = board.fen()

            # We give the fen to stockfish
            stockfish.set_fen_position(fen)

            # Nos we check if we played our turn yet or we didn't, in case is our rival's turn, we don't want to calculate the moves, is not necessary
            calculate = False
            if flip:
                if (len(new_moves) % 2) != 0:
                    calculate = True
            else:
                if (len(new_moves) % 2) == 0:
                    calculate = True

            # We create an empty set of arrows to draw
            arrow_moves = []

            # If we have to calculate our next moves
            if calculate:
                # We get the top 3 best moves from stockfish and we sort them by the Centipawn score
                best_moves = stockfish.get_top_moves(3)

                # This is a list of colors, green is the best posible move, blue is the second best and red is the third best move
                colors = ['green', 'blue', 'red']

                # Now we put from 1 to 3 Arrow objects with his respective moves and colors inside arrow_moves
                for i, best_move in enumerate(best_moves):
                    arrow_moves.append(chess.svg.Arrow(chess.parse_square(best_move['Move'][:2]), chess.parse_square(best_move['Move'][2:]), color=colors[i]))
            
            # Now we generate the svg code of the board
            boardsvg = chess.svg.board(board=board, arrows=arrow_moves, size=1920, flipped=flip)

            # Now we update our image
            update_image(boardsvg)
        
        # After we set to False our control variable we close the driver
        driver.close()

th = None

# A function to start our automated chrome inside a thread as a deamon
def button_start():
    global th

    th = web()
    th.daemon = True
    th.start()

# A function to stop our thread changing the value of our control variable
def button_stop():
    global th, keep_going

    keep_going = False
    th.join(0.1)

# A function to stop our thread and exit the program after
def button_exit():
    global th, keep_going

    keep_going = False
    th.join(0.1)
    exit()

# A function to move the window with left click
def move(_):
    x, y = root.winfo_pointerxy()
    root.geometry(f"+{x-(root.winfo_width() // 2)}+{y-(root.winfo_height() // 2)}")

# The root of our tkinter application
root = tkinter.Tk('Chess Bot - PatoOsoPatoso')

root.geometry("300x350")

# The canvas that is going to contain the buttons and the image
canvas = tkinter.Canvas(root, width=300, height=350)
canvas.pack(fill=tkinter.BOTH, expand=True)
canvas.bind("<B1-Motion>", move)

# First button
button1 = tkinter.Button(root, text="Start", command=button_start, anchor="center", cursor="hand2",bg='orange')
button1.configure(width=7, activebackground="#33B5E5", relief=tkinter.FLAT, padx=10)
button1_window = canvas.create_window(10, 10, anchor=tkinter.NW, window=button1)

# Second button
button2 = tkinter.Button(root, text="Stop", command=button_stop, anchor="center", cursor="hand2", bg='orange')
button2.configure(width=7, activebackground = "#33B5E5", relief=tkinter.FLAT, padx=10)
button2_window = canvas.create_window(110, 50, anchor=tkinter.NW, window=button2)

# Third button
button3 = tkinter.Button(root, text="Exit", command=button_exit, anchor="center", cursor="hand2", bg='orange')
button3.configure(width=7, activebackground = "#33B5E5", relief=tkinter.FLAT, padx=10)
button3_window = canvas.create_window(210, 100, anchor=tkinter.NW, window=button3)

# We create a "fake" non existing image
canvas.create_image(0, 50, image=img, anchor='nw')

# Function to resize the image and the buttons
def resize_image(e):
    global resized, img, button1, button2, button3, button1_window, button2_window, button3_window

    # If the height -50 is less than 0 there won't be any changes
    if e.height - 50 <= 0:
        return
    
    # We delete the previous image
    canvas.delete(img)

    # First we delete the windows created by the canvas
    canvas.delete(button1_window)
    canvas.delete(button2_window)
    canvas.delete(button3_window)

    # Then we configure the buttons to change it's width
    button1.configure(width=(e.width - 40) // 30)
    button2.configure(width=(e.width - 40) // 30)
    button3.configure(width=(e.width - 40) // 30)

    # Now we create new windows to contain our buttons with new x positions
    button1_window = canvas.create_window(10, 10, anchor=tkinter.NW, window=button1)
    button2_window = canvas.create_window(20 + (e.width - 40) // 3, 10, anchor=tkinter.NW, window=button2)
    button3_window = canvas.create_window(30 + 2 * ((e.width - 40) // 3), 10, anchor=tkinter.NW, window=button3)

    # If there is a new image
    if img != '':
        img = Image.open("current.png")
        resized = img.resize((e.width, e.height-50), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(resized)

    canvas.create_image(0, 50, image=img, anchor='nw')

root.protocol("WM_DELETE_WINDOW", root.destroy)

# Binding to resize the image and the buttons as the container is resized
root.bind("<Configure>", resize_image)

root.mainloop()