# Subayai
⚡A hopefully speedy touch keypad for rhythm gaming

## Why
I wanted a touch keypad and I didn't have the correct Arduino. So I made one for Uno.

## Flashing
You'll need:
- An Arduino Uno.
- The legacy Arduino IDE.
- [HoodLoader2](https://github.com/NicoHood/HoodLoader2)
- [HID-Project](https://github.com/NicoHood/HID)

After installing those:
- Open the sketch with the legacy IDE.
- Edit pins and modify keys in `Board.h` if desired.
- Flash once for `HoodLoader2 16u2`.
- Flash again for `HoodLoader2 Uno`.

The correct code is chosen automatically based on the selected board.

## Wiring
While simple, it doesn't scale too well for large key counts. As I don't need those, I'm not worried about it right now.

![Wiring diagram](WIRING.png)

To add a new key, simply add a new lane to the right. There's a hard limit at sixteen keys. Other resistor values between 400k and 1M should work, would advise against mixing values.

## Configuration
> [!NOTE]
> Utility currently not implemented.

## License
This project is licensed under the MIT License.
