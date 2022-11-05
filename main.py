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

        self.categories = []
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
                self.categories = [ line.rstrip() for line in file ]
        except:
            pass

    def update_files(self):
        with open(self.cat_file, "w") as file:
            file.write("\n".join(self.categories))

    def create_cat(self):
        name = self.cat_to_create.get()
        error_msg = ""

        if name in self.categories:
            error_msg = "Category already exists!"

        if re.match("^[A-Za-z0-9_-]+$", name) and not error_msg:
            self.categories.append(name)
            self.update_files()
            tk.messagebox.showinfo(
                "Information",
                f"Added category \"{name}\""
            )
        else:
            error_msg = "Category names must contain" \
                      + " alphanumeric characters, underscores," \
                      + " and/or dashes!"

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
