# Variable Speed Pump Guide for Pool Technicians

## Overview
Variable Speed Pumps (VSPs) have revolutionized pool equipment with their energy efficiency, quiet operation, and programmable flexibility. This guide covers everything technicians need to know about installing, programming, and maintaining VSPs.

---

## 1. Benefits Over Single-Speed Pumps

### Energy Efficiency
- A single-speed pump running at 3,450 RPM uses significantly more power than a VSP running at lower speeds
- **Pump Affinity Laws**: Power consumption drops drastically as speed decreases
- Running a VSP at half speed uses roughly **1/8th the energy**
- Power consumption is exponential: increasing RPM from 2,000 to 3,000 can increase wattage use by nearly 10 times (e.g., 140 watts vs 1,000+ watts)

### Cost Savings
- While VSPs are more expensive upfront, they pay for themselves quickly
- Single-speed pump: $60-90/month to run
- VSP optimized at lower speeds: ~$30/month
- **Typical savings**: 50% reduction in electrical bill

### Quiet Operation
- VSPs are significantly quieter at lower RPMs
- Often described as "not even audible" compared to the "screaming" of older single-speed models
- Great selling point for customers with equipment near living spaces

### Better Filtration
- Running the pump for longer periods at lower speeds improves water clarity
- Better filtration quality compared to short, high-speed blasts
- More consistent chemical distribution throughout the pool

---

## 2. Energy Savings Calculations

### ROI Formula
To explain the ROI to a customer, use this formula:
**kW × Cost per kWh × Hours × 30 Days**

### Example Calculation

| Pump Type | Power Draw | Run Time | Daily Cost | Monthly Cost |
|-----------|------------|----------|------------|--------------|
| Single Speed (1.5 HP) | 2.0 kW | 10 hours | $2.00 | **$60/month** |
| Variable Speed (Low RPM) | 0.5 kW | 20 hours | $1.00 | **$30/month** |

**The Result**: Customer saves $30/month while filtering the water for twice as many hours!

### Quick Reference for Common Scenarios
- 1,500 RPM ≈ 500 watts (0.5 kW)
- 2,500 RPM ≈ 800-1,000 watts
- 3,450 RPM ≈ 1,500-2,000 watts (1.5-2.0 kW)

---

## 3. Programming and Speed Settings

Programming depends on the specific flow requirements of the pool's equipment (heaters, salt cells, etc.).

### Common RPM Recommendations

| Task | RPM Range | Notes |
|------|-----------|-------|
| **Filtration (Eco Mode)** | 1,000 - 1,500 | Sufficient for basic circulation and skimming; maximizes energy savings |
| **Heating (Gas/Solar)** | 2,600 - 2,800 | Must run fast enough to close the pressure switch in the heater or push water to solar panels |
| **Suction Cleaners** | 2,300 - 2,400 | Mechanical cleaners need higher suction to move properly |
| **Spa Mode** | 3,250 - 3,450 | Maximum speed required to provide strong jet action |
| **Waterfalls/Features** | 3,100 | Higher RPMs needed to create the desired visual effect and push debris toward skimmers |
| **Quick Clean/Backwash** | 2,200 - 2,600 | Preset for maintenance tasks or clearing the pool after a storm |

### Pro Tips
- **Flow Switch Minimum**: Always ensure the minimum speed is high enough to trigger the flow switch on salt cells and heaters; otherwise, they will not function
- **Salt Cell Operation**: Most salt cells require a minimum of 1,800-2,200 RPM to generate chlorine
- **Heater Operation**: Gas heaters typically need 2,400+ RPM to satisfy the pressure switch

### Sample Daily Schedule
```
6:00 AM - 8:00 AM:  2,400 RPM (Morning cleanup, skimmer operation)
8:00 AM - 4:00 PM:  1,200 RPM (Eco filtration mode)
4:00 PM - 6:00 PM:  2,600 RPM (Heating cycle if needed)
6:00 PM - 10:00 PM: 1,500 RPM (Evening filtration)
10:00 PM - 6:00 AM: OFF or 800 RPM (overnight, if desired)
```

---

## 4. Installation Considerations

### Hydraulics (The 5x Rule)
- To prevent cavitation and improve efficiency, you need a **straight run of pipe entering the pump that is 5 times the pipe diameter**
- Example: 10 inches of straight pipe for a 2-inch pipe
- **Avoid**: Installing 90-degree elbows directly into the pump intake

### Wiring & Bonding
- Ensure the pump is **bonded** with a solid copper conductor (8 AWG or larger) to the motor housing
- For **230V installations**: Verify you have two hot lines (red/black) and a ground; there is typically no neutral used
- Always verify voltage requirements before installation

### Automation Wiring

| Brand | Wiring Setup |
|-------|--------------|
| **Pentair** | 2-wire communication cable (Green and Yellow) connected to the RS-485 terminal |
| **Hayward** | Newer Tristar 950 models may require a 3-wire setup (Black, Yellow, Ground/Bare) connected to the HS Bus port |

### Sizing Considerations
- **Do not oversize** the pump for the filter or plumbing
- A pump moving 3 HP worth of water through a small filter or small plumbing will be inefficient and noisy
- Match pump capacity to the system's hydraulic capabilities

### Electrical Requirements
- Most VSPs are **230V** (some models offer dual voltage)
- Dedicated circuit required (typically 20-30 amp)
- GFCI protection required per NEC code

---

## 5. Troubleshooting Common Issues

| Symptom | Probable Cause | Fix |
|---------|----------------|-----|
| **Pump Humming (Won't Start)** | Bad capacitor or seized impeller | Check/replace the capacitor (discharge it first for safety). Check if the impeller spins freely; if not, clear debris |
| **Not Priming** | Air leak or low water | Check the pump lid O-ring for cracks/dryness. Ensure water level is halfway up the skimmer. Use a drain bladder to clear suction clogs |
| **Bubbles in Return Jets** | Suction side air leak | Check the pump lid O-ring or union connections. Use shaving cream on fittings while running to find the leak (it will suck the cream in) |
| **Drive/Display Off** | Power failure | Check the breaker. If power is present but the screen is blank, the drive may have failed due to a surge or short |
| **Low Flow/Cavitation** | Clogged impeller | Turn off power. Remove the basket and reach into the volute to clear debris from the impeller |
| **Overheating/Shutting Down** | Restricted flow or high ambient temperature | Check for clogged baskets, dirty filters, or closed valves. Ensure adequate ventilation around the motor |
| **Error Codes** | Various | Consult manufacturer documentation; most brands have specific error code lookup guides |

### Common Error Codes (Pentair IntelliFlo)
- **E06**: Over-current (check for debris, seized impeller)
- **E09**: Under-voltage (check electrical supply)
- **E13**: Drive temperature high (improve ventilation)

### Common Error Codes (Hayward VS)
- **PS**: Pressure switch error (low flow)
- **SFS**: Suction flow sensor error

---

## 6. Maintenance Procedures

### Weekly Tasks
- **Pump Basket**: Inspect and clean weekly. A full basket restricts flow and damages efficiency
- **Visual Inspection**: Check for leaks around fittings and the pump lid

### Monthly Tasks
- **Lubrication**: Lubricate the pump lid O-ring regularly with a **silicone or Teflon-based lubricant** (e.g., Magic Lube)
- **Never use petroleum jelly (Vaseline)** as it destroys rubber
- **Check Union Connections**: Ensure they're tight but not over-tightened

### Seasonal/Annual Tasks
- **Shaft Seal**: If water is leaking from the bottom of the pump (between the motor and the wet end), the shaft seal has failed
- Replace it immediately to prevent water from damaging the motor bearings
- **Motor Vents**: Keep motor cooling vents clear of debris

### Winterization
- In freezing climates, enable the **"Anti-Freeze" feature** in the automation
- This runs the pump when temperatures drop to prevent pipes from freezing
- If completely winterizing, remove drain plugs and store pump indoors if possible

---

## 7. Brand-Specific Notes

### Pentair IntelliFlo
- Industry-leading efficiency
- RS-485 communication for automation integration
- Built-in freeze protection
- Common models: IntelliFlo VSF, IntelliFlo3 VSF

### Hayward TriStar VS
- Competitive pricing
- HS Bus communication protocol
- User-friendly interface
- Common models: TriStar 950, VS Omni

### Jandy VS FloPro
- Integrates seamlessly with Jandy automation
- RS-485 communication
- Common models: VS FloPro 1.65, VS FloPro 2.7

---

## Quick Reference Card

### Minimum RPM by Equipment
| Equipment | Minimum RPM |
|-----------|-------------|
| Basic Filtration | 1,000 |
| Skimmer Operation | 1,200 |
| Salt Cell | 1,800-2,200 |
| Gas Heater | 2,400+ |
| Suction Cleaner | 2,300 |
| Spa Jets | 3,250+ |

### Energy Comparison
| Speed | Approximate Watts | Monthly Cost* |
|-------|-------------------|---------------|
| 1,000 RPM | 100-150 W | $5-8 |
| 1,500 RPM | 300-400 W | $15-20 |
| 2,500 RPM | 800-1,000 W | $35-45 |
| 3,450 RPM | 1,500-2,000 W | $60-80 |

*Based on $0.12/kWh and 12 hours daily operation

---

## Sources
- Pool Industry Training Materials
- Manufacturer Technical Documentation
- CPO Certification Resources
