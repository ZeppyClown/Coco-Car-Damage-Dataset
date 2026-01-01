"""
Comprehensive OBD-II Fault Code Database
Contains detailed information about diagnostic trouble codes (DTCs)
"""

FAULT_CODE_DATABASE = {
    # Powertrain Codes (P0xxx)
    "P0420": {
        "description": "Catalyst System Efficiency Below Threshold (Bank 1)",
        "system": "engine",
        "severity": "moderate",
        "explanation": "The catalytic converter on Bank 1 is not operating efficiently. The ECU monitors catalyst efficiency by comparing upstream and downstream oxygen sensor readings. When the readings are too similar, it indicates the catalyst isn't converting emissions properly.",
        "common_causes": [
            {
                "cause": "Failing catalytic converter",
                "probability": 0.65,
                "explanation": "Most common cause. Catalysts degrade over time, especially on high-mileage vehicles or those using leaded fuel.",
                "typical_mileage": "80,000+ miles",
                "cost_estimate": {"min": 800, "max": 2500, "currency": "SGD"}
            },
            {
                "cause": "Faulty downstream oxygen sensor",
                "probability": 0.20,
                "explanation": "O2 sensor failure can send incorrect readings, triggering false catalyst efficiency codes.",
                "cost_estimate": {"min": 150, "max": 400, "currency": "SGD"}
            },
            {
                "cause": "Exhaust leak before catalyst",
                "probability": 0.10,
                "explanation": "Leaks allow unmetered air into exhaust, affecting O2 sensor readings.",
                "cost_estimate": {"min": 100, "max": 500, "currency": "SGD"}
            },
            {
                "cause": "Engine running rich/lean",
                "probability": 0.05,
                "explanation": "Fuel mixture problems can damage catalyst or trigger false codes.",
                "cost_estimate": {"min": 200, "max": 800, "currency": "SGD"}
            }
        ],
        "diagnostic_steps": [
            {
                "step": 1,
                "action": "Connect OBD-II scanner and verify code",
                "explanation": "Confirm P0420 is present and note if there are related codes (P0430, P0171, etc.)",
                "tools_needed": ["OBD-II scanner with live data capability"],
                "estimated_time": "5 minutes"
            },
            {
                "step": 2,
                "action": "Check for exhaust leaks",
                "explanation": "Visually and audibly inspect exhaust system from manifold to tailpipe while engine running",
                "tools_needed": ["Vehicle lift or jack stands"],
                "estimated_time": "15 minutes"
            },
            {
                "step": 3,
                "action": "Monitor oxygen sensor data",
                "explanation": "With scanner, watch upstream (before cat) and downstream (after cat) O2 sensor readings. Downstream should be stable and different from upstream. If they mirror each other, catalyst is failing.",
                "tools_needed": ["OBD-II scanner with live graphing"],
                "estimated_time": "10 minutes",
                "expected_values": {
                    "upstream_o2": "Fluctuating 0.1-0.9V",
                    "downstream_o2": "Stable around 0.45V",
                    "failing_pattern": "Both sensors fluctuating similarly"
                }
            },
            {
                "step": 4,
                "action": "Perform catalyst temperature test",
                "explanation": "Use infrared thermometer to measure catalyst inlet vs outlet temperature. Working catalyst should have outlet 50-100°F hotter.",
                "tools_needed": ["Infrared thermometer"],
                "estimated_time": "10 minutes"
            }
        ],
        "parts_needed": [
            {"part": "Catalytic Converter", "typical_cost": 1200, "oem_recommended": True},
            {"part": "Downstream Oxygen Sensor", "typical_cost": 180, "oem_recommended": False},
            {"part": "Exhaust Gaskets", "typical_cost": 30, "oem_recommended": False}
        ],
        "immediate_safety": {
            "driveable": True,
            "explanation": "Vehicle is safe to drive short distances, but should be repaired soon to avoid further damage and ensure emissions compliance.",
            "risks": ["Reduced fuel economy", "Failed emissions test", "Possible engine damage if running rich/lean"]
        },
        "diy_feasibility": {
            "diagnosis": "moderate",
            "repair": "difficult",
            "explanation": "Diagnosis is possible with proper scan tool. Repair requires exhaust system work, which is difficult for DIY due to rusted bolts and need for proper exhaust support."
        },
        "prevention": "Regular maintenance, use quality fuel, avoid short trips that don't let catalyst reach operating temperature"
    },

    "P0300": {
        "description": "Random/Multiple Cylinder Misfire Detected",
        "system": "engine",
        "severity": "high",
        "explanation": "The engine control unit has detected misfires occurring randomly across multiple cylinders. Misfires indicate incomplete combustion, which can damage the catalytic converter and cause poor performance.",
        "common_causes": [
            {
                "cause": "Worn spark plugs",
                "probability": 0.40,
                "explanation": "Most common cause of random misfires. Spark plugs wear over time, causing weak or inconsistent spark.",
                "typical_mileage": "30,000+ miles",
                "cost_estimate": {"min": 80, "max": 300, "currency": "SGD"}
            },
            {
                "cause": "Failing ignition coils",
                "probability": 0.25,
                "explanation": "Coils weaken with age and heat cycling, causing intermittent misfires.",
                "cost_estimate": {"min": 150, "max": 600, "currency": "SGD"}
            },
            {
                "cause": "Vacuum leak",
                "probability": 0.15,
                "explanation": "Unmetered air entering intake causes lean condition and misfires.",
                "cost_estimate": {"min": 50, "max": 400, "currency": "SGD"}
            },
            {
                "cause": "Low fuel pressure",
                "probability": 0.10,
                "explanation": "Weak fuel pump or clogged filter causes insufficient fuel delivery.",
                "cost_estimate": {"min": 200, "max": 800, "currency": "SGD"}
            },
            {
                "cause": "Compression loss",
                "probability": 0.10,
                "explanation": "Worn piston rings, valves, or head gasket causing low compression.",
                "cost_estimate": {"min": 1500, "max": 5000, "currency": "SGD"}
            }
        ],
        "diagnostic_steps": [
            {
                "step": 1,
                "action": "Scan for additional codes",
                "explanation": "Check for P030X codes (where X = specific cylinder) to identify which cylinders are misfiring",
                "tools_needed": ["OBD-II scanner"],
                "estimated_time": "5 minutes"
            },
            {
                "step": 2,
                "action": "Inspect spark plugs",
                "explanation": "Remove and examine plugs for wear, carbon buildup, or damage. Check gap with feeler gauge.",
                "tools_needed": ["Spark plug socket", "Feeler gauge"],
                "estimated_time": "30 minutes"
            },
            {
                "step": 3,
                "action": "Check for vacuum leaks",
                "explanation": "Inspect all vacuum hoses and intake manifold gaskets. Can use smoke test or propane enrichment method.",
                "tools_needed": ["Smoke machine (optional)"],
                "estimated_time": "20 minutes"
            },
            {
                "step": 4,
                "action": "Test ignition coils",
                "explanation": "Swap coils between cylinders and see if misfire follows the coil",
                "tools_needed": ["Basic hand tools"],
                "estimated_time": "20 minutes"
            },
            {
                "step": 5,
                "action": "Compression test",
                "explanation": "If above steps don't reveal issue, perform compression test on all cylinders",
                "tools_needed": ["Compression tester"],
                "estimated_time": "45 minutes"
            }
        ],
        "parts_needed": [
            {"part": "Spark Plugs (set)", "typical_cost": 60, "oem_recommended": True},
            {"part": "Ignition Coils", "typical_cost": 400, "oem_recommended": False},
            {"part": "Vacuum Hoses", "typical_cost": 40, "oem_recommended": False}
        ],
        "immediate_safety": {
            "driveable": False,
            "explanation": "Random misfires can damage the catalytic converter and cause sudden loss of power. Avoid driving until diagnosed and repaired.",
            "risks": ["Catalytic converter damage ($1000+)", "Poor fuel economy", "Engine damage", "Stalling in traffic"]
        },
        "diy_feasibility": {
            "diagnosis": "moderate",
            "repair": "easy to difficult",
            "explanation": "Spark plug replacement is DIY-friendly. Other causes may require professional diagnosis and repair."
        }
    },

    "P0171": {
        "description": "System Too Lean (Bank 1)",
        "system": "engine",
        "severity": "moderate",
        "explanation": "The engine is running with too much air or too little fuel on Bank 1. The ECU tries to compensate by adding fuel, but the mixture is still too lean.",
        "common_causes": [
            {
                "cause": "Vacuum leak",
                "probability": 0.45,
                "explanation": "Most common cause. Unmetered air entering after the mass airflow sensor causes lean condition.",
                "cost_estimate": {"min": 50, "max": 400, "currency": "SGD"}
            },
            {
                "cause": "Dirty or failing MAF sensor",
                "probability": 0.25,
                "explanation": "Mass airflow sensor not accurately measuring intake air, causing incorrect fuel calculations.",
                "cost_estimate": {"min": 100, "max": 450, "currency": "SGD"}
            },
            {
                "cause": "Weak fuel pump or clogged fuel filter",
                "probability": 0.15,
                "explanation": "Insufficient fuel pressure prevents proper fuel delivery.",
                "cost_estimate": {"min": 150, "max": 800, "currency": "SGD"}
            },
            {
                "cause": "Exhaust leak before O2 sensor",
                "probability": 0.10,
                "explanation": "Exhaust leaks allow oxygen into exhaust stream, fooling O2 sensor.",
                "cost_estimate": {"min": 100, "max": 500, "currency": "SGD"}
            },
            {
                "cause": "Faulty PCV valve or hose",
                "probability": 0.05,
                "explanation": "PCV system allowing excess air into intake.",
                "cost_estimate": {"min": 30, "max": 150, "currency": "SGD"}
            }
        ],
        "diagnostic_steps": [
            {
                "step": 1,
                "action": "Check fuel trims",
                "explanation": "Use scanner to monitor short-term and long-term fuel trims. Values above +25% confirm lean condition.",
                "tools_needed": ["OBD-II scanner with live data"],
                "estimated_time": "10 minutes"
            },
            {
                "step": 2,
                "action": "Inspect for vacuum leaks",
                "explanation": "Listen for hissing sounds, check all vacuum hoses, intake manifold gaskets, brake booster line.",
                "tools_needed": ["Smoke machine (optional)", "Propane torch (enrichment test)"],
                "estimated_time": "30 minutes"
            },
            {
                "step": 3,
                "action": "Check MAF sensor",
                "explanation": "Clean MAF sensor with MAF cleaner. Test with multimeter or compare readings to specifications.",
                "tools_needed": ["MAF cleaner", "Multimeter"],
                "estimated_time": "15 minutes"
            },
            {
                "step": 4,
                "action": "Test fuel pressure",
                "explanation": "Connect fuel pressure gauge and verify pressure meets specifications (typically 40-60 PSI).",
                "tools_needed": ["Fuel pressure gauge"],
                "estimated_time": "20 minutes"
            }
        ],
        "parts_needed": [
            {"part": "Vacuum Hoses", "typical_cost": 40, "oem_recommended": False},
            {"part": "Intake Manifold Gasket", "typical_cost": 120, "oem_recommended": True},
            {"part": "MAF Sensor", "typical_cost": 250, "oem_recommended": True},
            {"part": "PCV Valve", "typical_cost": 25, "oem_recommended": False}
        ],
        "immediate_safety": {
            "driveable": True,
            "explanation": "Vehicle can be driven, but may experience reduced performance and fuel economy. Repair soon to prevent damage.",
            "risks": ["Poor fuel economy", "Rough idle", "Possible engine damage from lean operation"]
        },
        "diy_feasibility": {
            "diagnosis": "moderate",
            "repair": "easy to moderate",
            "explanation": "Finding vacuum leaks requires patience. Fixes range from simple (replace hose) to moderate (intake manifold gasket)."
        }
    },

    "P0128": {
        "description": "Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)",
        "system": "engine",
        "severity": "low",
        "explanation": "The engine is not reaching proper operating temperature, or is taking too long to warm up. This is usually caused by a stuck-open thermostat.",
        "common_causes": [
            {
                "cause": "Stuck-open thermostat",
                "probability": 0.85,
                "explanation": "Thermostat fails in open position, preventing engine from reaching operating temperature.",
                "cost_estimate": {"min": 80, "max": 300, "currency": "SGD"}
            },
            {
                "cause": "Faulty coolant temperature sensor",
                "probability": 0.10,
                "explanation": "Sensor sending incorrect temperature readings to ECU.",
                "cost_estimate": {"min": 50, "max": 200, "currency": "SGD"}
            },
            {
                "cause": "Low coolant level",
                "probability": 0.05,
                "explanation": "Insufficient coolant prevents accurate temperature regulation.",
                "cost_estimate": {"min": 10, "max": 50, "currency": "SGD"}
            }
        ],
        "diagnostic_steps": [
            {
                "step": 1,
                "action": "Monitor coolant temperature",
                "explanation": "Use scanner to watch coolant temp during warm-up. Should reach 180-200°F within 10 minutes.",
                "tools_needed": ["OBD-II scanner"],
                "estimated_time": "15 minutes"
            },
            {
                "step": 2,
                "action": "Feel radiator hoses",
                "explanation": "Upper hose should be hot, lower hose cooler if thermostat working. If both warm early, thermostat stuck open.",
                "tools_needed": ["None"],
                "estimated_time": "10 minutes"
            },
            {
                "step": 3,
                "action": "Check coolant level",
                "explanation": "Verify coolant is at proper level in reservoir and radiator (when cold).",
                "tools_needed": ["None"],
                "estimated_time": "5 minutes"
            }
        ],
        "parts_needed": [
            {"part": "Thermostat", "typical_cost": 45, "oem_recommended": True},
            {"part": "Thermostat Gasket/O-ring", "typical_cost": 15, "oem_recommended": True},
            {"part": "Coolant", "typical_cost": 25, "oem_recommended": False}
        ],
        "immediate_safety": {
            "driveable": True,
            "explanation": "Safe to drive. Main issues are reduced fuel economy and poor heater performance in cold weather.",
            "risks": ["Reduced fuel economy", "Poor cabin heating", "Increased emissions", "Reduced engine longevity"]
        },
        "diy_feasibility": {
            "diagnosis": "easy",
            "repair": "moderate",
            "explanation": "Thermostat replacement is a common DIY job. Requires draining coolant and accessing thermostat housing."
        }
    },

    "P0441": {
        "description": "Evaporative Emission Control System Incorrect Purge Flow",
        "system": "evap",
        "severity": "low",
        "explanation": "The EVAP system, which captures fuel vapors from the tank, is not flowing correctly. Usually not affecting drivability but will cause emissions test failure.",
        "common_causes": [
            {
                "cause": "Faulty purge valve",
                "probability": 0.50,
                "explanation": "Purge solenoid stuck open or closed, preventing proper vapor control.",
                "cost_estimate": {"min": 80, "max": 250, "currency": "SGD"}
            },
            {
                "cause": "Loose or damaged gas cap",
                "probability": 0.25,
                "explanation": "Gas cap not sealing properly, allowing vapors to escape.",
                "cost_estimate": {"min": 15, "max": 40, "currency": "SGD"}
            },
            {
                "cause": "EVAP system leak",
                "probability": 0.15,
                "explanation": "Crack in EVAP hoses or canister allowing vapor leaks.",
                "cost_estimate": {"min": 100, "max": 600, "currency": "SGD"}
            },
            {
                "cause": "Faulty vent valve",
                "probability": 0.10,
                "explanation": "Vent solenoid not operating correctly.",
                "cost_estimate": {"min": 100, "max": 300, "currency": "SGD"}
            }
        ],
        "diagnostic_steps": [
            {
                "step": 1,
                "action": "Check gas cap",
                "explanation": "Remove and inspect gas cap for damage. Ensure it clicks 3 times when tightening. Clear code and see if it returns.",
                "tools_needed": ["None"],
                "estimated_time": "5 minutes"
            },
            {
                "step": 2,
                "action": "Perform EVAP smoke test",
                "explanation": "Introduce smoke into EVAP system to locate leaks. Professional shops have smoke machines.",
                "tools_needed": ["EVAP smoke machine"],
                "estimated_time": "30 minutes"
            },
            {
                "step": 3,
                "action": "Test purge valve",
                "explanation": "Remove purge valve and test operation. Should be closed at rest, open when 12V applied.",
                "tools_needed": ["Multimeter", "12V power source"],
                "estimated_time": "20 minutes"
            }
        ],
        "parts_needed": [
            {"part": "Purge Valve", "typical_cost": 120, "oem_recommended": True},
            {"part": "Gas Cap", "typical_cost": 25, "oem_recommended": True},
            {"part": "EVAP Hoses", "typical_cost": 80, "oem_recommended": False}
        ],
        "immediate_safety": {
            "driveable": True,
            "explanation": "Completely safe to drive. No performance impact. Main concern is emissions test failure.",
            "risks": ["Failed emissions test", "Slight fuel vapor odor", "Minor fuel economy reduction"]
        },
        "diy_feasibility": {
            "diagnosis": "moderate",
            "repair": "easy to moderate",
            "explanation": "Gas cap replacement is easy. Finding EVAP leaks can be challenging without smoke machine."
        }
    }
}

# System categories for routing
SYSTEM_CATEGORIES = {
    "engine": ["powertrain", "fuel system", "ignition"],
    "transmission": ["drivetrain", "clutch", "torque converter"],
    "brakes": ["ABS", "brake system", "traction control"],
    "suspension": ["steering", "wheels", "alignment"],
    "electrical": ["battery", "charging", "lights"],
    "evap": ["emissions", "fuel vapor"],
    "cooling": ["radiator", "thermostat", "fan"],
    "exhaust": ["catalyst", "oxygen sensors", "EGR"]
}

def get_fault_code_info(code: str) -> dict:
    """Retrieve fault code information from database"""
    return FAULT_CODE_DATABASE.get(code.upper())

def search_fault_codes_by_system(system: str) -> list:
    """Find fault codes related to a specific system"""
    results = []
    for code, info in FAULT_CODE_DATABASE.items():
        if info.get("system") == system.lower():
            results.append({"code": code, **info})
    return results
