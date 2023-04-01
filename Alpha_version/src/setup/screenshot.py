import pygetwindow as gw
import pyautogui

# Find the window you want to capture by its title (replace 'Window Title' with the actual title)
window = gw.getWindowsWithTitle('Procedural Knots')[0]

# Activate and bring the window to the foreground
window.activate()

# Get the window's dimensions (x, y, width, height)
x, y, width, height = window.left+400, window.top+400, window.width-720, window.height-720

# Capture the screenshot
screenshot = pyautogui.screenshot(region=(x, y, width, height))

# Save the screenshot to a file
screenshot.save('screenshot.png')
