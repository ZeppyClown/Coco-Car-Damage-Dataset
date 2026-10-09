# P0300 - Random/Multiple Cylinder Misfire Detected

## Code Definition
**OBD-II Generic Code**: P0300
**System**: Ignition/Engine Mechanical
**Severity**: Medium to High (can damage catalytic converter)
**Type**: Emission-related, will turn on Check Engine Light

## What It Means
The PCM has detected misfiring on multiple cylinders (not just one specific cylinder). The crankshaft position sensor is detecting irregular rotation patterns that indicate incomplete combustion in random cylinders.

**Related Codes:**
- P0301 - Cylinder 1 misfire
- P0302 - Cylinder 2 misfire
- P0303 - Cylinder 3 misfire
- (etc. - P030X where X = cylinder number)

**Note:** If you have P0300 **plus** specific cylinder codes (like P0302), diagnose the specific cylinder codes first.

---

## Real-World Causes (Workshop Probability)

### **1. Ignition System - 60% of P0300 cases**

**Most common:**
- **Multiple ignition coils failing** (40%)
  - Common on: BMW N52/N54/N55, VW/Audi 2.0T, Ford EcoBoost, Honda
  - Usually coils fail gradually - start with one, others follow
  - Coils fail more under load (acceleration) or when hot

- **Worn spark plugs** (15%)
  - Widened gap causes weak spark
  - Carbon fouling or oil fouling
  - Wrong heat range installed

- **Spark plug wires bad** (5% - older vehicles without coil-on-plug)
  - Arcing to ground
  - High resistance in wire

**Diagnosis:**
1. Pull ignition coils one at a time, inspect for:
   - Cracks in boot
   - Carbon tracking (black lines)
   - Oil contamination
2. Check spark plugs:
   - Gap spec (usually 0.028-0.043")
   - Electrode wear
   - Correct part number for vehicle
3. Test coil resistance (if available - many modern coils can't be tested this way)

**Fix:**
- Replace ALL coils and plugs if vehicle has >80k miles
- Don't replace one at a time - others will fail soon
- Use OEM coils on European cars (aftermarket often fails quickly)

---

### **2. Fuel System - 20% of cases**

**Common causes:**
- **Low fuel pressure** (12%)
  - Weak fuel pump
  - Clogged fuel filter
  - Failed fuel pressure regulator
  - Test: Fuel pressure should be 40-60 psi (port injection) at idle

- **Dirty/clogged fuel injectors** (5%)
  - Multiple injectors with restricted flow
  - Test: Injector flow balance test

- **Bad fuel quality** (3%)
  - Water in fuel
  - Wrong octane causing detonation (reads as misfire)

**Diagnosis:**
1. Check fuel pressure with gauge at rail
2. Check fuel trims with scan tool:
   - Both banks running rich (negative trim) = too much fuel
   - Both banks running lean (positive trim) = not enough fuel
3. Test fuel injector spray pattern (remove rail, watch spray during crank)

**Fix:**
- Replace fuel filter first (cheap, often fixes it)
- Fuel pump if pressure is low
- Injector cleaning service or replacement

---

### **3. Vacuum Leak - 10% of cases**

**Symptoms:**
- P0300 + lean codes (P0171, P0174)
- High idle RPM
- Hissing sound from engine bay

**Common leak points:**
- Intake manifold gaskets
- PCV valve and hoses
- Brake booster vacuum line
- EVAP purge valve stuck open
- Throttle body gasket

**Diagnosis:**
- Spray brake cleaner around suspected areas while engine runs
- If idle changes when spraying = leak found
- Better: Use smoke machine

**Fix:**
- Replace leaking gaskets/hoses
- Common: Intake manifold gaskets on BMW N52, GM 3800, Ford 4.6L

---

### **4. Engine Mechanical - 8% of cases**

**Causes:**
- **Low compression** (worn rings, burnt valves)
- **Valve timing off** (stretched timing chain, jumped timing)
- **Vacuum leak from worn valve guides** (older engines)
- **Carbon buildup on valves** (direct injection engines)

**Diagnosis:**
1. Compression test (should be 140-180 psi, <10% variance)
2. Leak-down test if compression is low
3. Check timing marks
4. Borescope inspection if available

**Fix:**
- Timing chain replacement if stretched
- Valve cleaning (walnut blasting for direct injection)
- Engine rebuild if compression is very low

---

### **5. Mass Airflow Sensor - 2% of cases**

**Symptoms:**
- P0300 + P0171/P0174 (lean codes)
- Poor throttle response
- Black smoke from exhaust

**Diagnosis:**
- Unplug MAF - if idle improves, MAF is bad
- Check MAF reading with scan tool at idle (should be 2-7 g/s depending on engine size)

**Fix:**
- Clean MAF sensor with MAF cleaner spray
- If cleaning doesn't help, replace MAF

---

## Diagnostic Steps (Priority Order)

### **Step 1: Read ALL codes**
- If you have P0300 + specific cylinder codes → start with those cylinders
- If ONLY P0300 → continue below

### **Step 2: Check for obvious issues**
- Loose/disconnected vacuum hoses
- Oil in spark plug wells (valve cover gasket leak)
- Cracked ignition coil boots

### **Step 3: Test ignition system** (Most likely - do this first)
1. Pull ignition coils - inspect for damage
2. Pull spark plugs - check condition, gap, part number
3. If plugs are old (>60k) or wrong - replace
4. If coils show signs of failure - replace all

### **Step 4: Check fuel system**
1. Check fuel pressure at rail
2. Check fuel trims on scan tool (should be ±5%)
3. If pressure low or trims out of range → fuel system problem

### **Step 5: Check for vacuum leaks**
1. Visual inspection of hoses and gaskets
2. Spray test or smoke test
3. Check PCV system

### **Step 6: If all above are good → mechanical issue**
1. Compression test
2. Timing chain inspection
3. Carbon cleaning (direct injection engines)

---

## Common Misdiagnoses

1. **Replacing PCM/ECU for P0300**
   - Almost never the PCM
   - Always check ignition, fuel, mechanical first

2. **Replacing catalytic converter**
   - Cat doesn't cause misfire - misfire damages cat
   - Fix the misfire first, then check cat

3. **Replacing MAF sensor without testing**
   - MAF rarely causes random misfire
   - Clean it first, test it, then replace if proven bad

4. **Ignoring obvious vacuum leaks**
   - Simple fix often overlooked

---

## Parts Commonly Needed

**Ignition:**
- Spark plugs (full set)
- Ignition coils (full set recommended)
- Valve cover gasket (if oil in plug wells)

**Fuel:**
- Fuel filter
- Fuel pump (if pressure test fails)
- Fuel injector cleaning service

**Other:**
- Intake manifold gaskets
- PCV valve
- Vacuum hoses

---

## Warning Signs

**Don't drive if:**
- Severe misfire (car barely runs)
- Strong fuel smell (unburned fuel = fire hazard)
- Catalyst overheating (can cause fire)

**Safe to drive temporarily:**
- Light misfire, car runs OK
- No fuel smell
- Taking it straight to shop

**Cat damage risk:**
- Unburned fuel from misfire goes into catalytic converter
- Causes converter to overheat and melt
- If misfire continues >100 miles, cat will likely be damaged

---

## Estimated Repair Costs

**DIY:**
- Spark plugs: $40-120 (set)
- Ignition coils: $120-600 (set, aftermarket to OEM)
- Fuel filter: $15-50
- PCV valve: $10-30

**Shop Labor:**
- Spark plug replacement: 0.5-2 hrs ($50-300)
- Ignition coil replacement: 1-3 hrs ($100-450)
- Fuel pump replacement: 2-4 hrs ($200-600)
- Compression test: 1-2 hrs ($100-300)

**Most common total repair:**
- Coils + plugs: $250-900 (DIY to shop)

---

## Metadata
```json
{
  "code": "P0300",
  "system": "ignition_fuel_mechanical",
  "severity": "medium_to_high",
  "common_causes": ["ignition_coils", "spark_plugs", "fuel_pressure", "vacuum_leak"],
  "manufacturer": "generic_obd2",
  "typical_repair_time": "1-3 hours",
  "urgency": "address_soon",
  "cat_damage_risk": "yes_if_continued"
}
```
