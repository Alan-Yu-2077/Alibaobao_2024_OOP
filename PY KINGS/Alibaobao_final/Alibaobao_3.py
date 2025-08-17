import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import json
import os
import sv_ttk
from datetime import datetime


# Logging decorator
def log_function_call(func):
    def wrapper(*args, **kwargs):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "function": func.__name__,
            "user": args[0].username if hasattr(args[0], 'username') else "Unknown"
        }
        
        result = func(*args, **kwargs)
        
        log_entry["status"] = "completed"
        
        # Write log to JSON file
        log_file = "function_logs.json"
        if os.path.exists(log_file):
            with open(log_file, "r+") as file:
                logs = json.load(file)
                logs.append(log_entry)
                file.seek(0)
                json.dump(logs, file, indent=4)
        else:
            with open(log_file, "w") as file:
                json.dump([log_entry], file, indent=4)
        
        return result
    return wrapper

class User:
    def __init__(self, username, password, master):
        self.master = master
        self.username = username
        self.__password = password
        self.__is_logged_in = False
    
    # Initial login page
    @log_function_call
    def create_login_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Title
        self.alibaobao_label = ttk.Label(self.master, text="Alibaobao", font=("Arial", 24, "bold"))
        self.alibaobao_label.pack(pady=20)

        self.username_label = ttk.Label(self.master, text="Username:")
        self.username_label.pack(pady=5)
        self.username_entry = ttk.Entry(self.master)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(self.master, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        self.login_button = ttk.Button(
            self.master, 
            text="Login", 
            style= "Accent.TButton",
            width=20,
            command=self.login)
        self.login_button.pack(pady=10)

        frame = ttk.Frame(self.master)
        frame.pack(pady=5)

        self.username_label = ttk.Label(frame, text="No account?")
        self.username_label.pack(side=tk.LEFT, padx=(0, 10))

        # Register link
        self.register_label = ttk.Label(
            frame,
            text="Register",
            foreground="blue",
            cursor="hand2")
        self.register_label.pack(side=tk.LEFT)
        self.register_label.bind("<Button-1>", lambda e: self.create_register_page())
    
    # Login logic
    @log_function_call
    def login(self, username=None, password=None, filename="users.json"):

        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            with open(filename, "r") as file:
                users = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "User data file not found")
            return False
    
        if username in users and users[username]["password"] == password:
            self.__is_logged_in = True
            self.username = username
            messagebox.showinfo("Login Successful", f"{username} has logged in successfully!")
            user_type = self.__get_user_type(username)
        
            if user_type == "Customer":
                consumer = Consumer(username, password, self.master)
                consumer.create_first_page()
                self.initialize_user_info(username)
            elif user_type == "Seller":
                seller = Seller(username, password, self.master)
                seller.create_first_page()
            elif user_type == "Admin":
                admin = Admin(username, password, self.master)
                admin.create_first_page()
            else:
                messagebox.showerror("Invalid User Type", "The user type is invalid!")
                return False
        
            return True
        else:
            messagebox.showerror("Login Failed", "Username or password is incorrect!")
            return False
    
    # Registration page
    @log_function_call
    def create_register_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Username and password input fields
        self.register_username_label = ttk.Label(self.master, text="Username:")
        self.register_username_label.pack(pady=5)
        self.register_username_entry = ttk.Entry(self.master)
        self.register_username_entry.pack(pady=5)
        self.register_password_label = ttk.Label(self.master, text="Password:")
        self.register_password_label.pack(pady=5)
        self.register_password_entry = ttk.Entry(self.master, show='*')
        self.register_password_entry.pack(pady=5)

        # User type selection box
        self.register_user_type_label = ttk.Label(self.master, text="User Type:")
        self.register_user_type_label.pack(pady=5)
        self.register_user_type = ttk.Combobox(self.master, values=["Customer", "Seller", "Admin"])
        self.register_user_type.pack(pady=5)

        # Submit registration button
        register_button = ttk.Button(
            self.master, 
            text="Submit Registration", 
            style= "Accent.TButton",
            command=self.register_user,
            width=20)
        register_button.pack(pady=10)

        # Back to login button
        back_to_login_button = ttk.Button(
            self.master, 
            text="Back to Login", 
            command=self.create_login_page,
            width=20)
        back_to_login_button.pack(pady=10)
    
    # Registration logic
    @log_function_call
    def register_user(self,filename="users.json"):
        username = self.register_username_entry.get()
        password = self.register_password_entry.get()
        user_type = self.register_user_type.get()
        try:
            with open(filename,"r") as file :
                users=json.load(file)
        except FileNotFoundError:
            users={}
        if username in users:
            messagebox.showerror("Registration Failed", "User Already Exists")
            return False
        users[username]={"password":password, "user_type": user_type}
        with open(filename,"w")as file:
            json.dump(users,file)
        messagebox.showinfo("Registration Successful", "Registration Successful")
        self.create_login_page()
    
    # Get user type
    @log_function_call
    def __get_user_type(self, username, filename="users.json"):
        try:
            with open(filename, "r") as file:
                users = json.load(file)
            return users[username]["user_type"] if username in users else None
        except FileNotFoundError:
            return None
    
    # Initialize user information
    @log_function_call
    def initialize_user_info(self, username):
        filename = f'{username}_information.json'
        if not os.path.exists(filename):
            data = {"money": 0}
            with open(filename, 'w') as file:
                json.dump(data, file, ensure_ascii=False)
        # Removed the error message box
    # Logout logic
    @log_function_call
    def logout(self):
        self.__is_logged_in = False
        self.create_login_page()
    
    @log_function_call
    # Abstract method, create the first interface after user login
    def create_first_page(self):
        pass
    # Check if logged in
    @log_function_call
    def __is_logged_in(self):
        return self.__is_logged_in

class Admin(User):
    def __init__(self, username, password, master):
        super().__init__(username, password, master)
        self.__admin_actions = []
    
    # Admin page
    @log_function_call
    def create_first_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ttk.Label(self.master, text="Admin Interface", font=("Arial", 24))
        title_label.pack(pady=20)

        # Frame
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=10)

        # View user information button
        view_users_button = ttk.Button(button_frame, text="View User Information", command=self.view_users)
        view_users_button.pack(side=tk.LEFT, padx=10)

        # View bills data button
        view_bills_button = ttk.Button(button_frame, text="View Bills Data", command=self.view_bills)
        view_bills_button.pack(side=tk.LEFT, padx=10)

        # View logs button
        view_logs_button = ttk.Button(button_frame, text="View Logs", command=self.view_logs)
        view_logs_button.pack(side=tk.LEFT, padx=10)

        # Delete user button
        delete_user_button = ttk.Button(button_frame, text="Delete User", command=self.prompt_delete_user)
        delete_user_button.pack(side=tk.LEFT, padx=10)

        # Modify product price button
        modify_price_button = ttk.Button(button_frame, text="Modify Product Price", command=self.prompt_modify_product_price)
        modify_price_button.pack(side=tk.LEFT, padx=10)
    
    # View logs
    @log_function_call
    def view_logs(self):
        logs_window = tk.Toplevel(self.master)
        logs_window.title("Function Logs")
        logs_window.geometry("800x600")

        # Create a Treeview to display logs
        tree = ttk.Treeview(logs_window, columns=("Timestamp", "Function", "User", "Status"), show="headings")
        tree.heading("Timestamp", text="Timestamp")
        tree.heading("Function", text="Function")
        tree.heading("User", text="User")
        tree.heading("Status", text="Status")
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Set column width
        tree.column("Timestamp", width=150)
        tree.column("Function", width=200)
        tree.column("User", width=100)
        tree.column("Status", width=100)

        # Read log file
        log_file = "function_logs.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as file:
                logs = json.load(file)
                for log in logs:
                    tree.insert("", "end", values=(
                        log["timestamp"],
                        log["function"],
                        log["user"],
                        log.get("status", "N/A")
                    ))
        else:
            messagebox.showinfo("Info", "No logs found")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(logs_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.__log_admin_action("Viewed function logs")

    # User data window
    @log_function_call
    def view_users(self):
        users_window = tk.Toplevel(self.master)
        users_window.title("User Information")

        # User information table
        tree = ttk.Treeview(users_window, columns=("Username", "Password"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Password", text="Password")
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Read and display user information
        try:
            with open("users.json", "r") as file:
                users = json.load(file)
                for username, user_data in users.items():
                    tree.insert("", "end", values=(username, user_data["password"]))
        except FileNotFoundError:
            messagebox.showerror("Error", "User data file not found")

        self.__log_admin_action("Viewed user information")

    # Bills data window
    @log_function_call
    def view_bills(self):
        bills_window = tk.Toplevel(self.master)
        bills_window.title("Bills Data")

        # Bills content table
        tree = ttk.Treeview(bills_window, columns=("Username", "Total", "Products", "Ratings", "Reviews"), show="headings")
        tree.heading("Username", text="Username")
        tree.heading("Total", text="Total Amount")
        tree.heading("Products", text="Purchased Products")
        tree.heading("Ratings", text="Ratings")
        tree.heading("Reviews", text="Reviews")
        tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Set column width
        tree.column("Username", width=100)
        tree.column("Total", width=100)
        tree.column("Products", width=200)
        tree.column("Ratings", width=100)
        tree.column("Reviews", width=300)

        # Read bills data and product data
        try:
            with open("bills.json", "r") as bills_file:
                bills = json.load(bills_file)
            with open("product_data.json", "r") as product_file:
                product_data = json.load(product_file)

            for bill in bills:
                products = bill.get("products", [])
                ratings = []
                reviews = []
                for product in products:
                    if product in product_data:
                        product_reviews = product_data[product].get("reviews", [])
                        user_reviews = [review for review in product_reviews if review["username"] == bill["username"]]
                        if user_reviews:
                            ratings.append(str(user_reviews[-1]["rating"]))
                            reviews.append(user_reviews[-1]["review_content"])
                        else:
                            ratings.append("N/A")
                            reviews.append("No review")
                    else:
                        ratings.append("N/A")
                        reviews.append("No review")
                
                tree.insert("", "end", values=(
                    bill["username"],
                    bill["total"],
                    ", ".join(products),
                    ", ".join(ratings),
                    " | ".join(reviews)
                ))

        except FileNotFoundError:
            messagebox.showerror("Error", "Data files not found")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in data files")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(bills_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.__log_admin_action("Viewed bills data")

    # Prompt to delete user
    def prompt_delete_user(self):
        username = simpledialog.askstring("Delete User", "Enter username to delete:")
        if username:
            self.delete_user(username)

    # Delete user
    @log_function_call
    def delete_user(self, username):
        filename = "users.json"
        try:
            with open(filename, "r") as file:
                users = json.load(file)
            if username in users:
                del users[username]
                with open(filename, "w") as file:
                    json.dump(users, file, indent=4)
                messagebox.showinfo("Success", f"User {username} deleted successfully.")
                self.__log_admin_action(f"Deleted user: {username}")
            else:
                messagebox.showerror("Error", "User not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "User data file not found.")

    # Prompt to modify product price
    def prompt_modify_product_price(self):
        product_name = simpledialog.askstring("Modify Product Price", "Enter product name:")
        new_price = simpledialog.askfloat("Modify Product Price", "Enter new price:")
        if product_name and new_price is not None:
            self.modify_product_price(product_name, new_price)

    # Modify product price
    @log_function_call
    def modify_product_price(self, product, new_price):
        filename = "product_data.json"
        try:
            with open(filename, "r") as file:
                products = json.load(file)
            if product in products:
                products[product]["price"] = new_price
                with open(filename, "w") as file:
                    json.dump(products, file, indent=4)
                messagebox.showinfo("Success", f"Price of {product} updated to ¥{new_price:.2f}.")
                self.__log_admin_action(f"Modified price of {product} to {new_price}")
            else:
                messagebox.showerror("Error", "Product not found.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Product data file not found.")

    # Log admin action
    def __log_admin_action(self, action):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin": self.username,
            "action": action
        }
        self.__admin_actions.append(log_entry)
        # Write log to JSON file
        log_file = "admin_actions.json"
        if os.path.exists(log_file):
            with open(log_file, "r+") as file:
                logs = json.load(file)
                logs.append(log_entry)
                file.seek(0)
                json.dump(logs, file, indent=4)
        else:
            with open(log_file, "w") as file:
                json.dump([log_entry], file, indent=4)

class Consumer(User):
    def __init__(self, username, password, master):
        super().__init__(username, password, master)
        self.__shopping_cart = {}


    def initialize_user_info(self, username):
        filename = f'{username}_information.json'
        if not os.path.exists(filename):
            data = {"money": 0}
            with open(filename, 'w') as file:
                json.dump(data, file, ensure_ascii=False)
    # Product page (user)
    @log_function_call
    def create_first_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        label = ttk.Label(self.master, text="Welcome to alibaobao!", font=("Arial", 24))
        label.pack(pady=20)

        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Product frame
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Product table
        table = ttk.Treeview(content_frame, columns=("Name", "Category", "Subcategory", "Price", "Stock", "Rating"), show="headings")
        table.heading("Name", text="Product Name")
        table.heading("Category", text="Category")
        table.heading("Subcategory", text="Subcategory")
        table.heading("Price", text="Product Price")
        table.heading("Stock", text="Product Stock")
        table.heading("Rating", text="Average Rating")
        table.pack(fill=tk.BOTH, expand=True)

        # Set column width
        table.column("Name", width=150)
        table.column("Category", width=100)
        table.column("Subcategory", width=100)
        table.column("Price", width=100)
        table.column("Stock", width=100)
        table.column("Rating", width=100)

        # Load product data
        if os.path.exists('product_data.json'):
            with open('product_data.json', 'r') as file:
                data = json.load(file)
            products = []
            for key, value in data.items():
                try:
                    price = f"¥{float(value.get('price', 0)):.2f}"
                except (ValueError, TypeError):
                    price = "N/A"
                
                stock = str(value.get('stock', 'N/A'))
                
                avg_rating = value.get('average_rating', 'N/A')
                if avg_rating != 'N/A':
                    try:
                        avg_rating = f"{float(avg_rating):.1f}"
                    except (ValueError, TypeError):
                        avg_rating = 'N/A'
                
                products.append((
                    key, 
                    value.get('category', 'N/A'),
                    value.get('subcategory', 'N/A'),
                    price, 
                    stock, 
                    avg_rating
                ))
        else:
            messagebox.showerror("Error", "product_data.json file not found")
            products = []

        for product in products:
            table.insert("", "end", values=product)

        # Bottom frame
        button_frame = ttk.Frame(self.master, relief=tk.RAISED, borderwidth=1, width=800, height=50)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        button_frame.pack_propagate(False)

        # Selection box
        self.product_combobox = ttk.Combobox(button_frame, values=[product[0] for product in products])
        self.product_combobox.pack(side=tk.LEFT, padx=5)
        self.amount_spinbox = ttk.Spinbox(button_frame, from_=0, to=100, width=5)
        self.amount_spinbox.pack(side=tk.LEFT, padx=5)

        # Add to cart button
        add_to_cart_button = ttk.Button(
            button_frame, 
            text="Add to Cart", 
            style="Accent.TButton",
            command=lambda: self.add_to_cart())
        add_to_cart_button.pack(side=tk.LEFT, padx=5)

        # Modify button text and command
        view_info_button = ttk.Button(
            button_frame,
            text="View Product Info",
            style="Accent.TButton",
            command=self.view_product_info
        )
        view_info_button.pack(side=tk.LEFT, padx=5)

        # Shopping cart button
        cart_button = ttk.Button(
            button_frame,
            text="Shopping Cart", 
            style="Accent.TButton",
            command=self.open_cart)
        cart_button.pack(side=tk.RIGHT, padx=5)

        # My info button
        my_info_button = ttk.Button(
            button_frame,
            text="My Info", 
            style="Accent.TButton",
            command=self.open_my_info)
        my_info_button.pack(side=tk.RIGHT, padx=10)
    
    # Add to cart logic
    @log_function_call
    def add_to_cart(self):
        filename=f'{self.username}_shoppingcart.json'
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                json.dump({}, file)

        product_name = self.product_combobox.get()
        amount = int(self.amount_spinbox.get())
        data1 = {}


        with open(filename, 'r') as json_file:

            data1 = json.load(json_file)
        
        # Check if product data file exists
        if not os.path.exists('product_data.json'):
            messagebox.showerror("Error", "product_data.json file not found")
            return

        with open('product_data.json', 'r') as file: 
            data2 = json.load(file)

        # Check if product exists and if stock is sufficient
        if product_name in data2 and data2[product_name]["stock"] >= amount:
            if product_name not in data1:
                data1[product_name] = data2[product_name]
                data1[product_name]['amount'] = amount
                data2[product_name]['stock'] -= amount
                with open('product_data.json', 'w') as file:
                    json.dump(data2, file, ensure_ascii=False)
                del data1[product_name]['stock']
                with open(filename, 'w') as file:
                    json.dump(data1, file, ensure_ascii=False)
                messagebox.showinfo("Success", "Added to cart successfully")
                self.create_first_page()
            else:
                data1[product_name]['amount'] += amount
                data2[product_name]['stock'] -= amount
                with open('product_data.json', 'w') as file:
                    json.dump(data2, file, ensure_ascii=False)
                with open(filename, 'w') as file:
                    json.dump(data1, file, ensure_ascii=False)
                messagebox.showinfo("Success", "Added to cart successfully")
                self.create_first_page()
        else:
            messagebox.showerror("Error", "Insufficient stock or product does not exist")
    
    # Shopping cart interface
    @log_function_call
    def open_cart(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Frame
        header_frame = ttk.Frame(self.master)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Back button
        back_button = ttk.Button(header_frame, text="Back", command=self.create_first_page)
        back_button.pack(side=tk.LEFT)

        # Title
        label = ttk.Label(header_frame, text="SHOPPING CART", font=("Helvetica", 24))
        label.pack(side=tk.LEFT, expand=True)

        # Checkout button
        checkout_button = ttk.Button(
            header_frame, 
            text="Checkout", 
            style="Accent.TButton",
            command=self.checkout)
        checkout_button.pack(side=tk.RIGHT)

        # Shopping cart content frame
        cart_frame = ttk.Frame(self.master)
        cart_frame.pack(pady=10)

        # Shopping cart content table
        cart_table = ttk.Treeview(cart_frame, columns=("Product Name", "Quantity", "Unit Price", "Total Price"), show="headings")
        cart_table.heading("Product Name", text="Product Name")
        cart_table.heading("Quantity", text="Quantity")
        cart_table.heading("Unit Price", text="Unit Price")
        cart_table.heading("Total Price", text="Total Price")
        cart_table.pack(fill=tk.BOTH, expand=True)

        # Read shopping cart data
        with open(f'{self.username}_shoppingcart.json', 'r') as file:
            cart_data = json.load(file)

        # Display shopping cart content
        for product, details in cart_data.items():
            total_price = details['amount'] * details['price']
            cart_table.insert("", "end", values=(product, details['amount'], details['price'], total_price))

    # Personal interface
    @log_function_call
    def open_my_info(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Frame
        header_frame = ttk.Frame(self.master)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Back button
        back_button = ttk.Button(header_frame, text="Back", command=self.create_first_page)
        back_button.pack(side=tk.LEFT)

        # Title
        label = ttk.Label(header_frame, text="My Information", font=("Arial", 24))
        label.pack(side=tk.LEFT, expand=True)

        # Logout button
        logout_button = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_button.pack(side=tk.RIGHT)

        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(pady=20)

        # Display user information
        ttk.Label(main_frame, text=f"Username: {self.username}", font=("Arial", 14)).pack(pady=5)
        
        # Check and initialize user information file
        filename = f'{self.username}_information.json'
        if not os.path.exists(filename):
            data = {"money": 0}
            with open(filename, 'w') as file:
                json.dump(data, file, ensure_ascii=False)
        else:
            with open(filename, 'r') as file:
                data = json.load(file)

        # Display balance
        ttk.Label(main_frame, text=f"Balance: ¥{data['money']:.2f}", font=("Arial", 14)).pack(pady=5)
        
        # Add top-up button
        top_up_button = ttk.Button(main_frame, text="Top Up", style="Accent.TButton", command=self.create_top_up_page)
        top_up_button.pack(pady=10)
    
    # Top-up page
    @log_function_call
    def create_top_up_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        # Frame
        header_frame = ttk.Frame(self.master)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Back button
        back_button = ttk.Button(header_frame, text="Back", command=self.open_my_info)
        back_button.pack(side=tk.LEFT)

        # Top-up label
        label = ttk.Label(header_frame, text="Top Up", font=("Arial", 24))
        label.pack(expand=True)

        # Top-up frame
        top_up_frame = ttk.Frame(self.master)
        top_up_frame.pack(pady=20)

        # Top-up entry
        ttk.Label(top_up_frame, text="Top Up Amount:", font=("Arial", 14)).pack(pady=5)
        self.top_up_amount_entry = ttk.Entry(top_up_frame)
        self.top_up_amount_entry.pack(pady=5)

        # Submit top-up button
        submit_button = ttk.Button(
            self.master, 
            text="Submit Top Up", 
            style="Accent.TButton",
            command=self.process_top_up)
        submit_button.pack(pady=10)
    
    # Top-up logic
    @log_function_call
    def process_top_up(self):
        amount = self.top_up_amount_entry.get()
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Top-up amount must be greater than 0")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        # Update balance
        filename = f'{self.username}_information.json'
        if not os.path.exists(filename):
            data = {"money": 0}
        else:
            with open(filename, 'r') as file:
                data = json.load(file)
        
        data['money'] += amount
        with open(filename, 'w') as file:
            json.dump(data, file, ensure_ascii=False)
    
        messagebox.showinfo("Top Up Successful", f"Top up successful ¥{amount:.2f}")
        self.open_my_info()
    
    # Review page
    @log_function_call
    def create_product_review_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Frame
        header_frame = ttk.Frame(self.master)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Back button
        back_button = ttk.Button(header_frame, text="Back", command=self.create_first_page)
        back_button.pack(side=tk.LEFT)

        # Product review label
        label = ttk.Label(header_frame, text="Product Review", font=("Arial", 24))
        label.pack(expand=True)

        # Review input frame
        review_frame = ttk.Frame(self.master)
        review_frame.pack(pady=20)

        ttk.Label(review_frame, text="Product Name:", font=("Arial", 14)).pack(pady=5)
        product_name_entry = ttk.Entry(review_frame, width=30)
        product_name_entry.pack(pady=5)

        ttk.Label(review_frame, text="Rating (1-5 stars):", font=("Arial", 14)).pack(pady=5)
        rating_var = tk.StringVar()
        rating_combobox = ttk.Combobox(review_frame, textvariable=rating_var, values=["1", "2", "3", "4", "5"], width=5)
        rating_combobox.pack(pady=5)

        ttk.Label(review_frame, text="Review Content:", font=("Arial", 14)).pack(pady=5)
        review_text = tk.Text(review_frame, height=5, width=40)
        review_text.pack(pady=5)

        # Submit review button
        submit_button = ttk.Button(self.master, text="Submit Review", command=lambda: self.submit_review(product_name_entry.get(), rating_var.get(), review_text.get("1.0", tk.END)))
        submit_button.pack(pady=10)
    
    # Checkout logic
    @log_function_call
    def checkout(self):
        filename = f'{self.username}_shoppingcart.json'
        with open(filename, 'r') as file:
            data1 = json.load(file)
        
        if not data1:
            messagebox.showerror("Error", "Shopping cart is empty")
            return
        
        self.bill = 0
        for key in data1:
            self.bill += data1[key]['amount'] * data1[key]['price']
        
        user_info_filename = f'{self.username}_information.json'
        if not os.path.exists(user_info_filename):
            self.initialize_user_info(self.username)
        
        with open(user_info_filename, 'r') as file:
            data = json.load(file)
        
        bill_filename = 'bills.json'
        if not os.path.exists(bill_filename):
            with open(bill_filename, 'w') as file:
                json.dump([], file)
        with open(bill_filename, 'r') as file:
            bills = json.load(file)
        bill_data = {
            "username": self.username,
            "products": [product for product in data1],
            "total": self.bill
        }
        bills.append(bill_data)
        with open(bill_filename, 'w') as file:
            json.dump(bills, file, ensure_ascii=False, indent=4)
        
        if data['money'] >= self.bill:
            data['money'] -= self.bill
            with open(user_info_filename, 'w') as file:
                json.dump(data, file, ensure_ascii=False)
            data1 = {}
            with open(filename, 'w') as file:
                json.dump(data1, file, ensure_ascii=False)
            messagebox.showinfo("Checkout", "Checkout completed")
            self.open_cart()
        else:
            messagebox.showerror("Error", "Insufficient balance")
        
        self.create_product_review_page()
    


    # Submit review logic
    @log_function_call
    def submit_review(self, product_name, rating, review_content):
        if not product_name or not rating or not review_content.strip():
            messagebox.showerror("Error", "Please fill in all review information")
            return
        
        review_data = {
            "username": self.username,
            "rating": int(rating),
            "review_content": review_content.strip()
        }
        
        try:
            with open("product_data.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "product_data.json file not found.")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "product_data.json file is not in a valid JSON format.")
            return
    
        if product_name not in data:
            messagebox.showerror("Error", "Product not found in database.")
            return
        
        if 'reviews' not in data[product_name]:
            data[product_name]['reviews'] = []
        
        data[product_name]['reviews'].append(review_data)
        
        # Calculate new average rating
        total_rating = sum(review['rating'] for review in data[product_name]['reviews'])
        count = len(data[product_name]['reviews'])
        average_rating = total_rating / count if count > 0 else 0
        data[product_name]['average_rating'] = round(average_rating, 2)
        
        with open("product_data.json", "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        messagebox.showinfo("Success", "Review submitted successfully")
        
        # Ask user if they want to continue reviewing or exit
        response = messagebox.askyesno("Continue?", "Do you want to submit another review?")
        if response:
            self.create_product_review_page()  # Return to review page to submit another review
        else:
            self.create_first_page()  # Return to product page if user chooses to exit
   
    #View product information
    @log_function_call
    def view_product_info(self):
        selected_product = self.product_combobox.get()
        if not selected_product:
            messagebox.showerror("Error", "Please select a product first")
            return

        info_window = tk.Toplevel(self.master)
        info_window.title(f"Information for {selected_product}")
        info_window.geometry("600x400")

        # Create a Notebook (tab widget)
        notebook = ttk.Notebook(info_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Product information tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Product Info")

        # Reviews tab
        reviews_frame = ttk.Frame(notebook)
        notebook.add(reviews_frame, text="Reviews")

        # Read product data
        try:
            with open("product_data.json", "r") as file:
                product_data = json.load(file)
            
            if selected_product in product_data:
                product_info = product_data[selected_product]
                
                # Display product information
                info_text = tk.Text(info_frame, wrap=tk.WORD, height=15, width=60)
                info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
                
                info_text.insert(tk.END, f"Product Name: {selected_product}\n")
                info_text.insert(tk.END, f"Category: {product_info.get('category', 'N/A')}\n")
                info_text.insert(tk.END, f"Subcategory: {product_info.get('subcategory', 'N/A')}\n")
                info_text.insert(tk.END, f"Price: ¥{product_info.get('price', 'N/A')}\n")
                info_text.insert(tk.END, f"Stock: {product_info.get('stock', 'N/A')}\n\n")
                
                info_text.insert(tk.END, "Attributes:\n")
                for attr, value in product_info.get('attributes', {}).items():
                    info_text.insert(tk.END, f"  {attr}: {value}\n")
                
                info_text.config(state=tk.DISABLED)  # Make the text box read-only
                
                # Display reviews
                reviews_tree = ttk.Treeview(reviews_frame, columns=("Username", "Rating", "Review"), show="headings")
                reviews_tree.heading("Username", text="Username")
                reviews_tree.heading("Rating", text="Rating")
                reviews_tree.heading("Review", text="Review")
                reviews_tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

                # Set column width
                reviews_tree.column("Username", width=100)
                reviews_tree.column("Rating", width=50)
                reviews_tree.column("Review", width=300)

                if 'reviews' in product_info:
                    reviews = product_info['reviews']
                    for review in reviews:
                        reviews_tree.insert("", "end", values=(review['username'], review['rating'], review['review_content']))
                else:
                    reviews_tree.insert("", "end", values=("", "", "No reviews available for this product"))

                # Add scrollbar to reviews treeview
                reviews_scrollbar = ttk.Scrollbar(reviews_frame, orient="vertical", command=reviews_tree.yview)
                reviews_scrollbar.pack(side="right", fill="y")
                reviews_tree.configure(yscrollcommand=reviews_scrollbar.set)

            else:
                messagebox.showerror("Error", "Product not found in database")

        except FileNotFoundError:
            messagebox.showerror("Error", "Product data file not found")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in product data file")

    #Get shopping cart contents
    @log_function_call
    def get_cart_contents(self):
        return self.__shopping_cart.copy()

class Seller(User):
    def __init__(self, username, password, master):
        super().__init__(username, password, master)
        self.attribute_entries = {}  # Used to store attribute input fields
    
    @log_function_call
    def create_first_page(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        
        title_label = ttk.Label(self.master, text="Seller Restock Interface", font=("Arial", 24))
        title_label.pack(pady=20)

        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left restock frame
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Restock form
        self.form_frame = ttk.Frame(left_frame)
        self.form_frame.pack(pady=10)

        # Product category
        ttk.Label(self.form_frame, text="Product Category:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(self.form_frame, values=["Electronics", "Clothing", "Food"])
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_subcategory)

        # Product subcategory
        ttk.Label(self.form_frame, text="Product Subcategory:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.subcategory_combobox = ttk.Combobox(self.form_frame)
        self.subcategory_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.subcategory_combobox.bind("<<ComboboxSelected>>", self.update_attributes)

        # Product name
        ttk.Label(self.form_frame, text="Product Name:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.product_name_entry = ttk.Entry(self.form_frame)
        self.product_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # Restock quantity
        ttk.Label(self.form_frame, text="Restock Quantity:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = ttk.Entry(self.form_frame)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)

        # Restock price
        ttk.Label(self.form_frame, text="Restock Price:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.price_entry = ttk.Entry(self.form_frame)
        self.price_entry.grid(row=4, column=1, padx=5, pady=5)

        # Submit button
        submit_button = ttk.Button(left_frame, text="Submit Restock", command=self.submit_restock)
        submit_button.pack(pady=10)
        
        # Right inventory frame
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Inventory title
        inventory_label = ttk.Label(right_frame, text="Current Inventory", font=("Arial", 18))
        inventory_label.pack(pady=10)

        # Inventory list
        inventory_tree = ttk.Treeview(right_frame, columns=("Product", "Quantity", "Price"), show="headings")
        inventory_tree.heading("Product", text="Product Name")
        inventory_tree.heading("Quantity", text="Stock Quantity")
        inventory_tree.heading("Price", text="Unit Price")
        inventory_tree.pack(fill=tk.BOTH, expand=True)

        # Load products from product_data.json
        if os.path.exists('product_data.json'):
            with open('product_data.json', 'r') as file:
                data = json.load(file)
            inventory_data = [(key, str(value['stock']), f"¥{value['price']}") for key, value in data.items()]
            for item in inventory_data:
                inventory_tree.insert("", "end", values=item)
        else:
            messagebox.showerror("Error", "product_data.json file not found")
        
        # Back button
        back_button = ttk.Button(self.master, text="Back", command=self.create_login_page)
        back_button.pack(pady=10)
    
    @log_function_call
    def update_subcategory(self, event):
        category = self.category_combobox.get()
        if category == "Electronics":
            self.subcategory_combobox['values'] = ["Smartphone", "Laptop", "Headphones", "Smartwatch"]
        elif category == "Clothing":
            self.subcategory_combobox['values'] = ["Shirt", "Pants", "Shoes"]
        elif category == "Food":
            self.subcategory_combobox['values'] = ["Fruit", "Beverage", "Snack", "Energy Bar"]
        self.subcategory_combobox.set('')
        self.update_attributes(None)
    
    @log_function_call
    def update_attributes(self, event):
        # Clear previous attribute input fields
        for widget in self.attribute_entries.values():
            widget.destroy()
        self.attribute_entries.clear()

        subcategory = self.subcategory_combobox.get()
        attributes = []

        if subcategory == "Smartphone":
            attributes = ["Brand", "Model", "Screen Size", "Storage Capacity", "Color"]
        elif subcategory == "Laptop":
            attributes = ["Brand", "Model", "Processor", "Memory", "Storage Capacity", "Graphics Card"]
        elif subcategory == "Headphones":
            attributes = ["Brand", "Model", "Type", "Connection Type", "Color"]
        elif subcategory == "Smartwatch":
            attributes = ["Brand", "Model", "Screen Size", "Operating System", "Color"]
        elif subcategory in ["Shirt", "Pants"]:
            attributes = ["Brand", "Size", "Color", "Material"]
        elif subcategory == "Shoes":
            attributes = ["Brand", "Size", "Color", "Type"]
        elif subcategory in ["Fruit", "Beverage", "Snack", "Energy Bar"]:
            attributes = ["Brand", "Weight/Volume", "Shelf Life", "Origin"]

        for i, attr in enumerate(attributes):
            ttk.Label(self.form_frame, text=f"{attr}:").grid(row=5+i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(self.form_frame)
            entry.grid(row=5+i, column=1, padx=5, pady=5)
            self.attribute_entries[attr] = entry

    @log_function_call
    def submit_restock(self):
        category = self.category_combobox.get()
        subcategory = self.subcategory_combobox.get()
        product_name = self.product_name_entry.get()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid quantity and price")
            return
        
        # Get attribute values
        attributes = {attr: entry.get() for attr, entry in self.attribute_entries.items()}
        
        # Check if product_data.json exists, if not create a new one
        if not os.path.exists('product_data.json'):
            with open('product_data.json', 'w') as file:
                json.dump({}, file)
        
        with open('product_data.json', 'r') as file:
            data = json.load(file)
        
        if product_name not in data:
            data[product_name] = {
                'category': category,
                'subcategory': subcategory,
                'price': price,
                'stock': quantity,
                'attributes': attributes
            }
        else:
            data[product_name]['stock'] += quantity
            data[product_name]['price'] = price
            data[product_name]['category'] = category
            data[product_name]['subcategory'] = subcategory
            data[product_name]['attributes'] = attributes
        
        with open('product_data.json', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        messagebox.showinfo("Restock Successful", f"Successfully restocked {quantity} {product_name} at ¥{price:.2f}")
        self.create_first_page()


from abc import ABC, abstractmethod

class Product(ABC):
    def __init__(self, product_name, price, amount):
        self.product_name = product_name
        self.price = price
        self.amount = amount

    @abstractmethod
    def display_info(self):
        pass

    @abstractmethod
    def calculate_discount(self):
        pass

# Three main categories
class ElectronicProduct(Product):
    def __init__(self, product_name, price, amount, brand):
        super().__init__(product_name, price, amount)
        self.brand = brand

    def display_info(self):
        return f"Electronic: {self.product_name}, Brand: {self.brand}, Price: {self.price}, Amount: {self.amount}"
    
    def calculate_discount(self):
        return self.price * 0.9

class ClothingProduct(Product):
    def __init__(self, product_name, price, amount, size):
        super().__init__(product_name, price, amount)
        self.size = size
     
    def calculate_discount(self):
        return self.price * 0.8

    def display_info(self):
        return f"Clothing: {self.product_name}, Size: {self.size}, Price: {self.price}, Amount: {self.amount}"

class FoodProduct(Product):
    def __init__(self, product_name, price, amount, expiry_date):
        super().__init__(product_name, price, amount)
        self.expiry_date = expiry_date
    
    def calculate_discount(self):
        return self.price * 0.95

    def display_info(self):
        return f"Food: {self.product_name}, Expiry Date: {self.expiry_date}, Price: {self.price}, Amount: {self.amount}"

# Subclasses of electronic products
class Smartphone(ElectronicProduct):
    def __init__(self, product_name, price, amount, brand, os):
        super().__init__(product_name, price, amount, brand)
        self.os = os

    def display_info(self):
        return f"Smartphone: {self.product_name}, Brand: {self.brand}, OS: {self.os}, Price: {self.price}, Amount: {self.amount}"

class Laptop(ElectronicProduct):
    def __init__(self, product_name, price, amount, brand, processor):
        super().__init__(product_name, price, amount, brand)
        self.processor = processor

    def display_info(self):
        return f"Laptop: {self.product_name}, Brand: {self.brand}, Processor: {self.processor}, Price: {self.price}, Amount: {self.amount}"

class Headphones(ElectronicProduct):
    def __init__(self, product_name, price, amount, brand, type):
        super().__init__(product_name, price, amount, brand)
        self.type = type

    def display_info(self):
        return f"Headphones: {self.product_name}, Brand: {self.brand}, Type: {self.type}, Price: {self.price}, Amount: {self.amount}"

# Subclasses of clothing products
class Shirt(ClothingProduct):
    def __init__(self, product_name, price, amount, size, material):
        super().__init__(product_name, price, amount, size)
        self.material = material

    def display_info(self):
        return f"Shirt: {self.product_name}, Size: {self.size}, Material: {self.material}, Price: {self.price}, Amount: {self.amount}"

class Pants(ClothingProduct):
    def __init__(self, product_name, price, amount, size, style):
        super().__init__(product_name, price, amount, size)
        self.style = style

    def display_info(self):
        return f"Pants: {self.product_name}, Size: {self.size}, Style: {self.style}, Price: {self.price}, Amount: {self.amount}"

class Shoes(ClothingProduct):
    def __init__(self, product_name, price, amount, size, type):
        super().__init__(product_name, price, amount, size)
        self.type = type

    def display_info(self):
        return f"Shoes: {self.product_name}, Size: {self.size}, Type: {self.type}, Price: {self.price}, Amount: {self.amount}"

# Subclasses of food products
class Fruit(FoodProduct):
    def __init__(self, product_name, price, amount, expiry_date, origin):
        super().__init__(product_name, price, amount, expiry_date)
        self.origin = origin

    def display_info(self):
        return f"Fruit: {self.product_name}, Origin: {self.origin}, Expiry Date: {self.expiry_date}, Price: {self.price}, Amount: {self.amount}"

class Beverage(FoodProduct):
    def __init__(self, product_name, price, amount, expiry_date, volume):
        super().__init__(product_name, price, amount, expiry_date)
        self.volume = volume

    def display_info(self):
        return f"Beverage: {self.product_name}, Volume: {self.volume}, Expiry Date: {self.expiry_date}, Price: {self.price}, Amount: {self.amount}"

class Snack(FoodProduct):
    def __init__(self, product_name, price, amount, expiry_date, flavor):
        super().__init__(product_name, price, amount, expiry_date)
        self.flavor = flavor

    def display_info(self):
        return f"Snack: {self.product_name}, Flavor: {self.flavor}, Expiry Date: {self.expiry_date}, Price: {self.price}, Amount: {self.amount}"

class SmartWatch(ElectronicProduct, ClothingProduct):
    def __init__(self, product_name, price, amount, brand, size, os):
        ElectronicProduct.__init__(self, product_name, price, amount, brand)
        ClothingProduct.__init__(self, product_name, price, amount, size)
        self.os = os

    def display_info(self):
        return f"SmartWatch: {self.product_name}, Brand: {self.brand}, Size: {self.size}, OS: {self.os}, Price: {self.price}, Amount: {self.amount}"

class EnergyBar(FoodProduct):
    def __init__(self, product_name, price, amount, expiry_date, size, flavor):
        FoodProduct.__init__(self, product_name, price, amount, expiry_date)
        self.flavor = flavor

    def display_info(self):
        return f"EnergyBar: {self.product_name}, Flavor: {self.flavor}, Size: {self.size}, Expiry Date: {self.expiry_date}, Price: {self.price}, Amount: {self.amount}"


def main():
    root = tk.Tk()
    root.title("alibaobao")
    root.geometry("800x600")

    sv_ttk.set_theme("light")
    
    # Provide default username and password
    username = "default_user"
    password = "default_password"

    user= User(username, password, root)
    user.create_login_page()
    root.mainloop()

main()

