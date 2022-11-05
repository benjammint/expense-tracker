import re
import tkinter as tk
import tkinter.messagebox

class App(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.title = "Expense Tracker"
        self.parent.title(self.title)
        self.parent.geometry("1000x600")

        self.build_frames()

        self.cat_names = []
        self.cat_file = "categories.txt"
        self.load_files()

        self.create_math_frame()
        self.create_cat_frame()
        self.create_add_cat_frame()

    def build_frames(self):
        self.math_frame = tk.Frame(self.parent)
        self.math_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.cat_frame = tk.Frame(self.parent)
        self.cat_frame.pack(side=tk.TOP, fill=tk.X)
        self.add_cat_frame = tk.Frame(self.parent)
        self.add_cat_frame.pack(fill=tk.X)

    def load_files(self):
        try:
            with open(self.cat_file, "r") as file:
                self.cat_names = [ line.rstrip() for line in file ]
        except:
            pass

    def update_files(self):
        with open(self.cat_file, "w") as file:
            file.write("\n".join(self.cat_names))

    def create_math_frame(self):
        tk.Label(self.math_frame, text="Math").pack()

    def create_cat_frame(self):
        tk.Label(self.cat_frame, text="Categories").pack()
        if not self.cat_names:
            tk.Label(self.cat_frame, text="Nothing yet!").pack()
        for cat in self.cat_names:
            tk.Button(self.cat_frame, text=cat, command=None).pack()

    def create_add_cat_frame(self):
        tk.Label(
            self.add_cat_frame,
            text="Create Category"
        ).pack(side=tk.LEFT)
        self.cat_to_create = tk.Entry(self.add_cat_frame)
        self.cat_to_create.pack(side=tk.LEFT)
        tk.Button(
            self.add_cat_frame,
            text="Create",
            command=self.create_cat
        ).pack(side=tk.LEFT)

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
            tk.Button(self.cat_frame, text=name, command=None).pack()
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
