# Secret Door Actuator Control

This project creates an automated door mechanism with LED effects and a secret unlock sequence. Perfect for escape rooms, hidden doors, or interactive displays!

## What It Does

- **Push Button Control**: Press once to move the actuator up/down, press again during movement to stop
- **LED Light Show**: Bright white sparkle effect that fades in/out as the door moves
- **Secret Unlock**: Enter a specific button sequence to unlock a secondary mechanism
- **Emergency Stop**: Button press during movement stops the actuator immediately

## Hardware You'll Need

- **Adafruit Huzzah32** (ESP32 microcontroller)
- **L298N Motor Driver** (controls the actuator)
- **Linear Actuator** (12V recommended)
- **NeoPixel LED Strip** (12 LEDs)
- **Push Buttons** (3 total - 1 main, 2 secret)
- **12V Power Supply** (for actuator)
- **Jumper wires and breadboard**

## How It Works

1. **Press the main button** - The actuator moves up with a bright LED fade-in effect
2. **Press again** - Actuator moves down with a fade-out effect
3. **Press during movement** - Emergency stop (great safety feature!)
4. **Secret sequence** - Press the hidden buttons in the right order to trigger the unlock mechanism

The LEDs create a "rain" sparkle effect that gets brighter as the door opens and dimmer as it closes.

## Setup Instructions

### 1. Install CircuitPython

Follow Adafruit's guide to install CircuitPython on your Huzzah32.

### 2. Enable Web Workflow (Optional)

This lets you edit files wirelessly:

1. Download [PuTTY](https://www.putty.org/)
2. Connect to your Huzzah32:
   - Connection type: Serial
   - Speed: 115200
3. In the REPL, set up your WiFi:
   ```python
    f = open('settings.toml', 'w')
    f.write('CIRCUITPY_WIFI_SSID = "wifissid"\n')
    f.write('CIRCUITPY_WIFI_PASSWORD = "wifipassword"\n')
    f.write('CIRCUITPY_WEB_API_PASSWORD = "webpassword"\n')
    f.close()
   ```

For detailed steps, see [Adafruit's Web Workflow Guide](https://learn.adafruit.com/circuitpython-with-esp32-quick-start/setting-up-web-workflow).

### 3. Wire Everything Up

- Connect the L298N motor driver to control your actuator
- Connect IN1 (L298N) to pin 21 (motor up)
- Connect IN2 (L298N) to pin SCL (motor down)
- Connect IN3 (L298n) to pin SDA (open lock mechanism)
- Connect motor to OUT1 and OUT2 on L298N
- Connect lock mechanism to OUT3 and OUT4 on L298N
- Wire the NeoPixel strip to pin A0
- Connect push buttons to pins D5, A1, and MISO

### 4. Upload the Code

Copy the Python script to your Huzzah32's CIRCUITPY drive as `code.py`.

## Customization

You can easily adjust:

- **Movement time**: Change `MOVEMENT_DURATION` (default: 13 seconds)
- **LED brightness**: Adjust `MIN_BRIGHTNESS` and `MAX_BRIGHTNESS`
- **Secret sequence**: Modify the `TARGET_SEQUENCE` list
- **Sparkle effect**: Change `SPARKLE_PROBABILITY` for more/fewer twinkling LEDs

## Safety Features

- **Emergency stop**: Press the button during movement to stop immediately
- **Automatic timeout**: Movement stops after the set duration
- **Motor protection**: Motors are turned off when not in use

## Helpful Resources

- [Huzzah32 ESP32 Feather Pinouts](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts)
- [L298N Motor Driver Guide](https://lastminuteengineers.com/l298n-dc-stepper-driver-arduino-tutorial/) - Everything about controlling motors
- [NeoPixel Library Docs](https://docs.circuitpython.org/projects/neopixel/en/latest/api.html) - LED control reference
- [Adafruit NeoPixel Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide/the-magic-of-neopixels) - The complete LED guide
- [Setting up Web Workflow](https://learn.adafruit.com/circuitpython-with-esp32-quick-start/setting-up-web-workflow)
- [Entering the REPL](https://learn.adafruit.com/welcome-to-circuitpython/the-repl)

## Troubleshooting

- **LEDs not working?** Check the power supply and pin A0 connection
- **Actuator not moving?** Verify L298N wiring and 12V power supply
- **WiFi issues?** Double-check your settings.toml file credentials

---

_This project uses CircuitPython - no complex programming knowledge required! Just upload and go._
