import calendar
import datetime
import json
import matplotlib.pyplot as plt
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

        self.view_ta_frame = StartViewTaFrame(parent=self)
        self.stats_frame = StartStatsFrame(parent=self)
        self.ta_frame = StartTaFrame(parent=self)
        self.cat_frame = StartCatFrame(parent=self)

    def refresh(self):
        self.parent.switch_frame(StartPage)

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

        self.parent.refresh()

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

        self.parent.refresh()

class StartStatsFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(side=tk.RIGHT, anchor=tk.N)
        self.parent = parent

        self.build()

    def build(self):
        self.frame = build_grid_frame(parent=self, anchor=tk.NE, cols=6)

        build_grid_label(
            parent=self.frame,
            text="Statistics Section",
            row=0,
            col=0,
            colspan=6,
            sticky=tk.N,
        )
        build_grid_label(
            parent=self.frame,
            text="Category",
            row=1,
            col=1,
            sticky=tk.N,
        )
        build_grid_label(
            parent=self.frame,
            text="Month",
            row=1,
            col=2,
            sticky=tk.N,
        )
        build_grid_label(
            parent=self.frame,
            text="Year",
            row=1,
            col=3,
            sticky=tk.N,
        )

        build_grid_label(
            parent=self.frame,
            text="Monthly Average",
            row=2,
            col=0,
        )
        self.average_monthly_ta_amt_selected = {
            "month": tk.StringVar(),
            "year": tk.StringVar(),
        }
        build_month_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_ta_amt_selected["month"],
            row=2,
            col=2,
        )
        self.average_monthly_year_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_ta_amt_selected["year"],
            row=2,
            col=3,
        )
        self.monthly_average_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=2,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=2,
            col=4,
            callback=self.display_monthly_average,
        )

        build_grid_label(
            parent=self.frame,
            text="Monthly Total",
            row=3,
            col=0,
        )
        self.total_monthly_ta_amt_selected = {
            "month": tk.StringVar(),
            "year": tk.StringVar(),
        }
        build_month_grid_dropdown(
            parent=self.frame,
            shownopt=self.total_monthly_ta_amt_selected["month"],
            row=3,
            col=2,
        )
        self.total_monthly_year_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.total_monthly_ta_amt_selected["year"],
            row=3,
            col=3,
        )
        self.monthly_total_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=3,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=3,
            col=4,
            callback=self.display_monthly_total,
        )

        build_grid_label(
            parent=self.frame,
            text="Monthly Category Average",
            row=4,
            col=0,
        )
        self.average_monthly_cat_ta_amt_selected = {
            "cat": tk.StringVar(),
            "month": tk.StringVar(),
            "year": tk.StringVar(),
        }
        self.average_monthly_cat_menu = build_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_cat_ta_amt_selected["cat"],
            options=data["categories"],
            row=4,
            col=1,
            errmsg="Create a category!",
        )
        build_month_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_cat_ta_amt_selected["month"],
            row=4,
            col=2,
        )
        self.average_monthly_cat_year_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.average_monthly_cat_ta_amt_selected["year"],
            row=4,
            col=3,
        )
        self.monthly_cat_average_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=4,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=4,
            col=4,
            callback=self.display_monthly_cat_average,
        )

        build_grid_label(
            parent=self.frame,
            text="Monthly Category Total",
            row=5,
            col=0,
        )
        self.total_monthly_cat_ta_amt_selected = {
            "cat": tk.StringVar(),
            "month": tk.StringVar(),
            "year": tk.StringVar(),
        }
        self.total_monthly_cat_menu = build_grid_dropdown(
            parent=self.frame,
            shownopt=self.total_monthly_cat_ta_amt_selected["cat"],
            options=data["categories"],
            row=5,
            col=1,
            errmsg="Create a category!",
        )
        build_month_grid_dropdown(
            parent=self.frame,
            shownopt=self.total_monthly_cat_ta_amt_selected["month"],
            row=5,
            col=2,
        )
        self.total_monthly_cat_year_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.total_monthly_cat_ta_amt_selected["year"],
            row=5,
            col=3,
        )
        self.monthly_cat_total_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=5,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=5,
            col=4,
            callback=self.display_monthly_cat_total,
        )

        build_grid_label(
            parent=self.frame,
            text="Yearly Average",
            row=6,
            col=0,
        )
        self.yearly_average_ta_amt_selected = tk.StringVar()
        self.yearly_average_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_average_ta_amt_selected,
            row=6,
            col=3,
        )
        self.yearly_average_amt_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=6,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=6,
            col=4,
            callback=self.display_yearly_average,
        )

        build_grid_label(
            parent=self.frame,
            text="Yearly Total",
            row=7,
            col=0,
        )
        self.yearly_total_ta_amt_selected = tk.StringVar()
        self.yearly_total_menu = build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_total_ta_amt_selected,
            row=7,
            col=3,
        )
        self.yearly_total_amt_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=7,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=7,
            col=4,
            callback=self.display_yearly_total,
        )

        build_grid_label(
            parent=self.frame,
            text="Yearly Category Average",
            row=8,
            col=0,
        )
        self.yearly_cat_average_ta_amt_selected = {
            "cat": tk.StringVar(),
            "year": tk.StringVar(),
        }
        build_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_cat_average_ta_amt_selected["cat"],
            options=data["categories"],
            row=8,
            col=1,
            errmsg="Create a category!",
        )
        build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_cat_average_ta_amt_selected["year"],
            row=8,
            col=3,
        )
        self.yearly_cat_average_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=8,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=8,
            col=4,
            callback=self.display_yearly_cat_average,
        )

        build_grid_label(
            parent=self.frame,
            text="Yearly Category Total",
            row=9,
            col=0,
        )
        self.yearly_cat_total_ta_amt_selected = {
            "cat": tk.StringVar(),
            "year": tk.StringVar(),
        }
        build_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_cat_total_ta_amt_selected["cat"],
            options=data["categories"],
            row=9,
            col=1,
            errmsg="Create a category!",
        )
        build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.yearly_cat_total_ta_amt_selected["year"],
            row=9,
            col=3,
        )
        self.yearly_cat_total_label = build_grid_label(
            parent=self.frame,
            text="<= Calculate!",
            row=9,
            col=5,
        )
        build_grid_button(
            parent=self.frame,
            text="Calculate",
            row=9,
            col=4,
            callback=self.display_yearly_cat_total,
        )

        build_grid_label(
            parent=self.frame,
            text="Graph Lifetime Transaction Amounts by Category",
            row=10,
            col=0,
        )
        build_grid_button(
            parent=self.frame,
            text="Graph",
            row=10,
            col=4,
            callback=self.graph_cat_vs_ta_amt,
        )

        build_grid_label(
            parent=self.frame,
            text="Graph Monthly Transaction Amounts in a Year",
            row=11,
            col=0,
        )
        self.monthly_tas_graph_year_selected = tk.StringVar()
        build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.monthly_tas_graph_year_selected,
            row=11,
            col=3,
        )
        build_grid_button(
            parent=self.frame,
            text="Graph",
            row=11,
            col=4,
            callback=self.graph_monthly_tas,
        )

    def graph_monthly_tas(self):
        months = [ calendar.month_abbr[i + 1] for i in range(12) ]
        amounts = [ 0 ] * len(months)
        for ta in data["transactions"]:
            amounts[int(ta["month"]) - 1] += float(ta["amount"])
        plt.bar(months, amounts)
        plt.title("Monthly Transactions")
        plt.xlabel("Month")
        plt.ylabel("Transaction Amount (in USD)")
        plt.grid(True)
        plt.show()

    def graph_cat_vs_ta_amt(self):
        amounts = [ 0 ] * len(data["categories"])
        for ta in data["transactions"]:
            i = data["categories"].index(ta["category"])
            amounts[i] += float(ta["amount"])
        plt.bar(data["categories"], amounts)
        plt.title("Transaction Amounts by Categories")
        plt.xlabel("Category")
        plt.ylabel("Transaction Amount (in USD)")
        plt.grid(True)
        plt.show()

    def calc_yearly_cat_total(self):
        year = self.yearly_cat_total_ta_amt_selected["year"].get()
        cat = self.yearly_cat_total_ta_amt_selected["cat"].get()
        return [
            float(ta["amount"]) for ta in data["transactions"] \
            if ta["year"] == year and ta["category"] == cat
        ]

    def display_yearly_cat_total(self):
        text = "${:.2f}".format(sum(self.calc_yearly_cat_total()))
        self.yearly_cat_total_label.config(text=text)

    def calc_yearly_cat_average(self):
        total = self.calc_yearly_cat_total()
        if len(total) == 0:
            return -1
        return sum(total) / len(total)

    def display_yearly_cat_average(self):
        average = self.calc_yearly_cat_average()
        text = "${:.2f}".format(average)
        if average == -1:
            text = "N/A"
        self.yearly_cat_average_label.config(text=text)

    def calc_yearly_total(self, year):
        total = [
            float(ta["amount"]) for ta in data["transactions"] \
            if ta["year"] == year
        ]
        return total

    def display_yearly_total(self):
        year = self.yearly_average_ta_amt_selected.get()
        text = "${:.2f}".format(sum(self.calc_yearly_total(year)))
        self.yearly_total_amt_label.config(text=text)

    def calc_yearly_average(self):
        year = self.yearly_average_ta_amt_selected.get()
        total = self.calc_yearly_total(year)
        if len(total) == 0:
            return -1
        return sum(total) / len(total)
    
    def display_yearly_average(self):
        average = self.calc_yearly_average()
        text = "${:.2f}".format(average)
        if average == -1:
            text = "N/A"
        self.yearly_average_amt_label.config(text=text)

    def calc_monthly_cat_total(self, month, year, category):
        total = [
            float(ta["amount"]) for ta in data["transactions"] \
            if ta["year"] == year \
            and calendar.month_name[int(ta["month"])] == month \
            and ta["category"] == category
        ]
        return total

    def display_monthly_cat_total(self):
        month = self.total_monthly_cat_ta_amt_selected["month"].get()
        year = self.total_monthly_cat_ta_amt_selected["year"].get()
        cat = self.total_monthly_cat_ta_amt_selected["cat"].get()
        text = "${:.2f}".format(
            sum(self.calc_monthly_cat_total(month, year, cat))
        )
        self.monthly_cat_total_label.config(text=text)

    def calc_monthly_cat_average(self):
        month = self.average_monthly_cat_ta_amt_selected["month"].get()
        year = self.average_monthly_cat_ta_amt_selected["year"].get()
        cat = self.average_monthly_cat_ta_amt_selected["cat"].get()
        total = self.calc_monthly_cat_total(month, year, cat)
        if len(total) == 0:
            return -1
        return sum(total) / len(total)

    def display_monthly_cat_average(self):
        average = self.calc_monthly_cat_average()
        text = "${:.2f}".format(average)
        if average == -1:
            text = "N/A"
        self.monthly_cat_average_label.config(text=text)

    def calc_monthly_total(self, month, year):
        total = [
            float(ta["amount"]) for ta in data["transactions"] \
            if ta["year"] == year \
            and calendar.month_name[int(ta["month"])] == month
        ]
        return total

    def display_monthly_total(self):
        month = self.total_monthly_ta_amt_selected["month"].get()
        year = self.total_monthly_ta_amt_selected["year"].get()
        text = "${:.2f}".format(sum(self.calc_monthly_total(month, year)))
        self.monthly_total_label.config(text=text)

    def calc_monthly_average(self):
        month = self.average_monthly_ta_amt_selected["month"].get()
        year = self.average_monthly_ta_amt_selected["year"].get()
        total = self.calc_monthly_total(month, year)
        if len(total) == 0:
            return -1
        return sum(total) / len(total)

    def display_monthly_average(self):
        average = self.calc_monthly_average()
        text = "${:.2f}".format(average)
        if average == -1:
            text = "N/A"
        self.monthly_average_label.config(text=text)

class StartViewTaFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.pack(side=tk.BOTTOM)
        self.parent = parent

        self.build()

    def build(self):
        self.frame = build_grid_frame(parent=self, cols=4)

        build_grid_label(
            parent=self.frame,
            text="View Transactions",
            row=0,
            col=0,
            colspan=4,
            sticky=tk.N,
        )

        build_grid_label(
            parent=self.frame,
            text="View for",
            row=1,
            col=0,
        )
        self.month_selected = tk.StringVar()
        build_month_grid_dropdown(
            parent=self.frame,
            shownopt=self.month_selected,
            row=1,
            col=1,
        )
        self.year_selected = tk.StringVar()
        build_year_grid_dropdown(
            parent=self.frame,
            shownopt=self.year_selected,
            row=1,
            col=2,
        )
        build_grid_button(
            parent=self.frame,
            text="View",
            row=1,
            col=3,
            callback=self.display_tas,
        )

    def display_tas(self):
        messages = ( "Category", "Date", "Description", "Amount")
        for i, m in enumerate(messages):
            build_grid_label(
                parent=self.frame,
                text=m,
                sticky=tk.N,
                row=2,
                col=i,
            )
            scrollbar = tk.Scrollbar(self.frame)
            talist = tk.Listbox(self.frame, yscrollcommand=scrollbar.set)
            talist.grid(row=3, column=i)
            for j, ta in enumerate(data["transactions"]):
                if calendar.month_name[int(ta["month"])] \
                        != self.month_selected.get() \
                    or ta["year"] != self.year_selected.get():
                        continue
                key = m.lower()
                text = f"[Entry {j + 1}] "
                if key == "date":
                    text += "{} {} {}".format(
                        ta["year"],
                        calendar.month_name[int(ta["month"])],
                        ta["day"],
                    )
                else:
                    if key == "amount":
                        text += "$"
                    text += ta[key]
                talist.insert(tk.END, text)
            scrollbar.config(command=talist.yview)
    
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

def build_month_grid_dropdown(parent, shownopt, row, col):
    calendar_months = [ calendar.month_name[i + 1] for i in range(12) ]
    build_grid_dropdown(
        parent=parent,
        shownopt=shownopt,
        options=calendar_months,
        row=row,
        col=col,
        defaultopt=calendar.month_name[datetime.datetime.now().month],
    )

def build_year_grid_dropdown(parent, shownopt, row, col):
    return build_grid_dropdown(
        parent=parent,
        shownopt=shownopt,
        options=data["years"],
        row=row,
        col=col,
        errmsg="Add a transaction!",
        defaultopt=str(datetime.datetime.now().year),
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
