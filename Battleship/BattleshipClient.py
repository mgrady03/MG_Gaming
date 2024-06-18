'''import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

class BattleshipClient:
    def __init__(self, root, mode, host='localhost', port=12345):
        self.root = root
        self.root.title("Battleship Client")
        self.board_size = 10
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.player_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.computer_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.player_ships = sum(self.ship_sizes)
        self.computer_ships = sum(self.ship_sizes)
        self.setup_phase = True
        self.selected_ship_size = None
        self.orientation = 'H'
        self.mode = mode
        self.load_images()
        self.create_widgets()
        if self.mode == "Computer":
            self.place_ships_randomly(self.computer_board)
        self.turn = "Player"
        if self.mode == "Network":
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

    def load_images(self):
        self.images = {
            "water": tk.PhotoImage(file="water.png"),
            "ship": tk.PhotoImage(file="ship.png"),
            "hit": tk.PhotoImage(file="hit.png"),
            "miss": tk.PhotoImage(file="miss.png"),
            "explosion": [tk.PhotoImage(file="explosion.gif", format=f"gif -index {i}") for i in range(5)]
        }

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="Place your ships", font='Helvetica 12 bold')
        self.status_label.pack()

        self.orientation_button = tk.Button(self.root, text="Orientation: Horizontal", command=self.toggle_orientation)
        self.orientation_button.pack()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.LEFT, padx=10)

        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(side=tk.RIGHT, padx=10)

        self.top_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                button = tk.Button(self.top_frame, image=self.images["water"], command=lambda i=i, j=j: self.on_attack_click(i, j))
                button.grid(row=i, column=j, padx=1, pady=1)
                row.append(button)
            self.top_buttons.append(row)

        self.bottom_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                button = tk.Button(self.bottom_frame, image=self.images["water"], command=lambda i=i, j=j: self.on_place_click(i, j))
                button.grid(row=i, column=j, padx=1, pady=1)
                row.append(button)
            self.bottom_buttons.append(row)

        self.ship_selection_frame = tk.Frame(self.root)
        self.ship_selection_frame.pack()

        self.ship_buttons = []
        for size in self.ship_sizes:
            button = tk.Button(self.ship_selection_frame, text=f"Ship {size}", command=lambda size=size: self.select_ship(size))
            button.pack(side=tk.LEFT)
            self.ship_buttons.append(button)

    def toggle_orientation(self):
        self.orientation = 'V' if self.orientation == 'H' else 'H'
        self.orientation_button.config(text=f"Orientation: {'Vertical' if self.orientation == 'V' else 'Horizontal'}")

    def select_ship(self, size):
        self.selected_ship_size = size
        self.status_label.config(text=f"Placing ship of size {size}")

    def on_place_click(self, i, j):
        if self.setup_phase:
            if self.selected_ship_size and self.can_place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation):
                self.place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation)
                if self.orientation == 'H':
                    for k in range(self.selected_ship_size):
                        self.bottom_buttons[i][j + k].config(image=self.images["ship"])
                else:
                    for k in range(self.selected_ship_size):
                        self.bottom_buttons[i + k][j].config(image=self.images["ship"])
                self.ship_sizes.remove(self.selected_ship_size)
                if not self.ship_sizes:
                    self.setup_phase = False
                    for btn in self.ship_buttons:
                        btn.config(state=tk.DISABLED)
                    self.status_label.config(text="Your turn")
                self.selected_ship_size = None
            else:
                messagebox.showerror("Error", "Invalid placement")

    def on_attack_click(self, i, j):
        if not self.setup_phase and self.turn == "Player":
            if self.mode == "Network":
                self.send_message(f"ATTACK {i} {j}")
            else:
                self.process_attack(i, j)

    def process_attack(self, i, j):
        if self.computer_board[i][j] == "S":
            self.top_buttons[i][j].config(image=self.images["explosion"][0])
            self.animate_explosion(i, j)
            self.computer_board[i][j] = "X"
            self.computer_ships -= 1
            if self.computer_ships == 0:
                messagebox.showinfo("Battleship", "You win")
                self.reset_game()
        elif self.computer_board[i][j] == "":
            self.top_buttons[i][j].config(image=self.images["miss"])
            self.computer_board[i][j] = "O"
            if self.mode == "Computer":
                self.turn = "Computer"
                self.status_label.config(text="Computer's turn")
                self.root.after(1000, self.computer_turn)

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                print("Received:", message)
                if message.startswith("ATTACK"):
                    parts = message.split()
                    i, j = int(parts[1]), int(parts[2])
                    self.process_attack(i, j)
                elif message.startswith("HIT") or message.startswith("MISS"):
                    parts = message.split()
                    action = parts[0]
                    i, j = int(parts[1]), int(parts[2])
                    if action == "HIT":
                        self.top_buttons[i][j].config(image=self.images["hit"])
                    elif action == "MISS":
                        self.top_buttons[i][j].config(image=self.images["miss"])
            except ConnectionResetError:
                break

    def animate_explosion(self, i, j, frame=0):
        if frame < len(self.images["explosion"]):
            self.top_buttons[i][j].config(image=self.images["explosion"][frame])
            self.root.after(100, self.animate_explosion, i, j, frame + 1)
        else:
            self.top_buttons[i][j].config(image=self.images["hit"])

    def can_place_ship(self, board, x, y, size, direction):
        if direction == 'H':
            if y + size > self.board_size:
                return False
            for i in range(size):
                if board[x][y + i] != "":
                    return False
        else:
            if x + size > self.board_size:
                return False
            for i in range(size):
                if board[x + i][y] != "":
                    return False
        return True

    def place_ship(self, board, x, y, size, direction):
        if direction == 'H':
            for i in range(size):
                board[x][y + i] = "S"
        else:
            for i in range(size):
                board[x + i][y] = "S"

    def computer_turn(self):
        while self.turn == "Computer":
            x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if self.player_board[x][y] == "S":
                self.player_board[x][y] = "X"
                self.player_ships -= 1
                self.bottom_buttons[x][y].config(image=self.images["hit"])
                if self.player_ships == 0:
                    messagebox.showinfo("Battleship", "Computer wins")
                    self.reset_game()
                break
            elif self.player_board[x][y] == "":
                self.player_board[x][y] = "O"
                self.bottom_buttons[x][y].config(image=self.images["miss"])
                break
        self.turn = "Player"
        self.status_label.config(text="Your turn")

    def reset_game(self):
        self.player_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.computer_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.player_ships = sum(self.ship_sizes)
        self.computer_ships = sum(self.ship_sizes)
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.top_buttons[i][j].config(image=self.images["water"])
                self.bottom_buttons[i][j].config(image=self.images["water"])
        if self.mode == "Computer":
            self.place_ships_randomly(self.computer_board)
        self.setup_phase = True
        for btn in self.ship_buttons:
            btn.config(state=tk.NORMAL)
        self.status_label.config(text="Place your ships")
        self.turn = "Player"

    def place_ships_randomly(self, board):
        for size in self.ship_sizes:
            placed = False
            while not placed:
                direction = random.choice(['H', 'V'])
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.can_place_ship(board, x, y, size, direction):
                    self.place_ship(board, x, y, size, direction)
                    placed = True

def start_game(mode):
    root = tk.Tk()
    client = BattleshipClient(root, mode)
    root.mainloop()

def show_menu():
    menu_root = tk.Tk()
    menu_root.title("Battleship Menu")

    tk.Label(menu_root, text="Choose Game Mode", font='Helvetica 12 bold').pack(pady=10)

    tk.Button(menu_root, text="Play vs Computer", command=lambda: (menu_root.destroy(), start_game("Computer"))).pack(pady=5)
    tk.Button(menu_root, text="Play 1v1 Network Game", command=lambda: (menu_root.destroy(), start_game("Network"))).pack(pady=5)

    menu_root.mainloop()

if __name__ == "__main__":
    show_menu()'''

import tkinter as tk
from tkinter import messagebox
import socket
import threading
import random

class BattleshipClient:
    def __init__(self, root, mode, host='localhost', port=12345):
        self.root = root
        self.root.title("Battleship Client")
        self.board_size = 10
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.player_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.opponent_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.player_ships = sum(self.ship_sizes)
        self.opponent_ships = sum(self.ship_sizes)
        self.setup_phase = True
        self.selected_ship_size = None
        self.orientation = 'H'
        self.mode = mode
        self.load_images()
        self.create_widgets()
        if self.mode == "Computer":
            self.place_ships_randomly(self.opponent_board)
        self.turn = "Player"
        if self.mode == "Network":
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

    def load_images(self):
        self.images = {
            "water": tk.PhotoImage(file="water.png"),
            "ship": tk.PhotoImage(file="ship.png"),
            "hit": tk.PhotoImage(file="hit.png"),
            "miss": tk.PhotoImage(file="miss.png"),
            "explosion": [tk.PhotoImage(file="explosion.gif", format=f"gif -index {i}") for i in range(5)]
        }

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="Place your ships", font='Helvetica 12 bold')
        self.status_label.pack()

        self.orientation_button = tk.Button(self.root, text="Orientation: Horizontal", command=self.toggle_orientation)
        self.orientation_button.pack()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.LEFT, padx=10)

        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(side=tk.RIGHT, padx=10)

        self.top_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                button = tk.Button(self.top_frame, image=self.images["water"], command=lambda i=i, j=j: self.on_attack_click(i, j))
                button.grid(row=i, column=j, padx=1, pady=1)
                row.append(button)
            self.top_buttons.append(row)

        self.bottom_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                button = tk.Button(self.bottom_frame, image=self.images["water"], command=lambda i=i, j=j: self.on_place_click(i, j))
                button.grid(row=i, column=j, padx=1, pady=1)
                row.append(button)
            self.bottom_buttons.append(row)

        self.ship_selection_frame = tk.Frame(self.root)
        self.ship_selection_frame.pack()

        self.ship_buttons = []
        for size in self.ship_sizes:
            button = tk.Button(self.ship_selection_frame, text=f"Ship {size}", command=lambda size=size: self.select_ship(size))
            button.pack(side=tk.LEFT)
            self.ship_buttons.append(button)

    def toggle_orientation(self):
        self.orientation = 'V' if self.orientation == 'H' else 'H'
        self.orientation_button.config(text=f"Orientation: {'Vertical' if self.orientation == 'V' else 'Horizontal'}")

    def select_ship(self, size):
        self.selected_ship_size = size
        self.status_label.config(text=f"Placing ship of size {size}")

    def on_place_click(self, i, j):
        if self.setup_phase:
            if self.selected_ship_size and self.can_place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation):
                self.place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation)
                if self.orientation == 'H':
                    for k in range(self.selected_ship_size):
                        self.bottom_buttons[i][j + k].config(image=self.images["ship"])
                else:
                    for k in range(self.selected_ship_size):
                        self.bottom_buttons[i + k][j].config(image=self.images["ship"])
                self.ship_sizes.remove(self.selected_ship_size)
                if not self.ship_sizes:
                    self.setup_phase = False
                    for btn in self.ship_buttons:
                        btn.config(state=tk.DISABLED)
                    self.status_label.config(text="Your turn")
                self.selected_ship_size = None
            else:
                messagebox.showerror("Error", "Invalid placement")

    def on_attack_click(self, i, j):
        if not self.setup_phase and self.turn == "Player":
            if self.mode == "Network":
                self.send_message(f"ATTACK {i} {j}")
            else:
                self.process_attack(i, j, self.opponent_board, self.top_buttons)

    def process_attack(self, i, j, board, buttons):
        if board[i][j] == "S":
            buttons[i][j].config(image=self.images["explosion"][0])
            self.animate_explosion(i, j, buttons)
            board[i][j] = "X"
            if board == self.opponent_board:
                self.opponent_ships -= 1
                if self.opponent_ships == 0:
                    messagebox.showinfo("Battleship", "You win")
                    self.reset_game()
        elif board[i][j] == "":
            buttons[i][j].config(image=self.images["miss"])
            board[i][j] = "O"
            if self.mode == "Computer":
                self.turn = "Computer"
                self.status_label.config(text="Computer's turn")
                self.root.after(1000, self.computer_turn)

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                print("Received:", message)
                if message.startswith("ATTACK"):
                    parts = message.split()
                    i, j = int(parts[1]), int(parts[2])
                    self.process_attack(i, j, self.player_board, self.bottom_buttons)
                    self.send_message(f"RESULT {i} {j} {'HIT' if self.player_board[i][j] == 'X' else 'MISS'}")
                elif message.startswith("RESULT"):
                    parts = message.split()
                    i, j = int(parts[1]), int(parts[2])
                    result = parts[3]
                    if result == "HIT":
                        self.top_buttons[i][j].config(image=self.images["hit"])
                    elif result == "MISS":
                        self.top_buttons[i][j].config(image=self.images["miss"])
                    self.turn = "Player"
                    self.status_label.config(text="Your turn")
            except ConnectionResetError:
                break

    def animate_explosion(self, i, j, buttons, frame=0):
        if frame < len(self.images["explosion"]):
            buttons[i][j].config(image=self.images["explosion"][frame])
            self.root.after(100, self.animate_explosion, i, j, buttons, frame + 1)
        else:
            buttons[i][j].config(image=self.images["hit"])

    def can_place_ship(self, board, x, y, size, direction):
        if direction == 'H':
            if y + size > self.board_size:
                return False
            for i in range(size):
                if board[x][y + i] != "":
                    return False
        else:
            if x + size > self.board_size:
                return False
            for i in range(size):
                if board[x + i][y] != "":
                    return False
        return True

    def place_ship(self, board, x, y, size, direction):
        if direction == 'H':
            for i in range(size):
                board[x][y + i] = "S"
        else:
            for i in range(size):
                board[x + i][y] = "S"

    def computer_turn(self):
        while self.turn == "Computer":
            x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if self.player_board[x][y] == "S":
                self.player_board[x][y] = "X"
                self.player_ships -= 1
                self.bottom_buttons[x][y].config(image=self.images["hit"])
                if self.player_ships == 0:
                    messagebox.showinfo("Battleship", "Computer wins")
                    self.reset_game()
                break
            elif self.player_board[x][y] == "":
                self.player_board[x][y] = "O"
                self.bottom_buttons[x][y].config(image=self.images["miss"])
                break
        self.turn = "Player"
        self.status_label.config(text="Your turn")

    def reset_game(self):
        self.player_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.opponent_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.player_ships = sum(self.ship_sizes)
        self.opponent_ships = sum(self.ship_sizes)
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.top_buttons[i][j].config(image=self.images["water"])
                self.bottom_buttons[i][j].config(image=self.images["water"])
        if self.mode == "Computer":
            self.place_ships_randomly(self.opponent_board)
        self.setup_phase = True
        for btn in self.ship_buttons:
            btn.config(state=tk.NORMAL)
        self.status_label.config(text="Place your ships")
        self.turn = "Player"

    def place_ships_randomly(self, board):
        for size in self.ship_sizes:
            placed = False
            while not placed:
                direction = random.choice(['H', 'V'])
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.can_place_ship(board, x, y, size, direction):
                    self.place_ship(board, x, y, size, direction)
                    placed = True

def start_game(mode):
    root = tk.Tk()
    client = BattleshipClient(root, mode)
    root.mainloop()

def show_menu():
    menu_root = tk.Tk()
    menu_root.title("Battleship Menu")

    tk.Label(menu_root, text="Choose Game Mode", font='Helvetica 12 bold').pack(pady=10)

    tk.Button(menu_root, text="Play vs Computer", command=lambda: (menu_root.destroy(), start_game("Computer"))).pack(pady=5)
    tk.Button(menu_root, text="Play 1v1 Network Game", command=lambda: (menu_root.destroy(), start_game("Network"))).pack(pady=5)

    menu_root.mainloop()

if __name__ == "__main__":
    show_menu()

