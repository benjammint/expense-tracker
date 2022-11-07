import csv
import re
import tkinter as tk
import tkinter.messagebox

data = {
    "categories": [],
    "transactions": [],
}
data_files = [
    "categories.txt",
    "transactions.csv",
]

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

        self.title("Expense Tracker")
        self.geometry("1000x600")

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
            [ "Name", None ],
            [ "Amount", None ],
            [ "Description", None ],
        ]

        for i, tae in enumerate(self.ta_entries):
            build_grid_label(self.frame, text=tae[0], row=i + 1, col=0)
            build_grid_entry(self.frame, row=i + 1, col=1)

        build_grid_label(self.frame, "Category", len(self.ta_entries) + 1, 0)
        self.ta_entry_cat = tk.StringVar()
        self.cat_menu = build_grid_dropdown(
            parent=self.frame,
            shownopt=self.ta_entry_cat,
            options=data["categories"],
            row=len(self.ta_entries) + 1,
            col=1,
            errmsg="Create a category!",
        )

        build_grid_button(
            parent=self.frame,
            text="Add transaction",
            row=len(self.ta_entries) + 2, 
            col=1,
            callback=None,
        )

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
        tk.messagebox.showinfo(
            "Information",
            f"Saved {desired_cat} successfully!",
        )
        self.parent.ta_frame.cat_menu = None
        self.cat_menu = build_grid_dropdown(
            parent=self.parent.ta_frame.frame,
            shownopt=self.parent.ta_frame.ta_entry_cat,
            options=data["categories"],
            row=len(self.parent.ta_frame.ta_entries) + 1,
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

def check_valid_str(test):
    if re.match("^[A-Za-z0-9_\- ]+$", test):
        return ""
    return "Strings must only contain alphanumeric characters, underscores," \
        + " dashes, and/or spaces!"

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
