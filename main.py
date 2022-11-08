import datetime
import json
import re
import tkinter as tk
import tkinter.messagebox
import tkcalendar

DATA_FILE = "data.json"
data = {
    "categories": [], # this is needed for tk.OptionMenu()
    "transactions": [],
        # dict inside list
        # contains { cat, yr, mon, day, amt, name, desc }
}

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None

        self.title("Expense Tracker")
        self.geometry("1000x600")

        load_data()
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill=tk.BOTH, expand=True)

class StartPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.ta_frame = StartTaFrame(self)
        self.cat_frame= StartCatFrame(self)

class StartTaFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH)
        self.parent = parent

        self.build()

    def build(self):
        self.frame = build_grid_frame(parent=self, anchor=tk.NW, cols=2)

        build_grid_label(
            parent=self.frame,
            text="Transaction Section",
            row=0,
            col=0,
            colspan=2,
            sticky=tk.N,
        )

        self.ta_entries = [
            [ l, None ] for l in (
                "Name",
                "Amount (USD)",
                "Description",
                "Date",
                "Category",
            )
        ]

        for i, tae in enumerate(self.ta_entries):
            build_grid_label(self.frame, text=tae[0], row=i + 1, col=0)
            if i < len(self.ta_entries) - 2:
                tae[1] = build_grid_entry(self.frame, row=i + 1, col=1)

        self.ta_cal = build_grid_cal(
            parent=self.frame,
            row=len(self.ta_entries) - 1,
            col=1
        )

        self.ta_selected_cat = tk.StringVar()
        self.cat_menu = build_grid_dropdown(
            parent=self.frame,
            shownopt=self.ta_selected_cat,
            options=data["categories"],
            row=len(self.ta_entries),
            col=1,
            errmsg="Create a category!",
        )

        build_grid_button(
            parent=self.frame,
            text="Add transaction",
            row=len(self.ta_entries) + 1,
            col=1,
            callback=self.save_ta,
        )

    def check_ta_input(self):
        if not self.ta_entries[0][1].get():
            return "Must provide a name for the transaction!"
        try:
            amt = float(self.ta_entries[1][1].get())
            if amt * 100 > int(amt * 100):
                return "There can only be two digits after the decimal!"
        except ValueError:
            return "The transaction amount must be a decimal number" \
                + " (without units)!"
        if not self.ta_entries[2][1].get():
            return "Please provide a description for this transaction!"
        if not data["categories"]:
            return "Must categorize this transaction!"
        return ""

    def save_ta(self):
        errmsg = self.check_ta_input()
        if errmsg:
            tk.messagebox.showinfo("Information", f"Operation failed: {errmsg}")
            return
        cat_key = self.ta_selected_cat.get()
        data["transactions"].append({
            "category": self.ta_selected_cat.get(),
            "name": self.ta_entries[0][1].get(),
            "amount": self.ta_entries[1][1].get(),
            "description": self.ta_entries[2][1].get(),
            "year": str(self.ta_cal.get_displayed_month()[1]),
            "month": str(self.ta_cal.get_displayed_month()[0]),
            "day": re.search("/(.+?)/", self.ta_cal.get_date()).group(1)
        })
        save_data()
        tk.messagebox.showinfo(
            "Information",
            f"Transaction saved successfully!"
        )
        for entry in self.ta_entries:
            if entry[0] == "Date":
                break
            entry[1].delete(0, tk.END)
        self.ta_cal.selection_set(datetime.date.today())
        self.ta_selected_cat.set(data["categories"][0])

class StartCatFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(fill=tk.BOTH)
        self.parent = parent
        
        self.build()

    def build(self):
        self.frame = build_grid_frame(parent=self, anchor=tk.NW, cols=3)

        build_grid_label(
            parent=self.frame,
            text="Category Section",
            row=0,
            col=0,
            colspan=3,
            sticky=tk.N,
        )

        build_grid_label(parent=self.frame, text="Create", row=1, col=0)
        self.cat_to_create = build_grid_entry(parent=self.frame, row=1, col=1)
        build_grid_button(
            parent=self.frame,
            text="Create category",
            row=1,
            col=2,
            callback=self.create_cat,
        )

    def create_cat(self):
        desired_cat = self.cat_to_create.get()
        errmsg = check_valid_str(desired_cat)
        if errmsg:
            tk.messagebox.showinfo("Information", f"Operation failed: {errmsg}")
            return
        if desired_cat in data["categories"]:
            tk.messagebox.showinfo(
                "Information",
                "Operation failed: Category already exists!",
            )
            return
        data["categories"].append(desired_cat)
        save_data()
        tk.messagebox.showinfo(
            "Information",
            f"Saved {desired_cat} successfully!",
        )
        self.parent.ta_frame.cat_menu = None
        self.cat_menu = build_grid_dropdown(
            parent=self.parent.ta_frame.frame,
            shownopt=self.parent.ta_frame.ta_selected_cat,
            options=data["categories"],
            row=len(self.parent.ta_frame.ta_entries),
            col=1,
            errmsg="Create a category!",
        )
        self.cat_to_create.delete(0, tk.END)

def build_grid_frame(parent, anchor=tk.CENTER, cols=1):
    frame = tk.Frame(
        parent,
        highlightbackground="black",
        highlightthickness=1,
    )
    frame.pack(anchor=anchor, padx=10, pady=10)
    for i in range(cols):
        frame.columnconfigure(i)
    return frame

def build_grid_label(parent, text, row, col, colspan=1, sticky=tk.W):
    return tk.Label(parent, text=text) \
        .grid(
            row=row,
            column=col,
            columnspan=colspan,
            sticky=sticky,
            padx=5,
            pady=5,
        )

def build_grid_entry(parent, row, col):
    entry = tk.Entry(parent)
    entry.grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)
    return entry

def build_grid_dropdown(parent, shownopt, options, row, col, errmsg):
    if not options:
        build_grid_label(parent, errmsg, row, col)
        return
    shownopt.set(options[0])
    return tk.OptionMenu(parent, shownopt, *options) \
        .grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)

def build_grid_button(parent, text, row, col, callback):
    return tk.Button(parent, text=text, command=callback) \
        .grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)

def build_grid_cal(parent, row, col):
    cal = tkcalendar.Calendar(
        parent,
        showweeknumbers=False,
        background="white",
        disabledbackground="white",
        bordercolor="white",
        headersbackground="white",
        normalbackground="white",
        foreground="black",
        normalforeground="black",
        headersforeground="black",
    )
    cal.grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)
    return cal

def check_valid_str(test):
    if re.match("^[A-Za-z0-9_\- ]+$", test):
        return ""
    return "Strings must only contain alphanumeric characters, underscores," \
        + " dashes, and/or spaces!"

def save_data():
    with open(DATA_FILE, "w") as file:
        file.write(json.dumps(data, indent=4))

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            global data
            data = json.load(file)
    except FileNotFoundError:
        pass

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
