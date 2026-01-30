# Equipment Error Codes - Troubleshooting Guide

## Pentair Heater Error Codes

### E05 - Stack Flue Sensor / High Exhaust Temperature

**What it means:** Exhaust temperature exceeded 176°F. The stack flue sensor detected overheating.

**Common Causes:**
- Sooted heat exchanger (combustion issue)
- Scaled heat exchanger (water side)
- Low water flow through heater
- Clogged exhaust or air vents
- Defective stack flue sensor
- Debris in burner area (rodent nests, spider webs)

**Troubleshooting Steps:**
1. **Check diagnostic temperature:** Press and hold POOL button to display exhaust temp. Should climb to 170-380°F within 3 minutes.
2. **Inspect venting:** Check intake and exhaust for obstructions. Remove any debris, nests, or spider webs.
3. **Clean the sensor:** Remove the stack flue sensor (bolt with 2 wires), clean terminals, reinstall.
4. **Check water flow:** Ensure filter is clean and pump is running at adequate GPM.
5. **Inspect heat exchanger:** Look for soot (combustion problem) or scale (water chemistry problem).

**If sensor replacement doesn't fix it:** Examine thermal governor and internal bypass assembly.

---

### PS - Pressure Switch Error

**What it means:** Pressure switch is stuck open due to insufficient water flow.

**Common Causes:**
- Dirty or clogged filter
- Pump not running or undersized
- Closed valve in system
- Variable speed pump running too slow
- Defective pressure switch

**Minimum Flow Requirements:**
- Most Pentair heaters require 40 GPM minimum (45 GPM recommended)
- Variable speed pumps must be programmed for adequate flow when heater is active

**Troubleshooting Steps:**
1. Verify pump is running
2. Check filter pressure - clean/backwash if high
3. Ensure all valves are fully open
4. Check flow rate on variable speed pump display
5. Inspect pressure switch wiring connections
6. Test pressure switch continuity

---

### E01 - Water Flow/Pressure Switch

**What it means:** No water flow detected at startup.

**Troubleshooting:** Same as PS error - focus on water flow issues first.

---

### E02 - Ignition Control Lockout

**What it means:** Heater failed to ignite after multiple attempts.

**Common Causes:**
- Gas supply issue (valve closed, empty tank)
- Failed igniter
- Dirty or failed flame sensor
- Gas valve failure
- Control board issue

**Troubleshooting Steps:**
1. Verify gas supply is on
2. Check for gas smell at heater (indicates supply is reaching unit)
3. Inspect igniter for cracks or damage
4. Clean flame sensor with fine sandpaper
5. Check gas pressure at manifold
6. If all else fails, may need control board replacement

---

### E03 - Vent Pressure Switch Error

**What it means:** Combustion air blower not operating properly.

**Common Causes:**
- Blocked vent/exhaust
- Failed blower motor
- Vent pressure switch stuck
- Wiring issue

---

### E04 - Thermal Regulator Limit

**What it means:** Water temperature exceeded safe limit.

**Troubleshooting:**
1. Check for adequate water flow
2. Inspect thermal regulator
3. Verify thermostat settings

---

### E06 - Water Temperature Sensor Failure

**What it means:** Temperature sensor is reading out of range or failed.

**Troubleshooting:**
1. Check sensor connections
2. Test sensor resistance with multimeter
3. Replace sensor if defective

---

## Hayward Heater Error Codes

### IF - Ignition Failure

**What it means:** Heater attempted to ignite but failed to detect flame.

**Common Causes:**
- Low gas pressure
- Failed igniter
- Dirty flame sensor
- Gas valve issue
- Control board (ICB) failure

**Troubleshooting Steps:**
1. Verify main gas supply is on
2. Check that internal gas valve is in ON position
3. Clean flame sensor with fine sandpaper or emery cloth
4. Check igniter for visible damage
5. Verify gas pressure at inlet and manifold
6. Inspect flame sensor wiring
7. If persistent, may need gas valve or ICB replacement

---

### LO - Low Flow / Pressure Switch

**What it means:** Insufficient water flow detected by pressure switch.

**Common Causes:**
- Pump not running or cycling off
- Dirty filter restricting flow
- Closed or partially closed valve
- Slow pump prime at startup
- Blocked flue affecting vent pressure switch
- Failed water pressure switch

**Troubleshooting Steps:**
1. Verify pump is running and primed
2. Check filter pressure - backwash or clean if high
3. Ensure all valves fully open
4. Inspect pressure switch wiring connections
5. Check vent pressure switch and ensure flue is clear
6. Test pressure switch for continuity
7. Replace pressure switch if faulty

**Note:** If pump is slow to prime, heater may show LO and will auto-restart after 2 minutes.

---

### BD - Bad Board / High Voltage Fault

**What it means:** Control board issue or high voltage problem detected.

**Troubleshooting Steps:**
1. Power down heater completely
2. Locate FC4 fuse on fuse board and test for continuity
3. If fuse is blown, replace it
4. Check voltage across pins as specified in service manual
5. If voltage tests fail, may need control module or harness replacement

**Warning:** High voltage diagnostics should be performed by qualified technicians.

---

### CE - Communication Error

**What it means:** Control module and display interface not communicating properly.

**Troubleshooting Steps:**
1. Power cycle heater (disconnect and reconnect power)
2. Check wiring between display and control module
3. Verify display interface plug is firmly seated
4. Inspect for damaged wires or corroded connections

**Common Fix:** Often requires replacement of both display board AND ICB (ignition control board) to fully resolve.

---

### AO - Air/Vacuum Switch Open

**What it means:** Vent pressure switch not closing during startup.

**Common Causes:**
- Blocked flue or exhaust
- Failed vacuum/vent switch
- Blower motor issue

---

### HS - High Limit Switch

**What it means:** Water temperature exceeded safe limit, high limit tripped.

**Troubleshooting:**
1. Allow heater to cool
2. Press red reset button on high limit switch
3. Check for adequate water flow
4. Clean filter
5. If trips repeatedly, investigate underlying cause

---

### HF - Hardware Failure

**What it means:** Internal hardware/component failure detected.

**Action:** Usually requires professional diagnosis and component replacement.

---

## Pentair Salt Cell Error Codes (IntelliChlor)

### No Flow

**What it means:** Cell not detecting adequate water flow.

**Troubleshooting:**
1. Ensure pump is running
2. Check filter pressure
3. Clean cell if scaled
4. Inspect flow sensor

---

### Check Salt

**What it means:** Salt level is outside acceptable range.

**Troubleshooting:**
1. Test salt level manually
2. Add salt if below 2700 ppm
3. Dilute if above 4500 ppm
4. Recalibrate cell if reading seems wrong

---

### Cold Water

**What it means:** Water temperature too low for chlorine generation (typically below 50°F).

**Action:** Normal in cold weather. Cell will resume when water warms.

---

### Inspect Cell

**What it means:** Cell may need cleaning or is reaching end of life.

**Troubleshooting:**
1. Remove and inspect cell for calcium buildup
2. Clean with diluted muriatic acid (4:1 water to acid)
3. If cleaning doesn't help, cell may need replacement

---

## Variable Speed Pump Error Codes (Pentair IntelliFlo)

### Power Out Failure

**What it means:** Drive detected power interruption.

**Action:** Usually clears on power restoration. Check electrical connections if persistent.

---

### Drive Overheating

**What it means:** Motor or drive electronics overheating.

**Troubleshooting:**
1. Check for adequate ventilation around pump
2. Verify pump is not running in dead-head condition
3. Check for debris blocking motor cooling vents
4. Allow pump to cool before restarting

---

### Priming Error

**What it means:** Pump failed to achieve prime within timeout period.

**Troubleshooting:**
1. Check water level in pool
2. Inspect pump lid O-ring
3. Check for air leaks on suction side
4. Ensure valves are open

---

## Automation System Troubleshooting

### Pentair IntelliCenter/IntelliTouch

**Communication Error:** Check wiring between control panel and equipment. Verify addresses.

**Equipment Not Responding:** Check individual equipment power and connections. Verify circuit assignments.

### Hayward OmniLogic/ProLogic

**Sensor Error:** Test sensor, check wiring, replace if faulty.

**Relay Click No Start:** Equipment relay clicking but device not starting - check equipment power supply and connections.

---

## General Troubleshooting Approach

1. **Document the error code** - Note exactly what displays and when
2. **Power cycle first** - Many codes clear with a power reset
3. **Check the basics** - Water flow, gas supply, electrical connections
4. **Consult manufacturer manual** - Each model has specific diagnostic procedures
5. **Check warranty status** - Many components have multi-year warranties
6. **Know when to call** - High voltage and gas issues require qualified technicians

## Resources

- Pentair Technical Support: 1-800-831-7133
- Hayward Technical Support: 1-888-429-9273
- Keep equipment manuals on-site for reference
- Download apps: Pentair Home, Hayward OmniLogic for remote diagnostics
