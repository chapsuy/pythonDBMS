import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from db import get_products
# --- Main Application Class ---
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("Inventory & Order Management System")
       
        # After self.geometry("1100x650")
        self.update_idletasks()  # Make sure the window size is calculated

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate x and y coordinates to center the window
        window_width = 1100
        window_height = 650
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set the geometry including position
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        
        self.configure(bg="#F5F6FA")

        # Containers
        self.active_frame = None

        # Load icons
        self.product_icon = self.load_icon("product_icon.png", (120, 120))
        self.order_icon = self.load_icon("order_icon.png", (120, 120))
        self.income_icon = self.load_icon("income_icon.png", (120, 120))

        # Start with login screen
        self.show_login()

    # Load image helper
    def load_icon(self, path, size):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.ANTIALIAS)
            return ImageTk.PhotoImage(img)
        except:
            return None

    # Clear previous frame
    def switch_frame(self, new_frame):
        if self.active_frame is not None:
            self.active_frame.destroy()
        self.active_frame = new_frame
        self.active_frame.pack(fill="both", expand=True)

    # --- LOGIN PANEL ---
    def show_login(self):
        frame = tk.Frame(self, bg="#F5F6FA")

        title = tk.Label(frame, text="ADMIN LOGIN", font=("Arial", 26, "bold"), bg="#F5F6FA", fg="#2C3A47")
        title.pack(pady=40)

        form = tk.Frame(frame, bg="#F5F6FA")
        form.pack()

        tk.Label(form, text="Username", font=("Arial", 14), bg="#F5F6FA").grid(row=0, column=0, pady=5, sticky="w")
        username_entry = tk.Entry(form, font=("Arial", 14), width=25)
        username_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Password", font=("Arial", 14), bg="#F5F6FA").grid(row=1, column=0, pady=5, sticky="N")
        password_entry = tk.Entry(form, font=("Arial", 14), width=25, show="*")
        password_entry.grid(row=1, column=1, pady=5)

        login_btn = tk.Button(frame, text="Login", font=("Arial", 16, "bold"), bg="#1B9CFC", fg="white", width=12,
                              command=self.show_dashboard)
        login_btn.pack(pady=30)

        self.switch_frame(frame)

    # --- DASHBOARD PANEL ---
    def show_dashboard(self):
        frame = tk.Frame(self, bg="#FFFFFF", padx=40, pady=40)

        header = tk.Label(frame, text="Dashboard", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#2C3A47")
        header.pack(anchor="n", pady=(0, 30))

        # ICON GRID
        grid = tk.Frame(frame, bg="#FFFFFF")
        grid.pack(pady=20)

        # Product Icon Button
        product_frame = self.create_icon_button(
            grid,
            self.product_icon,
            "Products",
            self.show_products)
        product_frame.grid(row=0, column=0, padx=20)

        # Orders Icon Button
        order_frame = self.create_icon_button(grid, self.order_icon, "Orders", self.show_orders)
        order_frame.grid(row=1, column=0, padx=20)

        # Income Reports
        income_frame = self.create_icon_button(grid, self.income_icon, "Income Report", self.show_income)
        income_frame.grid(row=2, column=0, padx=20)

        self.switch_frame(frame)

    # Helper to create icon buttons
    def create_icon_button(self, parent, icon, label, command):
        frame = tk.Frame(parent, bg="#FFFFFF")
        btn = tk.Button(frame, image=icon, command=command, relief="flat", bg="#FFFFFF", activebackground="#F0F0F0")
        btn.pack()

        lbl = tk.Label(
            frame, 
            text=label, 
            font=("Arial", 14, "bold"), 
            bg="#FDFDFD",
            fg="#2C3A47",
            relief="solid",
            borderwidth=2,
            width=18,
            height=2,
            anchor="center",
            padx=10,
            pady=5
              )
        lbl.pack(pady=5)


        for widget in (frame, btn, lbl):
             widget.bind("<Button-1>", lambda e: command())

        return frame

    # --- PRODUCT PANEL ---
    def show_products(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)

        title = tk.Label(frame, text="Product Management", font=("Arial", 22, "bold"), bg="#F5F6FA", fg="#2C3A47")
        title.pack(anchor="w", pady=10)

        #Return button
        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                       bg="#BDC3C7", fg="#2C3A47", width=10,
                       relief="flat", command=self.show_dashboard)
        return_btn.pack(side="top", anchor="ne", padx=10, pady=10)

        # Product Form Section
        form = tk.Frame(frame, bg="#F5F6FA")
        form.pack(anchor="w", pady=10)

        tk.Label(form, text="Product Name", font=("Arial", 14), bg="#F5F6FA").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(form, font=("Arial", 14), width=30).grid(row=0, column=1, padx=5)

        tk.Label(form, text="Price", font=("Arial", 14), bg="#F5F6FA").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(form, font=("Arial", 14), width=30).grid(row=1, column=1, padx=5)

        tk.Label(form, text="Stock", font=("Arial", 14), bg="#F5F6FA").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(form, font=("Arial", 14), width=30).grid(row=2, column=1, padx=5)

        # Buttons
        btn_frame = tk.Frame(frame, bg="#F5F6FA")
        btn_frame.pack(anchor="w", pady=10)

        tk.Button(btn_frame, text="Add", width=12, bg="#20BF6B", fg="white", font=("Arial", 12, "bold"), relief="flat").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=12, bg="#3867D6", fg="white", font=("Arial", 12, "bold"), relief="flat").grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=12, bg="#FC5C65", fg="white", font=("Arial", 12, "bold"), relief="flat").grid(row=0, column=2, padx=5)

        # Table
        table_frame = tk.Frame(frame)
        table_frame.pack(fill="both", expand=True, pady=20)

        columns = ("ID", "Name", "Price", "Stock")
        table = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=150, anchor="center")

        table.pack(fill="both", expand=True)


        # REFRESH TABLE
        def refresh_table():
            for item in table.get_children():
                table.delete(item)

            products = get_products()
            for prod in products:
                table.insert("", "end", values=prod)

        refresh_table()        

        self.switch_frame(frame)

    # --- ORDER PANEL ---
    def show_orders(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)

        title = tk.Label(frame, text="Order Management", font=("Arial", 22, "bold"), bg="#F5F6FA")
        title.pack(anchor="n", pady=10)

        #Return button
        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                       bg="#BDC3C7", fg="#2C3A47", width=10,
                       relief="flat", command=self.show_dashboard)
        return_btn.pack(side="top", anchor="ne", padx=10, pady=10)

        # TODO: Add CRUD Order UI

        self.switch_frame(frame)

    # --- INCOME PANEL ---
    def show_income(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)

        title = tk.Label(frame, text="Income Report", font=("Arial", 22, "bold"), bg="#F5F6FA")
        title.pack(anchor="n", pady=10)

        #Return button
        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                       bg="#BDC3C7", fg="#2C3A47", width=10,
                       relief="flat", command=self.show_dashboard)
        return_btn.pack(side="top", anchor="ne", padx=10, pady=10)

        # TODO: Add Income Tables/Graphs

        self.switch_frame(frame)


# Run the app
if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
