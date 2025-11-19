import sys
import signal
from gpiozero import Button
from time import sleep

button_1 = 5
button_2 = 6
button_3 = 13
button_4 = 19
navbutton_events = {}
gpio_button_pins = [button_1, button_2, button_3, button_4]

# A dictionary to hold the Button objects
buttons = {}

def button_pressed_handler(button):
    """Callback function to handle a button press."""
    print(f"Button on GPIO {button.pin.number} was pressed!")
    if "on_button_press_callback" in navbutton_events:
        print("Callback")
        navbutton_events["on_button_press_callback"](button.pin.number)

def setup_buttons():
    """Initializes a Button object for each pin and sets its callback."""
    print("Setting up GPIO buttons...")
    for pin in gpio_button_pins:
        try:
            # Create a Button object for the pin with an internal pull-up resistor.
            buttons[pin] = Button(pin, pull_up=True, bounce_time=0.1)
            # Assign the callback function to the 'when_pressed' event.
            buttons[pin].when_pressed = button_pressed_handler
            print(f"    - Listening for events on GPIO {pin}.")
        except Exception as e:
            print(f"    - Error setting up GPIO {pin}: {e}")

def watchButtons(button_press_callback):
    """Watch the button press events."""
    if button_press_callback is not None:
        print("assign callback")
        navbutton_events["on_button_press_callback"] = button_press_callback
        
    setup_buttons()
    print("\nWatching Buttons. Press CTRL+C to exit.\n")

    # Wait indefinitely while the gpiozero event loop handles button presses.
    # The 'pause()' function is a simple way to do this.
    # try:
    #     signal.pause()
    # except KeyboardInterrupt:
    #     print("\nExiting script.")
    # finally:
    #     # The gpiozero library automatically handles cleanup, but it's good practice
    #     # to know that it's taken care of.
    #     print("Cleanup complete.")
    #     sys.exit(0)

