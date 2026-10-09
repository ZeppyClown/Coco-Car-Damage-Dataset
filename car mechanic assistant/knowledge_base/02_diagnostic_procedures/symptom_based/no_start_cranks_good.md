# No Start - Cranks Good but Won't Fire

## Symptom Description
- Starter motor cranks engine normally (good compression sound)
- Engine turns over but doesn't fire/run
- No odd noises during cranking
- Battery voltage good (>12V)

## Quick Verification
- **Cranking speed normal?** (Not slow/labored)
- **Any codes?** (Check for security system, fuel pump, cam/crank sensor codes)
- **Fuel gauge reading?** (Confirm actual fuel in tank - gauges lie)

---

## The Three Essentials: Air, Fuel, Spark

Every engine needs these three to run. Test in this order:

---

### **1. Check for Spark (Test First - Easiest)**

**Why first?** 90% of no-start conditions are ignition-related.

**Quick Test:**
1. Pull a spark plug or use inline spark tester
2. Ground plug body to engine
3. Crank engine, look for strong blue spark
4. **Strong blue spark every crank** = ignition OK
5. **Weak orange spark or no spark** = ignition problem

**No spark - Most likely causes:**
1. **Crankshaft position sensor failed** (70% of no-spark cases)
   - No code may be stored if sensor completely dead
   - Common on: Honda, Nissan, Hyundai/Kia
2. **Ignition coil(s) failed** (15%)
   - Multiple coils can fail together
   - Test: Check for power at coil connector during crank
3. **Cam position sensor** (10%)
   - Some engines won't fire without cam sensor signal
4. **Ignition module/PCM** (5%)
   - Rare but possible

**Fix priority:**
- Replace crank sensor first if no codes (cheap, common failure)
- If has power to coil but no spark → bad coil or PCM

---

### **2. Check for Fuel**

**Quick Test:**
1. Remove air intake, spray starting fluid into throttle body
2. Crank engine
3. **If it fires briefly then dies** → fuel delivery problem confirmed
4. **If nothing changes** → not a fuel issue (check spark/compression)

**No fuel - Most likely causes:**

**A. Fuel Pump Not Running (80% of no-fuel cases)**

Test procedure:
1. Turn key to ON (don't crank) - listen for 2-second fuel pump prime
2. No pump sound? Check:
   - Fuel pump fuse
   - Fuel pump relay (swap with identical relay to test)
   - Fuel pump power at tank connector
   - Anti-theft system active? (flashing security light)

**Common failures:**
- Fuel pump relay (very common - $15 part)
- Fuel pump failed (listen for hum in tank)
- Inertia switch tripped (Ford - check trunk/footwell)
- Immobilizer/security system active

**B. Clogged Fuel Filter (15%)**
- More common on high-mileage vehicles
- Check fuel pressure: should be 40-60 psi (port injection) or 500+ psi (direct injection)

**C. Failed Fuel Injectors (5%)**
- Rare for ALL injectors to fail
- Test: Use noid light to check for injector pulse during crank
- No pulse on ANY injector = PCM or cam/crank sensor issue

---

### **3. Check for Air (Rare - But Check if 1 & 2 Are Good)**

**Air blockage causes:**
- Completely clogged air filter (rodent nest)
- Closed throttle body (stuck/frozen)
- Intake manifold blocked

**Quick test:**
- Remove air filter and intake tube
- Look into throttle body - blade should open when you press gas pedal
- Crank with intake open - does it try to fire?

---

## Code-Specific Scenarios

### **P0335 - Crank Position Sensor**
- **Action:** Replace crank sensor immediately
- **Common on:** Honda, Nissan, Hyundai, Kia
- **Part cost:** $30-80
- **Location:** Usually near crankshaft pulley or on transmission bell housing

### **P0340 - Cam Position Sensor**
- **Action:** Replace cam sensor
- **Note:** Some engines run rough without cam sensor, others won't start at all
- **Common on:** Nissan VQ engines, Toyota 2AZ

### **P0230 - Fuel Pump Primary Circuit**
- **Action:** Check fuel pump relay and fuse first
- **Then:** Check wiring to fuel pump

### **No codes stored**
- **Most likely:** Crank position sensor failed completely (no signal = no code)
- **Also check:** Anti-theft system, fuel pump relay

---

## Anti-Theft / Immobilizer Issues

**Symptoms:**
- No start, cranks fine
- Security light flashing on dash
- May have fuel and spark but still won't fire

**Common systems:**
- **GM PassLock/PassKey** - flashing security light
- **Ford PATS** - flashing theft light
- **Chrysler Sentry Key** - flashing red dot

**Quick test:**
- Leave key in ON position for 10 minutes (don't crank)
- Security light should stop flashing and stay solid or turn off
- Try to start - if it works, system was locked out

**If security system is the issue:**
- May need key relearn procedure (varies by manufacturer)
- Could be bad key, ignition cylinder, or theft module

---

## Timing Belt/Chain Failure

**Symptoms:**
- Cranks very easily (no compression)
- May have fuel and spark but won't fire
- Might hear rattling before it died

**Quick test:**
1. Remove valve cover or timing cover
2. Watch cam(s) while cranking
3. **If cam doesn't turn** → belt/chain broken

**Interference engine?**
- Honda, VW/Audi, Subaru, Mazda = YES (valves hit pistons)
- Toyota, Nissan (most) = NO (non-interference)
- If interference engine with broken belt → expect bent valves

---

## Compression Check (If Spark and Fuel Are Good)

**When to test:**
- Have spark and fuel but still won't fire
- Cranks very easily (too fast)
- History of overheating or timing belt replacement

**Test:**
1. Remove all spark plugs
2. Disable fuel and ignition
3. Screw compression tester into cylinder #1
4. Crank engine 5-7 times
5. Record pressure, repeat for all cylinders

**Good compression:**
- 150-180 psi per cylinder
- Less than 10% variance between cylinders

**Bad compression:**
- Below 120 psi on any cylinder
- More than 15% variance
- Causes: Bent valves, worn rings, blown head gasket, broken piston

---

## Common Misdiagnoses to Avoid

1. **Replacing PCM for no-start** (very rarely the cause - test everything else first)
2. **Replacing fuel pump without testing** (check relay and fuse first - saves $300+)
3. **Missing anti-theft system lockout** (costs nothing to check)
4. **Assuming "crank sensor" based on symptoms alone** (confirm with testing)

---

## Diagnostic Flowchart Summary

```
No Start (Cranks Good)
│
├─ Check for SPARK
│   ├─ No Spark → Crank sensor (70%), Coil (15%), Cam sensor (10%)
│   └─ Has Spark → Go to Fuel
│
├─ Check for FUEL
│   ├─ No Fuel → Pump relay (40%), Pump (30%), Filter (15%), Security (15%)
│   └─ Has Fuel → Go to Air/Compression
│
└─ Check AIR and COMPRESSION
    ├─ Blocked intake → Remove air filter, check throttle body
    └─ Low/no compression → Timing belt/chain, bent valves, engine damage
```

---

## Tools Required
- **Essential:** Spark tester, starting fluid, fuel pressure gauge, test light
- **Helpful:** Scan tool, noid light set, compression tester
- **Advanced:** Oscilloscope (for crank/cam sensor waveform analysis)

---

## Metadata
```json
{
  "symptom": "no_start_cranks_good",
  "difficulty": "beginner_to_intermediate",
  "diagnostic_time": "15-60 minutes",
  "common_causes": ["crank_sensor", "fuel_pump_relay", "ignition_coil", "security_system"],
  "success_rate": "98%",
  "category": "no_start"
}
```
