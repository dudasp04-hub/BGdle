import tkinter as tk
from tkinter import ttk
import random

cards = []
with open("bg.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            parts = line.strip().split(";")
            card = {
                "Name": parts[0],
                "Tier": int(parts[1]),
                "Tribe": [t.strip() for t in parts[2].split(",") if t.strip()],
                "Attack": int(parts[3]),
                "Health": int(parts[4]),
                "Keywords": [k.strip() for k in parts[5].split(",") if k.strip()]
            }
            cards.append(card)

target = random.choice(cards)

CELL_SIZE = 100
CELL_FONT = ("Arial", 9, "bold")

header_visible = False 

root = tk.Tk()
root.title("BGdle")

guessed_names=set()

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

table_container = tk.Frame(root)
table_container.pack(padx=10, pady=10, fill="both", expand=True)

header_container = tk.Frame(table_container)
header_container.pack(fill="x")

canvas = tk.Canvas(table_container, height=420)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(
    table_container,
    orient="vertical",
    command=canvas.yview
)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

table_frame = tk.Frame(canvas)
table_window_id = canvas.create_window((0, 0), window=table_frame, anchor="n")

def on_canvas_configure(event):
    canvas.itemconfigure(table_window_id, width=event.width)


def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

table_frame.bind("<Configure>", on_frame_configure)
canvas.bind("<Configure>", on_canvas_configure)

autocomplete_list = tk.Listbox(frame, height=5)
autocomplete_list = tk.Listbox(
    frame,
    height=5,
    takefocus=False
)

autocomplete_list=None

def create_header():
    HEADER_CELL_HEIGHT = CELL_SIZE // 3

    header_row = tk.Frame(table_frame)
    header_row.grid(row=0, column=0, pady=(0, 6))
    header_row.grid_anchor("center")

    headers = ["Minion", "Tier", "Tribe", "Attack", "Health", "Keywords"]

    for col, text in enumerate(headers):
        cell = tk.Frame(
            header_row,
            width=CELL_SIZE,
            height=HEADER_CELL_HEIGHT,
            bg="#333333",
            relief="solid",
            borderwidth=1
        )
        cell.grid(row=0, column=col, padx=2)
        cell.grid_propagate(False)

        lbl = tk.Label(
            cell,
            text=text,
            bg="#333333",
            fg="white",
            font=("Arial", 9, "bold"),
            wraplength=CELL_SIZE - 8,
            justify="center"
        )
        lbl.place(relx=0.5, rely=0.5, anchor="center")

def make_cell(parent, text, bg):
    cell = tk.Frame(
        parent,
        width=CELL_SIZE,
        height=CELL_SIZE,
        bg=bg,
        relief="solid",
        borderwidth=1
    )
    cell.grid_propagate(False)

    lbl = tk.Label(
        cell,
        text=text,
        bg=bg,
        fg="black",
        font=CELL_FONT,
        wraplength=CELL_SIZE - 8,
        justify="center"
    )
    lbl.place(relx=0.5, rely=0.5, anchor="center")

    return cell

def suggest(event=None):
    global autocomplete_list

    typed = entry.get().lower()

    if autocomplete_list:
        autocomplete_list.destroy()
        autocomplete_list=None

    if not typed:
        return

    suggestions = [
        c["Name"] for c in cards
        if typed in c["Name"].lower() and c["Name"] not in guessed_names][:5]
    if not suggestions:
        return

    autocomplete_list = tk.Listbox(frame, height=5, takefocus=False)
    autocomplete_list.pack(fill="x")

    for s in suggestions:
        autocomplete_list.insert(tk.END, s)

    autocomplete_list.bind("<<ListboxSelect>>", select_autocomplete)

    autocomplete_list.pack(fill="x")
    entry.focus_set()

def select_autocomplete(event):
    selection = autocomplete_list.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, autocomplete_list.get(selection[0]))
        autocomplete_list.delete(0, tk.END)
        autocomplete_list.pack_forget()

def check_guess():
    global autocomplete_list, submit_btn, target, guessed_names, header_visible

    name_guess = entry.get()
    guess_card = next((c for c in cards if c["Name"].lower() == name_guess.lower()), None)

    if not guess_card:
        result_label.config(text="There is no such minion!", fg="red")
        return

    if guess_card["Name"] in guessed_names:
        result_label.config(
            text="You've already guessed this minion in this game!",
            fg="orange"
        )
        entry.delete(0, tk.END)
        return

    guessed_names.add(guess_card["Name"])

    if not header_visible:
        create_header()
        header_visible = True

    for child in table_frame.winfo_children():
        info = child.grid_info()
        if not info:
            continue
        if info.get("row", 0) != 0:
            child.grid(row=info["row"] + 1, column=info["column"])


    table_frame.grid_columnconfigure(0, weight=1)

    row = max(
        (child.grid_info()["row"] for child in table_frame.winfo_children()),
        default=0
    ) + 1

    row_frame = tk.Frame(table_frame)
    row_frame.grid(row=row, column=0, pady=4)
    row_frame.grid_anchor("center")

    entry.delete(0, tk.END)
    autocomplete_list.pack_forget()

    name_cell = make_cell(row_frame, guess_card["Name"], "lightgray")
    name_cell.grid(row=0, column=0, padx=2)

    if guess_card["Tier"] == target["Tier"]:
        tier_bg = "green"
        tier_text = str(guess_card["Tier"])
    elif guess_card["Tier"] < target["Tier"]:
        tier_bg = "red"
        tier_text = f"{guess_card['Tier']} ↑"
    else:
        tier_bg = "red"
        tier_text = f"{guess_card['Tier']} ↓"

    tier_cell = make_cell(row_frame, tier_text, tier_bg)
    tier_cell.grid(row=0, column=1, padx=2)

    guess_tribes = set(guess_card["Tribe"])
    target_tribes = set(target["Tribe"])

    if guess_tribes == target_tribes:
        tribe_bg = "green"

    elif "All" in guess_tribes or "All" in target_tribes:
        tribe_bg = "yellow"

    elif guess_tribes & target_tribes:
        tribe_bg = "yellow"

    else:
        tribe_bg = "red"

    tribe_text = ", ".join(guess_card["Tribe"]) or "-"
    tribe_cell = make_cell(row_frame, tribe_text, tribe_bg)
    tribe_cell.grid(row=0, column=2, padx=2)

    if guess_card["Attack"] == target["Attack"]:
        atk_bg = "green"
        atk_text = str(guess_card["Attack"])
    elif guess_card["Attack"] < target["Attack"]:
        atk_bg = "red"
        atk_text = f"{guess_card['Attack']} ↑"
    else:
        atk_bg = "red"
        atk_text = f"{guess_card['Attack']} ↓"

    atk_cell = make_cell(row_frame, atk_text, atk_bg)
    atk_cell.grid(row=0, column=3, padx=2)

    if guess_card["Health"] == target["Health"]:
        hp_bg = "green"
        hp_text = str(guess_card["Health"])
    elif guess_card["Health"] < target["Health"]:
        hp_bg = "red"
        hp_text = f"{guess_card['Health']} ↑"
    else:
        hp_bg = "red"
        hp_text = f"{guess_card['Health']} ↓"

    hp_cell = make_cell(row_frame, hp_text, hp_bg)
    hp_cell.grid(row=0, column=4, padx=2)

    guess_kw = set(guess_card["Keywords"])
    target_kw = set(target["Keywords"])

    if guess_kw == target_kw:
        kw_bg = "green"
    elif guess_kw & target_kw:
        kw_bg = "yellow"
    else:
        kw_bg = "red"

    kw_text = ", ".join(guess_card["Keywords"]) or "-"
    kw_cell = make_cell(row_frame, kw_text, kw_bg)
    kw_cell.grid(row=0, column=5, padx=2)

    if guess_card["Name"] == target["Name"]:
        result_label.config(text=f"Congratulations! You guessed it: {target['Name']}", fg="green")
        submit_btn.config(text="New game", command=new_game)
    else:
        result_label.config(text="Try again!", fg="blue")

    canvas.yview_moveto(0)


def new_game():
    global target, table_frame, submit_btn, guessed_names, header_visible
    header_visible = False
    target = random.choice(cards)
    guessed_names.clear()
    for widget in table_frame.winfo_children():
        widget.destroy()
    submit_btn.config(text="Guess", command=check_guess)
    result_label.config(text="")
    entry.delete(0,tk.END)

INPUT_WIDTH=600

input_frame = tk.Frame(frame, width=INPUT_WIDTH)
input_frame.pack()

ENTRY_FONT=("Arial",14)

entry = tk.Entry(input_frame, font=ENTRY_FONT,width=30)
entry.pack(fill="x", ipady=6)
entry.bind("<KeyRelease>", suggest)

submit_btn = tk.Button(frame, text="Guess", command=check_guess)
submit_btn.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=5)

root.mainloop()
