import customtkinter as ctk
import tkinter as ttk
from tkinter import ttk
from PIL import Image
import os
import sys
from tkinter import messagebox
from Dashboard import InfoFrame, TableFrame
from Dashboard import TableHeader as OriginalTableHeader
import sqlite3

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.window_width = 1280
        self.window_height = 800
        self.configure(fg_color="#ffffff")

        self.title("Admin")
        self.iconbitmap("images/icon.ico")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.after(100, lambda: self.state("zoomed"))
        self.bind("<Map>", self.on_restore)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.HeadFrame = HeadFrame(self)
        self.HeadFrame.grid(row=0, column=0, columnspan=2, sticky="nwe")

        self.MainView = MainView(self)
        self.MainView.grid(row=1, column=1, sticky="nwes")

        self.TabFrame = TabFrame(self, self.MainView)
        self.TabFrame.grid(row=1, column=0, sticky="nws")

    def on_restore(self, event=None):
        if self.state() == "normal":
            position_top = int((self.screen_height - self.window_height) / 2) - 30
            position_left = int((self.screen_width - self.window_width) / 2)
            self.geometry(f"{self.window_width}x{self.window_height}+{position_left}+{position_top}")

class HeadFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((0,1),weight=1)
        self.grid_columnconfigure((0,1,2),weight=1)
        self.configure(fg_color="#115272", corner_radius=0)

        self.Label1 = ctk.CTkLabel(self, text="Quezon City University - RFID Attendance System", text_color="white", font=("Arial", 25, "bold"))
        self.Label1.grid(row=0, column=1, sticky="nsew",pady=5)
        self.Label2 = ctk.CTkLabel(self, text="San Bartolome Campus", text_color="white", font=("Arial", 15))
        self.Label2.grid(row=1, column=1, sticky="nsew",pady=3)

        self.Qcuimg = ctk.CTkImage(light_image=Image.open("images/img_1.png"), size=(40, 40))
        self.ImageLabel1 = ctk.CTkLabel(self, image=self.Qcuimg, text="")
        self.ImageLabel1.grid(row=0, column=0, rowspan=2, pady=3)
        self.Qcimg = ctk.CTkImage(light_image=Image.open("images/img_2.png"), size=(53, 40))
        self.ImageLabel2 = ctk.CTkLabel(self, image=self.Qcimg, text="")
        self.ImageLabel2.grid(row=0, column=2, rowspan=2, pady=3)

class TabFrame(ctk.CTkFrame):
    def __init__(self, master, main_view):
        super().__init__(master)
        self.main_view = main_view

        self.configure(fg_color="#115272", corner_radius=0, width=275)
        self.grid_rowconfigure((0,1,2,3), weight=0)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.MainView = main_view
        self.MenuLabel = ctk.CTkLabel(self, fg_color="#45b45d", width=260, height=50, font=("Arial", 20, "bold"), text_color="#ffffff", text="Menu")
        self.MenuLabel.grid(row=0, column=0, sticky="nwe", pady=15)

        self.RoomsButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                         text_color="#ffffff", text="Rooms", hover_color="#1a6e98", command=self.RoomsTab)
        self.RoomsButton.grid(row=1, column=0, sticky="nwe", pady=5)
        self.RegisterButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                         text_color="#ffffff", text="Student Register", hover_color="#1a6e98", command=self.StudentTab)
        self.RegisterButton.grid(row=2, column=0, sticky="nwe", pady=5)
        self.ScheduleButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                         text_color="#ffffff", text="Schedule", hover_color="#1a6e98", command=self.ScheduleTab)
        self.ScheduleButton.grid(row=3, column=0, sticky="nwe", pady=5)

        self.LogoutButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 15, "bold"),
                                         text_color="#ffffff", text="Logout", hover_color="#1a6e98", command=self.Logout)
        self.LogoutButton.grid(row=4, column=0, sticky="swe")

    def RoomsTab(self):
        self.main_view.set("Rooms")

    def StudentTab(self):
        self.main_view.set("Student Register")

    def ScheduleTab(self):
        self.main_view.set("Schedule")

    def Logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.master.destroy()
            python = sys.executable
            os.execv(python, [python, "AdminLogin.py"])


class TableHeader(OriginalTableHeader):
    def __init__(self, master):
        super().__init__(master)

        self.ComboBox.destroy()

        self.ComboBox = ctk.CTkComboBox(self,
                                        values=["Dashboard", "View Room Schedule"],
                                        corner_radius=0,
                                        border_color="#115272",
                                        button_color="#28A745",
                                        button_hover_color="#208637",
                                        text_color="#ffffff",
                                        fg_color="#115272",
                                        justify="right",
                                        dropdown_font=("Arial", 13, "bold"),
                                        state="readonly",
                                        dropdown_fg_color="#ffffff",
                                        font=("Arial", 15, "bold"),
                                        command=self.on_select)
        self.ComboBox.grid(row=0, column=2, sticky="e", pady=5, padx=20)

class MainView(ctk.CTkTabview):
    def __init__(self, master):
        super().__init__(master)

        self.add("Rooms")
        self.add("Student Register")
        self.add("Schedule")

        self.configure(fg_color="#ffffff", corner_radius=0)
        self._segmented_button.grid_forget()

        self.setup_rooms_tab()

        self.setup_schedule_tab()

    def setup_rooms_tab(self):
        self.room_tab = self.tab("Rooms")
        self.room_tab.grid_columnconfigure((0, 1), weight=1)
        self.room_tab.grid_rowconfigure(0, weight=0)
        self.room_tab.grid_rowconfigure(1, weight=0)
        self.room_tab.grid_rowconfigure(2, weight=3)

        self.dropdown_frame = ctk.CTkFrame(self.room_tab, fg_color="transparent")
        self.dropdown_frame.grid(row=0, column=1, sticky="news")
        self.dropdown_frame.grid_columnconfigure(0, weight=1)
        self.dropdown_frame.grid_rowconfigure((0, 1), weight=1)

        self.room_label = ctk.CTkLabel(
            self.dropdown_frame,
            text="Select Room:",
            font=("Arial", 18, "bold"),
            text_color="#115272"
        )
        self.room_label.grid(row=0, column=0, sticky="s", pady=(0, 5))

        self.dropdown = ctk.CTkComboBox(
            self.dropdown_frame,
            button_color="#28A745",
            button_hover_color="#208637",
            justify="center",
            state="readonly",
            dropdown_fg_color="#ffffff",
            font=("Arial", 18, "bold"),
            text_color="#115272",
            dropdown_font=("Arial", 15, "bold"),
            corner_radius=0,
            width=300,
            height=35,
            border_color="#115272"
        )
        self.dropdown.grid(row=1, column=0, sticky="n", pady=(5, 0))

        self.info_frame = InfoFrame(self.room_tab)
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_header = TableHeader(self.room_tab)
        self.table_header.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10)

        self.table_frame = TableFrame(self.room_tab)
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.load_room_ids()

    def setup_schedule_tab(self):
        self.Sched_tab = self.tab("Schedule")
        self.Sched_tab.grid_columnconfigure(0, weight=1)
        self.Sched_tab.grid_rowconfigure(0, weight=0)
        self.Sched_tab.grid_rowconfigure(1, weight=1)

        self.SchedTableFrame = SchedTableFrame(self.Sched_tab)
        self.SchedTableFrame.grid(row=1, column=0, sticky="nsew")

        self.AddSchedFrame = AddScheduleFrame(self.Sched_tab, self.SchedTableFrame)
        self.AddSchedFrame.grid(row=0, column=0, sticky="nsew")

        self.SchedTableFrame.grid_columnconfigure(0, weight=1)
        self.SchedTableFrame.grid_rowconfigure(0, weight=1)

    def load_room_ids(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT RoomCode FROM Rooms")
            room_ids = [str(row[0]) for row in cursor.fetchall()]
            self.dropdown.configure(values=room_ids)
            conn.close()
        except sqlite3.Error as e:
            print("Database error:", e)

class AddScheduleFrame(ctk.CTkFrame):
    def __init__(self, master, table_frame):
        super().__init__(master)

        self.table_frame = table_frame
        self.configure(fg_color="#ffffff", height=300)
        self.grid_propagate(False)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.create_widgets()
        self.load_room_ids()

    def create_widgets(self):
        self.Sched_tab_Head = ctk.CTkLabel(self,
                                           text="ADD CLASS SCHEDULE",
                                           font=("Arial", 25, "bold", "underline"),
                                           text_color="#545454")
        self.Sched_tab_Head.grid(row=0, column=0, columnspan=2, sticky="nw", padx=30)

        self.Subject_Entry = self.create_entry("Enter Subject Code", 1, 0)
        self.Section_Entry = self.create_entry("Enter Section", 1, 1)
        self.Professor_Entry = self.create_entry("Enter Subject Professor", 1, 2)

        self.Day_Dropdown = self.create_day_dropdown(2, 0)

        times = [f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}" for hour in range(7, 22)]
        self.Time_in = self.create_time_dropdown("Time In", times, 2, 1)
        self.Time_out = self.create_time_dropdown("Time Out", times, 2, 2)

        self.Room_Dropdown = self.create_room_dropdown(3, 0)
        self.SaveSched_Button = self.create_save_button(3, 1)

    def create_entry(self, placeholder, row, column):
        entry = ctk.CTkEntry(self,
                             width=300,
                             height=40,
                             corner_radius=0,
                             placeholder_text=placeholder,
                             font=("Arial", 15, "bold"))
        entry.grid(row=row, column=column, sticky="nw", padx=40)
        return entry

    def create_day_dropdown(self, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly",
                                   values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        dropdown.set("Day")
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_time_dropdown(self, default_text, values, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly",
                                   values=values)
        dropdown.set(default_text)
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_room_dropdown(self, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly")
        dropdown.set("Room")
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_save_button(self, row, column):
        button = ctk.CTkButton(self,
                               width=300,
                               height=50,
                               font=("Arial", 15, "bold"),
                               text_color="#ffffff",
                               fg_color="#45b45d",
                               hover_color="#308042",
                               corner_radius=0,
                               text="SAVE SCHEDULE",
                               command=self.save_schedule)
        button.grid(row=row, column=column, sticky="nw", padx=40)
        return button

    def load_room_ids(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT RoomCode FROM Rooms")
            room_ids = [str(row[0]) for row in cursor.fetchall()]
            self.Room_Dropdown.configure(values=room_ids)
            conn.close()
        except sqlite3.Error as e:
            print("Database error:", e)

    def save_schedule(self):
        subject = self.Subject_Entry.get()
        section = self.Section_Entry.get()
        professor = self.Professor_Entry.get()
        day = self.Day_Dropdown.get()
        time_in = self.Time_in.get()
        time_out = self.Time_out.get()
        room = self.Room_Dropdown.get()

        if not all([subject, section,
                    professor]) or day == "Day" or time_in == "Time In" or time_out == "Time Out" or room == "Room":
            messagebox.showwarning("Warning", "Please fill in all fields before saving.")
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Schedule (Subject, Section, Professor, Day, TimeIn, TimeOut, Room)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (subject, section, professor, day, time_in, time_out, room))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Schedule saved successfully!")
            self.clear_form()
            self.table_frame.load_data()  # Refresh the table

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Selected Room does not exist in Rooms table.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def clear_form(self):
        self.Subject_Entry.delete(0, "end")
        self.Section_Entry.delete(0, "end")
        self.Professor_Entry.delete(0, "end")
        self.Day_Dropdown.set("Day")
        self.Time_in.set("Time In")
        self.Time_out.set("Time Out")
        self.Room_Dropdown.set("Room")


class SchedTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(corner_radius=10, fg_color="#f5f5f5")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=40,
                        fieldbackground="#f8f8f8",
                        font=("Arial", 12, "bold"))
        style.configure("Treeview.Heading",
                        font=("Arial", 14, "bold"),
                        background="#115272",
                        foreground="white")
        style.map("Treeview.Heading",
                  background=[("active", "#115272"), ("pressed", "#115272")],
                  foreground=[("active", "white"), ("pressed", "white")])

        columns = ("Subject", "Section", "Professor", "Day", "Time In", "Time Out", "Room", "Action")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        self.tree.bind("<Button-1>", self.on_treeview_click)

        col_widths = {
            "Subject": 120, "Section": 80, "Professor": 150,
            "Day": 80, "Time In": 80, "Time Out": 80,
            "Room": 80, "Action": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths[col], anchor="center")

            if col != "Action":
                self.tree.heading(col, command=lambda _col=col: self.sort_treeview_by_column(_col))

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.sort_frame = ctk.CTkFrame(self, fg_color="#f5f5f5")
        self.sort_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.sort_label = ctk.CTkLabel(self.sort_frame, text="Sort by:", font=("Arial", 12, "bold"))
        self.sort_label.grid(row=0, column=0, padx=5, pady=5)

        self.sort_button = ctk.CTkButton(
            self.sort_frame,
            text="Day & Time",
            font=("Arial", 12, "bold"),
            fg_color="#115272",
            hover_color="#1a6e98",
            corner_radius=5,
            height=30,
            command=self.sort_by_day_and_time
        )
        self.sort_button.grid(row=0, column=1, padx=5, pady=5)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.tree.tag_configure("evenrow", background="#f0f0f0")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.day_order = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
        }

        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Subject, Section, Professor, Day, TimeIn, TimeOut, Room FROM Schedule")
            rows = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert("", "end",
                                 values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], "Archive | Delete"),
                                 tags=(tag,))

            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def sort_treeview_by_column(self, column):
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]

        items.sort()

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))

    def sort_by_day_and_time(self):
        items = []
        for item in self.tree.get_children(""):
            values = self.tree.item(item, "values")
            day = values[3]
            time_in = values[4]

            day_value = self.day_order.get(day, 99)

            time_parts = time_in.split()
            if len(time_parts) == 2:
                time_value, am_pm = time_parts
                hours, minutes = time_value.split(":")
                hours = int(hours)

                if am_pm == "PM" and hours < 12:
                    hours += 12
                elif am_pm == "AM" and hours == 12:
                    hours = 0

                time_value = hours * 60 + int(minutes)
            else:
                time_value = 0

            items.append((day_value, time_value, item))

        items.sort()

        for index, (_, _, item) in enumerate(items):
            self.tree.move(item, "", index)

            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))

        messagebox.showinfo("Success", "Schedule sorted by day and time!")

    def on_treeview_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if column == "#8":
                x, y, width, height = self.tree.bbox(item, column)
                if event.x > x + width / 2:
                    self.delete_schedule(item)
                else:
                    self.archive_schedule(item)

    def archive_schedule(self, item):
        values = self.tree.item(item, "values")
        print(f"Archive action for: {values[:7]}")
        self.tree.item(item, values=(*values[:7], "✔Archived | Delete"))

    def delete_schedule(self, item):
        values = self.tree.item(item, "values")
        subject = values[0]
        section = values[1]
        day = values[3]
        time_in = values[4]
        time_out = values[5]
        room = values[6]

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete this schedule?\n\nSubject: {subject}\nSection: {section}\nDay: {day}\nTime: {time_in} - {time_out}\nRoom: {room}")

        if confirm:
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM Schedule 
                    WHERE Subject = ? AND Section = ? AND Day = ? AND TimeIn = ? AND TimeOut = ? AND Room = ?
                """, (subject, section, day, time_in, time_out, room))

                conn.commit()
                conn.close()

                self.tree.delete(item)

                messagebox.showinfo("Success", "Schedule deleted successfully!")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting: {e}")
        else:
            print("Delete operation cancelled")

if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()