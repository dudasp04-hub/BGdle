import tkinter as tk
import random


class BGdleApp:
    CELL_SIZE = 100
    CELL_FONT = ("Arial", 9, "bold")

    def __init__(self, root):
        self.root = root
        self.root.title("BGdle")

        self.cards = self.load_cards("bg.txt")
        self.filtered_cards = []
        self.target = None
        self.guessed_names = set()
        self.header_visible = False

        self.create_menu()
        self.create_game_ui()

    # DATA
    def load_cards(self, filename):
        cards = []
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(";")

                    mode = parts[6].strip() if len(parts) > 6 else ""

                    card = {
                        "Name": parts[0],
                        "Tier": int(parts[1]),
                        "Tribe": [t.strip() for t in parts[2].split(",") if t.strip()],
                        "Attack": int(parts[3]),
                        "Health": int(parts[4]),
                        "Keywords": [k.strip() for k in parts[5].split(",") if k.strip()],
                        "Mode": mode
                    }
                    cards.append(card)
        return cards

    # MENU
    def create_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(fill="both", expand=True)

        tk.Label(self.menu_frame, text="BGdle", font=("Arial", 24, "bold")).pack(pady=20)

        tk.Button(
            self.menu_frame,
            text="Solo Mode",
            width=20,
            command=lambda: self.start_game(False)
        ).pack(pady=10)

        tk.Button(
            self.menu_frame,
            text="Include Duos",
            width=20,
            command=lambda: self.start_game(True)
        ).pack(pady=10)

    def start_game(self, include_duos):
        self.filtered_cards = [
            c for c in self.cards
            if include_duos or c["Mode"] != "Duos"
        ]

        if not self.filtered_cards:
            return

        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)

        self.new_game()

    # GAME UI
    def create_game_ui(self):
        self.game_frame = tk.Frame(self.root)

        # input
        self.top_frame = tk.Frame(self.game_frame)
        self.top_frame.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.top_frame, font=("Arial", 14), width=30)
        self.entry.pack(fill="x", ipady=6)
        self.entry.bind("<KeyRelease>", self.suggest)

        self.submit_btn = tk.Button(self.top_frame, text="Guess", command=self.check_guess)
        self.submit_btn.pack(pady=5)

        self.result_label = tk.Label(self.game_frame, text="", font=("Arial", 12))
        self.result_label.pack(pady=5)

        tk.Button(self.game_frame, text="Back to Menu", command=self.back_to_menu).pack(pady=5)

        # table
        self.table_container = tk.Frame(self.game_frame)
        self.table_container.pack(padx=10, pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(self.table_container, height=420)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.table_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.table_frame = tk.Frame(self.canvas)
        self.table_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor="n")

        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.center_table)

        self.table_frame.grid_columnconfigure(0, weight=1)

        self.autocomplete_list = None

    # GAME FLOW
    def new_game(self):
        self.target = random.choice(self.filtered_cards)
        self.guessed_names.clear()
        self.header_visible = False

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.result_label.config(text="")
        self.entry.delete(0, tk.END)
        self.submit_btn.config(text="Guess", command=self.check_guess)

    def back_to_menu(self):
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    # UI HELPERS
    def create_header(self):
        header_row = tk.Frame(self.table_frame)
        header_row.grid(row=0, column=0, pady=(0, 6))

        headers = ["Minion", "Tier", "Tribe", "Attack", "Health", "Keywords"]

        for col, text in enumerate(headers):
            cell = tk.Frame(header_row, width=self.CELL_SIZE, height=30, bg="#333", relief="solid", borderwidth=1)
            cell.grid(row=0, column=col, padx=2)
            cell.grid_propagate(False)

            tk.Label(cell, text=text, bg="#333", fg="white").place(relx=0.5, rely=0.5, anchor="center")

    def make_cell(self, parent, text, bg):
        cell = tk.Frame(parent, width=self.CELL_SIZE, height=self.CELL_SIZE, bg=bg, relief="solid", borderwidth=1)
        cell.grid_propagate(False)

        tk.Label(cell, text=text, bg=bg, font=self.CELL_FONT, wraplength=self.CELL_SIZE - 8).place(
            relx=0.5, rely=0.5, anchor="center"
        )
        return cell

    def center_table(self, event):
            self.canvas.coords(self.table_window, event.width // 2, 0)

    # AUTOCOMPLETE
    def suggest(self, event=None):
        typed = self.entry.get().lower()

        if self.autocomplete_list:
            self.autocomplete_list.destroy()
            self.autocomplete_list = None

        if not typed:
            return

        suggestions = [
            c["Name"] for c in self.filtered_cards
            if typed in c["Name"].lower() and c["Name"] not in self.guessed_names
        ][:5]

        if not suggestions:
            return

        self.autocomplete_list = tk.Listbox(self.top_frame, height=5)
        self.autocomplete_list.pack(fill="x")

        for s in suggestions:
            self.autocomplete_list.insert(tk.END, s)

        self.autocomplete_list.bind("<<ListboxSelect>>", self.select_autocomplete)

    def select_autocomplete(self, event):
        selection = self.autocomplete_list.curselection()
        if selection:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.autocomplete_list.get(selection[0]))
            self.autocomplete_list.destroy()
            self.autocomplete_list = None

    # GAME LOGIC
    def check_guess(self):
        name_guess = self.entry.get()

        guess_card = next(
            (c for c in self.filtered_cards if c["Name"].lower() == name_guess.lower()),
            None
        )

        if not guess_card:
            self.result_label.config(text="There is no such minion!", fg="red")
            return

        if guess_card["Name"] in self.guessed_names:
            self.result_label.config(text="Already guessed!", fg="orange")
            return

        self.guessed_names.add(guess_card["Name"])
        self.entry.delete(0, tk.END)

        if self.autocomplete_list:
            self.autocomplete_list.destroy()
            self.autocomplete_list = None

        self.entry.bind("<Return>", lambda e: self.check_guess())

        if not self.header_visible:
            self.create_header()
            self.header_visible = True

        row = len(self.table_frame.winfo_children())

        row_frame = tk.Frame(self.table_frame)
        row_frame.grid(row=row, column=0, pady=4)

        self.make_cell(row_frame, guess_card["Name"], "lightgray").grid(row=0, column=0, padx=2)

        # Tier
        if guess_card["Tier"] == self.target["Tier"]:
            bg = "green"
            text = str(guess_card["Tier"])
        elif guess_card["Tier"] < self.target["Tier"]:
            bg = "red"
            text = f"{guess_card['Tier']} ↑"
        else:
            bg = "red"
            text = f"{guess_card['Tier']} ↓"

        self.make_cell(row_frame, text, bg).grid(row=0, column=1, padx=2)

        # Tribe
        gt = set(guess_card["Tribe"])
        tt = set(self.target["Tribe"])

        if gt == tt:
            bg = "green"
        elif "All" in gt or "All" in tt or gt & tt:
            bg = "yellow"
        else:
            bg = "red"

        self.make_cell(row_frame, ", ".join(guess_card["Tribe"]) or "-", bg).grid(row=0, column=2, padx=2)

        # Attack
        if guess_card["Attack"] == self.target["Attack"]:
            bg = "green"
            text = str(guess_card["Attack"])
        elif guess_card["Attack"] < self.target["Attack"]:
            bg = "red"
            text = f"{guess_card['Attack']} ↑"
        else:
            bg = "red"
            text = f"{guess_card['Attack']} ↓"

        self.make_cell(row_frame, text, bg).grid(row=0, column=3, padx=2)

        # Health
        if guess_card["Health"] == self.target["Health"]:
            bg = "green"
            text = str(guess_card["Health"])
        elif guess_card["Health"] < self.target["Health"]:
            bg = "red"
            text = f"{guess_card['Health']} ↑"
        else:
            bg = "red"
            text = f"{guess_card['Health']} ↓"

        self.make_cell(row_frame, text, bg).grid(row=0, column=4, padx=2)

        # Keywords
        gk = set(guess_card["Keywords"])
        tk_ = set(self.target["Keywords"])

        if gk == tk_:
            bg = "green"
        elif gk & tk_:
            bg = "yellow"
        else:
            bg = "red"

        self.make_cell(row_frame, ", ".join(guess_card["Keywords"]) or "-", bg).grid(row=0, column=5, padx=2)

        # win
        if guess_card["Name"] == self.target["Name"]:
            self.result_label.config(text=f"You got it! {self.target['Name']}", fg="green")
            self.submit_btn.config(text="New Game", command=self.new_game)
        else:
            self.result_label.config(text="Try again!", fg="blue")


# RUN
root = tk.Tk()
app = BGdleApp(root)
root.mainloop()