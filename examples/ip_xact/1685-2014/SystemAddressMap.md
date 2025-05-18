# System Address Map for FutureSystemMap

This document lists the system-level address assignments for each block instance in the IP-XACT design `FutureSystemMap`. This approach is fully compliant with the IEEE 1685-2014 (IP-XACT) standard, which does not encode system addresses directly in the XML files.

| Instance   | Component | System Base Address |
|------------|-----------|--------------------|
| BlockA_1   | BlockA    | 0x0000             |
| BlockB     | BlockB    | 0x2000             |
| BlockC     | BlockC    | 0x3000             |
| BlockD     | BlockD    | 0x6000             |
| BlockA_2   | BlockA    | 0x8000             |

## Notes
- The base addresses are determined by the system integrator and are not encoded in the IP-XACT XML files per the 2014 standard.
- Each component's internal registers are mapped relative to these base addresses as defined in their respective component files.
- This table should be kept in sync with the actual system integration and any tool-specific configuration files.