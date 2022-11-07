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
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Expense Tracker")
        self.geometry("1000x600")

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage,):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.ta_frame = HomeTaFrame(self)
        self.cat_frame = HomeCatFrame(self)

    def refresh_frame(self, builder):
        if builder.frame:
            builder.frame.grid_forget()
        builder.build()

class HomeTaFrame(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.parent.refresh_frame(self)

    def build(self):
        self.frame = build_grid_frame(
            parent=self.parent,
            anchor=tk.NW,
            columns=2,
        )

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
        ta_entry_cat = tk.StringVar()
        build_grid_dropdown(
            parent=self.frame,
            shownopt=ta_entry_cat,
            options=data["categories"],
            row=len(self.ta_entries) + 1,
            col=1,
            errmsg="Create a category!",
        )

        build_grid_button(
            parent=self.frame,
            text="Create category",
            row=len(self.ta_entries) + 2, 
            col=1,
            callback=None,
        )

class HomeCatFrame(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.parent.refresh_frame(self)

    def build(self):
        self.frame = build_grid_frame(
            parent=self.parent,
            anchor=tk.NW,
            columns=3,
        )

        build_grid_label(
            parent=self.frame,
            text="Category Section",
            row=0,
            col=0,
            colspan=3,
            sticky=tk.N,
        )

        build_grid_label(
            parent=self.frame,
            text="Create",
            row=1,
            col=0,
        )
        build_grid_entry(parent=self.frame, row=1, col=1)
        build_grid_button(
            parent=self.frame,
            text="Create category",
            row=1,
            col=2,
            callback=None,
        )


def build_grid_frame(parent, anchor=tk.CENTER, columns=1):
    frame = tk.Frame(
        parent,
        highlightbackground="black",
        highlightthickness=1,
    )
    frame.pack(anchor=anchor, padx=10, pady=10)
    for i in range(columns):
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
    return tk.Entry(parent) \
        .grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)

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

def main():
    App().mainloop()

if __name__ == "__main__":
    main()
