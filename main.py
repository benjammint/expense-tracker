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

        self.build_frames()

    def build_frames(self):
        self.build_ta_frame()

    def build_ta_frame(self):
        ta_frame = tk.Frame(
                self,
                highlightbackground="black",
                highlightthickness=1
        )
        ta_frame.pack(anchor=tk.NW, padx=10, pady=10)

        ta_frame.columnconfigure(0, weight=3)
        ta_frame.columnconfigure(1, weight=5)

        self.ta_entries = [
            ["Transaction Name", None],
            ["Transaction Amount", None],
            ["Transaction Description", None],
        ]
        for i, tae in enumerate(self.ta_entries):
            tk.Label(ta_frame, text=tae[0]) \
                .grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
            tae[1] = tk.Entry(ta_frame)
            tae[1].grid(column=1, row=i, sticky=tk.E, padx=5, pady=5)

        # get previously saved data
        # 0 transaction data
        # 1 category names
        self.data = [[]] * 2
        self.data_files = [
            "ta_data.csv",
            "cat_names",
        ]
        self.load_files()

        tk.Label(ta_frame, text="Category") \
            .grid(
                column=0,
                row=len(self.ta_entries),
                sticky=tk.W,
                padx=5,
                pady=5
            )
        if self.data[1]:
            self.cat_selected = StringVar()
            self.cat_selected(self.data[1][0])
            cat_drop = tk.OptionMenu(
                ta_frame,
                self.cat_selected,
                *self.data[1]
            ).grid(
                column=1,
                row=len(self.ta_entries),
                sticky=tk.E,
                padx=5,
                pady=5
            )
        else:
            tk.Label(ta_frame, text="Create a category!") \
                .grid(
                    column=1,
                    row=len(self.ta_entries),
                    sticky=tk.W,
                    padx=5,
                    pady=5
                )

        tk.Button(ta_frame, text="Save transaction", command=self.save_ta) \
            .grid(
                column=1,
                row=len(self.ta_entries) + 1,
                sticky=tk.E,
                padx=5,
                pady=5
            )

    def load_files(self):
        for i, f in enumerate(self.data):
            try:
                with open(f, "r") as file:
                    self.data[i] = [ line.rstrip() for line in file ]
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

        self.ta_data.append([ row[1].get() for row in self.ta_entries ] \
            .extend([ self.cat_selected.get() ]))
        with open(self.data_files[0], "w") as file:
            writer = csv.writer(file)
            writer.writerows(self.data[0])
            tk.messagebox.showinfo("Information", "Saved successfully!")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
