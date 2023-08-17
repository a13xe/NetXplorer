import time
import psutil
import socket
import platform
import threading
import subprocess
import customtkinter


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("theme.json")


class NetXplorer(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("NetXplorer - Network Analysis Tool")
        self.geometry(f"{750}x{480}")
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # host frame
        self.frame_hostinfo = customtkinter.CTkFrame(self, width=730, corner_radius=10)
        self.frame_hostinfo.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.frame_hostinfo.grid_rowconfigure(1, weight=1)
        self.frame_hostinfo.grid_columnconfigure(4, weight=1)
        # host name entry
        self.entry = customtkinter.CTkEntry(self.frame_hostinfo, placeholder_text="Host name", width=300)
        self.entry.grid(row=0, column=0, padx=(10, 0), pady=(10, 10), sticky="nsew")
        # optionemenu
        self.actions = ["Ping", "IP Info", "Resolve IP"]
        self.optionemenu_action = customtkinter.CTkOptionMenu(self.frame_hostinfo, values=self.actions)
        self.optionemenu_action.grid(row=0, column=2, padx=(10, 0), pady=(10, 10), sticky="nsew")
        # action button
        self.button_action = customtkinter.CTkButton(master=self.frame_hostinfo, text="GO", border_width=2, text_color=("gray10", "#DCE4EE"), command=self.perform_action)
        self.button_action.grid(row=0, column=3, padx=(10, 0), pady=(10, 10), sticky="nsew")
        # checkbox
        self.clear_text_var = customtkinter.IntVar()
        self.checkbox_clear = customtkinter.CTkCheckBox(master=self.frame_hostinfo, text="Clear Text", variable=self.clear_text_var)
        self.checkbox_clear.grid(row=0, column=4, padx=(10, 10), pady=(10, 10), sticky="nsew")
        
        # textbox
        self.textbox = customtkinter.CTkTextbox(self, wrap=customtkinter.WORD, height=350)
        self.textbox.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="nsew")
        
        # button frame
        self.frame_buttons = customtkinter.CTkFrame(self, width=730, corner_radius=10)
        self.frame_buttons.grid(row=2, column=0, padx=(10, 10), pady=(0, 10), sticky="nsew")
        self.frame_buttons.grid_rowconfigure(1, weight=1)
        self.frame_buttons.grid_columnconfigure(2, weight=1)
        self.button_system_info = customtkinter.CTkButton(master=self.frame_buttons, width=230, fg_color="transparent", border_width=2, text="Show System Information", command=self.show_system_info)
        self.button_system_info.grid(row=0, column=0, padx=(10, 0), pady=(10, 10), sticky="nsew")
        self.button_connections = customtkinter.CTkButton(master=self.frame_buttons, width=230, fg_color="transparent", border_width=2, text="Show Connections", command=self.show_connections)
        self.button_connections.grid(row=0, column=1, padx=(10, 0), pady=(10, 10), sticky="nsew")
        self.button_monitor_traffic = customtkinter.CTkButton(master=self.frame_buttons, width=230, fg_color="transparent", border_width=2, text="Monitor Traffic (5s)", command=lambda: threading.Thread(target=self.monitor_traffic, daemon=True).start())
        self.button_monitor_traffic.grid(row=0, column=2, padx=(10, 10), pady=(10, 10), sticky="nsew")

        # set default values
        self.checkbox_clear.select()


    def perform_action(self):
        if self.clear_text_var.get():
            self.textbox.delete(1.0, customtkinter.END)
        input_value = self.entry.get()
        if self.optionemenu_action.get() == "Ping":
            self.ping_host(input_value)
        elif self.optionemenu_action.get() == "IP Info":
            self.get_ip_info(input_value)
        elif self.optionemenu_action.get() == "Resolve IP":
            self.resolve_ip(input_value)


    def ping_host(self, host):
        response = subprocess.run(["ping", "-c", "4", host], stdout=subprocess.PIPE)
        self.textbox.insert(customtkinter.END, response.stdout.decode())

    def get_ip_info(self, host):
        try:
            ip_address = socket.gethostbyname(host)
            self.textbox.insert(customtkinter.END, f"IP address of {host}: {ip_address}\n")
        except socket.gaierror:
            self.textbox.insert(customtkinter.END, f"Unable to resolve {host}.\n")

    def resolve_ip(self, ip_to_resolve):
        try:
            host_name = socket.gethostbyaddr(ip_to_resolve)
            self.textbox.insert(customtkinter.END, f"Hostname for {ip_to_resolve}: {host_name[0]}\n")
        except socket.herror:
            self.textbox.insert(customtkinter.END, f"Unable to resolve {ip_to_resolve}.\n")


    def show_system_info(self):
        if self.clear_text_var.get():
            self.textbox.delete(1.0, customtkinter.END)
        uname_info = platform.uname()
        cpu_count = psutil.cpu_count(logical=False)
        virtual_memory = psutil.virtual_memory()
        self.textbox.insert(customtkinter.END, f"System: {uname_info.system}\n")
        self.textbox.insert(customtkinter.END, f"Release: {uname_info.release}\n")
        self.textbox.insert(customtkinter.END, f"Machine: {uname_info.machine}\n")
        self.textbox.insert(customtkinter.END, f"Processor: {uname_info.processor}\n")
        self.textbox.insert(customtkinter.END, f"CPU cores: {cpu_count}\n")
        self.textbox.insert(customtkinter.END, f"Total RAM: {virtual_memory.total >> 20} MB\n")

    def show_connections(self):
        if self.clear_text_var.get():
            self.textbox.delete(1.0, customtkinter.END)
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            self.textbox.insert(customtkinter.END, f"Protocol: {conn.type} Address: {conn.laddr} Status: {conn.status}\n")

    def monitor_traffic(self):
        if self.clear_text_var.get():
            self.textbox.delete(1.0, customtkinter.END)
        initial_counts = psutil.net_io_counters()
        time.sleep(5)
        final_counts = psutil.net_io_counters()
        sent_bytes = final_counts.bytes_sent - initial_counts.bytes_sent
        recv_bytes = final_counts.bytes_recv - initial_counts.bytes_recv
        self.textbox.insert(customtkinter.END, f"Sent: {sent_bytes} bytes, Received: {recv_bytes} bytes in the last 5 seconds.\n")


if __name__ == "__main__":
    app = NetXplorer()
    app.mainloop()
