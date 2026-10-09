# BMW INPA - Fuel Injector Coding Procedure

## Overview
After replacing fuel injectors on BMW vehicles, the DME must be programmed with each injector's unique correction code. Without coding, the engine will run rough and set misfire codes.

**Applies to:**
- N52, N54, N55, S65, N63 engines (and most modern BMW engines)
- Any injector replacement (even single injector)

**Software Required:**
- INPA 5.0.2 or newer
- EDIABAS configured
- BMW Standard Tools installed

**Hardware Required:**
- INPA K+DCAN cable (or BMW ICOM interface)
- Windows laptop (32-bit preferred, 64-bit requires workarounds)

---

## Before You Start

### **Locate Injector Correction Codes**
Each injector has a unique 6-character code laser-etched on the injector body.

**Code format:**
- 6 characters: Letters and numbers
- Example: `4A2B01`, `8D3F12`
- Usually on the side of injector body (hard to see once installed)

**CRITICAL:** Write down each code BEFORE installing injectors and note which cylinder it goes into.

**If you forgot to record codes:**
- Must remove injectors again to read codes
- No workaround - DME needs exact codes

---

## Setup INPA Connection

### **Step 1: Connect Hardware**
1. Plug INPA cable into vehicle OBD port (under steering column)
2. Connect cable to laptop USB
3. Turn ignition to position 2 (dash lights on, engine OFF)
4. **Do not start engine during coding**

### **Step 2: Install Drivers** (if first time)
1. Install FTDI drivers for K+DCAN cable
2. Confirm cable is detected in Device Manager (should show as COM port)
3. Note COM port number (e.g., COM3)

### **Step 3: Configure EDIABAS**
1. Open EDIABAS configuration tool
2. Set interface to K+DCAN
3. Set COM port to match Device Manager
4. Test connection (should communicate with vehicle)

---

## Injector Coding Procedure

### **N54 Engine (Twin Turbo 6-cylinder)**

**Step 1: Launch INPA**
1. Open INPA software
2. Click "F5" or select "Identify Vehicle"
3. INPA will auto-detect vehicle VIN and modules
4. Wait for identification to complete

**Step 2: Select DME Module**
1. Once identified, select "DME / DDE" from module list
2. Click to enter DME diagnostics

**Step 3: Access Job Menu**
1. Press "F6" or click "Job" button
2. Wait for job list to load

**Step 4: Select Test Plan**
1. Press "F3" or select "Test Plan"
2. Scroll through list to find "Injector Programming" or "Injector Correction Codes"
   - May be listed as "Injektor Programmierung" (German)
   - Or "Correction Code Programming"

**Step 5: Enter Coding Mode**
1. Select "Injector Programming"
2. Click "Execute" or press Enter
3. Screen will show 6 fields (one for each cylinder)

**Step 6: Enter Injector Codes**
1. Cylinder 1 field: Enter code for injector in cylinder 1
2. Cylinder 2 field: Enter code for injector in cylinder 2
3. Continue for all 6 cylinders
4. **CRITICAL:** Verify each code is entered correctly
   - Wrong code = rough running
   - Transposed codes = uneven combustion

**Code entry format:**
- Enter exactly as written on injector
- Mix of letters (uppercase) and numbers
- No spaces or dashes
- Example: Type `4A2B01` not `4a2b01` or `4A-2B-01`

**Step 7: Execute Programming**
1. Verify all 6 codes are correct
2. Click "Program" or "Execute"
3. INPA will write codes to DME
4. Progress bar will show status
5. Wait for "Programming Successful" or "OK" message
6. **Do not turn off ignition during programming**

**Step 8: Exit and Verify**
1. Exit job menu
2. Turn ignition off
3. Wait 10 seconds
4. Turn ignition back to position 2
5. Re-enter INPA DME diagnostics
6. Re-open injector programming job
7. Verify codes are stored correctly (should display your entered codes)

---

## N52 Engine (Naturally Aspirated 6-cylinder)

**Procedure is similar to N54 with these differences:**

**Coding location:**
- Job → Test Plan → "Injector Correction Code Programming"
- May be under "Service Functions" instead of Test Plan

**Code format:**
- Same 6-character codes
- Same entry method

---

## N55 Engine (Single Turbo 6-cylinder)

**Same as N54 procedure**
- Uses same DME software interface
- 6 injector codes required

---

## 4-Cylinder Engines (N20, N26, B48)

**Differences:**
- Only 4 injector codes to enter (not 6)
- Otherwise same procedure

---

## V8 Engines (N63, S63)

**Differences:**
- 8 injector codes to enter
- DME may show 2 banks separately
- Some models require coding each bank individually

---

## Troubleshooting

### **INPA Won't Connect**
**Symptoms:**
- "Interface not found"
- "No response from vehicle"

**Solutions:**
1. Check COM port in EDIABAS matches Device Manager
2. Turn ignition to position 2 (not ACC, not ON)
3. Check OBD port fuses (fuse 38 on most BMWs)
4. Try different USB port on laptop
5. Reinstall FTDI drivers
6. Cable may be faulty - test with known-good cable

### **Can't Find Injector Programming Job**
**Symptoms:**
- Job menu doesn't show injector programming

**Solutions:**
1. Update INPA to 5.0.2 or newer
2. Some vehicles require ISTA+ instead of INPA (2012+ models)
3. Try different DME variant in INPA (some have multiple options)
4. Check if vehicle uses DDE (diesel) instead of DME

### **Programming Failed Error**
**Symptoms:**
- "Programming Error"
- "Write Failed"

**Solutions:**
1. Check battery voltage (must be >12.5V, ideally 13+ with charger)
2. Turn off all accessories (radio, lights, climate control)
3. Disconnect battery, wait 5 min, reconnect, retry
4. Cable communication issue - check cable connection

### **Codes Won't Save**
**Symptoms:**
- Enter codes, programming says OK, but codes are gone when checking again

**Solutions:**
1. Battery voltage too low during programming
2. May need to clear DME adaptation first (Job → Delete Adaptations)
3. Retry programming with battery charger connected

---

## After Coding

### **Step 1: Clear Fault Codes**
1. In INPA DME diagnostics
2. Press "F4" or select "Fault Codes"
3. Read and note any stored codes
4. Delete all codes
5. Exit INPA

### **Step 2: Start Engine**
1. Turn ignition off, wait 5 seconds
2. Start engine
3. Engine may run slightly rough for first 10-30 seconds (normal - DME is learning)
4. Idle should smooth out quickly

### **Step 3: Test Drive**
1. Drive vehicle normally for 10-15 minutes
2. Include some acceleration (DME needs to learn under load)
3. Check for smooth idle, good throttle response
4. No misfires or hesitation

### **Step 4: Verify No Codes**
1. Re-connect INPA
2. Read fault codes
3. Should be clear (no misfire codes)
4. If codes return → verify injector codes were entered correctly

---

## Alternative: Using ISTA+

**For 2012+ BMW models**, ISTA+ may be required instead of INPA.

**Procedure:**
1. Open ISTA+
2. Identify vehicle
3. Service Functions → Engine → Replace Components → Fuel Injector
4. Follow on-screen prompts
5. Enter injector codes when prompted
6. ISTA+ will automatically program DME

**Advantages of ISTA+:**
- More user-friendly interface
- Automatically detects which injectors were replaced
- Guides you through process

**Disadvantages:**
- Requires higher-end interface (ICOM)
- Software is larger and more complex
- Slower than INPA

---

## Common Mistakes

1. **Not recording injector codes before installation**
   - Solution: Must remove injectors to read codes

2. **Entering codes in wrong order**
   - Solution: Cylinder 1 is front of engine (closest to radiator)

3. **Typing lowercase instead of uppercase**
   - INPA may accept it but could cause issues
   - Always use uppercase

4. **Not waiting for programming to complete**
   - Turning off ignition mid-programming can corrupt DME
   - Wait for "OK" message

5. **Programming with low battery voltage**
   - DME programming requires stable 12.5V+
   - Use battery charger

6. **Using INPA on 2015+ models**
   - Newer models may require ISTA+ only
   - INPA won't have option for these DME versions

---

## Required Hardware/Software Summary

### **Minimum Setup:**
- Windows laptop (Windows 7 32-bit ideal)
- INPA K+DCAN cable ($20-50 on Amazon)
- INPA software (free download)
- EDIABAS configured
- 1-2 hours to set up first time

### **Professional Setup:**
- Windows laptop or tablet
- BMW ICOM interface ($200+ genuine, $50-100 clone)
- ISTA+ software (download from BMW repositories)
- Faster and more reliable

### **Dealer:**
- Have dealer code injectors: $150-300
- Bring list of injector codes and cylinder locations
- 30 minutes at dealer

---

## Time Estimates

**First time (including INPA setup):** 2-3 hours
**Subsequent times:** 15-30 minutes
**Dealer:** 30 minutes + drive time

---

## Metadata
```json
{
  "procedure": "injector_coding",
  "software": "INPA",
  "manufacturer": "BMW",
  "affected_engines": ["N52", "N54", "N55", "S65", "N63", "N20", "B48"],
  "difficulty": "intermediate",
  "time_estimate": "15-30 minutes after setup",
  "required_hardware": "K+DCAN cable or ICOM",
  "alternatives": "ISTA+ or dealer coding"
}
```
