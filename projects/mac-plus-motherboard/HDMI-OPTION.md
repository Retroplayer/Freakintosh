# Macintosh Plus motherboard: optional HDMI conversion

This is an alternative for projects using HDMI displays. The PWP 425 conversion
instead targets its existing CRT; see [that project's plan](../pwp-425-mac/README.md).
HDMI is not a prerequisite for the shared motherboard build.

Status: converter recommendation, not a completed schematic or tested assembly.
The analog board and CRT are omitted. The goal is to view native Mac video
during startup and normal use without depending on a running Mac application.

## Recommended first path: RGBtoHDMI

Use a dedicated RGBtoHDMI converter and an HDMI monitor or HDMI-input LCD
controller. Keep the Pico 2 GPIO controller separate from video capture.

```text
Plus motherboard video and timing signals
    → documented pickup / buffering and input-level interface
    → compatible RGBtoHDMI hardware and Mac Plus profile
    → HDMI monitor or LCD controller
```

The upstream [RGBtoHDMI project](https://github.com/hoglet67/RGBtoHDMI)
contains an explicit
[Mac_128-512-Plus_TTL profile](https://github.com/hoglet67/RGBtoHDMI/blob/3c3151783ca78bf966b918f4309e6848fd11389c/src/scripts/Profiles/6-12_BIT_RGB/Apple/Mac_128-512-Plus_TTL.txt).
Its presence was verified at commit
`3c3151783ca78bf966b918f4309e6848fd11389c`. This establishes software profile
availability, not compatibility of every product sold under the RGBtoHDMI name.

The project's documented architecture uses a Raspberry Pi with a CPLD capture
board and dedicated firmware. A bare Raspberry Pi or an arbitrary HDMI adapter
is not equivalent. The Mac profile is under `6-12_BIT_RGB`; select hardware,
CPLD firmware, and input circuitry documented to support that profile. Confirm
the seller's supported Pi model, included boards, input connector, 5 V TTL input
handling, power requirements, and Mac wiring before purchase. An Amiga-specific
pickup board is not automatically suitable for a Plus.

## Source video and timing

The Plus screen is 512 × 342 monochrome pixels. Its native scan timing differs
from ordinary VGA. The upstream profile contains the following timing values:

| Parameter | Profile value / derived rate |
| --- | --- |
| Active image | 512 × 342 |
| Pixel sampling clock | 15.6672 MHz |
| Total pixels per line | 704 |
| Total lines per frame | 370 |
| Horizontal rate | Approximately 22.2545 kHz, calculated from the above |
| Vertical rate | Approximately 60.1474 Hz, calculated from the above |

Use these as capture setup references and verify the actual board on the bench.
A VGA cable adapter cannot change scan rate. A generic VGA-to-HDMI converter
may reject this timing even with proper analog-level conversion. Likewise, a
generic composite-video converter expects a different signal format.

The visible video is a one-bit pixel stream accompanied by timing signals,
not analog RGB or composite video. Identify the accessible video, horizontal
timing, vertical timing, and ground nets from the exact Plus schematics.
Do not assume an exported timing signal has standard VGA sync pulse shape or
polarity: a CRT drive/timing net may need interpretation by the input circuit.
Determine whether the selected converter requires separate sync, combined
sync, an external pixel clock, or internal clock recovery. Do not join timing
outputs together to manufacture composite sync.

## Electrical interface still to design

Before making a pickup harness, document:

- Motherboard connector orientation, signal pin numbers, net names, and whether
  a buffered connector output or an internal test point is being used.
- Measured voltage levels, polarity, pulse timing, and load presented by the
  converter. The Mac's TTL-era outputs must not be connected directly to
  unprotected 3.3 V Pi or Pico GPIO.
- Exact converter input pin mapping and its specified level interface. Use
  documented TTL-compatible buffering or translation where required; a generic
  slow bidirectional I2C level-shifter board is unsuitable for a 15.7 MHz stream.
- A short signal/ground harness, appropriate grounding, and any source damping
  required by the actual driver and cable. Do not add a 75 Ω load directly to
  a TTL video output just because VGA normally uses 75 Ω inputs.
- A verified power arrangement for the converter and display, including any
  risk of back-powering through signals when one device is switched off.

There is intentionally no pin-by-pin construction drawing yet: converter
hardware and the motherboard connector view must be verified first.

## Alternatives

| Approach | When it makes sense | Main limitation |
| --- | --- | --- |
| RGBtoHDMI with verified Plus interface | First working display and boot diagnostics | Extra Pi/CPLD hardware; assembly compatibility must be checked |
| Dedicated FPGA converter | Integrated custom board or specialized output | HDL, capture timing, memory, and output development |
| Dedicated Pico/RP2350 capture converter | A separate low-cost video development project | Needs proven capture/output firmware and electrical interface |
| Direct connection to a timing-compatible monitor | A specific monitor explicitly accepts the source format | Uncommon compatibility; electrical adaptation still required |

A custom Pico converter is plausible, but it is not just connecting two pins.
One 512 × 342 one-bit framebuffer uses 21,888 bytes; double buffering needs
43,776 bytes before output buffers and firmware. RAM alone does not prove
capture and display feasibility. Sampling, clock recovery, frame-rate mismatch,
scaling, and output timing must all work together. Use a separate controller
if pursuing this rather than coupling robot I/O reliability to video firmware.

## Display selection and acceptance

For projects selecting this option, use an existing HDMI monitor with the
converter for initial tests. An HDMI display assembly is one option; a raw LCD panel needs its own
matching controller and power supply. Preserve square source pixels and the
512:342 image aspect ratio; do not stretch the desktop to fill a widescreen
panel. Prefer integer scaling when the converter/output resolution permits it.

Acceptance requires cold-boot visibility before System software loads, stable
sync, correct black/white polarity, all four image edges, readable single-pixel
text and checkerboard patterns, and no tearing or dropouts during disk/audio/
serial activity. Repeat across power cycles. A persistent wrong border or
shimmering text is a capture/timing problem to investigate, not proof of a bad
Mac framebuffer. No video hardware tests have been performed yet.

## Sources and next decision

- [RGBtoHDMI README](https://github.com/hoglet67/RGBtoHDMI): converter architecture.
- [RGBtoHDMI wiki](https://github.com/hoglet67/RGBtoHDMI/wiki): hardware and setup documentation to consult for the selected board.
- The pinned Mac Plus profile above: active dimensions and timing parameters.

If a project selects HDMI, choose the converter assembly and target display.
Then complete the verified pickup harness
drawing against the Plus schematic and that converter's input documentation.
