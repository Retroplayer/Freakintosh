# Macintosh Plus serial GPIO prototype

Status: initial design and MicroPython firmware. Hardware communication has
not yet been tested. This prototype establishes the serial link, toggles an
external LED, reads a button, and samples an analog input. It does not control
motors.

## Architecture

Mac Plus printer port → full-duplex SP3490 module → Pico 2 UART0.

Use ordinary asynchronous serial, 9600 baud, 8 data bits, no parity, 1 stop bit,
and no hardware or software flow control. Disable AppleTalk on the printer port.
This is a direct serial peripheral, not a LocalTalk device or printer emulator.
A future classic Mac application can open the Serial Driver's `.BIn` and
`.BOut` drivers; for initial testing, use a terminal program that supports the
printer port.

## Parts

- Raspberry Pi Pico 2 (RP2350), with current official Pico 2 MicroPython firmware.
- SP3490 full-duplex module supporting a 3.3 V supply and exposing DI/RO and A/B/Y/Z.
- Mini-DIN-8 plug or breakout, with verified pin numbering.
- LED and 1 kΩ series resistor; normally open pushbutton.
- Optional 10 kΩ potentiometer for an analog test.
- USB power for the Pico, jumper wires, and breadboard.

## Wiring

Power off both devices before wiring. Connector pin numbers refer to the Mac
port's signal assignments, not a drawing of the plug. Establish the actual
connector view with a connector datasheet and continuity meter before assembly.
Do not use a cable's colors as pin identification; printer cables may cross pairs.

| Mac Plus mini-DIN-8 pin | Signal | SP3490 chip signal |
| --- | --- | --- |
| 3 | TxD− | B, receiver inverting input |
| 6 | TxD+ | A, receiver noninverting input |
| 5 | RxD− | Z, driver inverting output |
| 8 | RxD+ | Y, driver noninverting output |
| 4 | Signal ground | GND |
| 1 | HSKo | Leave disconnected |
| 2 | HSKi | Leave disconnected |
| 7 | Unused on Plus | Leave disconnected |

| Pico 2 | SP3490 module / peripheral |
| --- | --- |
| 3V3 OUT, physical pin 36 | Module VCC |
| GND, physical pin 3 | Module GND and Mac signal ground |
| GP0, physical pin 1 | DI (often labeled TXD) |
| GP1, physical pin 2 | RO (often labeled RXD) |
| GP2, physical pin 4 | 1 kΩ resistor → LED anode; LED cathode → GND |
| GP3, physical pin 5 | Pushbutton → GND; firmware enables internal pull-up |
| GP26/ADC0, physical pin 31 | Optional potentiometer wiper |

Wire the potentiometer ends to 3V3 and GND. Keep ADC input between ground and
3.3 V. Disconnect the potentiometer when testing a different analog source.

The SP3490 chip uses A/B for receive and Y/Z for transmit. Confirm the module's
terminal labels against its schematic or continuity to the chip; vendor labels
can differ. Use the exact part's datasheet for chip pin numbers; do not assume
it has the pinout of a half-duplex transceiver.

Use the module's decoupling or add 100 nF close to its supply pins. Power the
Pico by USB; do not connect module VCC to 5 V or draw power from the Mac port.
For this short-cable, low-speed prototype, begin without added termination or
bias networks. Identify any resistors already installed on the module before
connecting it: a 120 Ω termination is not automatically appropriate for the
Mac's driver. Remove or disable optional termination only using the module's
documented configuration. Long cables and a final PCB need a separate review
of loading, termination, connector protection, and grounding.

## Firmware installation

1. Download the official MicroPython UF2 specifically for **Raspberry Pi Pico 2**
   from <https://micropython.org/download/RPI_PICO2/>. Follow its BOOTSEL flashing
   instructions. A Pico 1 UF2 is not interchangeable.
2. Use Thonny's MicroPython interpreter over USB to save
   [firmware/main.py](firmware/main.py) as `main.py` on the Pico.
3. Reset the Pico. The USB REPL remains available for debugging; commands from
   the Mac use UART0 on GP0/GP1, not USB.

There are no third-party Python packages. The runtime uses MicroPython's
`machine` and `time` modules, so running this program with desktop Python is not
a hardware test. Use the existing checkout for development; no worktree is needed.

## Protocol v0

The [MacGPIO 1.0 specification](PROTOCOL.md) defines the planned framed protocol
with sequence numbers, CRC, discovery, and output leases. It is not yet
implemented by this firmware. The commands below describe the current v0 only.

ASCII commands, one per line, terminated by CR, LF, or CRLF. Responses end in
CRLF. Maximum command length is 64 bytes. Send one command and wait for its
response before sending another. Commands are uppercase and case-sensitive.

| Command | Response / action |
| --- | --- |
| `PING` | `OK PONG` |
| `INFO` | `OK MACGPIO 0` |
| `WRITE 2 1` | `OK`; LED on |
| `WRITE 2 0` | `OK`; LED off |
| `READ 3` | `VALUE 3 0` when pressed, `VALUE 3 1` when released |
| `ADC 0` | `VALUE ADC0 n`, MicroPython 16-bit scaled reading, 0–65535 |
| `STOP` | `OK`; LED off |

Other commands return `ERR COMMAND`. Overlong lines return `ERR TOO_LONG`
and are discarded through the next line ending. Non-ASCII lines return
`ERR ASCII`. Blank lines are ignored. Only the LED output is writable; arbitrary
GPIO configuration is intentionally absent so commands cannot reconfigure UART
or other reserved pins.

After two seconds without a valid command, firmware turns the LED off. This
exercises a communication timeout; it is not a motor safety system. A later
motion protocol must define explicit arming, a movement heartbeat independent
of sensor queries, local control loops, driver enable behavior, and a physical
emergency stop before motors are attached.

## Hardware acceptance test

1. With power off, check all grounds and pair polarity, verify no short between
   power and ground, and confirm the module's supply requirements.
2. Power the Pico and measure module VCC at approximately 3.3 V.
3. Open the Plus printer port at 9600 8-N-1 with flow control disabled. Turn off
   terminal local echo if it causes confusing duplicate display.
4. Send `PING`; require exactly `OK PONG`. Send `INFO`; require `OK MACGPIO 0`.
5. Send `WRITE 2 1`; require `OK` and LED illumination. Stop sending commands;
   require the LED to turn off after approximately two seconds.
6. Send `READ 3` with the button released and pressed; require values 1 and 0.
7. If fitted, move the potentiometer between its endpoints and send `ADC 0`;
   require readings approaching 0 and 65535 respectively.
8. Send `WRITE 0 1`; require `ERR COMMAND` and continued response to `PING`.

Record the terminal program, Mac system version, module identity, cable length,
and results before increasing the baud rate or adding robot peripherals.

If there is no reply, confirm AppleTalk is disabled, the printer port is selected,
and flow control is off. Check Pico UART traffic and module pair assignments
with a scope or logic analyzer on the logic side. Do not attach a single-ended
logic analyzer directly across differential pairs or swap wires while powered.
