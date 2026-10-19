"""Mac Plus serial GPIO prototype; MicroPython on Raspberry Pi Pico 2."""

from machine import ADC, Pin, UART
import time


MAX_LINE = 64
TIMEOUT_MS = 2000


def main():
    led = Pin(2, Pin.OUT, value=0)
    button = Pin(3, Pin.IN, Pin.PULL_UP)
    analog = ADC(Pin(26))
    uart = UART(0, baudrate=9600, bits=8, parity=None, stop=1,
                tx=Pin(0), rx=Pin(1), rxbuf=256)
    line = bytearray()
    discarding = False
    last_valid = time.ticks_ms()

    def reply(message):
        uart.write(message + "\r\n")

    def dispatch(command):
        fields = command.split()
        if fields == ["PING"]:
            reply("OK PONG")
        elif fields == ["INFO"]:
            reply("OK MACGPIO 0")
        elif fields == ["STOP"]:
            led.value(0)
            reply("OK")
        elif fields in (["WRITE", "2", "0"], ["WRITE", "2", "1"]):
            led.value(int(fields[2]))
            reply("OK")
        elif fields == ["READ", "3"]:
            reply("VALUE 3 %d" % button.value())
        elif fields == ["ADC", "0"]:
            reply("VALUE ADC0 %d" % analog.read_u16())
        else:
            reply("ERR COMMAND")
            return False
        return True

    try:
        while True:
            # Bound each batch so incoming traffic cannot starve the timeout.
            data = uart.read(64) if uart.any() else None
            if data:
                for byte in data:
                    if byte in (10, 13):
                        if discarding:
                            discarding = False
                        elif line:
                            try:
                                command = line.decode("ascii")
                            except UnicodeError:
                                reply("ERR ASCII")
                            else:
                                if dispatch(command):
                                    last_valid = time.ticks_ms()
                        line.clear()
                    elif not discarding:
                        if len(line) >= MAX_LINE:
                            line.clear()
                            discarding = True
                            reply("ERR TOO_LONG")
                        else:
                            line.append(byte)
            if time.ticks_diff(time.ticks_ms(), last_valid) >= TIMEOUT_MS:
                led.value(0)
            time.sleep_ms(1)
    finally:
        led.value(0)


if __name__ == "__main__":
    main()
