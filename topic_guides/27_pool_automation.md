# Pool Automation Systems Guide for Service Technicians

## Overview
Pool automation serves as the "brain" of the equipment pad, moving beyond simple mechanical timers to integrated digital control. This guide covers types of automation controllers, common brands, programming, troubleshooting, and salt system integration.

---

## 1. Types of Automation Systems

### Entry-Level/Single Body (IoT)
- **Example**: Pentair IntelliConnect
- Designed for pools without spas or complex water features
- Relies heavily on smartphone apps for control and updates
- Typically handles 1-2 high-voltage relays (pumps/lights) and heater control via a fireman's switch

### Full Automation (Pool/Spa Combo)
- **Examples**: Pentair EasyTouch, Jandy AquaLink
- Handle actuators to switch valves between pool and spa modes
- Manage multiple pumps
- Integrate complex lighting and chemical systems

### Vendor-Agnostic/Modern
- **Example**: The Attendant by Poolside Tech
- Unlike the "Big Three" (Pentair, Hayward, Jandy) which create "walled gardens"
- Designed to integrate components from different manufacturers
- Focus on "feature-based" programming (e.g., "Heat to 85°") rather than device-based programming

---

## 2. Common Brands and Specific Procedures

### Pentair (IntelliFlo & EasyTouch/IntelliConnect)

**Pump Communication (RS-485)**
- Pentair Variable Speed (VS) pumps communicate via a low-voltage cable
- Connect the **Green and Yellow** wires to the COMM port on the automation board
- Black and Red are often unused for basic comms

**IntelliConnect Setup**
- **Logic**: Uses current detection. If a relay is assigned to a filtration pump, the system checks if the pump is drawing at least 100 watts. If not, it will not allow the heater or salt cell to fire
- **Connectivity**: Requires a strong 2.4GHz WiFi signal. If the router has special characters in the password (like #, %, &), older firmware may reject it until an over-the-air update is performed

**EasyTouch Programming**
- **Service Mode**: Press the "Mode" button to enter Service Mode to stop schedules from running while you work. "Timeout Mode" allows you to run equipment manually for a short period (e.g., 3 hours) before it reverts to Auto
- **Clock**: System schedules rely entirely on the internal clock. If power outages occur, verify the clock settings under Menu > Settings > Clock

### Hayward (Omni, AquaRite, Tristar)

**Pump Communication Upgrade**
- When upgrading to newer **Hayward Tristar 950** pumps, the communication wiring has changed
- Older models used a 2-wire setup
- Newer models require a **3-wire setup** (Black, Yellow, and Ground/Bare) connected to the HS Bus port

**Salt System Diagnosis (AquaRite)**
- **PCB Errors**: If the display reads "PCB" or the power light goes out, the main circuit board usually needs replacement
- **Diagnostic Button**: Pressing the diagnostic button 5 times triggers the instant salinity reading. This is used for recalibration

**AquaRite Calibration** (if salt reading doesn't match manual water test):
1. Switch to "Auto"
2. Press the Diagnostic button 5 times to see the instant salinity
3. Flip the switch to "Super Chlorinate" and back to "Auto" to lock in the new reading

**Flow Switch**: A common failure point. Ensure the arrows on the switch align with the direction of water flow. The "No Flow" light indicates the cell has stopped producing chlorine for safety

### Jandy (AquaLink, AquaPure)

**Pump Addressing**
- When installing a new Jandy VS pump (e.g., DV2A) into an existing automation system, the pump may automatically populate to **Address 5** rather than the traditional Filter Pump address
- You must assign schedules to Pump 5 in the service controller for it to function

**Temperature Sensors**
- Wired into the green 10-pin terminal bar
- If readings are erratic, check for corrosion or loose wires

**AquaPure Tri-Sensor Codes**
- **172/180 Errors**: Indicate a problem with the Tri-Sensor (flow/salinity/temp sensor). Usually requires replacing the sensor module or the entire cord assembly
- **125/194 Errors**: Indicate low current or electrical issues often caused by corroded terminals on the cell cord. If the studs on the cell are corroded, the entire cell unit must be replaced

---

## 3. Programming Timers and Schedules

### Schedules vs Egg Timers

**Schedules**
- Used for daily filtration and circulation
- Example: Running the pool from 9:00 AM to 4:00 PM daily
- On variable speed pumps, you can program different speeds for different times to maximize energy efficiency

**Egg Timers**
- Countdown timers used for temporary functions
- **Usage**: Great for spa jets, lights, or cleanup cycles
- **Setup**: You program a duration (e.g., 3 hours). When the client presses the button (physically or in the app), the equipment runs for that duration and then shuts off automatically

### Variable Speed (VS) Optimization

**Flow Requirements**
- Ensure the scheduled RPM is high enough to trigger the flow switches for heaters and salt cells
- If the RPM is too low (e.g., <1500 RPM depending on plumbing), the heater may lockout or the salt cell will stop generating

**Priming Mode**
- Most pumps have a priming cycle (e.g., high speed for 3 minutes) upon startup
- This can be adjusted in the automation settings if the equipment pad is close to the water level and requires less priming time

---

## 4. Integration with Salt Systems

### Pentair IntelliChlor

**Power**
- The salt cell transformer should be wired to the **Load** side of the filter pump relay (or have a communication cable that ensures the pump is running)
- The automation sends a signal via RS-485 to tell the cell what percentage to produce

**Safety Logic**
- Automation systems like IntelliConnect actively check if the pump is consuming power before allowing the salt cell to generate, preventing gas buildup in stagnant pipes

### Hayward AquaRite

**Calibration Steps**:
1. Switch to "Auto"
2. Press the Diagnostic button 5 times to see the instant salinity
3. Flip the switch to "Super Chlorinate" and back to "Auto" to lock in the new reading

**Flow Switch**
- A common failure point
- Ensure the arrows on the switch align with the direction of water flow
- The "No Flow" light indicates the cell has stopped producing chlorine for safety

### Jandy AquaPure

**Tri-Sensor Codes**
- **172/180 Errors**: Problem with the Tri-Sensor (flow/salinity/temp sensor). Usually requires replacing the sensor module or the entire cord assembly
- **125/194 Errors**: Low current or electrical issues often caused by corroded terminals on the cell cord. If the studs on the cell are corroded, the entire cell unit must be replaced

---

## 5. Troubleshooting Automation Issues

### 1. Sensor Failures (Air/Water/Solar)

**Symptoms**: Erratic temperature readings (e.g., pool reads 135°F or -20°F) or heater not firing

**Fix**: These are typically 10k ohm thermistors. Check wiring at the board for rust or loose connections. If wiring is good, replace the sensor

### 2. Pump Not Responding to Automation

**Check the Comm Cable**: Ensure the low-voltage RS-485 cable is intact. Rodents frequently chew these wires

**Check the Address**: Ensure the pump address in the pump's onboard menu matches the automation (usually Address 1 for the main filtration pump, but check for Address 5 on newer Jandy units)

**Service Mode**: Ensure the system is in "Auto." If left in "Service" or "Timeout," the schedule will not run

### 3. Salt System "No Flow" or Low Salt

**Verify Pump Speed**: Increase RPM to ensure the flow switch is physically closing

**Clean the Cell**: Calcium buildup bridges the plates and causes false low salt readings. Clean with a mild acid solution

**Cold Water**: Salt cells stop producing when water temperature drops below ~60°F. This is a safety feature, not a failure

### 4. Blank Screen or No Power

**Breakers**: Check the high-voltage breakers at the sub-panel

**Low Voltage Breakers**: Many panels (like Pentair EasyTouch) have small button-style circuit breakers for the low voltage (electronics) side. Press to reset them

---

## Quick Reference

| Issue | First Check | Common Fix |
|-------|-------------|------------|
| No communication with pump | RS-485 cable | Check Green/Yellow wires |
| Erratic temperature | Sensor wiring | Replace 10k thermistor |
| Salt cell not generating | Flow switch | Clean cell, check RPM |
| Schedules not running | System mode | Switch from Service to Auto |
| WiFi connection issues | Password special chars | Update firmware |

---

## Sources
- Pool Operations & Installation Manual
- NotebookLM Pool Service Knowledge Base
