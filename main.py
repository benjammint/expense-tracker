import calendar
import datetime
import json
import re
import tkinter as tk
import tkinter.messagebox
import tkcalendar

DATA_FILE = "data.json"
data = {
    "categories": [], # required for tk.OptionMenu()
    "years": [], # will be sorted in ascending order
    "transactions": [],
        # dict inside list
        # contains { category, year, month, day, amount, description }
}

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None

        self.title("Expense Tracker")

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

        self.stats_frame = StartStatsFrame(parent=self)
        self.ta_frame = StartTaFrame(parent=self)
        self.cat_frame = StartCatFrame(parent=self)

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
                "Description",
                "Amount (USD)",
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
            return "Please provide a description for this transaction!"
        try:
            amt = float(self.ta_entries[1][1].get())
            if amt * 100 > int(amt * 100):
                return "There can only be two digits after the decimal!"
        except ValueError:
            return "The transaction amount must be a decimal number" \
                + " (without units)!"
        if not data["categories"]:
            return "Must categorize this transaction!"
        return ""

    def save_ta(self):
        errmsg = self.check_ta_input()
        if errmsg:
            tk.messagebox.showinfo("Information", f"Operation failed: {errmsg}")
            return
        year = self.ta_cal.get_displayed_month()[1]
        if str(year) not in data["years"]:
            added = False
            for i, v in enumerate(data["years"]):
                if year <= int(v):
                    data["years"].insert(i, str(year))
                    added = True
                    break
            if not added:
                data["years"].append(str(year))
                added ^= True
        data["transactions"].append({
            "category": self.ta_selected_cat.get(),
            "description": self.ta_entries[0][1].get(),
            "amount": self.ta_entries[1][1].get(),
            "year": str(year),
            "month": str(self.ta_cal.get_displayed_month()[0]),
            "day": re.search("/(.+?)/", self.ta_cal.get_date()).group(1)
        })
        save_data()
        tk.messagebox.showinfo(
            "Information",
            f"Transaction saved successfully!"
        )
        refresh_grid_dropdown(
            section_frame=self.parent.stats_frame,
            dropdown_menu=self.parent.stats_frame.average_monthly_year_menu,
            shownopt=self.parent.stats_frame.stats_selected_year,
            options=data["years"],
            row=1,
            col=2,
            errmsg="Add a transaction!",
            defaultopt=str(datetime.datetime.now().year),
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
        refresh_grid_dropdown(
            section_frame=self.parent.ta_frame,
            dropdown_menu=self.parent.ta_frame.cat_menu,
            shownopt=self.parent.ta_frame.ta_selected_cat,
            options=data["categories"],
            row=len(self.parent.ta_frame.ta_entries),
            col=1,
            errmsg="Create a category!",
        )
        self.cat_to_create.delete(0, tk.END)

class StartStatsFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(side=tk.RIGHT, anchor=tk.N)
        self.parent = parent

        self.build()

    def build(self):
        self.frame = build_grid_frame(parent=self, anchor=tk.NE, cols=5)

        build_grid_label(
            parent=self.frame,
            text="Statistics Section",
            row=0,
            col=0,
            colspan=5,
            sticky=tk.N,
        )

        calendar_months = [ calendar.month_name[i + 1] for i in range(12) ]

        build_grid_label(
            parent=self.frame,
            text="Average Monthly Transactions Amount",
            row=1,
            col=0,
        )
        self.average_monthly_ta_amt_selected = {
            "month": tk.StringVar(),
            "year": tk.StringVar(),
        }
        build_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_ta_amt_selected["month"],
            options=calendar_months,
            row=1,
            col=1,
            defaultopt=calendar.month_name[datetime.datetime.now().month],
        )
        self.average_monthly_year_menu = build_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_ta_amt_selected["year"],
            options=data["years"],
            row=1,
            col=2,
            errmsg="Add a transaction!",
            defaultopt=str(datetime.datetime.now().year),
        )
        self.monthly_average_label = build_grid_label(
            parent=self.frame,
            text="<- Calculate!",
            row=1,
            col=4,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=1,
            col=3,
            callback=self.display_monthly_average,
        )

        build_grid_label(
            parent=self.frame,
            text="Monthly total",
            row=2,
            col=0,
        )
#        build_grid_dropdown(
#            parent=self.frame,
#            shownopt=self.stats_selected_month,
#            options=calendar_months,
#            row = 2,
#            col=1,
#            defaultopt=calendar.month_name[datetime.datetime.now().month],
#        )

    def calc_monthly_average(self):
        month = self.average_monthly_ta_amt_selected["month"].get()
        year = self.average_monthly_ta_amt_selected["year"].get()
        total = [
            int(ta["amount"]) for ta in data["transactions"] \
            if ta["year"] == year \
            and calendar.month_name[int(ta["month"])] == month
        ]
        if len(total) == 0:
            return -1
        return sum(total) / len(total)

    def display_monthly_average(self):
        average = self.calc_monthly_average()
        text = "${:.2f}".format(average)
        if average == -1:
            text = "No transactions during this month!"
        self.monthly_average_label.config(text=text)

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

def build_grid_label(parent, row, col, text="", colspan=1, sticky=tk.W):
    label = tk.Label(parent, text=text)
    label.grid(
        row=row,
        column=col,
        columnspan=colspan,
        sticky=sticky,
        padx=5,
        pady=5,
    )
    return label

def build_grid_entry(parent, row, col):
    entry = tk.Entry(parent)
    entry.grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)
    return entry

def build_grid_dropdown(
    parent,
    shownopt,
    options,
    row,
    col,
    errmsg="",
    defaultopt=None,
):
    if not options:
        build_grid_label(parent=parent, text=errmsg, row=row, col=col)
        return
    if defaultopt:
        shownopt.set(defaultopt)
    else:
        shownopt.set(options[0])
    dropdown = tk.OptionMenu(parent, shownopt, *options)
    dropdown.grid(row=row, column=col, sticky=tk.NSEW, padx=5, pady=5)
    return dropdown

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

def refresh_grid_dropdown(
    section_frame,
    dropdown_menu,
    shownopt,
    options,
    row,
    col,
    errmsg,
    defaultopt=None
):
    dropdown_menu = None
    dropdown_menu = build_grid_dropdown(
        parent=section_frame.frame,
        shownopt=shownopt,
        defaultopt=defaultopt,
        options=options,
        row=row,
        col=col,
        errmsg=errmsg,
    )

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
