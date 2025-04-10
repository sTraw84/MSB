import sys
import time
import os
import pyautogui
from pywinauto import application
import pythoncom
import ctypes

def send_securecrt_keys():
    try:
        # Initialize COM in STA mode
        pythoncom.CoInitialize()

        # Find and activate the SecureCRT window using pywinauto
        app = application.Application().connect(title_re="WMS - SecureCRT")
        securecrt_window = app.window(title_re="WMS - SecureCRT")
        securecrt_window.set_focus()

        # Wait a moment to ensure the window is active
        time.sleep(0.5)

        # Send the key sequence to SecureCRT
        pyautogui.keyDown('alt')
        pyautogui.press('s')
        pyautogui.press('r')
        pyautogui.keyUp('alt')

        # Wait for the "Run Script" dialog to appear
        time.sleep(0.5)

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Insert the directory path into the address bar of the "Run Script" dialog
        pyautogui.write(script_dir)
        pyautogui.press('enter')

        # Wait for the directory to change
        time.sleep(0.5)

        # Insert 'WMS_Script_1.5.1' into the file name field
        pyautogui.write('WMS_Script_1.5.1')

        # Press 'Enter' to open the file
        pyautogui.press('enter')
    except Exception as e:
        print(f"SecureCRT window not found or could not be focused: {str(e)}")
    finally:
        # Uninitialize COM
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    # Ensure the application is running in STA mode
    ctypes.windll.ole32.CoInitialize(None)

    send_securecrt_keys()

    ctypes.windll.ole32.CoUninitialize()