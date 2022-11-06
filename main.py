import csv
import re
import tkinter as tk
import tkinter.messagebox

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Expense Tracker")
        self.geometry("1000x600")

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Home,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Home")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class Home(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # saved data
        # 0 transaction data
        # 1 category names
        self.data = [[]] * 2
        self.data_files = [
            "transactions.csv",
            "categories.txt",
        ]

        self.load_files()

        self.build_frames()

    def build_frames(self):
        self.build_ta_frame()
        self.build_cat_frame()

    def build_ta_frame(self):
        self.ta_frame = tk.Frame(
            self,
            highlightbackground="black",
            highlightthickness=1
        )
        self.ta_frame.pack(anchor=tk.NW, padx=10, pady=10)

        self.ta_frame.columnconfigure(0, weight=3)
        self.ta_frame.columnconfigure(1, weight=5)

        tk.Label(self.ta_frame, text="Transaction Section") \
            .grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        self.ta_entries = [
            [ "Name", None ],
            [ "Amount", None ],
            [ "Description", None ],
        ]
        for i, tae in enumerate(self.ta_entries):
            tk.Label(self.ta_frame, text=tae[0]) \
                .grid(row=i + 1, column=0, sticky=tk.W, padx=5, pady=5)
            tae[1] = tk.Entry(self.ta_frame)
            tae[1].grid(row=i + 1, column=1, sticky=tk.E, padx=5, pady=5)

        tk.Label(self.ta_frame, text="Category") \
            .grid(
                row=len(self.ta_entries) + 1,
                column=0,
                sticky=tk.W,
                padx=5,
                pady=5
            )
        self.create_cat_dropdown()

        tk.Button(
            self.ta_frame,
            text="Save transaction",
            command=self.save_ta
        ).grid(
            row=len(self.ta_entries) + 2,
            column=1,
            sticky=tk.E,
            padx=5,
            pady=5
        )

    def create_cat_dropdown(self):
        if self.data[1]:
            self.cat_selected = tk.StringVar()
            self.cat_selected.set(self.data[1][0])
            cat_drop = tk.OptionMenu(
                self.ta_frame,
                self.cat_selected,
                *self.data[1]
            ).grid(
                row=len(self.ta_entries) + 1,
                column=1,
                sticky=tk.E,
                padx=5,
                pady=5
            )
        else:
            self.cat_dd_placeholder = tk.Label(
                self.ta_frame,
                text="Create a category!"
            )
            self.cat_dd_placeholder.grid(
                row=len(self.ta_entries) + 1,
                column=1,
                sticky=tk.W,
                padx=5,
                pady=5
            )

    def update_cat_dropdown(self):
        if len(self.data[1]) == 1:
            self.cat_dd_placeholder.config(text="")
        elif len(self.data[1]) == 0:
            self.cat_dd_placeholder.config(text="Create a category!")
            return
        self.create_cat_dropdown()

    def load_files(self):
        try:
            with open(self.data_files[0], "r") as file:
                reader = csv.reader(file)
                self.data[0] = [ row for row in reader ]
        except:
            pass

        try:
            with open(self.data_files[1], "r") as file:
                self.data[1] = [ line.rstrip() for line in file ]
        except:
            pass
        
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
        if not self.data[1]:
            return "Must categorize this transaction!"
        return ""

    def save_ta(self):
        error_msg = self.check_ta_input()
        if error_msg:
            tk.messagebox.showinfo("Information", f"{error_msg}")
            return

        self.data[0].append(
            [ row[1].get() for row in self.ta_entries ]
            + [ self.cat_selected.get() ]
        )
        with open(self.data_files[0], "w") as file:
            writer = csv.writer(file)
            writer.writerows(self.data[0])
            tk.messagebox.showinfo("Information", "Saved successfully!")
            for tae in self.ta_entries:
                tae[1].delete(0, tk.END)
            self.cat_selected.set(self.data[1][0])

    def build_cat_frame(self):
        cat_frame = tk.Frame(
            self,
            highlightbackground="black",
            highlightthickness=1
        )
        cat_frame.pack(anchor=tk.NW, padx=10, pady=10)

        cat_frame.columnconfigure(0, weight=3)
        cat_frame.columnconfigure(1, weight=5)
        cat_frame.columnconfigure(2, weight=5)

        tk.Label(cat_frame, text="Category Section") \
            .grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        tk.Label(cat_frame, text="Create") \
            .grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cat_to_create = tk.Entry(cat_frame)
        self.cat_to_create.grid(
            row=1,
            column=1,
            sticky=tk.E,
            padx=5,
            pady=5
        )
        tk.Button(
            cat_frame,
            text="Create category",
            command=self.create_cat
        ).grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)

    def save_cats(self):
        with open(self.data_files[1], "w") as file:
            file.write("\n".join(self.data[1]))

    def create_cat(self):
        name = self.cat_to_create.get()
        error_msg= ""

        if not re.match("^[A-Za-z0-9_-]+$", name):
            error_msg = "Category names must contain" \
                      + " alphanumeric characters, underscores," \
                      + " and/or dashes!"
        elif name in self.data[1]:
            error_msg = "Category already exists!"
        else:
            self.data[1].append(name)
            self.save_cats()
            self.update_cat_dropdown()
            tk.messagebox.showinfo(
                "Information",
                f"Added category \"{name}\""
            )

        if error_msg:
            tk.messagebox.showinfo(
                "Information",
                f"Operation failed: {error_msg}"
            )

        self.cat_to_create.delete(0, tk.END)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
