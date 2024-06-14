import tkinter as tk
from tkinter import messagebox
import random

class Battleship:
    def __init__(self, root):
        self.root = root
        self.root.title("Battleship")
        self.board_size = 10
        self.ship_sizes = [5, 4, 3, 3, 2]
        self.player_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.computer_board = [[""] * self.board_size for _ in range(self.board_size)]
        self.player_ships = sum(self.ship_sizes)
        self.computer_ships = sum(self.ship_sizes)
        self.setup_phase = True
        self.selected_ship_size = None
        self.orientation = 'H' 
        self.load_images()
        self.create_widgets()
        self.place_ships_randomly(self.computer_board)
        self.turn = "Player"

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

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                button = tk.Button(self.frame, image=self.images["water"], command=lambda i=i, j=j: self.on_button_click(i, j))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)

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

    def place_ships_randomly(self, board):
        for size in self.ship_sizes:
            placed = False
            while not placed:
                direction = random.choice(['H', 'V'])
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.can_place_ship(board, x, y, size, direction):
                    self.place_ship(board, x, y, size, direction)
                    placed = True

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

    def on_button_click(self, i, j):
        if self.setup_phase:
            if self.selected_ship_size and self.can_place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation):
                self.place_ship(self.player_board, i, j, self.selected_ship_size, self.orientation)
                if self.orientation == 'H':
                    for k in range(self.selected_ship_size):
                        self.buttons[i][j + k].config(image=self.images["ship"])
                else:
                    for k in range(self.selected_ship_size):
                        self.buttons[i + k][j].config(image=self.images["ship"])
                self.ship_sizes.remove(self.selected_ship_size)
                if not self.ship_sizes:
                    self.setup_phase = False
                    for btn in self.ship_buttons:
                        btn.config(state=tk.DISABLED)
                    self.status_label.config(text="Your turn")
                self.selected_ship_size = None
            else:
                messagebox.showerror("Error", "Invalid placement")
        else:
            if self.turn == "Player":
                if self.computer_board[i][j] == "S":
                    self.buttons[i][j].config(image=self.images["explosion"][0])
                    self.animate_explosion(i, j)
                    self.computer_board[i][j] = "X"
                    self.computer_ships -= 1
                    if self.computer_ships == 0:
                        messagebox.showinfo("Battleship", "You win")
                        self.reset_game()
                elif self.computer_board[i][j] == "":
                    self.buttons[i][j].config(image=self.images["miss"])
                    self.computer_board[i][j] = "O"
                    self.turn = "Computer"
                    self.status_label.config(text="Computer's turn")
                    self.root.after(1000, self.computer_turn)
                else:
                    messagebox.showerror("Error", "Already attacked this position")

    def animate_explosion(self, i, j, frame=0):
        if frame < len(self.images["explosion"]):
            self.buttons[i][j].config(image=self.images["explosion"][frame])
            self.root.after(100, self.animate_explosion, i, j, frame + 1)
        else:
            self.buttons[i][j].config(image=self.images["hit"])

    def computer_turn(self):
        while self.turn == "Computer":
            x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
            if self.player_board[x][y] == "S":
                self.player_board[x][y] = "X"
                self.player_ships -= 1
                self.buttons[x][y].config(image=self.images["hit"])
                if self.player_ships == 0:
                    messagebox.showinfo("Battleship", "Computer wins")
                    self.reset_game()
                break
            elif self.player_board[x][y] == "":
                self.player_board[x][y] = "O"
                self.buttons[x][y].config(image=self.images["miss"])
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
                self.buttons[i][j].config(image=self.images["water"])
        self.place_ships_randomly(self.computer_board)
        self.setup_phase = True
        for btn in self.ship_buttons:
            btn.config(state=tk.NORMAL)
        self.status_label.config(text="Place your ships")
        self.turn = "Player"

if __name__ == "__main__":
    root = tk.Tk()
    game = Battleship(root)
    root.mainloop()
