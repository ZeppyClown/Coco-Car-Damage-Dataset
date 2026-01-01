#!/usr/bin/env python
"""Seed database with sample data"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.models import Part, Vehicle, Specification, PartCompatibility, PaintCode, FaultCode
from sqlalchemy.exc import IntegrityError


def seed_vehicles():
    """Seed sample vehicles"""
    print("Seeding vehicles...")
    db = SessionLocal()

    vehicles = [
        Vehicle(vin="1HGBH41JXMN109186", make="Honda", model="Civic", year=2015, trim="LX"),
        Vehicle(vin="1FTFW1ET5BFC10312", make="Ford", model="F-150", year=2018, trim="XLT"),
        Vehicle(vin="5YFBURHE5HP588522", make="Toyota", model="Corolla", year=2017, trim="LE"),
        Vehicle(vin="3VWDX7AJ9CM632919", make="Volkswagen", model="Jetta", year=2012, trim="SE"),
        Vehicle(vin="1N4AL3AP8JC231472", make="Nissan", model="Altima", year=2018, trim="S"),
        Vehicle(make="BMW", model="3 Series", year=2020, trim="330i"),
        Vehicle(make="Mercedes-Benz", model="C-Class", year=2019, trim="C300"),
        Vehicle(make="Audi", model="A4", year=2021, trim="Premium"),
        Vehicle(make="Chevrolet", model="Silverado", year=2020, trim="LT"),
        Vehicle(make="Tesla", model="Model 3", year=2022, trim="Long Range"),
    ]

    try:
        for vehicle in vehicles:
            db.add(vehicle)
        db.commit()
        print(f"✓ Seeded {len(vehicles)} vehicles")
    except IntegrityError:
        db.rollback()
        print("! Vehicles already exist, skipping...")
    finally:
        db.close()


def seed_specifications():
    """Seed sample specifications"""
    print("Seeding specifications...")
    db = SessionLocal()

    # Get a sample vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.make == "Honda", Vehicle.model == "Civic").first()

    if vehicle:
        specs = [
            Specification(vehicle_id=vehicle.id, spec_type="engine", spec_key="type", spec_value="1.8L 4-Cylinder"),
            Specification(vehicle_id=vehicle.id, spec_type="engine", spec_key="horsepower", spec_value="143 hp"),
            Specification(vehicle_id=vehicle.id, spec_type="engine", spec_key="torque", spec_value="129 lb-ft"),
            Specification(vehicle_id=vehicle.id, spec_type="transmission", spec_key="type", spec_value="CVT Automatic"),
            Specification(vehicle_id=vehicle.id, spec_type="fuel", spec_key="city_mpg", spec_value="30"),
            Specification(vehicle_id=vehicle.id, spec_type="fuel", spec_key="highway_mpg", spec_value="39"),
            Specification(vehicle_id=vehicle.id, spec_type="dimensions", spec_key="length", spec_value="182.3 in"),
            Specification(vehicle_id=vehicle.id, spec_type="dimensions", spec_key="width", spec_value="70.8 in"),
            Specification(vehicle_id=vehicle.id, spec_type="dimensions", spec_key="height", spec_value="55.7 in"),
            Specification(vehicle_id=vehicle.id, spec_type="capacity", spec_key="fuel_tank", spec_value="12.4 gal"),
            Specification(vehicle_id=vehicle.id, spec_type="capacity", spec_key="seating", spec_value="5"),
        ]

        try:
            for spec in specs:
                db.add(spec)
            db.commit()
            print(f"✓ Seeded {len(specs)} specifications")
        except IntegrityError:
            db.rollback()
            print("! Specifications already exist, skipping...")
    else:
        print("! No Honda Civic found, skipping specifications")

    db.close()


def seed_parts():
    """Seed sample parts"""
    print("Seeding parts...")
    db = SessionLocal()

    parts = [
        Part(part_number="BRK-FP-001", name="Front Brake Pad Set", description="Ceramic brake pads for front axle", category="Brakes", oem=False),
        Part(part_number="BRK-RP-001", name="Rear Brake Pad Set", description="Ceramic brake pads for rear axle", category="Brakes", oem=False),
        Part(part_number="BRK-FR-001", name="Front Brake Rotor", description="Ventilated front brake rotor", category="Brakes", oem=False),
        Part(part_number="BRK-RR-001", name="Rear Brake Rotor", description="Solid rear brake rotor", category="Brakes", oem=False),
        Part(part_number="OIL-FILTER-001", name="Oil Filter", description="Standard oil filter", category="Filters", oem=False),
        Part(part_number="AIR-FILTER-001", name="Air Filter", description="Engine air filter", category="Filters", oem=False),
        Part(part_number="CABIN-FILTER-001", name="Cabin Air Filter", description="HVAC cabin filter", category="Filters", oem=False),
        Part(part_number="SPARK-PLUG-001", name="Spark Plug Set", description="Iridium spark plugs (set of 4)", category="Ignition", oem=False),
        Part(part_number="WIPER-BLADE-001", name="Wiper Blade Set", description="Front wiper blades (pair)", category="Wipers", oem=False),
        Part(part_number="BATTERY-001", name="Car Battery", description="12V automotive battery", category="Electrical", oem=False),
        Part(part_number="ALTERNATOR-001", name="Alternator", description="Remanufactured alternator", category="Electrical", oem=False),
        Part(part_number="STARTER-001", name="Starter Motor", description="Remanufactured starter", category="Electrical", oem=False),
        Part(part_number="STRUT-F-001", name="Front Strut Assembly", description="Complete strut assembly with mount", category="Suspension", oem=False),
        Part(part_number="SHOCK-R-001", name="Rear Shock Absorber", description="Gas-charged shock absorber", category="Suspension", oem=False),
        Part(part_number="TIRE-001", name="All-Season Tire 215/45R17", description="All-season radial tire", category="Tires", oem=False),
    ]

    try:
        for part in parts:
            db.add(part)
        db.commit()
        print(f"✓ Seeded {len(parts)} parts")
    except IntegrityError:
        db.rollback()
        print("! Parts already exist, skipping...")
    finally:
        db.close()


def seed_part_compatibility():
    """Seed part compatibility data"""
    print("Seeding part compatibility...")
    db = SessionLocal()

    # Get sample parts and vehicles
    civic = db.query(Vehicle).filter(Vehicle.make == "Honda", Vehicle.model == "Civic").first()
    brake_pads = db.query(Part).filter(Part.part_number == "BRK-FP-001").first()

    if civic and brake_pads:
        compatibility = PartCompatibility(
            part_id=brake_pads.id,
            vehicle_id=civic.id,
            compatible=True,
            notes="Direct fit for 2015 Honda Civic LX/EX/Touring"
        )

        try:
            db.add(compatibility)
            db.commit()
            print("✓ Seeded part compatibility")
        except IntegrityError:
            db.rollback()
            print("! Compatibility already exists, skipping...")
    else:
        print("! Required parts/vehicles not found, skipping compatibility")

    db.close()


def seed_paint_codes():
    """Seed paint codes"""
    print("Seeding paint codes...")
    db = SessionLocal()

    paint_codes = [
        PaintCode(manufacturer="Honda", paint_code="NH-731P", color_name="Crystal Black Pearl", year_start=2010, year_end=2023),
        PaintCode(manufacturer="Honda", paint_code="NH-788P", color_name="Modern Steel Metallic", year_start=2015, year_end=2023),
        PaintCode(manufacturer="Honda", paint_code="R-81", color_name="Milano Red", year_start=2012, year_end=2023),
        PaintCode(manufacturer="Toyota", paint_code="040", color_name="Super White", year_start=2010, year_end=2023),
        PaintCode(manufacturer="Toyota", paint_code="1G3", color_name="Magnetic Gray Metallic", year_start=2015, year_end=2023),
        PaintCode(manufacturer="Ford", paint_code="J7", color_name="Magnetic", year_start=2018, year_end=2023),
        PaintCode(manufacturer="Ford", paint_code="UM", color_name="Agate Black", year_start=2015, year_end=2023),
        PaintCode(manufacturer="BMW", paint_code="300", color_name="Alpine White", year_start=2010, year_end=2023),
        PaintCode(manufacturer="BMW", paint_code="416", color_name="Carbon Black Metallic", year_start=2015, year_end=2023),
        PaintCode(manufacturer="Tesla", paint_code="PBSB", color_name="Pearl White Multi-Coat", year_start=2019, year_end=2023),
    ]

    try:
        for paint_code in paint_codes:
            db.add(paint_code)
        db.commit()
        print(f"✓ Seeded {len(paint_codes)} paint codes")
    except IntegrityError:
        db.rollback()
        print("! Paint codes already exist, skipping...")
    finally:
        db.close()


def seed_fault_codes():
    """Seed diagnostic fault codes"""
    print("Seeding fault codes...")
    db = SessionLocal()

    fault_codes = [
        FaultCode(code="P0300", system="engine", description="Random/Multiple Cylinder Misfire Detected", severity="high"),
        FaultCode(code="P0420", system="emissions", description="Catalyst System Efficiency Below Threshold", severity="medium"),
        FaultCode(code="P0171", system="engine", description="System Too Lean (Bank 1)", severity="medium"),
        FaultCode(code="P0172", system="engine", description="System Too Rich (Bank 1)", severity="medium"),
        FaultCode(code="P0455", system="emissions", description="Evaporative Emission System Leak Detected (Large Leak)", severity="medium"),
        FaultCode(code="P0442", system="emissions", description="Evaporative Emission System Leak Detected (Small Leak)", severity="low"),
        FaultCode(code="P0128", system="cooling", description="Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)", severity="low"),
        FaultCode(code="P0401", system="emissions", description="Exhaust Gas Recirculation (EGR) Flow Insufficient", severity="medium"),
        FaultCode(code="P0715", system="transmission", description="Input/Turbine Speed Sensor Circuit Malfunction", severity="high"),
        FaultCode(code="P0720", system="transmission", description="Output Speed Sensor Circuit Malfunction", severity="high"),
        FaultCode(code="P0700", system="transmission", description="Transmission Control System Malfunction", severity="high"),
        FaultCode(code="C1201", system="abs", description="Engine Control System Malfunction", severity="high"),
        FaultCode(code="C0035", system="abs", description="Left Front Wheel Speed Sensor Circuit Malfunction", severity="medium"),
        FaultCode(code="B1342", system="electrical", description="ECU Is Defective", severity="critical"),
        FaultCode(code="U0100", system="communication", description="Lost Communication With ECM/PCM", severity="critical"),
    ]

    try:
        for fault_code in fault_codes:
            db.add(fault_code)
        db.commit()
        print(f"✓ Seeded {len(fault_codes)} fault codes")
    except IntegrityError:
        db.rollback()
        print("! Fault codes already exist, skipping...")
    finally:
        db.close()


def main():
    """Main seeding function"""
    print("=" * 50)
    print("Database Seeding Script")
    print("=" * 50)

    seed_vehicles()
    seed_specifications()
    seed_parts()
    seed_part_compatibility()
    seed_paint_codes()
    seed_fault_codes()

    print("=" * 50)
    print("✓ Database seeding complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
