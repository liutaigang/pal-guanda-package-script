import os
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory
import script
import cache

class GUI:
    def __init__(self):
        self.window = Tk()
        self.window.title('Pal K8s 发包脚本')
        self.window.geometry("550x600+600+250")
        self.cache = cache.Cache()
        self.render_window()
        self.recover_input_information()

    def recover_input_information(self):
        data = self.cache.get()
        if type(data) is dict:
            if "hostname" in data:
                self.var_hostname.set(data["hostname"])
            if "port" in data:
                self.var_port.set(data["port"])
            if "username" in data:
                self.var_username.set(data["username"])
            if "devopsNamespace" in data:
                self.var_namesapce_ip.set(data["devopsNamespace"])
            if "packageName" in data:
                self.var_package_name.set(data["packageName"])
            if "downloadPath" in data:
                self.var_download_path.set(data["downloadPath"])

    def query_docker_id(self):
        hostname = self.var_hostname.get()
        port = self.var_port.get()
        username = self.var_username.get()
        password = self.var_password.get()
        devopsNamespace = self.var_namesapce_ip.get()
        
        if hostname and port and username and password and devopsNamespace:
            self.script = script.Script(hostname, port, username, password, devopsNamespace)
            dockerIdList, errText = self.script.query_docker_id()
            if errText:
                print(errText)
            elif dockerIdList:
                self.entry_docker_id.config(values = dockerIdList, state="normal")
                self.btn_to_package.config(state = "normal")
                self.cache.save({
                    "hostname": hostname,
                    "port": port,
                    "username":username,
                    "devopsNamespace": devopsNamespace
                })
    
    def to_package(self):
        dockerName = self.var_docker_id.get()
        packageName = self.var_package_name.get()
        downloadPath = self.var_download_path.get()

        if dockerName and packageName and downloadPath:
            localPath, errText = self.script.to_package_download(dockerName, packageName, downloadPath)
            print(localPath, errText)
            self.cache.save({
               "packageName": packageName,
               "downloadPath": downloadPath
            })
            self.script.close_ssh()
            self.script.close_sftp()
            self.window.quit()

    def select_path(self):
        path_ = askdirectory()
        if path_:
            self.var_download_path.set(path_)

    def render_window(self):
        Label(self.window, text = 'Hostname').place(x = 100, y = 50)
        Label(self.window, text = 'Port').place(x = 100, y = 100)
        Label(self.window, text = 'Username').place(x = 100, y = 150)
        Label(self.window, text = 'Password').place(x = 100, y = 200)     
        Label(self.window, text = 'Namesapce/IP').place(x = 100, y = 250)
        Label(self.window, text = 'Docker ID').place(x = 100, y = 350)     
        Label(self.window, text = 'Package Name').place(x = 100, y = 400)   
        Label(self.window, text = 'Download Path').place(x = 100, y = 450)
 
        self.var_hostname = StringVar()
        entry_hostname = Entry(self.window, textvariable = self.var_hostname, width = 35)
        entry_hostname.place(x = 200, y = 50)

        self.var_port = IntVar(value=22)
        entry_port = Entry(self.window, textvariable = self.var_port, width = 35)
        entry_port.place(x = 200, y = 100)

        self.var_username = StringVar()
        entry_username = Entry(self.window, textvariable = self.var_username, width = 35)
        entry_username.place(x = 200, y = 150)

        self.var_password = StringVar()
        entry_password = Entry(self.window, textvariable = self.var_password, width = 35, show="*")
        entry_password.place(x = 200, y = 200)

        self.var_namesapce_ip = StringVar()
        entry_namesapce_ip = Entry(self.window, textvariable = self.var_namesapce_ip, width = 35)
        entry_namesapce_ip.place(x = 200, y = 250)

        Button(self.window, text = '获取容器ID',  bg='#54FA9B', command = self.query_docker_id, width=10).place(x = 370, y = 290)
        
        self.var_docker_id = StringVar()
        self.entry_docker_id = ttk.Combobox(self.window, textvariable = self.var_docker_id, values = [], state="disabled", width = 33)
        self.entry_docker_id.place(x = 200, y = 350)

        self.var_package_name = StringVar()
        entry_package_name = Entry(self.window, textvariable = self.var_package_name, width = 35)
        entry_package_name.place(x = 200, y = 400)

        self.var_download_path = StringVar(self.window, value=os.path.abspath(os.path.curdir))
        entry_download_path = Entry(self.window, textvariable = self.var_download_path, width = 35)
        entry_download_path.place(x = 200, y = 450)
        Button(self.window, text = '选择目录', command = self.select_path).place(x = 460, y = 445)

        self.btn_to_package = Button(self.window, text = '开始打包', bg='#54FA9B', command = self.to_package, state="disabled", width=10)
        self.btn_to_package.place(x = 370, y = 500)

if __name__ == '__main__':
    gui = GUI()
    gui.window.mainloop()