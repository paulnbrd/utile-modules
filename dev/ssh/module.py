from utile import utils
import os
import json
import termcolor
import platform
import subprocess


ERROR_CODES = {
    "2": "Connection failed",
    "65": "Host not allowed to connect",
    "66": "General error in ssh protocol",
    "67": "Key exchange failed",
    "68": "Reserved",
    "69": "MAC error",
    "70": "Compression error",
    "71": "Service not available",
    "72": "Protocol version not supported",
    "73": "Host key not verifiable",
    "74": "Connection failed",
    "75": "Disconnected by application",
    "76": "Too many connections",
    "77": "Authentication cancelled by user",
    "78": "No more authentication methods available",
    "79": "Invalid user name",
    "255": "Timeout error"
}


def filename_validify(string: str):
    """Converts the given string into a valid filename
    """
    return "".join([c for c in string if c.isalpha() or c.isdigit() or c==' ']).rstrip()



class Executor:
    def __init__(self) -> None:
        self.connections = []
        self.connections_directory = utils.Directory.create_storage_directory("ssh")
        self.load_connections()
    
    def is_valid_connection(self, connection: dict):
        if len(connection.keys()) != 3:
            return False
        if "name" not in connection.keys():
            return False
        if "username" not in connection.keys():
            return False
        if "host" not in connection.keys():
            return False
        return True
    
    def get_connection_save_path(self, connection_name: str):
        return os.path.join(self.connections_directory, connection_name)
    
    def load_connections(self):
        l = os.listdir(self.connections_directory)
        for save_name in l:
            save_real_path = self.get_connection_save_path(save_name)
            if not os.path.isfile(save_real_path):
                continue
            try:
                with open(save_real_path, "r") as f:
                    data = json.load(f)
                    if not self.is_valid_connection(data):
                        print("Invalid connection found for {}".format(save_name))
                        continue
                    self.connections.append(data)
            except Exception as e:
                print(e)
                print("Could not load SSH connection at {}".format(save_name))
    
    def save_connection(self, connection_name: str, username: str, host: str):
        data = {
            "name": connection_name,
            "username": username,
            "host": host
        }
        try:
            with open(self.get_connection_save_path(connection_name), 'w') as f:
                json.dump(data, f)
            return True
        except:
            return False
    
    def get_connection_by_name(self, name: str):
        for conn in self.connections:
            if conn["name"] == name:
                return conn
        return None
    
    def has_connection_with_name(self, name: str):
        conn = self.get_connection_by_name(name)
        if conn is not None:
            return True
    
    def register_ssh(self, connection_name: str, username: str, host: str):
        if self.has_connection_with_name(connection_name):
            print("This name is already used")
            return False
        self.connections.append({
            "name": connection_name,
            "username": username,
            "host": host
        })
        if not self.save_connection(connection_name, username, host):
            print("Could not save the connection")
        return True
    
    def has_ssh(self):
        try:
            if "linux" in platform.platform().lower():
                subprocess.check_output(["which", "ssh"])
            elif "windows" in platform.platform().lower():
                subprocess.check_output(["where", "ssh"])
            return True
        except:
            return False
        
    def connect(self, name: str):
        if not self.has_ssh():
            print(termcolor.colored("SSH is not installed"))
        if not self.has_connection_with_name(name):
            print("Could not find connection {}".format(name))
        connection = self.get_connection_by_name(name)
        print("Connecting to {}".format(termcolor.colored(name, "green")))
        try:
            subprocess.check_output(["ssh", "{}@{}".format(connection["username"], connection["host"])])
            print(termcolor.colored("SSH connection terminated successfully", "green"))
        except subprocess.CalledProcessError as e:
            if str(e.returncode) in ERROR_CODES.keys():
                print(termcolor.colored(
                    ERROR_CODES.get(str(e.returncode)), "red"
                ))
            else:
                print(termcolor.colored("SSH exited with error code {}".format(e.returncode), "red"))
                
    def remove_connection(self, name: str):
        if self.has_connection_with_name(name):
            conn = self.get_connection_by_name(name)
            self.connections.remove(conn)
            os.unlink(self.get_connection_save_path(name))

instance = Executor()

class SSH:
    def register(self, connection_name: str, username: str, host: str):
        instance.register_ssh(connection_name, username, host)
        
    def remove(self, name: str):
        if not instance.has_connection_with_name(name):
            print(termcolor.colored("Could not find any connection with name {}".format(name), "red"))
            return
        try:
            instance.remove_connection(name)
            print(termcolor.colored("Removed successfully", "green"))
        except:
            print(termcolor.colored("Could not remove connection", "red"))
    def list(self, show_addresses: bool = False):
        print("List of registered SSH connections:")
        for connection in instance.connections:
            if show_addresses:
                print("> {} ({}@{})".format(
                    termcolor.colored(connection["name"], "green"),
                    connection["username"],
                    connection["host"]
                ))
            else:
                print("> {}".format(
                    termcolor.colored(connection["name"], "green")
                ))
        if len(instance.connections) == 0:
            print("> No registered connection")
        
    def connect(self, name: str):
        instance.connect(name)


MODULE = SSH
