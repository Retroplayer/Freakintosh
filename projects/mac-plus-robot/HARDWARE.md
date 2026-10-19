# Macintosh Plus robot: hardware baseline

## Selected hardware

These are project decisions supplied by the owner, not a tested assembly:

| Component | Plan / status |
| --- | --- |
| Computer | Macintosh Plus motherboard |
| Analog board | Omitted |
| Internal SCSI adapter | Clipper Plus, ordered |
| ROM upgrade | ROM-inator, ordered; exact version and image not yet recorded |
| Main storage | Zip drive; exact model and interface not yet recorded |
| GPIO controller | Raspberry Pi Pico 2 |
| Serial electrical interface | SP3490 full-duplex module |
| Host connection | Motherboard printer serial port, asynchronous serial |
| Display | Replacement approach undecided; original analog-board/CRT path absent |
| Power supply | Considering RGEEK-300L Pico-ATX; harness and input supply not yet specified |
| Audio amplifier | LM386-based amplifier; module/suffix and speaker not yet specified |

The serial GPIO project and [MacGPIO protocol](../mac-plus-gpio/PROTOCOL.md)
remain applicable to this motherboard-only build. The Pico handles local I/O;
the Mac runs the host application from its boot storage.

## Consequences of omitting the analog board

The original analog board provided the motherboard's power and the CRT display
electronics. Its absence requires an engineered power harness and a separate
decision about viewing the Mac's video. It does not change the serial protocol.

Before applying power, obtain the Macintosh Plus motherboard connector pinout
and electrical requirements for the actual board revision. Identify every
required rail, ground connection, connector orientation, current requirement,
and any startup/reset-related connections from authoritative schematics.
Record verified values in a harness drawing before construction. Do not infer
pin assignments from wire colors or use a later Macintosh model's pinout.

Do not assume a 5 V-only supply is sufficient: serial line-driver circuitry may
depend on additional rails. Verify both transmit and receive operation with the
replacement supply, rather than treating a successful CPU boot as proof that
the serial port is electrically functional. An ATX supply is only a candidate
after its available rails, regulation, minimum-load behavior, and connector
mapping have been checked against the Plus's requirements.

Keep motor power out of the motherboard supply path during initial bring-up.
The final design must account for motor starting/stall current, noise, return
paths, and the signal-ground connection through the nonisolated SP3490 module.
Provide mounting, cooling, insulation, and appropriate supply protection for
the exposed motherboard. No CRT high-voltage circuitry is part of this plan.

## Candidate power supply: RGEEK-300L

The owner supplied this output-rating table. These are advertised ratings,
not independently verified measurements or a complete manufacturer datasheet.

| Output | Advertised average / peak current | Advertised ripple maximum |
| --- | --- | --- |
| +3.3 V | 6 / 8 A | 50 mV |
| +5 V standby | 1.5 / 2 A | 50 mV |
| +5 V main | 6 / 8 A | 50 mV |
| +12 V | 15 / 18 A | 120 mV |
| −12 V | 0.1 / 0.2 A | 120 mV |

The rail set makes this a plausible candidate for the Plus. Selection depends
on the motherboard's actual rail requirements, loaded voltage measurements,
and the complete system budget. The +5 V main rail's 6 A continuous rating and
the −12 V rail's 100 mA continuous rating deserve particular attention; peak
ratings are not continuous design allowances. Do not choose by the product's
headline wattage or sum per-rail maxima as guaranteed simultaneous capacity.
The table's −12 V minimum/maximum labels are numerically reversed; treat its
apparent −12.6 to −11.4 V range as an advertised tolerance to confirm, not a
verified operating requirement for the motherboard.

Before selecting the unit, verify:

- Required DC input voltage range, polarity, input connector current capacity,
  external adapter rating, and whether +12 V is regulated or passed through.
  A regulated adapter and a variable robot battery are different input cases.
- Combined output limits, temperature derating, minimum-load requirements,
  startup timing, and protection behavior from documentation for the exact unit.
- +5 V budget for motherboard, upgrades, storage if powered here, and peripherals;
  −12 V budget for the actual serial circuitry. Measure startup and operating
  loads and retain margin. Do not place the Mac on the standby rail.
- Standard ATX PS_ON# behavior and the connector's actual pinout. If confirmed
  ATX-compatible, an appropriate switch can pull PS_ON# to COM to enable main
  outputs. PWR_OK is a status signal, not automatically a Mac reset input.
- A custom, documented motherboard harness. An ATX connector is not a direct
  replacement for the Plus connector. Leave unused supply outputs insulated.
- Loaded rail voltage and ripple at the motherboard, including Zip activity
  and audio playback. Scope startup and shutdown for overshoot or sequencing
  issues before relying on the supply for an unattended robot.

For bench work, power the Pico by USB as in the GPIO guide. For integrated
power, use a supported Pico VSYS input arrangement; do not feed its 3V3 pin
from the ATX 3.3 V rail. Plan USB power isolation or the documented power-ORing
arrangement before combining external power and USB. Keep the SP3490 on the
Pico's regulated 3.3 V output.

## Audio: LM386 amplifier

An LM386-based amplifier is the selected replacement speaker-amplifier path.
Use the motherboard audio signal identified in the Plus schematic; do not
assume it is a line-level output or route it directly to a speaker.

Start with the LM386's base gain of 20 rather than adding the optional gain
capacitor for gain 200. A premade module may already have that capacitor.
Provide input AC coupling and a volume/attenuation control as needed after
checking the source's amplitude and DC bias. Keep amplifier input impedance
high enough to avoid loading the motherboard output.

Choose supply voltage from the exact LM386 suffix or module specification;
do not assume every LM386 variant accepts 12 V. A regulated 5 V branch is a
candidate if supported by the module. Specify the speaker's impedance and
power rating against that supply and the amplifier's output capability.
Follow the datasheet application circuit for output coupling, bypassing,
local bulk/ceramic decoupling, and stability components; a module may already
include them. An ordinary single-supply LM386 output needs a series output
capacitor before a ground-referenced speaker.

Route speaker and amplifier supply return currents away from the low-level
audio input return. Test at low volume first, then check clipping, noise,
oscillation, and interaction with disk and serial activity. This amplifier
does not require a new MacGPIO command: the Mac continues generating audio
through its existing sound hardware.

## Video and startup diagnostics

A motherboard-only Mac can still generate its native video signals, but those
signals are not a direct VGA or HDMI interface. A replacement display requires
a converter designed for the Plus's video timing and signal levels. Do not
connect raw motherboard video directly to a modern monitor.

Prefer a working diagnostic display path for initial RAM, ROM, and disk tests.
A later headless build must boot into the host application unattended and offer
an independent way to observe failures. The Pico cannot report Mac boot errors
through MacGPIO unless Mac software is running and communicating. Determine
whether a ROM-inator boot image provides a useful recovery path only after its
exact version, contents, and compatibility are verified.

## SCSI and Zip storage

Use the Clipper Plus manufacturer's installation instructions for its revision,
including ROM-inator clearance, cable orientation, power requirements, and
termination arrangements. Installing an internal connector does not by itself
establish bootability or correct termination.

The Zip drive must provide a compatible **SCSI interface** for this storage
path. USB, parallel-port, and IDE/ATAPI Zip drives are not directly usable on
the Plus's SCSI bus. Record the drive model before choosing cables and media;
do not assume every Zip drive reads the same disk capacities.

Plan one SCSI bus, including any internal and external devices: assign unique
target IDs, reserve the initiator's ID, and terminate only its two physical
ends. Verify termination power and terminator type against the actual Plus,
Clipper Plus, and Zip documentation. Do not assume the Plus supplies termination
power or that the adapter adds it. Avoid accidental double termination or an
unterminated stub when combining internal and external connectors.

Prepare compatible Macintosh-formatted media with an appropriate disk driver,
System software, and the host application. A formatted data disk is not
necessarily bootable. Validate cold boot from the actual Zip drive and cartridge
with the installed ROM before relying on it as main storage. Keep a second
known-good boot/recovery cartridge and a separate backup of development files.
The system version and ROM image remain to be selected; no compatibility claim
is made yet.

## Bring-up sequence and evidence

1. Inventory board revision, RAM, ROM-inator version/image, Clipper Plus revision,
   Zip model/interface, and the selected power supply.
2. Complete and independently check the power harness drawing. Measure supply
   outputs before connection and verify rails under motherboard load using
   appropriate instruments. Stop on incorrect voltage or abnormal current.
3. Establish a diagnostic video path and verify reset/startup, RAM, and ROM
   behavior before introducing motor electronics.
4. Install and inspect SCSI hardware; verify IDs, termination, and power.
   Prove repeatable cold boot and file read/write on a backed-up test cartridge.
5. Run a Mac terminal and complete the GPIO project's LED/button/ADC hardware
   acceptance test over the printer port.
6. Implement and verify MacGPIO v1 on both ends before relying on its checksum,
   retry, or output-lease behavior; current firmware still implements v0.
7. Add unattended application startup and recovery diagnostics. Design a
   separately reviewed motor interface and motion-safety extension before
   attaching actuators.

None of these hardware checks has been completed in the cloud environment.
Exact harness wiring, display conversion, and boot-media preparation remain
open engineering work, not reasons to change the agreed serial interface.
