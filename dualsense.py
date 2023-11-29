# Brian Lesko
# receive and translate DualSense controller io (PS5 remote) over a usb connection
# Uses HID which uses HIDapi 
# alternatives: https://github.com/pyusb/pyusb/tree/master  
# decodings based on https://github.com/flok/pydualsense/blob/master/pydualsense/pydualsense.py
# Future work caching the connection in a streamlit app: https://docs.streamlit.io/library/advanced-features/caching
# 11/27/23

import hid
import numpy as np
import usb.core
import usb.util

class DualSense:

    def __init__(self, vendorID, productID):
        self.vendorID = vendorID
        self.productID = productID
        self.device = hid.device()
        self.data = []

        # Initialize Dpad states
        self.DpadUp = False
        self.DpadDown = False
        self.DpadLeft = False
        self.DpadRight = False

        # Initialize button states
        self.dpad_up = False
        self.dpad_right = False
        self.dpad_down = False
        self.dpad_left = False
        self.L1 = False
        self.L2 = False
        self.R1btn = False
        self.R2btn = False

        # Initialize gyro readings
        self.Pitch = []
        self.Yaw = []
        self.Roll = []

        # Initialize accelerometer readings
        self.X = []
        self.Y = []
        self.Z = []

        # Initialize the Touchpad 
        self.touchpad_x = []
        self.touchpad_y = []
        # Touchpad two finger touch
        self.touchpad1_x = []
        self.touchpad1_y = []

        # Initialize the battery readings
        self.battery_state = "POWER_SUPPLY_STATUS_UNKNOWN"
        self.battery_level = 0

        # Initialize R3 and L3
        self.R3 = False
        self.L3 = False

    def disconnect(self):
        self.device.close()

    def connect(self):
        self.device.open(self.vendorID, self.productID)

    def receive(self, size=64):
        self.data = self.device.read(size)

    def send(self, command):
        self.device.write(command)

    def updateButtons(self):
        buttonState = self.data[8]
        self.triangle = (buttonState & (1 << 7)) != 0
        self.circle = (buttonState & (1 << 6)) != 0
        self.cross = (buttonState & (1 << 5)) != 0
        self.square = (buttonState & (1 << 4)) != 0

    def updateDpad(self):
        buttonState = self.data[8]
        dpad_state = buttonState & 0x0F
        if dpad_state == 0:
            self.DpadUp = True
            self.DpadDown = False
            self.DpadLeft = False
            self.DpadRight = False
        elif dpad_state == 1:
            self.DpadUp = True
            self.DpadDown = False
            self.DpadLeft = False
            self.DpadRight = True
        elif dpad_state == 2:
            self.DpadUp = False
            self.DpadDown = False
            self.DpadLeft = False
            self.DpadRight = True
        elif dpad_state == 3:
            self.DpadUp = False
            self.DpadDown = True
            self.DpadLeft = False
            self.DpadRight = True
        elif dpad_state == 4:
            self.DpadUp = False
            self.DpadDown = True
            self.DpadLeft = False
            self.DpadRight = False
        elif dpad_state == 5:
            self.DpadUp = False
            self.DpadDown = True
            self.DpadLeft = False
            self.DpadRight = False
        elif dpad_state == 6:
            self.DpadUp = False
            self.DpadDown = False
            self.DpadLeft = True
            self.DpadRight = False
        elif dpad_state == 7:
            self.DpadUp = True
            self.DpadDown = False
            self.DpadLeft = True
            self.DpadRight = False
        else:
            self.DpadUp = False
            self.DpadDown = False
            self.DpadLeft = False
            self.DpadRight = False

    def updateGyrometer(self, n=20):
        data = self.data
        self.Pitch.append(int.from_bytes(([data[22], data[23]]), byteorder='little', signed=True))
        self.Yaw.append(int.from_bytes(([data[24], data[25]]), byteorder='little', signed=True))
        self.Roll.append(int.from_bytes(([data[26], data[27]]), byteorder='little', signed=True))
        # Remove the oldest reading if the length exceeds n, we do this so that we can use an averaged gyro reading because the raw gyro readings are noisy
        if len(self.Pitch) > n:
            self.Pitch.pop(0), self.Yaw.pop(0), self.Roll.pop(0)
    
    def updateAccelerometer(self, n=20):
        data = self.data
        self.X.append(int.from_bytes(([data[16], data[17]]), byteorder='little', signed=True))
        self.Y.append(int.from_bytes(([data[18], data[19]]), byteorder='little', signed=True))
        self.Z.append(int.from_bytes(([data[20], data[21]]), byteorder='little', signed=True))
        if len(self.X) > n:
            self.X.pop(0), self.Y.pop(0), self.Z.pop(0)

    def updateTriggers(self):
        misc = self.data[9]
        self.R1 = (misc & (1 << 1)) != 0
        self.R2 = self.data[6]
        self.R2btn = (misc & (1 << 3)) != 0

        self.L1 = (misc & (1 << 0)) != 0
        self.L2 = self.data[5]
        self.L2btn = (misc & (1 << 2)) != 0

    def updateTouchpad(self, n=1):
        data = self.data

        #self.touchpadID = data[33] & 0x7F
        self.touchpad_isActive = (data[33] & 0x80) == 0
        self.touchpad_x.append(((data[35] & 0x0f) << 8) | data[34])
        self.touchpad_y.append(((data[36]) << 4) | ((data[35] & 0xf0) >> 4))

        # touchpad two finger touch
        #self.touchpad1ID = data[37] & 0x7F
        self.touchpad1_isActive = (data[37] & 0x80) == 0
        self.touchpad1_x.append(((data[39] & 0x0f) << 8) | data[38])
        self.touchpad1_y.append(((data[40]) << 4) | ((data[39] & 0xf0) >> 4))

        if len(self.touchpad_x) > n:
            self.touchpad_x.pop(0), self.touchpad_y.pop(0)
        if len(self.touchpad1_x) > n:
            self.touchpad1_x.pop(0), self.touchpad1_y.pop(0)

    def updateBattery(self):
        battery = self.data[53]
        state = (battery & 0xF0) >> 4
        BATTERY_STATES = {
            0x0: "POWER_SUPPLY_STATUS_DISCHARGING",
            0x1: "POWER_SUPPLY_STATUS_CHARGING",
            0x2: "POWER_SUPPLY_STATUS_FULL",
            0xb: "POWER_SUPPLY_STATUS_NOT_CHARGING",
            0xf: "POWER_SUPPLY_STATUS_ERROR",
            0xa: "POWER_SUPPLY_TEMP_OR_VOLTAGE_OUT_OF_RANGE",
            # Note: 0x0 is repeated, so we only keep one mapping for it
        }
        self.battery_state = BATTERY_STATES.get(state, "POWER_SUPPLY_STATUS_UNKNOWN")
        self.battery_level = min((battery & 0x0F) * 10 + 5, 100)

    def format_data_to_send(self):
        outReport = [0] * 64
        OUTPUT_REPORT_USB = 0x02
        outReport[0] = OUTPUT_REPORT_USB
        outReport[1] = 0xff # [1]
        outReport[2] = 0x1 | 0x2 | 0x4 | 0x10 | 0x40 # [2] # This is a flag for what is being sent, not sure what the values mean
        outReport[3] = self.rightMotor # right low freq motor 0-255 # [3]
        outReport[4] = self.leftMotor # left low freq motor 0-255 # [4]
        # outReport[5] - outReport[8] audio related
        outReport[9] = self.audio.microphone_led # [9] #set Micrphone LED, setting doesnt effect microphone settings
        outReport[10] = 0x10 if self.audio.microphone_mute is True else 0x00
        # ...

    def updateThumbStickPress(self):
        misc = self.data[9]
        self.R3 = (misc & (1 << 7)) != 0
        self.L3 = (misc & (1 << 6)) != 0

    def updateThumbsticks(self):
        data = self.data
        self.LX = data[1] - 127
        self.LY = data[2] - 127
        self.RX = data[3] - 127
        self.RY = data[4] - 127

    def updateMisc(self):
        misc = self.data[9]
        self.options = (misc & (1 << 5)) != 0
        self.share = (misc & (1 << 4)) != 0
        misc2 = self.data[10]
        self.ps = (misc2 & (1 << 0)) != 0
        self.touchButon = (misc2 & 0x02) != 0
        self.micButon = (misc2 & 0x04) != 0

    def updateAll(self):
        self.receive()
        self.updateMisc()
        self.updateThumbsticks()
        self.updateBattery()
        self.updateTouchpad(n=1)
        self.updateTriggers()
        self.updateAccelerometer(n=1)
        self.updateGyrometer(n=1)
        self.updateDpad()
        self.updateButtons()

