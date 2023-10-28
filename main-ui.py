import ctypes, sys
import os
import tkinter
import tkinter.messagebox
from subprocess import Popen, PIPE
from tkinter import filedialog, Listbox
import customtkinter
import pyautogui
from system_hotkey import SystemHotkey

from scanner import StatsScanner
from ppadb.client import Client
from config import getParameters, setParameters
import threading

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class CustomScrollableListBox(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, height=0)

        self.columnconfigure(0, weight=1)
        self.windowsList = Listbox(self, background="gray30", borderwidth=0, highlightthickness=0,
                                   height=0)
        self.windowsList.grid(row=0, column=0, padx=0, pady=0, sticky="nsew", columnspan=2)

    def insert(self, key, value):
        self.windowsList.insert(key, value)

    def select(self, index):
        self.windowsList.select_set(index)

    def clear(self):
        self.windowsList.delete(0, tkinter.END)


class ADBSelector(customtkinter.CTkFrame):
    def __init__(self, master, params):
        super().__init__(master)

        self.descLabel = customtkinter.CTkLabel(master=self, text="Select the ADB Device")
        self.grid_columnconfigure(0, weight=1)
        self.descLabel = customtkinter.CTkLabel(self, text="ADB Device Address")
        self.descLabel.grid(row=0, column=0, padx=(12, 10), pady=(10, 0), sticky="nw")
        self.devAddress = customtkinter.CTkEntry(self)
        self.devAddress.insert(0, params["serial"])
        self.devAddress.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="new")

        # self.grid_columnconfigure(0, weight=1)
        # self.descLabel = customtkinter.CTkLabel(self, text="Select the ADB device")
        # self.descLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
        # self.refreshButton = customtkinter.CTkButton(self, text="Refresh", width=50,
        #                                              command=self.refresh_button_callback)
        # self.refreshButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ne")
        #
        # self.windowlistscroll = CustomScrollableListBox(self)
        # self.windowlistscroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew", columnspan=2)
        # self.fillWindows()

    # def fillWindows(self):
    #     # get all windows
    #
    #     adb = Client(host='localhost', port=5037)
    #     devices = adb.devices()
    #     index = 0
    #     for device in devices:
    #         self.windowlistscroll.insert(index, device)
    #     self.windowlistscroll.select(0)

    # def refresh_button_callback(self):
    #     self.windowlistscroll.clear()
    #     self.fillWindows()

    def get(self):
        return self.devAddress.get()


class PCWindowSelector(customtkinter.CTkFrame):
    def __init__(self, master, params):
        super().__init__(master)
        # self.configure(fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.descLabel = customtkinter.CTkLabel(master=self, text="Rok Window Name")
        self.descLabel.grid(row=0, column=0, padx=(12, 10), pady=(10, 0), sticky="nw")
        self.windowName = customtkinter.CTkEntry(self)
        self.windowName.insert(0, params["window"])
        self.windowName.grid(row=1, column=0, padx=(10, 10), pady=(0, 10), sticky="new")

    #     self.descLabel = customtkinter.CTkLabel(self, text="Select RoK Window")
    #     self.descLabel.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nw")
    #
    #     self.refreshButton = customtkinter.CTkButton(self, text="Refresh", width=50,
    #                                                  command=self.refresh_button_callback)
    #     self.refreshButton.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ne")
    #
    #     self.windowlistscroll = CustomScrollableListBox(self)
    #     self.windowlistscroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew", columnspan=2)
    #
    #     self.fillWindows()
    #
    # def fillWindows(self):
    #     # get all windows
    #     windTitles = pyautogui.getAllTitles()
    #     index = 0
    #     rokIndex = 0
    #     for wind in windTitles:
    #         if wind:
    #             self.windowlistscroll.insert(index, wind)
    #             if wind == "Rise of Kingdoms":
    #                 rokIndex = index
    #     self.windowlistscroll.select(rokIndex)
    #
    # def refresh_button_callback(self):
    #     self.windowlistscroll.clear()
    #     self.fillWindows()

    def get(self):
        return self.windowName.get()


class SourceFrame(customtkinter.CTkFrame):
    def __init__(self, master, params):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "Scanning Device"
        self.deviceVariable = customtkinter.StringVar(value="")

        # Title label
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color=("gray65", "gray30"), corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="ew")

        # Radio buttons
        self.devChoiceFrame = customtkinter.CTkFrame(self)  # , fg_color="transparent"
        self.devChoiceFrame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.devChoiceFrame.columnconfigure(1, weight=1)

        self.pcRadioButton = customtkinter.CTkRadioButton(self.devChoiceFrame, text="PC Version", value="pc",
                                                          variable=self.deviceVariable, command=self.setInfoView)
        self.pcRadioButton.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.adbRadioButton = customtkinter.CTkRadioButton(self.devChoiceFrame, text="ADB (BlueStacks)", value="adb",
                                                           variable=self.deviceVariable, command=self.setInfoView)
        self.adbRadioButton.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="w")

        self.adbInfo = ADBSelector(self, params)
        self.adbInfo.grid(row=1, column=1, padx=(0, 10), pady=(10, 10), sticky="nsew")
        self.pcInfo = PCWindowSelector(self, params)
        self.pcInfo.grid(row=1, column=1, padx=(0, 10), pady=(10, 10), sticky="nsew")

        self.deviceVariable.set(params["device"])
        self.setInfoView()

        msg1 = "Required Resolution: 1920x1080 in Fullscreen"
        msg2 = "The game must be opened on the individual power ranking"
        self.msg1 = customtkinter.CTkLabel(self, text=msg1, fg_color="transparent", corner_radius=6, height=15)
        self.msg1.grid(row=3, column=0, padx=10, pady=(0, 0), columnspan=2, sticky="w")
        self.msg2 = customtkinter.CTkLabel(self, text=msg2, fg_color="transparent", corner_radius=6, height=15)
        self.msg2.grid(row=4, column=0, padx=10, pady=(5, 10), columnspan=2, sticky="w")

    def setInfoView(self):
        selected = self.deviceVariable.get()
        if selected == "pc":
            self.adbInfo.grid_remove()
            self.pcInfo.grid()
        else:
            self.pcInfo.grid_remove()
            self.adbInfo.grid()

    def get(self):
        devType = self.deviceVariable.get()
        ret = {"device": devType}
        ret.update({"window": self.pcInfo.get()})
        ret.update({"serial": self.adbInfo.get()})
        return ret


class ScanParametersFrame(customtkinter.CTkFrame):
    def __init__(self, master, params):
        super().__init__(master)

        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "Scan Parameters"

        # Title label
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color=("gray65", "gray30"), corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="ew")

        # number of profiles
        self.descLabel = customtkinter.CTkLabel(self, text="Number of profiles to scan")
        self.descLabel.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="nw")
        self.profilesNumber = customtkinter.CTkEntry(self)
        self.profilesNumber.insert(0, params["count"])
        self.profilesNumber.grid(row=1, column=1, padx=(0, 10), pady=(10, 10), sticky="nsew")

    def get(self):
        return {"count": self.profilesNumber.get()}


class OutputFrame(customtkinter.CTkFrame):
    def __init__(self, master, params):
        super().__init__(master)

        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "Output"

        # Title label
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color=("gray65", "gray30"), corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="ew")

        # Output directory
        self.descLabel = customtkinter.CTkLabel(self, text="Output folder:")
        self.descLabel.grid(row=1, column=0, padx=10, pady=(10, 0), columnspan=2, sticky="nw")
        self.browseButton = customtkinter.CTkButton(self, text="Browse", width=50, height=14,
                                                    command=self.browse_button_callback)
        self.browseButton.grid(row=1, column=1, padx=10, pady=(10, 0), columnspan=2, sticky="ne")
        self.outPath = customtkinter.CTkEntry(self)
        self.outPath.insert(0, params["dir"])
        self.outPath.grid(row=2, column=0, padx=10, pady=(0, 10), columnspan=2, sticky="nsew")

        self.descLabel = customtkinter.CTkLabel(self, text="Tag (subfolder name)")
        self.descLabel.grid(row=3, column=0, padx=(10, 0), pady=(0, 10), sticky="nw")
        self.tag = customtkinter.CTkEntry(self)
        self.tag.insert(0, params["tag"])
        self.tag.grid(row=3, column=1, padx=(0, 10), pady=(0, 10), sticky="new")

    def browse_button_callback(self):
        filename = filedialog.askdirectory()
        self.outPath.delete(0, tkinter.END)
        self.outPath.insert(0, filename)

    def get(self):
        return {
            "dir": self.outPath.get(),
            "tag": self.tag.get()
        }


SIZE_STR = "380x558"


class App(customtkinter.CTk):
    def __init__(self, params):
        super().__init__()

        hk = SystemHotkey()
        hk.register(['f10'], callback=lambda event: self.stopScanning())

        self.title("RoKStat")
        self.geometry(SIZE_STR)
        self.attributes('-topmost', True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Source Frame
        self.sourceFrame = SourceFrame(self, params)
        self.sourceFrame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Scan Parameters Frame
        self.scanParams = ScanParametersFrame(self, params)
        self.scanParams.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Output frame
        self.outFrame = OutputFrame(self, params)
        self.outFrame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsew")

        # Scan Controls Frame
        self.scanFrame = customtkinter.CTkFrame(self)
        self.scanFrame.grid(row=3, column=0, padx=10, pady=10, sticky="sew", columnspan=2)
        self.scanFrame.grid_columnconfigure((1, 2), weight=1)

        self.button = customtkinter.CTkButton(self.scanFrame, text="Start Scan", command=self.button_callback,
                                              width=100)
        self.button.grid(row=0, column=0, padx=10, pady=(10, 3), sticky="nsw", rowspan=2)

        self.stopButton = customtkinter.CTkButton(self.scanFrame, text="Stop (F10)", command=self.stopScanning,
                                                  width=100, height=18, state="disabled")
        self.stopButton.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="sw")

        # TODO: add stop button

        self.progressbar = customtkinter.CTkProgressBar(self.scanFrame, orientation="horizontal", height=20,
                                                        mode="determinate")
        self.progressbar.set(0)
        self.progressbar.grid(row=0, column=1, padx=(0, 10), pady=(10, 8), sticky="new", columnspan=2)

        self.scannedNoLabel = customtkinter.CTkLabel(self.scanFrame, text="Scanned", corner_radius=6, height=18)
        self.scannedNoLabel.grid(row=1, column=1, padx=(0, 10), pady=(0, 8), sticky="nw")

        self.scannedNoVar = customtkinter.StringVar()
        self.scannedNo = customtkinter.CTkLabel(self.scanFrame, textvariable=self.scannedNoVar,
                                                fg_color=("gray80", "gray20"), corner_radius=12,
                                                width=80, height=18, anchor="e")
        self.scannedNo.grid(row=1, column=2, padx=(0, 10), pady=(0, 5), sticky="ne")

        self.timeLabel = customtkinter.CTkLabel(self.scanFrame, text="Time to finish (m.ss)", corner_radius=6,
                                                height=18)
        self.timeLabel.grid(row=2, column=1, padx=(0, 10), pady=(0, 10), sticky="nw")

        self.timeToFinishVar = customtkinter.StringVar()
        self.timeToFinish = customtkinter.CTkLabel(self.scanFrame, textvariable=self.timeToFinishVar,
                                                   fg_color=("gray80", "gray20"), corner_radius=12,
                                                   width=80, height=18, anchor="e")
        self.timeToFinish.grid(row=2, column=2, padx=(0, 10), pady=(0, 5), sticky="ne")

    def updateProgress(self, value, total, timeInterval):
        self.progressbar.set(value / total)
        self.scannedNoVar.set(str(value))
        timePerProfile = int(timeInterval.total_seconds() / value)
        secondRem = timePerProfile * (total - value)
        secondsParts = secondRem % 60
        self.timeToFinishVar.set("{}.{:02d}".format(int((secondRem - secondsParts) / 60), secondsParts))

        # check if scanning finished
        if value == total:
            # Disable/enable the start/stop buttons
            self.button.configure(state="normal")
            self.stopButton.configure(state="disabled")

    def stopScanning(self):
        self.stopButton.configure(state="disabled")
        self.stopButton.configure(text="Stopping ...")
        self.update_idletasks()

        self.stopEvent.set()
        while self.scanThread.is_alive():
            self.scanThread.join(2.0)

        # TODO: using only the join function does not work as expected. Even when the thread finishes the work, it
        #  never joins the main thread. It will join on the timeout only. I had to use the while loop above.

        self.button.configure(state="normal")
        self.stopButton.configure(text="Stop (F10)")

    def button_callback(self):
        params = self.sourceFrame.get()
        params.update(self.scanParams.get())
        params.update(self.outFrame.get())

        setParameters(params)

        # Validation
        if params["device"] == "pc":
            # The program must be running in administration mode. If not restart with admin privileges.
            if not is_admin():
                tkinter.messagebox.showinfo(
                    title="RokStat - Must Run as Administrator!",
                    message="To run with the PC version, this application must run as administrator.\n\nThe program "
                            "will now restart and prompt you for administrator privileges.")
                # Re-run the program with admin rights
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()

            # check if the game is running
            windTitles = pyautogui.getAllTitles()
            if params["window"] not in windTitles:
                tkinter.messagebox.showwarning(
                    title="RokStat - Rok Not Running!",
                    message="The Rise of Kingdom is not running.\n\nPlease start RoK, open the individual power "
                            "ranking list and start the scan again."
                )
                return

            # move the application to the top-left corner.
            self.geometry("{}+10+10".format(SIZE_STR))

        else:
            # Check if adb installed
            if not StatsScanner.is_tool("adb"):
                tkinter.messagebox.showerror(title="RoKStat - Missing Dependencies",
                                             message="We could not find the required adb engine in the PATH "
                                                     "variable.\n\nPlease refer to the documentation to install adb, "
                                                     "add it to the PATH, and restart the program.")
                sys.exit()

            # start the adb server
            # Try to connect to the device to the adb daemon and start the server
            process = Popen(["adb.exe", "connect", params["serial"]], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            print("ADB output: {}".format(output))

            # check if the device is connected
            adb = Client(host='localhost', port=5037)
            devices = adb.devices()

            found = False
            for device in devices:
                if device.serial == params["serial"]:
                    found = True
                    break

            if not found:
                tkinter.messagebox.showerror(title="RoKStat - Missing Dependencies",
                                             message="Could not find the device in the connected adb "
                                                     "devices.\n\nPlease double-check the device IP and port numbers.")
                return

        self.stopEvent = threading.Event()
        scanner = StatsScanner(params, self.stopEvent)
        self.progressbar.set(0)
        self.scannedNoVar.set(0)
        self.timeToFinishVar.set("...")
        self.scanThread = threading.Thread(name="scanner", target=scanner.start, args=(self.updateProgress,))

        # Disable/enable the start/stop buttons
        self.button.configure(state="disabled")
        self.stopButton.configure(state="normal")

        # Start the scanner
        self.scanThread.start()

    def key_pressed(self):
        print("F10 Pressed")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":

    customtkinter.set_appearance_mode("system")  # Modes: "system" (standard), "light", "dark"
    customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

    # get the initial parameters
    initialParams = getParameters()
    app = App(initialParams)

    if os.path.isfile("images/icon-32.ico"):
        app.iconbitmap("images/icon-32.ico")

    # Check if tesseract is installed
    if not StatsScanner.is_tool("tesseract"):
        tkinter.messagebox.showerror(title="RoKStat - Missing Dependencies", message="We could not find the required "
                                                                                     "Tesseract OCR executable in the "
                                                                                     "PATH variable.\n\nPlease refer "
                                                                                     "to the documentation to install "
                                                                                     "Tesseract, add it to the PATH, "
                                                                                     "and restart the program.")
        sys.exit()

    app.mainloop()

# customtkinter References
# https://customtkinter.tomschimansky.com/tutorial/frames
