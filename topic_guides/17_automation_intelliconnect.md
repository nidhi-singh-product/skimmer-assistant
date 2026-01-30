# Pentair IntelliConnect Automation System

## System Overview

The Pentair IntelliConnect is a control and monitoring system designed for single-body pools (no attached spa with shared equipment). It simplifies pool ownership by placing control in the client's fingertips via a smartphone app, and provides technicians with remote monitoring capabilities.

## Key Features

| Feature | Description |
|---------|-------------|
| Relay Control | Controls two high-voltage relays for single-speed pumps, booster pumps, or lights (including color light shows) |
| Variable Speed Pump Control | Digitally controls Pentair IntelliFlo VSP via RS-485 data cable for custom speeds |
| Heater Control | Controls gas heater or heat pump via fireman switch circuit and 10k ohm temperature sensor (sensor sold separately) |
| Salt System Control | Controls Pentair IntelliChlor salt chlorine generator for remote chlorine output adjustment and boost mode |
| Energy Monitoring | Real-time wattage display for connected equipment - great for demonstrating VSP energy savings |
| Freeze Protection | Uses AccuWeather internet data based on zip code to automatically activate pump at user-set temperature |

## Installation Preparation

### Pre-Install Checklist
Before arriving at the job site, obtain from the homeowner:
- Wi-Fi network name (SSID)
- Wi-Fi password (case-sensitive)
- Email address for app login
- Desired password for app login

This prevents delays and eliminates the need for the homeowner to be present.

### Wi-Fi Requirements
- IntelliConnect only operates on the 2.4 GHz band
- Verify signal strength at the equipment pad before mounting hardware
- Connect to homeowner's network with your smartphone to confirm password

## Installation Procedure

### Step 1: Power and Pair
1. Power on the unit
2. Unit enters "access point mode" for 10 minutes (blinking green "Link" LED)
3. The unit broadcasts its own Wi-Fi signal during this time
4. On your phone, connect to the IntelliConnect network in Wi-Fi settings

### Step 2: Configure Network Access
1. With phone connected to IntelliConnect, open a web browser
2. Navigate to 192.168.123.1
3. This opens the unit's pairing page
4. Select homeowner's Wi-Fi network from the drop-down list
5. Enter the password carefully
6. Once confirmed, the "Link" LED will turn solid green

### Step 3: Firmware Updates
After connecting to the internet, perform required firmware updates. These are mandatory to enable key features such as:
- Heater control
- Color light control

### Step 4: Configure Devices in App
Using the Pentair Link2O app:
1. Log in with homeowner's credentials
2. Navigate to device setup page
3. Assign equipment type to each relay:
   - Filter Pump
   - Color Light
   - Booster Pump
4. Establish running schedules
5. Set up egg timers for temporary operation
6. Configure custom pump speeds

## Troubleshooting

### Common Issues

| Symptom | Solution |
|---------|----------|
| Can't connect to IntelliConnect network | Wait for blinking green LED; unit must be in access point mode |
| "Link" LED not turning solid green | Verify Wi-Fi password is correct; check 2.4 GHz vs 5 GHz |
| Heater control not available | Perform firmware update |
| No internet weather data | Check Wi-Fi connection; verify zip code in settings |

### LED Indicators
- Blinking green: Access point mode (ready for setup)
- Solid green: Connected to Wi-Fi
- Red: Error condition (check connections)

## Energy Savings Demonstration

Use the energy monitoring feature to show homeowners VSP savings:

### Example Calculation
Single-speed 1.5 HP pump running 2,000 watts for 10 hours/day at $0.10/kWh = $60/month

VS

VSP running 500 watts for 20 hours/day at $0.10/kWh = $30/month

**Monthly Cost Formula:**
(kW) x (Cost per kWh) x (Run Time per Day) x 30 Days = Monthly Cost
