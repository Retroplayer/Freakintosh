# MacGPIO protocol 1.0

Status: proposed wire specification. The current `firmware/main.py` implements
the earlier v0 console protocol, not this specification. Do not send v1 frames
to that firmware and expect these responses.

## Scope and transport

The Mac is the host; the Pico is the device. The device handles GPIO timing
locally. The host requests operations and polls for readings. This protocol is
independent of the SP3490 electrical interface and of the Mac application language.

Initial transport is 9600 baud, 8-N-1, full duplex, no flow control. Disable
AppleTalk on the printer port. No baud negotiation is defined. Both ends must
be explicitly configured to change speed. At 9600 baud, allow roughly 960 bytes
per second in each direction; this is a control interface, not a waveform stream.

Version 1 has no unsolicited telemetry. Polling keeps reception predictable on
the Mac Plus and avoids buffer overflow while a classic Mac application is busy.
PWM, encoders, I2C, SPI, and motor control are future extensions, not v1 features.

## Frame format

Every request and response is an ASCII line:

```text
@<body>*<crc>\r\n
```

`\r\n` above means bytes 0D 0A, not literal backslashes. The body contains
tokens separated by exactly one ASCII space. No leading/trailing spaces, tabs,
quoting, or free-text strings are allowed. Tokens are uppercase ASCII letters,
decimal digits, underscores, or the hyphen in a version token. Numeric fields
are unsigned canonical decimal (no sign or leading zeros, except `0`).

CRC is CRC-16/CCITT-FALSE: polynomial 0x1021, initial value 0xFFFF,
no reflection, xor-out 0x0000. Compute over body bytes only, excluding `@`, `*`,
CRC digits, and line ending. Encode as four uppercase hexadecimal digits.
The standard check input `123456789` yields `29B1`.
[frame.py](tools/frame.py) creates frames for terminal testing.

Maximum frame length is 128 bytes, including `@`, `*`, four CRC digits, and
CRLF; thus the body is at most 120 bytes. Transmit CRLF. Receivers also accept
CR or LF alone and treat a CRLF pair as one ending. Ignore empty lines.
On a new `@`, discard any partial frame and start fresh. On an overlong frame,
discard until a new `@` or line ending. Discard incomplete frames after 500 ms
without a received byte. UART framing/overrun errors also discard the frame.
Bad CRC, illegal bytes, malformed framing, or an unparseable sequence field
produce no reply and no operation: the host must time out. Check the entire
frame before changing any output.

## Requests, responses, and retries

Request body: `<seq> <command> [arguments]`.

Response body: `<seq> OK [result]` or `<seq> ERR <code>`.

Sequence numbers are 1–65535. The host increments after each completed
transaction and wraps from 65535 to 1. There is exactly one outstanding request.
The device sends exactly one response for each valid request, except reset or
transport failure. The host ignores replies whose sequence does not match.
No debug logs or boot banners may appear on this UART.

Device commands must finish and begin responding within 100 ms of receiving
the complete request. The host waits 1000 ms after sending its complete frame.
On timeout, it may resend the identical frame up to twice; after three attempts,
report link failure. Do not advance the sequence number between attempts.

The device caches the last accepted request body and its complete response.
An identical duplicate with the same sequence replays that response without
repeating the operation or refreshing the output timeout. Reuse of the cached
sequence with a different body returns `SEQ` and leaves the cache intact.
Other valid requests replace the cache, including requests returning errors.
Malformed frames never replace it. This is one-entry duplicate suppression,
not durable exactly-once execution across resets.

All v1 state-changing operations set an absolute state and are idempotent.
There are no toggle, increment, or pulse commands. A timeout does not prove an
operation failed. On connection or suspected reset, send `STOP` with a fresh
sequence, then `HELLO 1`, then inspect `STATUS` before issuing output commands.
If `STOP` returns `SEQ`, try the next sequence number. A host must never send
old queued output commands after reconnecting.

## Commands

All commands below are mandatory for a device advertising protocol major 1.
No command writes flash or persists settings across reboot.

| Request body after sequence | Successful response after sequence | Meaning |
| --- | --- | --- |
| `HELLO 1` | `OK HELLO 1 0 MACGPIO PICO2 LED_BUTTON` | Select major 1; report major, minor, product, board, pin profile |
| `PING` | `OK PONG` | Link check; does not renew outputs |
| `STATUS` | `OK STATUS <state> <remaining_ms>` | `SAFE` or `ACTIVE`, output lease remaining |
| `PIN 2` | `OK PIN 2 OUT 0` | GP2 is a digital output with safe value 0 |
| `PIN 3` | `OK PIN 3 IN PULLUP` | GP3 is a digital input with pull-up |
| `PIN 26` | `OK PIN 26 ADC 0` | GP26 supplies analog channel 0 |
| `WRITE 2 <value>` | `OK` | Set LED output to 0 or 1; renew output lease |
| `READ 3` | `OK DIGITAL 3 <value>` | Read physical level: 0 pressed, 1 released |
| `ADC 0` | `OK ADC 0 <value> 65535` | Unsigned 16-bit scaled sample and full scale |
| `KEEPALIVE` | `OK` | Renew an existing ACTIVE output lease |
| `STOP` | `OK` | Apply safe output values and enter SAFE |

The table shows bodies without framing or CRC. `HELLO` must succeed before
any command except `STOP`; otherwise return `NOT_READY`. Unsupported major
versions return `VERSION` and do not change the current session. Successful
`HELLO` always applies safe outputs and starts a new SAFE session, but keeps
the duplicate cache rules above. Unknown optional commands return `COMMAND`.

`LED_BUTTON` is the initial fixed wiring profile: GP0/GP1 are reserved for
UART, GP2 is the LED, GP3 the button, GP26 ADC0. Raw pin numbers mean RP2350 GPIO
numbers, not physical header positions. Analog channel numbers are a separate
namespace. `PIN` queries capability; it does not configure a pin. Requests for
other pins/channels return `PIN`. A later board profile must document its pin
map and safe levels; clients must recognize the profile before writing outputs.

Digital values are 0 or 1. ADC samples are scaled values, not a claim of 16-bit
physical accuracy. Convert to nominal volts as `sample * 3.3 / 65535`; actual
accuracy depends on the reference, supply, and input circuit.

## Output lease and safe state

On boot, reset, session initialization, STOP, or lease expiry, GP2 is low.
The device must establish that level before accepting serial commands.
`WRITE` enters ACTIVE, even when writing 0, and grants a 2000 ms lease.
`KEEPALIVE` in ACTIVE renews it to 2000 ms; in SAFE it returns `STATE` and cannot
reactivate an output. The host should send a fresh numbered keepalive every
500 ms when it wants outputs retained. Reads, PING, errors, malformed frames,
and replayed duplicates do not renew the lease.

Check expiry before dispatching each newly completed command and at least
every 10 ms while idle or receiving traffic. On expiry, set output low and
enter SAFE. `STATUS` reports 0 remaining in SAFE, otherwise 1–2000 ms at the
instant sampled. Expiry is observed by polling; no event frame is emitted.
After expiry, a fresh explicit WRITE is needed to resume operation.

This lease protects only this LED prototype. Motors must not be connected to
the v1 output profile. A robot extension requires explicit arming, a dedicated
motion heartbeat, driver disable on reset/fault, locally enforced speed limits,
and a physical emergency stop. Generic GPIO traffic must not keep motion alive.

## Error codes

| Code | Meaning |
| --- | --- |
| `COMMAND` | Unknown command |
| `ARGS` | Wrong argument count or invalid token/numeric syntax |
| `RANGE` | Recognized numeric argument outside its permitted range |
| `PIN` | Pin/channel unavailable or operation incompatible with it |
| `VERSION` | Unsupported protocol major |
| `NOT_READY` | HELLO required |
| `STATE` | Command unavailable in current state |
| `SEQ` | Cached sequence reused with a different body |
| `INTERNAL` | Device failure; device must also apply safe outputs |

For checksum-valid requests with parseable sequences, validation order is:
duplicate handling, command recognition, argument syntax, session requirement,
version/range/pin/state checks, execution. Errors have no command side effects
except INTERNAL entering SAFE; independently due lease expiry still occurs.
CRC protects against accidental corruption, not malicious commands or replay.

## Compatibility and verification

Minor versions may add commands or profiles but cannot change existing command
meanings, required responses, or safety behavior. Clients ignore an unfamiliar
minor version only if the known profile and required responses still match.
Breaking changes require a new major. There is no automatic fallback to the
unchecksummed v0 protocol.

Before declaring a v1 implementation ready, test on host and device:

1. CRC check vector and framing at 120-byte body limit; reject 121 bytes.
2. CR, LF, CRLF, partial frames, a fresh `@`, non-ASCII, bad CRC, and UART overflow.
3. Discovery, all commands, error codes, unavailable pins, and ADC endpoints.
4. Duplicate WRITE replay without a repeated operation or lease renewal;
   same sequence with different body returns SEQ; sequence wrap works.
5. Lost request, lost reply, device reboot during retry, and reconnect STOP.
6. Boot/STOP/HELLO/timeout safe state; reads and corrupt traffic cannot renew
   the lease; KEEPALIVE cannot revive an expired lease.
7. Mac Plus terminal and eventual Mac client over the actual SP3490 link.

These are acceptance requirements, not tests already completed. The initial
implementation milestone is the framed parser and host-side protocol tests,
followed by firmware integration and Mac hardware validation.
