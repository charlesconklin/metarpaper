import board # type: ignore
import neopixel # type: ignore

pixels = neopixel.NeoPixel(board.D18, 50)
pixels.deinit()

print("LEDs off")

exit(0) # Successful exit