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
| Power supply | Replacement supply and harness not yet specified |

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
