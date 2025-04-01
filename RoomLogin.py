import customtkinter as ctk
from PIL import Image
from Dashboard import Dashboard
import sqlite3
from sqlite3 import Error

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 900
        window_height = 600
        position_top = int((screen_height - window_height) / 2) - 30
        position_left = int((screen_width - window_width) / 2)

        background_image = ctk.CTkImage(light_image=Image.open("images/bg.png"), size=(screen_width, screen_height))
        background_label = ctk.CTkLabel(self, image=background_image, text="")
        background_label.place(relwidth=1, relheight=1)

        self.title("Room Login")
        self.iconbitmap("images/icon.ico")
        self.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        self.HeadFrame = HeadFrame(self)
        self.HeadFrame.grid(row=0, column=0, sticky="nwe")

        self.LoginFrame = LoginFrame(self)
        self.LoginFrame.grid(row=1, column=0, sticky="n")

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

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        self.configure(width=500, height=336, fg_color="#FFFFFF", corner_radius=0)

        self.LoginLabel = ctk.CTkLabel(self, text="LOGIN", font=("Arial", 25, "bold"), text_color="#545454")
        self.LoginLabel.grid(row=0, column=0, sticky="nwe", pady=25)

        self.UserEntry = ctk.CTkEntry(self, placeholder_text="Enter RoomCode", height=40, placeholder_text_color="#545454", border_width=2,
                                      font=("Arial", 13, "bold"), fg_color="#F4F4F4", border_color="#CECECE", text_color="#545454", corner_radius=0)
        self.UserEntry.grid(row=1, column=0, sticky="nwe", padx=30)
        self.PassEntry = ctk.CTkEntry(self, placeholder_text="Enter Password", height=40, placeholder_text_color="#545454", border_width=2, show="*",
                                      font=("Arial", 13, "bold"), fg_color="#F4F4F4", border_color="#CECECE", text_color="#545454", corner_radius=0)
        self.PassEntry.grid(row=2, column=0, sticky="nwe", padx=30)

        self.ShowPassVar = ctk.BooleanVar()
        self.ShowPassCheck = ctk.CTkCheckBox(
            self, text="Show Password", variable=self.ShowPassVar, font=("Arial", 12, "bold"),
            text_color="#545454", hover_color="#115272", border_color="#545454",
            corner_radius=0, command=self.toggle_password, fg_color="#115272", checkbox_width=20, checkbox_height=20
        )
        self.ShowPassCheck.grid(row=3, column=0, sticky="w", padx=30, pady=5)

        self.LoginButton = ctk.CTkButton(self, text="Login", font=("Arial", 15, "bold"), height=40, corner_radius=0,
                                         fg_color="#115272", hover_color="#07212e", command=self.authenticate_room)
        self.LoginButton.grid(row=4, column=0, pady=20, padx=30, sticky="nwe")

    def toggle_password(self):
            if self.ShowPassVar.get():
                self.PassEntry.configure(show="")
            else:
                self.PassEntry.configure(show="*")

    def authenticate_room(self):
        room_code = self.UserEntry.get()
        password = self.PassEntry.get()

        if not room_code or not password:
            self.show_error("Please enter both room code and password")
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Rooms WHERE RoomCode = ? AND Password = ?",
                           (room_code, password))
            room = cursor.fetchone()

            if room:
                self.open_dashboard()
            else:
                self.show_error("Invalid room code or password")

        except Error as e:
            self.show_error("Login failed. Please try again.")
        finally:
            if conn:
                conn.close()

    def show_error(self, message):
        error_label = ctk.CTkLabel(self, text=message, text_color="red", font=("Arial", 12))
        error_label.grid(row=5, column=0, sticky="nwe", pady=5)
        self.after(3000, error_label.destroy)

    def open_dashboard(self):
        self.master.destroy()
        dashboard = Dashboard()
        dashboard.mainloop()

if __name__ == "__main__":
    app = Login()
    app.mainloop()