from shutil import which
import pyperclip
import io
import re
import os
import time
from ppadb.client import Client as AdbClient
from PIL import Image, ImageFilter
import pytesseract
import csv
from datetime import datetime, timezone
from PIL.ImageOps import autocontrast, invert, grayscale
import pyautogui
from enum import Enum


class ImageProcessingProfile(Enum):
    PLAIN = 1
    KILLS = 2
    ID = 3
    ALLIANCE = 4
    POWER = 5
    INFO = 6
    KILLPOINTS = 7

class DevicePC:

    def __init__(self):
        self.width, self.height = pyautogui.size()

        print("Resolution: {}x{}".format(self.width, self.height))

        self.TAPS = {
            "1": (self.scaleHorizontal(530), self.scaleVertical(400)),
            "2": (self.scaleHorizontal(530), self.scaleVertical(485)),
            "3": (self.scaleHorizontal(530), self.scaleVertical(570)),
            "4": (self.scaleHorizontal(530), self.scaleVertical(655)),
            "info": (self.scaleHorizontal(810), self.scaleVertical(780), self.scaleHorizontal(967),
                     self.scaleVertical(193), self.scaleHorizontal(89), self.scaleVertical(36), False,
                     ImageProcessingProfile.PLAIN, False, True, "info"),
            "kills": (self.scaleHorizontal(913), self.scaleVertical(538), self.scaleHorizontal(1007),
                      self.scaleVertical(558), self.scaleHorizontal(50), self.scaleVertical(32), False,
                      ImageProcessingProfile.PLAIN, False, False, "kill"),
            "exitinfo": (self.scaleHorizontal(1456), self.scaleVertical(210), self.scaleHorizontal(979),
                         self.scaleVertical(234), self.scaleHorizontal(145), self.scaleVertical(36), False,
                         ImageProcessingProfile.PLAIN, False, True, "profile"),
            "exitprofile": (self.scaleHorizontal(1430), self.scaleVertical(250), self.scaleHorizontal(908),
                            self.scaleVertical(193), self.scaleHorizontal(128), self.scaleVertical(38), False,
                            ImageProcessingProfile.PLAIN, False, True, "power"),
            "+": (self.scaleHorizontal(530), self.scaleVertical(672)),
            "namecopy": (self.scaleHorizontal(607), self.scaleVertical(294)),
            "profile-exit-button": (self.scaleHorizontal(1400), self.scaleVertical(228), self.scaleHorizontal(61),
                                    self.scaleVertical(46), False, ImageProcessingProfile.PLAIN, True, True, "x"),
        }

        # format (x, y, width, height, numbers_only, invert, filters)
        self.PROFILE_PAGE_COORDINATES = {
            "id": (self.scaleHorizontal(1220), self.scaleVertical(323), self.scaleHorizontal(190),
                   self.scaleVertical(32), False, ImageProcessingProfile.ID, True, False),
            "alliance": (self.scaleHorizontal(1025), self.scaleVertical(438), self.scaleHorizontal(390),
                         self.scaleVertical(34), False, ImageProcessingProfile.ALLIANCE, True, True,
                         self.scaleHorizontal(8)),
            "power": (self.scaleHorizontal(1194), self.scaleVertical(480), self.scaleHorizontal(220),
                      self.scaleVertical(34), True, ImageProcessingProfile.POWER, True, False),
            "kill-points": (self.scaleHorizontal(1175), self.scaleVertical(522), self.scaleHorizontal(240),
                            self.scaleVertical(34), True, ImageProcessingProfile.KILLPOINTS, True, False),
        }

        # format (x, y, width, height, numbers_only, invert, filters)
        self.TOP_LIST_PAGE_COORDINATES = {
            "name": (self.scaleHorizontal(564), self.scaleVertical(648), self.scaleHorizontal(384),
                     self.scaleVertical(32), False, ImageProcessingProfile.PLAIN, True, False),
            "power": (self.scaleHorizontal(1246), self.scaleVertical(648), self.scaleHorizontal(140),
                      self.scaleVertical(44), True, ImageProcessingProfile.PLAIN, True, False),
        }

        # format (x, y, width, height, numbers_only, invert, filters)
        self.INFO_PAGE_COORDINATES = {
            "res-gather": (self.scaleHorizontal(1185), self.scaleVertical(672), self.scaleHorizontal(226),
                           self.scaleVertical(38), True, ImageProcessingProfile.INFO, True, False),
            "res-assist": (self.scaleHorizontal(1185), self.scaleVertical(724), self.scaleHorizontal(226),
                           self.scaleVertical(38), True, ImageProcessingProfile.INFO, True, False),
            "dead-count": (self.scaleHorizontal(1220), self.scaleVertical(532), self.scaleHorizontal(190),
                           self.scaleVertical(38), True, ImageProcessingProfile.INFO, True, True),
        }

        # format (x, y, width, height, numbers_only, invert)
        # "kill-points": (1058, 492, 240, 30, True, False, False),
        # Note, for the kills, decrease 6 from the x coordinates because we fill the first 7 pixels with white as margine.
        self.KILLS_PAGE_COORDINATES = {
            "t5-kills": (self.scaleHorizontal(868), self.scaleVertical(780), self.scaleHorizontal(190),
                         self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t5-points": (self.scaleHorizontal(1124), self.scaleVertical(780), self.scaleHorizontal(220),
                          self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t4-kills": (self.scaleHorizontal(868), self.scaleVertical(743), self.scaleHorizontal(190),
                         self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t4-points": (self.scaleHorizontal(1124), self.scaleVertical(743), self.scaleHorizontal(220),
                          self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t3-kills": (self.scaleHorizontal(868), self.scaleVertical(706), self.scaleHorizontal(190),
                         self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t3-points": (self.scaleHorizontal(1124), self.scaleVertical(706), self.scaleHorizontal(220),
                          self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t2-kills": (self.scaleHorizontal(868), self.scaleVertical(669), self.scaleHorizontal(190),
                         self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t2-points": (self.scaleHorizontal(1124), self.scaleVertical(669), self.scaleHorizontal(220),
                          self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t1-kills": (self.scaleHorizontal(868), self.scaleVertical(632), self.scaleHorizontal(190),
                         self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
            "t1-points": (self.scaleHorizontal(1124), self.scaleVertical(632), self.scaleHorizontal(220),
                          self.scaleVertical(30), True, ImageProcessingProfile.KILLS, False, False),
        }

        # format (x, y, width, height, numbers_only, invert)
        self.SELF_INFO_PAGE = {
            "name": (self.scaleHorizontal(618), self.scaleVertical(274), self.scaleHorizontal(292),
                     self.scaleVertical(39), False, ImageProcessingProfile.PLAIN, True, False),
            "verify": (self.scaleHorizontal(545), self.scaleVertical(488), self.scaleHorizontal(66),
                       self.scaleVertical(29), False, ImageProcessingProfile.PLAIN, True, False, "troops")
        }

    def get_tap_coords(self, key):
        return self.TAPS[key]

    def get_clipboard(self):
        return pyperclip.paste()

    def take_screenshot(self):
        return pyautogui.screenshot()

    def tap(self, coords, isFast: bool = True):
        if isFast:
            pyautogui.click(coords[0], coords[1])
        else:
            pyautogui.moveTo(coords[0], coords[1])
            pyautogui.mouseDown()
            pyautogui.mouseUp()

    def swipeProfileUp(self):
        pyautogui.moveTo(self.scaleHorizontal(530), self.scaleVertical(672))
        pyautogui.dragRel(0, -1 * self.scaleVertical(85), duration=2)
        time.sleep(1)

    def trimToSave(self, img):
        return img.crop((self.scaleHorizontal(412), self.scaleVertical(170), self.scaleHorizontal(1508), self.scaleVertical(978)))

    def scaleVertical(self, val):
        return val if self.height == 1080 else int(val/1080*self.height)

    def scaleHorizontal(self, val):
        return val if self.width == 1920 else int(val/1920*self.width)


class DeviceADB:
    TAPS = {
        "1": (342, 340),
        "2": (342, 462),
        "3": (342, 584),
        "4": (342, 706),
        "info": (426, 886, 968, 40, 128, 52, False, ImageProcessingProfile.PLAIN, False, True, "info"),
        "kills": (1342, 380, 1230, 405, 68, 43, False, ImageProcessingProfile.PLAIN, False, False, "kill"),
        "exitinfo": (1675, 66, 986, 102, 203, 50, False, ImageProcessingProfile.PLAIN, False, True, "profile"),
        "exitprofile": (1637, 120, 886, 42, 180, 50, False, ImageProcessingProfile.PLAIN, False, True, "power"),
        "+": (342, 733),
        "namecopy": (450, 186),
        "profile-exit-button": (1590, 90, 92, 70, False, ImageProcessingProfile.PLAIN, False, False, 'x'),
    }

    # format (x, y, width, height, numbers_only, invert, filters)
    PROFILE_PAGE_COORDINATES = {
        "id": (838, 232, 277, 42, False, ImageProcessingProfile.ID, True, False),
        "alliance": (708, 400, 324, 33, False, ImageProcessingProfile.ALLIANCE, True, True, 16),
        "power": (1055, 392, 281, 48, True, ImageProcessingProfile.POWER, True, False),
        "kill-points": (1355, 392, 283, 48, True, ImageProcessingProfile.KILLPOINTS, True, False),
    }

    # format (x, y, width, height, numbers_only, invert, filters)
    TOP_LIST_PAGE_COORDINATES = {
        "alliance-name": (400, 700, 400, 40, False, ImageProcessingProfile.PLAIN, True, False),
        "power": (1380, 700, 232, 50, True, ImageProcessingProfile.PLAIN, True, False),
    }

    # format (x, y, width, height, numbers_only, invert, filters)
    INFO_PAGE_COORDINATES = {
        "res-gather": (1290, 730, 315, 60, True, ImageProcessingProfile.INFO, True, False),
        "res-assist": (1290, 800, 315, 60, True, ImageProcessingProfile.INFO, True, False),
        "dead-count": (1290, 532, 315, 48, True, ImageProcessingProfile.INFO, True, True),
    }

    # format (x, y, width, height, numbers_only, invert, Filters)
    # Note, for the kills, decrease 6 from the x coordinates because we fill the first 7 pixels with white as margine.
    KILLS_PAGE_COORDINATES = {
        "t5-kills": (1031, 722, 272, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t5-points": (1416, 722, 300, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t4-kills": (1031, 670, 272, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t4-points": (1416, 670, 300, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t3-kills": (1031, 615, 272, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t3-points": (1416, 615, 300, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t2-kills": (1031, 564, 272, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t2-points": (1416, 564, 300, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t1-kills": (1031, 512, 272, 40, True, ImageProcessingProfile.KILLS, False, False),
        "t1-points": (1416, 512, 300, 40, True, ImageProcessingProfile.KILLS, False, False),
    }

    def __init__(self, serial):
        # Connect to ADB device
        client = AdbClient(host="127.0.0.1", port=5037)
        self.adbdev = client.device(serial)
        print("Connected to", self.adbdev.serial)

    def get_tap_coords(self, key):
        return self.TAPS[key]

    def get_clipboard(self):
        raw = self.adbdev.shell('am broadcast -n "ch.pete.adbclipboard/.ReadReceiver"')
        dataMatcher = re.compile('^.*\n.*data="(.*)"$', re.DOTALL)
        dataMatch = dataMatcher.match(raw)
        return dataMatch.group(1)

    def take_screenshot(self):
        screencap = self.adbdev.screencap()
        image = Image.open(io.BytesIO(screencap))
        return image

    def tap(self, coords, isFast: bool = True):
        self.adbdev.shell("input tap " + str(coords[0]) + " " + str(coords[1]))

    def swipeProfileUp(self):
        self.adbdev.shell("input swipe 456 977 456 875 1000")
        time.sleep(1)

    def trimToSave(self, img):
        return img

    def scaleVertical(self, val):
        return val

    def scaleHorizontal(self, val):
        return val


class StatsScanner:
    JUMP_DELAY = 0.25
    CSV_DETAILS = [
        "Timestamp",
        "Rank",
        "ID",
        "Alliance",
        "Name",
        "Power",
        "RSS Gathered",
        "RSS Assistance",
        "Dead Count",
        "Kill Points",
        "T5 Kills",
        "T5 Points",
        "T4 Kills",
        "T4 Points",
        "T3 Kills",
        "T3 Points",
        "T2 Kills",
        "T2 Points",
        "T1 Kills",
        "T1 Points",
    ]

    @staticmethod
    def is_tool(name):
        """Check whether `name` is on PATH and marked as executable."""
        return which(name) is not None

    def __init__(self, params, event):
        self.currentProfile = 0
        self.params = params
        self.stopEvent = event

        if params["device"] == "pc":
            print("Starting in PC mode ...")
            self.device = DevicePC()
            # Switch to the game window
            pyautogui.getWindowsWithTitle(params["window"])[0].activate()
        elif params["device"] == "adb":
            # Start the ADB daemon
            print("Starting in ADB mode ...")
            self.device = DeviceADB(params["serial"])
        else:
            print("Unknown device type. Accepted types: {pc,adb}")
            quit(-1)

    def start(self, progressCallBack=None):

        # Create project folder
        projectFolder = "{}\\{}\\".format(self.params["dir"], self.params["tag"])
        if not os.path.exists(projectFolder):
            os.makedirs(projectFolder)

        csvFileName = projectFolder + self.params["tag"] + ".csv"
        with open(csvFileName, "w", encoding="utf-8", newline="") as f:
            write = csv.writer(f)
            write.writerow(StatsScanner.CSV_DETAILS)

        time.sleep(2)

        totalProfiles = int(self.params["count"])

        startTime = datetime.now()
        print("Starting at: {}".format(startTime))

        # Get the first 4 accounts in the first page
        for i in range(1, 5):
            if self.stopEvent.is_set():
                break

            self.currentProfile = i
            st = self.capture_profile(self.device.get_tap_coords(str(i)), projectFolder + str(i), i)
            st.insert(0, i)
            st.insert(0, datetime.now(timezone.utc).strftime("%m-%d-%Y %H:%M:%S UTC"))
            print(st)
            self.append_csv_row(csvFileName, st)

            # update progress bar
            if progressCallBack:
                progressCallBack(i, totalProfiles, datetime.now()-startTime)

        # After the first 4, profiles will start shifting up in the list, read them one-by-one
        for i in range(5, int(totalProfiles) + 1):
            if self.stopEvent.is_set():
                break

            self.currentProfile = i
            st = self.capture_profile(self.device.get_tap_coords("+"), projectFolder + str(i))
            st.insert(0, i)
            st.insert(0, datetime.now(timezone.utc).strftime("%m-%d-%Y %H:%M:%S UTC"))
            print(st)
            self.append_csv_row(csvFileName, st)

            # update progress bar
            if progressCallBack:
                progressCallBack(i, totalProfiles, datetime.now()-startTime)

        print("Ending at: {}".format(datetime.now()))

        print("Completed! Output was written to {}".format(csvFileName))

    def read_string_from_image(self, image, coords):
        isNumber = coords[4]
        preProcessingProfile = coords[5]
        invertImg = coords[6]
        applyFilters = coords[7]

        # consider using "--oem 1"

        confStr = " -c tessedit_char_whitelist=0123456789," if isNumber else ""
        subImg = image.crop((coords[0], coords[1], coords[0] + coords[2], coords[1] + coords[3]))

        if preProcessingProfile == ImageProcessingProfile.KILLS:
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 75))
            subImg = subImg.filter(ImageFilter.UnsharpMask(radius=5, percent=100, threshold=0))
            # Fill the first 7 pixels by white. This requires cutting the images at least 6 pixels ahead in the x-axis.
            subImg.paste(255, [0, 0, self.device.scaleHorizontal(7), subImg.size[1]])
        elif preProcessingProfile == ImageProcessingProfile.ID:
            subImg = subImg.convert("RGB")
            subImg = invert(subImg)
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 78))
            subImg = subImg.filter(ImageFilter.UnsharpMask(radius=10, percent=300, threshold=0))
            # Fill the first 3 pixels by white.
            subImg.paste(255, [0, 0, self.device.scaleHorizontal(3), subImg.size[1]])
            confStr = " -c tessedit_char_whitelist=ID0123456789():"
        elif preProcessingProfile == ImageProcessingProfile.ALLIANCE:
            fillWidth = coords[8]
            subImg = subImg.convert("RGB")
            subImg = invert(subImg)
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 85))
            subImg.paste(255, [0, 0, fillWidth, subImg.size[1]])
        elif preProcessingProfile == ImageProcessingProfile.POWER:
            subImg = subImg.convert("RGB")
            subImg = invert(subImg)
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 65))
            subImg = subImg.filter(ImageFilter.UnsharpMask(radius=8, percent=10, threshold=0))
            # subImg.save("C:/rok-scans/debug/{}-power.png".format(self.currentProfile), "PNG")
        elif preProcessingProfile == ImageProcessingProfile.KILLPOINTS:
            subImg = subImg.convert("RGB")
            subImg = invert(subImg)
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 65))
            subImg = subImg.filter(ImageFilter.UnsharpMask(radius=8, percent=10, threshold=0))
            # subImg.save("C:/rok-scans/debug/{}-kp.png".format(self.currentProfile), "PNG")
        elif preProcessingProfile == ImageProcessingProfile.INFO:
            subImg = subImg.convert("RGB")
            subImg = invert(subImg)
            subImg = grayscale(subImg)
            subImg = autocontrast(subImg, cutoff=(0, 75))
            subImg = subImg.filter(ImageFilter.UnsharpMask(radius=8, percent=125, threshold=0))
        else:
            if invertImg or applyFilters:
                subImg = subImg.convert("RGB")

            if invertImg:
                subImg = invert(subImg)

            if applyFilters:
                # Apply filters
                subImg = grayscale(subImg)
                subImg = autocontrast(subImg, cutoff=(0, 75))
                # bbox = autocontrast(invert(rgbimage), cutoff=(0, 90)).getbbox()
                # if bbox: rgbimage = rgbimage.crop((bbox[0], bbox[1], bbox[2] + bonusRightTrim, bbox[3]))
                # subImg = contain(subImg, (800, 800), method=1)
                # subImg = subImg.filter(ImageFilter.EDGE_ENHANCE_MORE)
                subImg = subImg.filter(ImageFilter.SHARPEN)

        ret = (
            pytesseract.image_to_string(subImg, config="--oem 1 --psm 7" + confStr)
            .strip()
            .replace(",", "")
            .replace(".", "")
            .replace(" ", "")
        )

        # for some reason, in many times 0 is read recognized as '(i)'. For now, I am just replacing it manually
        # TODO: find why this happens, may be expand the crop area
        if ret == "(i)" or ret == "i)":
            print("i issue happened")
            return "0"

        return ret

    def read_stats(self, image, coords_dict) -> list:
        stats = []
        for k in coords_dict.keys():
            stats.append(self.read_string_from_image(image, coords_dict[k]))
        return stats

    def is_exit_button(self, image, coords) -> bool:
        buttonTxt = self.read_string_from_image(image, coords).lower()
        return buttonTxt == "x"

    def show_next_screen(self, screen, fastClick=True, baseCoords=None, maxTrials=100):
        sInfo = self.device.get_tap_coords(screen)
        if baseCoords is None:
            screenInfo = sInfo
        else:
            screenInfo = baseCoords + sInfo

        # Tab to show the screen
        self.device.tap(screenInfo[:2], fastClick)

        # wait until the screen is loaded
        trial = 0
        while trial < maxTrials and not self.stopEvent.is_set():
            trial += 1

            # Occasionally, the click/tap fails. Repeat the click from time to time
            if trial % 16 == 0:
                # Not a usual delay, try to tap again
                self.device.tap(screenInfo[:2], fastClick)

            time.sleep(StatsScanner.JUMP_DELAY)
            screenImg = self.device.take_screenshot()
            verifyTxt = self.read_string_from_image(screenImg, screenInfo[2:]).lower()
            if verifyTxt == screenInfo[10]:
                return screenImg

        return None

    def capture_profile(self, coords, imgName: str, index=100):
        pstats = []

        # Show the profile
        proImg = self.show_next_screen("profile-exit-button", baseCoords=coords, maxTrials=20)

        if proImg is None:
            # We waited around 5 seconds, but the profile could not be open, may be a deserted account
            # for now, we do not handle the case when the deserted account among the top 4
            if index <= 4:
                return [""]

            # It is still not a profile page
            # Take a screenshot of the list and attempt to read the name and power from the top list page
            listImg = self.device.take_screenshot()
            idlInfo = self.read_stats(listImg, self.device.TOP_LIST_PAGE_COORDINATES)

            # The first element is the "[Alliance] Name", attempt to split them
            sIndex = idlInfo[0].find("[")
            if sIndex < 0:
                # no alliance
                name = idlInfo[0]
                alliance = ""
            else:
                eIndex = idlInfo[0].find("]")
                alliance = idlInfo[0][sIndex + 1: eIndex]
                name = idlInfo[0][eIndex + 1:].strip()
            # Ad-hoc fixes for the alliance name
            alliance.replace("2R04", "ZRO4")

            power = idlInfo[1]

            # scroll up and wait for the swipe animation to complete
            self.device.swipeProfileUp()
            return ["", alliance, name, power]

        # This is a profile page, extract the alliance name and the power from the profile page
        profInfo = self.read_stats(proImg, self.device.PROFILE_PAGE_COORDINATES)

        # The first element in the result is the ID. Remove "(ID:" and ")".
        profInfo[0] = (
            profInfo[0]
            .replace("ID:", "")
            .replace("1D:", "")
            .replace("(", "")
            .replace(")", "")
        )

        # The second element in the result is the alliance, cut the name and keep the short alliance name
        sIndex = profInfo[1].find("[")
        if sIndex < 0:
            # no alliance
            profInfo[1] = "-"
        else:
            # The closing bracket ']' is sometimes recognized as one of '}|)'
            # first, check if it is recognized correctly
            eIndex = profInfo[1].find("]")
            if eIndex < 0:
                eIndex = (
                    profInfo[1]
                    .replace("}", "]")
                    .replace("|", "]")
                    .replace(")", "]")
                    .find("]")
                )

            # if ']' is still not found, cut the first 6 chars in the alliance name
            if eIndex < 0:
                eIndex = 7

            profInfo[1] = profInfo[1][sIndex + 1: eIndex]

        # The forth element is the kill points. We need to hold them as they should be inserted later after the more
        # info
        killpoints = profInfo[3]
        pstats.extend(profInfo[:3])

        # Show the kills info
        image = self.show_next_screen("kills", fastClick=False)
        self.device.trimToSave(image).save(imgName + ".png", "PNG")

        # Read the kill stats
        # Insert the kill points at the beginning of the killInfo list
        killInfo = self.read_stats(image, self.device.KILLS_PAGE_COORDINATES)
        killInfo.insert(0, killpoints)

        # Show more info page
        # first, hid the kills window, wait a moment, then click "More Info"
        self.device.tap((self.device.scaleHorizontal(625), self.device.scaleVertical(681)), True)
        time.sleep(StatsScanner.JUMP_DELAY)
        infoImg = self.show_next_screen("info")

        # We have two cases here, your own more-info page is different from others more-info TBD: Handle this case
        # where you get to your own more-info selfInfo = read_string_from_image(infoImg,
        # device.SELF_INFO_PAGE["verify"]) == device.SELF_INFO_PAGE["verify"][7]

        # Read the RSS gathered, assistance, and the dead count
        self.device.trimToSave(infoImg).save(imgName + "-info.png", "PNG")
        pstats.extend(self.read_stats(infoImg, self.device.INFO_PAGE_COORDINATES))

        # Add the kill info now
        pstats.extend(killInfo)

        # Copy and save the player name
        self.device.tap(self.device.get_tap_coords("namecopy"))
        time.sleep(2 * StatsScanner.JUMP_DELAY)
        username = self.device.get_clipboard()
        pstats.insert(2, username)

        # Exit the info page
        self.show_next_screen("exitinfo")

        # Exit the profile
        self.show_next_screen("exitprofile")

        return pstats

    def append_csv_row(self, filename, row):
        with open(filename, "a", encoding="utf-8", newline="") as f:
            csf_writer = csv.writer(f)
            csf_writer.writerow(row)
