# Macintosh Plus in a Smith Corona PWP 425

## Project goal

Install a Macintosh Plus motherboard in a Smith Corona PWP 425 chassis and
reuse the PWP's existing CRT. This is a separate project from the Macintosh
robot. Do not assume an HDMI display, motor hardware, or robot requirements.

The Plus's original analog board will not be installed. That does not imply
removing the PWP CRT's own support electronics. The first approach to evaluate
is retaining the PWP CRT board, including its deflection, high-voltage, and
video amplification circuitry, and adapting its low-voltage video interface.
Whether that board operates independently of the PWP logic board is unverified.

Shared motherboard power, storage, ROM, and audio notes are in the
[hardware baseline](../mac-plus-motherboard/HARDWARE.md). The PWP CRT board's
power requirements need a separate budget; the proposed Mac supply has not
been shown to power it. Existing PWP mains circuitry and isolation must also
be understood before tying signal grounds together.

## Video question to resolve first

The Plus emits 512 × 342 monochrome video. The known RGBtoHDMI profile gives
a 15.6672 MHz sampling clock, 704 clocks per line, and 370 lines per frame:
approximately 22.2545 kHz horizontal and 60.1474 Hz vertical. See the
[source reference](../mac-plus-motherboard/HDMI-OPTION.md#source-video-and-timing).
These are source timing references, not proof that the PWP CRT accepts them.

The PWP 425's CRT scan rates, signal interface, polarity, video bandwidth,
power requirements, and connector pinout are not established in this repository.
Do not substitute specifications from another Smith Corona model or infer them
from the screen size. The CRT tube alone does not define the supported timing:
the deflection and high-voltage electronics are critical.

| Finding at the PWP display interface | Likely approach |
| --- | --- |
| Accepts Plus scan timing and sufficient video bandwidth | Buffer/translate video and timing; match polarity and blanking as required |
| Different fixed horizontal or vertical timing | Capture the Mac raster and regenerate video at the PWP's native timing |
| Requires PWP logic-generated control or power sequencing | Reproduce documented controls or retain necessary original circuitry |
| Insufficient bandwidth or usable raster for readable 512 × 342 | Evaluate scaling tradeoffs or a different compatible display subsystem |

Level conversion alone cannot correct incompatible scan rates. Do not feed
unverified sync into the CRT board or assume its deflection stage can be retuned
safely to the Mac rate. A scan converter should leave the original CRT drive
electronics operating within their intended timing.

## Information needed for an interface drawing

Start with a PWP 425 service manual/schematic, or identify the CRT board part
number and connector labels. Establish the exact revision and document:

1. Power inputs, signal ground, isolation, and any display-enable controls.
2. Video input type and amplitude: digital monochrome, analog intensity,
   composite video, or another interface.
3. Horizontal and vertical timing, pulse widths, polarity, blanking, and whether
   sync is separate, combined, or embedded in video.
4. Active raster dimensions and pixel timing, measured with an original working
   PWP logic board if available.
5. Corresponding Plus output nets and the required buffering, translation, or
   scan-conversion circuit between the two boards.

Measurements should target an identified, isolated low-voltage interface.
CRT boards can retain hazardous voltages and may have a nonisolated ground;
do not connect an earth-grounded scope or the Mac until isolation and grounding
are established. Tube, flyback, and deflection connections are not logic inputs.

## If scan conversion is required

Keep the display path independent of Mac application software so boot screens
remain visible. A dedicated FPGA or a proven microcontroller video-capture
design could buffer the Plus image and generate the PWP's native raster.
Choose hardware after measuring both interfaces, rather than selecting HDMI
and then converting it back to an unknown CRT format.

One native Mac monochrome frame uses 21,888 bytes; two use 43,776 bytes.
The design must additionally solve sampling, frame-rate mismatch, output timing,
blanking, polarity, and any scaling. RAM capacity alone is not a working converter.
Preserve the full desktop where possible; cropping can hide menus and dialogs.

## Validation milestones

- Identify the PWP display electronics and document its electrical interface.
- Confirm timing compatibility before selecting direct adaptation or conversion.
- Complete a reviewed wiring drawing and power/ground plan.
- Display Mac cold-boot output, then verify all screen edges, black/white
  polarity, text, and single-pixel patterns.
- Check stability and readability during disk access and audio playback, and
  across power cycles. Keep CRT operation within its original design limits.

No PWP wiring or timing compatibility has yet been verified. The next useful
input is identification/documentation of its CRT board, not display shopping.
