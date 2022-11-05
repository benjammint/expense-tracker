import re
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk

class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.title = "Expense Tracker"
        self.parent.title(self.title)
        self.parent.geometry("1000x600")

        self.cat_names = []
        self.cat_file = "categories.txt"
        self.load_files()

        tk.Label(self.parent, text="Create Category").pack()
        self.cat_to_create = tk.Entry()
        self.cat_to_create.pack()
        tk.Button(
            self.parent,
            text="Create",
            command=self.create_cat
        ).pack()

    def load_files(self):
        try:
            with open(self.cat_file, "r") as file:
                self.cat_names = [ line.rstrip() for line in file ]
        except:
            pass

    def update_files(self):
        with open(self.cat_file, "w") as file:
            file.write("\n".join(self.cat_names))

    def create_cat(self):
        name = self.cat_to_create.get()
        error_msg = ""

        if not re.match("^[A-Za-z0-9_-]+$", name):
            error_msg = "Category names must contain" \
                      + " alphanumeric characters, underscores," \
                      + " and/or dashes!"
        elif name in self.cat_names:
            error_msg = "Category already exists!"
        else:
            self.cat_names.append(name)
            self.update_files()
            tk.messagebox.showinfo(
                "Information",
                f"Added category \"{name}\""
            )

        if error_msg:
            tk.messagebox.showinfo(
                self.title,
                f"Operation failed: {error_msg}"
            )

        self.cat_to_create.delete(0, tk.END)

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
