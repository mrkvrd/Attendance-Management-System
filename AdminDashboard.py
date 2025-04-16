import customtkinter as ctk
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

        self.window_width = 1080
        self.window_height = 720
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

        self.room_tab = self.tab("Rooms")
        self.room_tab.grid_columnconfigure((0,1), weight=1)
        self.room_tab.grid_rowconfigure(0, weight=0)
        self.room_tab.grid_rowconfigure(1, weight=0)
        self.room_tab.grid_rowconfigure(2, weight=3)

        self.dropdown_frame = ctk.CTkFrame(self.room_tab, fg_color="transparent")
        self.dropdown_frame.grid(row=0, column=1, sticky="news")
        self.dropdown_frame.grid_columnconfigure(0, weight=1)
        self.dropdown_frame.grid_rowconfigure((0,1), weight=1)

        self.room_label = ctk.CTkLabel(
            self.dropdown_frame,
            text="Select Room:",
            font=("Arial", 18, "bold"),
            text_color="#115272"
        )
        self.room_label.grid(row=0, column=0, sticky="s", pady=(0, 5))

        self.dropdown = ctk.CTkComboBox(
            self.dropdown_frame, button_color="#28A745", button_hover_color="#208637",
            justify="center", state="readonly", dropdown_fg_color="#ffffff",
            font=("Arial", 18, "bold"), text_color="#115272",
            dropdown_font=("Arial", 15, "bold"),
            corner_radius=0,
            width=300, height=35, border_color="#115272"
        )
        self.dropdown.grid(row=1, column=0, sticky="n", pady=(5, 0))
        self.load_room_ids()

        self.info_frame = InfoFrame(self.room_tab)
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_header = TableHeader(self.room_tab)
        self.table_header.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10)

        self.table_frame = TableFrame(self.room_tab)
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

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


if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()