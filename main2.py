import tkinter as tk
from tkinter import ttk, messagebox, simpledialog 
from PIL import Image, ImageTk
from db import get_products, handle_add_or_update, update_product, delete_product ,check_user_credentials
from db import get_orders, create_new_order, delete_order, update_payment_status, get_income_report, get_order_items


class StatusDialog(tk.Toplevel):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.order_id = order_id
        self.transient(parent) 
        self.grab_set()        
        self.title(f"Change Status for Order {order_id}")
        self.result_status = None
        
   
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        self.update_idletasks() 
        dialog_width = 300 
        dialog_height = 150 
        
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')

        
        ttk.Label(self, text="Select New Status:", font=("Arial", 12, "bold")).pack(pady=10)

        # Buttons 
        statuses = ['Paid', 'Pending', 'Cancelled']
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        for status in statuses:
            ttk.Button(
                button_frame, 
                text=status, 
                command=lambda s=status: self.select_status(s)
            ).pack(side=tk.LEFT, padx=5)

    def select_status(self, status):
        """Called when a status button is pressed."""
        self.result_status = status
        self.destroy() 
        
    def show(self):
        """Waits for the user to make a selection."""
        self.wait_window(self)
        return self.result_status
    
#  Main Application Class 
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        
        self.title("Order Flow Inventory & Order Management System")
        
       
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 1100
        window_height = 650
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.configure(bg="#F5F6FA")

        
        self.active_frame = None

        # Load icons
        self.product_icon = self.load_icon("product_icon.png", (120, 120))
        self.order_icon = self.load_icon("order_icon.png", (120, 120))
        self.income_icon = self.load_icon("income_icon.png", (120, 120))

       
        self.show_login()

    # Load image helper
    def load_icon(self, path, size):
        try:
            img = Image.open(path)
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            # Fallback if image files are missing
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

        tk.Label(form, text="Username ", font=("Arial", 14), bg="#F5F6FA").grid(row=0, column=0, pady=5, sticky="w")
        self.username_entry = tk.Entry(form, font=("Arial", 14), width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        tk.Label(form, text="Password ", font=("Arial", 14), bg="#F5F6FA").grid(row=1, column=0, pady=5, sticky="w")
        self.password_entry = tk.Entry(form, font=("Arial", 14), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)


        self.login_message_label = tk.Label(frame, text="", fg="red", bg="#F5F6FA", font=("Arial", 12))
        self.login_message_label.pack(pady=10)


        login_btn = tk.Button(frame, 
        text="Login", 
        font=("Arial", 16, "bold"), 
        bg="#1B9CFC", fg="white",
            width=12,
        command=self.authenticate_user)
        login_btn.pack(pady=30)
        
        self.switch_frame(frame)

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get() 
        
        
        stored_password = check_user_credentials(username) 
        
        if stored_password:
            
            if password == stored_password:
                self.login_message_label.config(text="")
                self.show_dashboard()
            else:
                self.login_message_label.config(text="Invalid Username or Password.", fg="red")
                self.password_entry.delete(0, tk.END)
        else:
            
            self.login_message_label.config(text="Invalid Username or Password.", fg="red")
            self.password_entry.delete(0, tk.END) 


    # DASHBOARD PANEL 
    def show_dashboard(self):
        frame = tk.Frame(self, bg="#FFFFFF", padx=40, pady=40)

        logout_btn = tk.Button(
            frame, 
            text="Logout", 
            font=("Arial", 12, "bold"), 
            bg="#FC5C65", 
            fg="white", 
            relief="flat", 
            command=self.show_login
        )
        logout_btn.place(relx=1.0, rely=0, x=-20, y=20, anchor="ne") 

        header = tk.Label(frame, text="Dashboard", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#2C3A47")
        header.pack(anchor="n", pady=(0, 30))
        
       
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

        # Income Report
        income_frame = self.create_icon_button(grid, self.income_icon, "Income Report", self.show_income)
        income_frame.grid(row=2, column=0, padx=20)

        self.switch_frame(frame)

    
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

    
    def show_products(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)

        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                             bg="#BDC3C7", fg="#2C3A47", width=10,
                             relief="flat", command=self.show_dashboard)
        return_btn.place(relx=1.0, rely=0, x=-20, y=20, anchor="ne") 
        
        title = tk.Label(frame, text="Product Management", font=("Arial", 22, "bold"), bg="#F5F6FA", fg="#2C3A47")
        title.pack(anchor="w", pady=(0, 10))

        
        self.product_status_label = tk.Label(frame, text="", bg="#F5F6FA", font=("Arial", 12, "bold"))
        self.product_status_label.pack(anchor="w", pady=(5, 5))

        
        form = tk.Frame(frame, bg="#F5F6FA")
        form.pack(anchor="w", pady=10)

       
        tk.Label(form, text="Product Name", font=("Arial", 14), bg="#F5F6FA").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = tk.Entry(form, font=("Arial", 14), width=30)
        name_entry.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Price", font=("Arial", 14), bg="#F5F6FA").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        price_entry = tk.Entry(form, font=("Arial", 14), width=30)
        price_entry.grid(row=1, column=1, padx=5)

        tk.Label(form, text="Stock", font=("Arial", 14), bg="#F5F6FA").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        stock_entry = tk.Entry(form, font=("Arial", 14), width=30)
        stock_entry.grid(row=2, column=1, padx=5)
        
        
        table_frame = tk.Frame(frame)
        table_frame.pack(fill="both", expand=True, pady=(20, 0)) 
        
        columns = ("ID", "Name", "Price", "Stock")
        table = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        table.pack(side='left', fill="both", expand=True)
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=150, anchor="center")

       
        def refresh_table():
            for item in table.get_children():
                table.delete(item)

            products = get_products()
            for prod in products:
                table.insert("", "end", values=prod)

       
        def select_item(event):
            selected_item = table.focus()
            
            if selected_item:
                values = table.item(selected_item, 'values')
                
                name_entry.delete(0, tk.END)
                price_entry.delete(0, tk.END)
                stock_entry.delete(0, tk.END)
                
                name_entry.insert(0, values[1])
                price_entry.insert(0, values[2])
                stock_entry.insert(0, values[3]) 

        
        table.bind("<<TreeviewSelect>>", select_item)

      
        def add_product_btn():
            try:
                name = name_entry.get()
                price = float(price_entry.get())
                
                stock_input = stock_entry.get()
                if not stock_input:
                    tk.messagebox.showerror("Input Error", "Stock quantity is required for an Add operation.")
                    self.product_status_label.config(text="Stock quantity required.", fg="red")
                    return
                
                stock = int(stock_input)
                
                message, success = handle_add_or_update(name, price, stock) 
                
                if success:
                    refresh_table()
                    self.product_status_label.config(text=message, fg="green")
                    
                    name_entry.delete(0, tk.END)
                    price_entry.delete(0, tk.END)
                    stock_entry.delete(0, tk.END)
                else:
                    self.product_status_label.config(text=message, fg="red")
                    
            except ValueError:
                tk.messagebox.showerror("Input Error", "Price must be a number and Stock must be an integer.")
                self.product_status_label.config(text="Input Error: Check Price and Stock fields.", fg="red")

        def update_product_btn():
            selected = table.focus()
            if selected:
                try:
                    values = table.item(selected, "values")
                    product_id = values[0]
                    name = name_entry.get()
                    price = float(price_entry.get())
                    
                  
                    new_stock_input = stock_entry.get()
                    if new_stock_input:
                        stock = int(new_stock_input)
                    else:
                        stock = int(values[3]) 
                    
                    if update_product(product_id, name, price, stock):
                        refresh_table()
                        self.product_status_label.config(text=f"Product ID {product_id} updated successfully.", fg="green")

                        name_entry.delete(0, tk.END)
                        price_entry.delete(0, tk.END)
                        stock_entry.delete(0, tk.END)
                        
                except ValueError:
                    tk.messagebox.showerror("Input Error", "Price must be a number and Stock must be an integer.")
                    self.product_status_label.config(text="Input Error: Check Price and Stock fields.", fg="red")
                except Exception as e:
                    tk.messagebox.showerror("DB Error", f"Failed to update: {e}")
                    self.product_status_label.config(text="Database Update Error.", fg="red")

        def delete_product_btn():
            selected = table.focus()
            if selected:
                if tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected product?"):
                    values = table.item(selected, "values")
                    product_id = values[0]
                    if delete_product(product_id):
                        refresh_table()
                        self.product_status_label.config(text=f"Product ID {product_id} deleted successfully.", fg="green")

                        name_entry.delete(0, tk.END)
                        price_entry.delete(0, tk.END)
                        stock_entry.delete(0, tk.END)
                    else:
                         self.product_status_label.config(text="Delete failed. Product may be linked to an order.", fg="red")

       
        btn_frame = tk.Frame(frame, bg="#F5F6FA")
        btn_frame.pack(anchor="w", pady=10)
        
        tk.Button(btn_frame, text="Add", width=12, bg="#20BF6B", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", command=add_product_btn).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Update", width=12, bg="#3867D6", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", command=update_product_btn).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete", width=12, bg="#FC5C65", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", command=delete_product_btn).grid(row=0, column=2, padx=5)
        
       
        refresh_table() 
        
        self.switch_frame(frame)

   
    #  ORDER PANEL 
    
    def show_orders(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)
        
       
        self.current_cart = {} 
        self.current_total = tk.StringVar(value="0.00")
        
        
        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                               bg="#BDC3C7", fg="#2C3A47", width=10,
                               relief="flat", command=self.show_dashboard)
        return_btn.place(relx=1.0, rely=0, x=-20, y=20, anchor="ne")

        title = tk.Label(frame, text="Order & POS Management", font=("Arial", 22, "bold"), bg="#F5F6FA", fg="#2C3A47")
        title.pack(anchor="w", pady=(0, 10))

        self.order_status_label = tk.Label(frame, text="", bg="#F5F6FA", font=("Arial", 12, "bold"))
        self.order_status_label.pack(anchor="w", pady=(5, 5))

        
        main_split = tk.Frame(frame, bg="#F5F6FA")
        main_split.pack(fill="both", expand=True)

      
        new_order_panel = tk.Frame(main_split, bg="#F5F6FA")
        new_order_panel.pack(side="left", fill="y", padx=(0, 20))
        
        total_frame = tk.Frame(new_order_panel, bg="#FFFFFF", padx=10, pady=5, relief="raised")
        total_frame.pack(fill="x", pady=(0, 10))
        tk.Label(total_frame, text="ORDER TOTAL:", font=("Arial", 14), bg="#FFFFFF", fg="#2C3A47").pack(side="left")
        tk.Label(total_frame, textvariable=self.current_total, font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#20BF6B").pack(side="right")

      
        tk.Label(new_order_panel, text="Current Order Cart", font=("Arial", 14, "bold"), bg="#F5F6FA").pack(anchor="w", pady=(10, 5))
        cart_table_frame = tk.Frame(new_order_panel)
        cart_table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        cart_columns = ("ID", "Name", "Qty", "Price", "Subtotal")
        self.cart_table = ttk.Treeview(cart_table_frame, columns=cart_columns, show="headings", height=8)
        self.cart_table.pack(side="left", fill="both", expand=True)
        self.cart_table.column("ID", width=40, anchor="center")
        self.cart_table.column("Name", width=150, anchor="w")
        self.cart_table.column("Qty", width=50, anchor="center")
        self.cart_table.column("Price", width=70, anchor="e")
        self.cart_table.column("Subtotal", width=80, anchor="e")
        for col in cart_columns:
            self.cart_table.heading(col, text=col)

       
        cart_btn_frame = tk.Frame(new_order_panel, bg="#F5F6FA")
        cart_btn_frame.pack(fill="x", pady=5)
        
        
        def remove_item_from_cart():
            selected = self.cart_table.focus()
            if selected:
                values = self.cart_table.item(selected, 'values')
                product_id = int(values[0])
                
                if product_id in self.current_cart:
                    del self.current_cart[product_id]
                    self.refresh_cart_display()

        tk.Button(cart_btn_frame, text="Remove Item", bg="#FCA3A8", fg="black", command=remove_item_from_cart).pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(cart_btn_frame, text="Clear Cart", bg="#FFD479", fg="black", command=lambda: (self.current_cart.clear(), self.refresh_cart_display())).pack(side="right", fill="x", expand=True)


        #  Finalize Button 
        def finalize_order():
            if not self.current_cart:
                messagebox.showwarning("Warning", "The cart is empty.")
                return

            customer_name = simpledialog.askstring("Customer Information", "Enter Customer Name:", parent=frame)
            if not customer_name:
                messagebox.showwarning("Warning", "Customer name is required.")
                return

           
            order_items_list = [(id, item['qty']) for id, item in self.current_cart.items()]
            
           
            order_id, message = create_new_order(customer_name, order_items_list)
            
            if order_id is not None:
                messagebox.showinfo("Success", f"Order {order_id} placed successfully!\nTotal: ₱{self.current_total.get()}")
                self.current_cart.clear()
                self.refresh_cart_display()
                self.refresh_order_history()
                self.refresh_product_table_in_orders() 
            else:
                messagebox.showerror("Error", f"Failed to finalize order: {message}")
                self.order_status_label.config(text=f"Failed: {message}", fg="red")

        tk.Button(new_order_panel, text="RECORD SALE", 
                  font=("Arial", 16, "bold"), bg="#20BF6B", fg="white", 
                  relief="flat", command=finalize_order).pack(fill="x", pady=10)

        #  Available Products List
        tk.Label(new_order_panel, text="Available Products (Double Click to Add)", font=("Arial", 14, "bold"), bg="#F5F6FA").pack(anchor="w", pady=(10, 5))
        product_table_frame = tk.Frame(new_order_panel)
        product_table_frame.pack(fill="both", expand=True)

        product_columns = ("ID", "Name", "Price", "Stock")
        self.product_table = ttk.Treeview(product_table_frame, columns=product_columns, show="headings", height=10)
        self.product_table.pack(side="left", fill="both", expand=True)
        self.product_table.column("ID", width=40, anchor="center")
        self.product_table.column("Name", width=150, anchor="w")
        self.product_table.column("Price", width=70, anchor="e")
        self.product_table.column("Stock", width=60, anchor="center")
        for col in product_columns:
            self.product_table.heading(col, text=col)

        # Refresh Product Table 
        def refresh_product_table_in_orders():
            for item in self.product_table.get_children():
                self.product_table.delete(item)
            products = get_products()
            for prod in products:
                if int(prod[3]) > 0: 
                    self.product_table.insert("", "end", values=prod)
        
       
        self.refresh_product_table_in_orders = refresh_product_table_in_orders

        refresh_product_table_in_orders()


        # Item Adding 
        def add_item_to_cart(event):
            selected = self.product_table.focus()
            if selected:
                values = self.product_table.item(selected, 'values')
                product_id = int(values[0])
                name = values[1]
                price = float(values[2])
                stock = int(values[3])
                
                current_qty_in_cart = self.current_cart.get(product_id, {}).get('qty', 0)

               
                quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {name} (Max available: {stock - current_qty_in_cart}):", 
                                                    parent=frame, minvalue=1, maxvalue=(stock - current_qty_in_cart))
                
                if quantity:
                    if product_id in self.current_cart:
                       
                        new_qty = current_qty_in_cart + quantity
                        self.current_cart[product_id]['qty'] = new_qty
                    else:
                        
                        self.current_cart[product_id] = {'name': name, 'price': price, 'qty': quantity}

                    self.refresh_cart_display()
                
        self.product_table.bind("<Double-1>", add_item_to_cart)
        
    
       
        history_panel = tk.Frame(main_split, bg="#FFFFFF", padx=10, pady=10, relief="groove")
        history_panel.pack(side="right", fill="both", expand=True)

        tk.Label(history_panel, text="Order History", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="#2C3A47").pack(anchor="w", pady=(0, 10))

        # Order History Table 
        history_table_frame = tk.Frame(history_panel)
        history_table_frame.pack(fill="both", expand=True)

        history_columns = ("ID", "Customer", "Date", "Total", "Status")
        self.history_table = ttk.Treeview(history_table_frame, columns=history_columns, show="headings")
        self.history_table.pack(side='left', fill="both", expand=True)
        vsb = ttk.Scrollbar(history_table_frame, orient="vertical", command=self.history_table.yview)
        vsb.pack(side='right', fill='y')
        self.history_table.configure(yscrollcommand=vsb.set)

        self.history_table.column("ID", width=40, anchor="center")
        self.history_table.column("Customer", width=120, anchor="w")
        self.history_table.column("Date", width=120, anchor="center")
        self.history_table.column("Total", width=80, anchor="e")
        self.history_table.column("Status", width=80, anchor="center")
        for col in history_columns:
            self.history_table.heading(col, text=col)

        # History Buttons
        history_btn_frame = tk.Frame(history_panel, bg="#FFFFFF")
        history_btn_frame.pack(fill="x", pady=10)
        
       
        def refresh_orders_table():
            for item in self.history_table.get_children():
                self.history_table.delete(item)
            orders = get_orders() 
            for order in orders:
                self.history_table.insert("", "end", values=order)

        self.refresh_order_history = refresh_orders_table # 

        def view_order_details():
            selected = self.history_table.focus()
            if selected:
                values = self.history_table.item(selected, "values")
                order_id = int(values[0])
                customer = values[1]
                total = values[3]
                status = values[4]
                
                items = get_order_items(order_id)
                detail_text = f"Order ID: {order_id}\nCustomer: {customer}\nStatus: {status}\n\nItems:\n"
                
                for item_id, name, quantity, price in items:
                    subtotal = quantity * price
                    detail_text += f"- {name} ({quantity} x ₱{price:.2f}) = ₱{subtotal:.2f}\n"

                detail_text += f"\nTOTAL: ₱{total}"
                messagebox.showinfo("Order Details", detail_text)

        def delete_history_order():
            
            selected = self.history_table.focus()
            if selected:
                values = self.history_table.item(selected, "values")
                order_id = int(values[0])
                
                if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Order ID {order_id}?\n\nNOTE: If this order was Paid, stock will be returned to inventory."):
                    success, msg = delete_order(order_id)
                    if success:
                        messagebox.showinfo("Success", msg)
                        self.refresh_order_history()
                        self.refresh_product_table_in_orders() 
                    else:
                        messagebox.showerror("Error", f"Deletion Failed: {msg}")

       
        def change_order_status():
            selection = self.history_table.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select an order to change status.")
                return

            order_values = self.history_table.item(selection[0], 'values')
            order_id = int(order_values[0])

            
            dialog = StatusDialog(self, order_id) 
            new_status = dialog.show() 

            if not new_status:
                return

           
            success, message = update_payment_status(order_id, new_status) 

            if success:
                messagebox.showinfo("Success", message)
                self.refresh_order_history() 
                self.refresh_product_table_in_orders() 
            else:
                messagebox.showerror("Error", f"Failed to update status: {message}")
        
        # Buttons for History Panel
        tk.Button(history_btn_frame, text="View Details", bg="#1B9CFC", fg="white", command=view_order_details).pack(side="left", padx=5)
        tk.Button(history_btn_frame, text="Change Status", bg="#3867D6", fg="white", command=change_order_status).pack(side="left", padx=5)
        tk.Button(history_btn_frame, text="Delete Order", bg="#FC5C65", fg="white", command=delete_history_order).pack(side="left", padx=5)


        refresh_orders_table()
        self.switch_frame(frame)

 
    def refresh_cart_display(self):
        """Refreshes the cart Treeview and updates the total label."""
        if not hasattr(self, 'cart_table'):
            return 
            
       
        for item in self.cart_table.get_children():
            self.cart_table.delete(item)
        
        current_total_value = 0.0
        
        for id, item in self.current_cart.items():
            subtotal = item['price'] * item['qty']
            current_total_value += subtotal
            
            self.cart_table.insert("", "end", values=(
                id, 
                item['name'], 
                item['qty'], 
                f"{item['price']:.2f}", 
                f"{subtotal:.2f}"
            ))
        
        self.current_total.set(f"{current_total_value:.2f}")
    
    # INCOME PANEL 
    def show_income(self):
        frame = tk.Frame(self, bg="#F5F6FA", padx=20, pady=20)

        
        return_btn = tk.Button(frame, text="← Back", font=("Arial", 12, "bold"),
                               bg="#BDC3C7", fg="#2C3A47", width=10,
                               relief="flat", command=self.show_dashboard)
        return_btn.place(relx=1.0, rely=0, x=-20, y=20, anchor="ne")

        title = tk.Label(frame, text="Income Report", font=("Arial", 22, "bold"), bg="#F5F6FA", fg="#2C3A47")
        title.pack(anchor="w", pady=(0, 20))
        
        
        summary_container = tk.Frame(frame, bg="#F5F6FA")
        summary_container.pack(anchor="w", pady=10)

       
        card1 = tk.Frame(summary_container, bg="#FFFFFF", padx=20, pady=10, relief="flat", borderwidth=1)
        card1.grid(row=0, column=0, padx=10)
        tk.Label(card1, text="TOTAL SALES (ALL TIME)", font=("Arial", 12), bg="#FFFFFF", fg="#7F8C8D").pack(anchor="w")
        self.total_sales_label = tk.Label(card1, text="₱0.00", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#2C3A47")
        self.total_sales_label.pack(anchor="w", pady=(5, 0))

       
        card2 = tk.Frame(summary_container, bg="#FFFFFF", padx=20, pady=10, relief="flat", borderwidth=1)
        card2.grid(row=0, column=1, padx=10)
        tk.Label(card2, text="SALES (LAST 30 DAYS)", font=("Arial", 12), bg="#FFFFFF", fg="#7F8C8D").pack(anchor="w")
        self.last_30_days_label = tk.Label(card2, text="₱0.00", font=("Arial", 24, "bold"), bg="#FFFFFF", fg="#20BF6B")
        self.last_30_days_label.pack(anchor="w", pady=(5, 0))

      
        detail_title = tk.Label(frame, text="Detailed Sales Records (Last 60 Days)", font=("Arial", 18, "bold"), bg="#F5F6FA", fg="#2C3A47")
        detail_title.pack(anchor="w", pady=(30, 10))

        table_frame = tk.Frame(frame)
        table_frame.pack(fill="both", expand=True) 
        
        columns = ("Date Period", "Orders Count", "Gross Income")
        income_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=income_table.yview)
        income_table.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        income_table.pack(side='left', fill="both", expand=True)
        
        income_table.column("Date Period", width=150, anchor="center")
        income_table.column("Orders Count", width=150, anchor="center")
        income_table.column("Gross Income", width=150, anchor="center")
        
        for col in columns:
            income_table.heading(col, text=col)
            
     
        def load_income_report():
            try:
                report_data = get_income_report() 
                
               
                self.total_sales_label.config(text=f"₱{report_data['total_sales']:.2f}")
                self.last_30_days_label.config(text=f"₱{report_data['last_30_days']:.2f}")
            
               
                for item in income_table.get_children():
                    income_table.delete(item)
                    
                for row in report_data['details']:
                    
                    income_table.insert("", "end", values=row)

            except Exception as e:
                self.total_sales_label.config(text="N/A", fg="red")
                self.last_30_days_label.config(text="DB Error", fg="red")
                messagebox.showerror("Database Error", f"Could not load income report: {e}")
            
        load_income_report()
        self.switch_frame(frame)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()