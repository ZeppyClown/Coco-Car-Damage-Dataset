# Rough Idle Diagnosis - Symptom-Based Flowchart

## Symptom Description
- Engine shakes/vibrates at idle
- RPM fluctuates (hunting)
- Engine feels like it's misfiring when stopped
- May smooth out at higher RPM

## Quick Context Questions
1. **Check engine light on?** (Yes = read codes first)
2. **Idle RPM?** (Too low <500 rpm vs normal 600-800 rpm vs high >1000 rpm)
3. **Cold or warm or both?** (Cold only = different causes)

---

## Diagnostic Path - Most Likely to Least Likely

### **1. Ignition System Issues (60% of cases)**

**Quick Check:**
- Pull codes (misfires will set P030X codes)
- Note which cylinders are misfiring

**Test Procedure:**
1. **Swap ignition coils** between misfiring and good cylinder
2. Clear codes, test drive 5 minutes
3. Re-scan: If misfire **moved** to new cylinder → bad coil
4. If misfire **stayed** on same cylinder → spark plug or compression issue

**Parts to check:**
- Ignition coils (common failure on BMW N52, VW/Audi 2.0T, Honda K-series)
- Spark plugs (fouled, worn, wrong gap)
- Plug wires (older vehicles without coil-on-plug)

**Real-world note:** On high-mileage engines (>80k miles), replace ALL coils and plugs together even if only one is bad. Others will fail soon.

---

### **2. Vacuum Leak (25% of cases)**

**Symptoms specific to vacuum leak:**
- Idle RPM too high (>900 rpm)
- Hissing sound from engine bay
- Lean codes (P0171, P0174)

**Quick Check:**
- Spray brake cleaner or carb cleaner around intake manifold, vacuum hoses, PCV system
- If RPM changes when spraying → leak found

**Common leak points:**
- Intake manifold gaskets (BMW N52, N54, N55)
- PCV valve/hoses
- Brake booster vacuum line
- EVAP purge valve
- Throttle body gasket

**Tools needed:** Smoke machine (best) or spray cleaner method

---

### **3. Fuel System Issues (10% of rough idle cases)**

**Symptoms:**
- Rough idle + hesitation on acceleration
- Long crank before start
- Fuel trims out of spec (>±10%)

**Test Procedure:**
1. Check fuel pressure at rail
   - Most vehicles: 40-60 psi at idle
   - Direct injection: 500-2000+ psi (need special gauge)
2. Check fuel trims with scan tool (short-term and long-term)

**Common causes:**
- Clogged fuel filter
- Weak fuel pump
- Dirty fuel injectors
- Failed fuel pressure regulator

---

### **4. Air Intake/MAF Issues (3% of cases)**

**Symptoms:**
- Rough idle + poor throttle response
- Black smoke from exhaust
- MAF sensor dirty or failed

**Quick Check:**
- Unplug MAF sensor: If idle **improves**, MAF is bad
- Clean MAF with MAF cleaner spray (CRC MAF sensor cleaner)

**Note:** Don't use carb cleaner on MAF - damages sensor

---

### **5. Mechanical Issues (2% of rough idle cases)**

**Symptoms:**
- Rough idle that doesn't change with tests above
- Low compression on one or more cylinders
- Valve train noise

**Test Procedure:**
1. Compression test (wet and dry)
   - Good: >150 psi, <10% variance between cylinders
   - Bad: <120 psi or >15% variance
2. Leak-down test if compression is low

**Causes:**
- Burnt valve
- Worn piston rings
- Bent valve (timing belt failure)
- Valve adjustment needed (Honda, older Toyota)

---

## Special Cases

### **Rough Idle ONLY When Cold**
**Most likely causes:**
1. Coolant temp sensor lying to ECU (check with scan tool)
2. Cold-start injector or enrichment system fault
3. Throttle body carbon buildup (common on direct injection engines)

**Fix:** Clean throttle body, test coolant temp sensor

---

### **Rough Idle ONLY When Warm**
**Most likely causes:**
1. Ignition coils breaking down under heat
2. Fuel pressure dropping when hot (weak pump)
3. EVAP purge valve stuck open

---

### **Idle OK in Park, Rough in Drive**
**Not an engine problem - this is transmission related:**
- Bad motor mounts (engine shaking from bad mount)
- Torque converter shudder
- Low transmission fluid

**Quick test:** Put in neutral while stopped - if idle smooths out, it's not engine

---

## Common Misdiagnoses to Avoid

1. **Replacing throttle body for rough idle** (rarely the cause - clean it first)
2. **Replacing MAF sensor without testing** (expensive and often not the issue)
3. **Replacing fuel injectors for rough idle** (only if fuel trim data supports it)
4. **Ignoring vacuum leaks** (most common missed diagnosis)

---

## Tools Required
- **Basic:** Scan tool, spark plug socket, coil puller
- **Intermediate:** Fuel pressure gauge, vacuum gauge, compression tester
- **Advanced:** Smoke machine, oscilloscope, leak-down tester

---

## Metadata
```json
{
  "symptom": "rough_idle",
  "difficulty": "beginner_to_intermediate",
  "diagnostic_time": "30-90 minutes",
  "common_tools": ["scan_tool", "spark_plug_socket", "vacuum_gauge"],
  "success_rate": "95% when following flowchart",
  "category": "drivability"
}
```
