"""
Generate Synthetic Automotive Parts Database for Singapore Market

HYBRID SYSTEM: SYNTHETIC DATA - Can be removed when real APIs are active
This script generates realistic automotive parts data for testing and development

To remove synthetic data later:
    DELETE FROM parts_catalog WHERE data_source = 'synthetic';
    DELETE FROM part_prices WHERE part_id IN (
        SELECT id FROM parts_catalog WHERE data_source = 'synthetic'
    );
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import PartsCatalog, PartPrice, PartCompatibilityEnhanced
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Singapore Market Data
SINGAPORE_VEHICLE_MAKES = [
    "Toyota", "Honda", "Nissan", "Mazda", "Mitsubishi",
    "Hyundai", "Kia", "Volkswagen", "BMW", "Mercedes-Benz",
    "Audi", "Lexus", "Subaru", "Suzuki", "Perodua"
]

POPULAR_MODELS = {
    "Toyota": ["Corolla", "Camry", "Vios", "Altis", "Wish", "Sienta", "C-HR"],
    "Honda": ["Civic", "Accord", "Jazz", "CR-V", "HR-V", "City", "Odyssey"],
    "Nissan": ["Sunny", "Almera", "Sylphy", "Qashqai", "X-Trail", "Latio"],
    "Mazda": ["2", "3", "6", "CX-3", "CX-5", "CX-9"],
    "Mitsubishi": ["Lancer", "Attrage", "ASX", "Outlander"],
    "Hyundai": ["Avante", "Elantra", "Tucson", "i30", "Kona"],
    "Kia": ["Cerato", "Optima", "Sportage", "Picanto"],
    "Volkswagen": ["Golf", "Polo", "Jetta", "Passat", "Tiguan"],
    "BMW": ["3 Series", "5 Series", "X1", "X3", "X5"],
    "Mercedes-Benz": ["C-Class", "E-Class", "A-Class", "GLC"],
}

# Automotive Parts Categories (50+ categories)
PARTS_CATALOG = {
    "Brake System": {
        "parts": [
            "Brake Pad Set (Front)", "Brake Pad Set (Rear)",
            "Brake Disc Rotor (Front)", "Brake Disc Rotor (Rear)",
            "Brake Caliper (Front)", "Brake Caliper (Rear)",
            "Brake Master Cylinder", "Brake Fluid Reservoir",
            "Brake Line Kit", "Handbrake Cable", "Brake Booster",
            "ABS Sensor", "Brake Hose", "Wheel Cylinder"
        ],
        "price_range": (30, 800),
        "brands": ["Brembo", "Akebono", "Bosch", "TRW", "ATE", "OEM"]
    },
    "Engine": {
        "parts": [
            "Engine Oil Filter", "Air Filter", "Fuel Filter",
            "Spark Plug Set", "Ignition Coil", "Timing Belt",
            "Serpentine Belt", "Water Pump", "Thermostat",
            "Engine Mount", "Oil Pan Gasket", "Head Gasket",
            "Valve Cover Gasket", "Camshaft Sensor", "Crankshaft Sensor",
            "Oxygen Sensor", "MAF Sensor", "Throttle Body"
        ],
        "price_range": (15, 1200),
        "brands": ["Denso", "NGK", "Bosch", "Gates", "OEM", "Aisin"]
    },
    "Electrical": {
        "parts": [
            "Car Battery", "Alternator", "Starter Motor",
            "Headlight Bulb", "Tail Light Assembly", "Fog Light",
            "Turn Signal Bulb", "Wiper Motor", "Horn",
            "Fuse Box", "Relay", "Battery Terminal"
        ],
        "price_range": (10, 800),
        "brands": ["Bosch", "Amaron", "Denso", "Philips", "Osram", "OEM"]
    },
    "Suspension": {
        "parts": [
            "Shock Absorber (Front)", "Shock Absorber (Rear)",
            "Strut Assembly (Front)", "Strut Assembly (Rear)",
            "Ball Joint", "Control Arm", "Tie Rod End",
            "Stabilizer Link", "Coil Spring", "Bushing Kit",
            "Wheel Bearing", "Sway Bar"
        ],
        "price_range": (40, 900),
        "brands": ["Monroe", "KYB", "Bilstein", "Sachs", "OEM"]
    },
    "Transmission": {
        "parts": [
            "Transmission Fluid", "Transmission Filter",
            "Clutch Kit", "Clutch Disc", "Pressure Plate",
            "Flywheel", "CV Joint", "CV Boot", "Driveshaft",
            "Transmission Mount", "Gear Oil"
        ],
        "price_range": (25, 1500),
        "brands": ["Exedy", "Sachs", "LUK", "OEM", "Aisin"]
    },
    "HVAC": {
        "parts": [
            "AC Compressor", "AC Condenser", "AC Evaporator",
            "Cabin Air Filter", "Blower Motor", "AC Expansion Valve",
            "AC Pressure Switch", "Heater Core", "AC Hose"
        ],
        "price_range": (20, 1200),
        "brands": ["Denso", "Sanden", "Valeo", "Delphi", "OEM"]
    },
    "Exhaust System": {
        "parts": [
            "Muffler", "Catalytic Converter", "Exhaust Manifold",
            "Exhaust Pipe", "Resonator", "Exhaust Gasket",
            "O2 Sensor", "EGR Valve"
        ],
        "price_range": (50, 2000),
        "brands": ["Walker", "Magnaflow", "Bosal", "OEM"]
    },
    "Fuel System": {
        "parts": [
            "Fuel Pump", "Fuel Injector", "Fuel Pressure Regulator",
            "Fuel Tank Cap", "Fuel Line", "Fuel Filter"
        ],
        "price_range": (20, 800),
        "brands": ["Bosch", "Denso", "Delphi", "OEM", "Walbro"]
    },
    "Cooling System": {
        "parts": [
            "Radiator", "Radiator Hose", "Coolant Reservoir",
            "Radiator Cap", "Cooling Fan", "Temperature Sensor",
            "Thermostat Housing", "Radiator Fan Motor"
        ],
        "price_range": (25, 800),
        "brands": ["Denso", "Koyo", "Mishimoto", "OEM"]
    },
    "Lighting": {
        "parts": [
            "Headlight Assembly", "Tail Light Assembly",
            "LED Headlight Bulb", "Halogen Bulb", "HID Conversion Kit",
            "Corner Light", "License Plate Light", "Interior Light"
        ],
        "price_range": (10, 600),
        "brands": ["Philips", "Osram", "Sylvania", "OEM"]
    },
    "Wipers & Fluids": {
        "parts": [
            "Wiper Blade Set", "Rear Wiper Blade",
            "Windshield Washer Fluid", "Engine Oil (Synthetic)",
            "Engine Oil (Mineral)", "Brake Fluid", "Power Steering Fluid",
            "Coolant", "Transmission Fluid"
        ],
        "price_range": (8, 80),
        "brands": ["Bosch", "3M", "Castrol", "Mobil", "Shell", "Motul"]
    },
    "Body & Trim": {
        "parts": [
            "Side Mirror (Left)", "Side Mirror (Right)",
            "Door Handle", "Hood", "Trunk Lid", "Fender",
            "Bumper (Front)", "Bumper (Rear)", "Grille",
            "Mud Flap Set", "Weather Stripping", "Window Regulator"
        ],
        "price_range": (30, 1500),
        "brands": ["OEM", "Aftermarket"]
    }
}

# Singapore Sellers (Synthetic)
SINGAPORE_SELLERS = [
    {"name": "AutoParts SG", "rating": 4.8},
    {"name": "SG Motor Parts", "rating": 4.6},
    {"name": "CarHub Singapore", "rating": 4.7},
    {"name": "Parts Direct SG", "rating": 4.5},
    {"name": "Singapore Auto Supply", "rating": 4.9},
    {"name": "Fast Parts SG", "rating": 4.4},
    {"name": "Quality Auto Parts", "rating": 4.7},
    {"name": "SG Automart", "rating": 4.6},
]


def generate_part_number(category: str, brand: str, index: int) -> str:
    """Generate realistic part number"""
    category_code = category[:3].upper().replace(" ", "")
    brand_code = brand[:2].upper()
    return f"{brand_code}-{category_code}-{index:05d}"


def generate_synthetic_parts(db: Session, num_parts: int = 5000):
    """
    Generate synthetic parts database

    LABELED AS: data_source='synthetic'
    """
    logger.info(f"🔧 Generating {num_parts} synthetic parts for Singapore market...")
    logger.info("📌 All parts labeled with data_source='synthetic' for easy removal")

    parts_created = 0
    prices_created = 0
    compatibility_created = 0

    # Calculate parts per category
    categories = list(PARTS_CATALOG.keys())
    parts_per_category = num_parts // len(categories)

    for category, cat_data in PARTS_CATALOG.items():
        logger.info(f"Creating parts for category: {category}")

        parts_list = cat_data["parts"]
        brands = cat_data["brands"]
        price_min, price_max = cat_data["price_range"]

        # Generate parts for this category
        for i in range(parts_per_category):
            # Select random part and brand
            part_name = random.choice(parts_list)
            brand = random.choice(brands)
            is_oem = brand == "OEM"

            # Generate part data
            part_number = generate_part_number(category, brand, i)

            # Create description
            description = f"{brand} {part_name} for automotive use. "
            if is_oem:
                description += "Original Equipment Manufacturer (OEM) quality. "
            else:
                description += "Aftermarket replacement part. "
            description += f"Suitable for various {random.choice(SINGAPORE_VEHICLE_MAKES)} models."

            # Random price in SGD
            base_price = random.uniform(price_min, price_max)

            # Create part in catalog
            part = PartsCatalog(
                part_number=part_number,
                name=f"{brand} {part_name}",
                description=description,
                category=category,
                subcategory=part_name,
                brand=brand,
                oem_or_aftermarket="OEM" if is_oem else "Aftermarket",
                image_url=f"https://example.com/images/{part_number}.jpg",
                source="synthetic",
                source_id=f"SYNTH-{parts_created}",
                ships_to_singapore=True,
                data_source="synthetic",  # 🏷️ LABEL: Synthetic data marker
                retrieved_at=datetime.utcnow()
            )

            db.add(part)
            db.flush()  # Get the part ID
            parts_created += 1

            # Create 1-3 price entries (different sellers)
            num_sellers = random.randint(1, 3)
            for _ in range(num_sellers):
                seller = random.choice(SINGAPORE_SELLERS)

                # Price variation between sellers
                price_variation = random.uniform(0.9, 1.1)
                seller_price = round(base_price * price_variation, 2)

                part_price = PartPrice(
                    part_id=part.id,
                    seller_name=seller["name"],
                    seller_rating=seller["rating"],
                    price_sgd=seller_price,
                    currency="SGD",
                    availability="in_stock" if random.random() > 0.1 else "limited",
                    condition="new" if random.random() > 0.2 else "used",
                    source_url=f"https://example.com/parts/{part_number}",
                    last_updated=datetime.utcnow()
                )

                db.add(part_price)
                prices_created += 1

            # Create compatibility entries (2-5 vehicle combinations)
            num_vehicles = random.randint(2, 5)
            for _ in range(num_vehicles):
                make = random.choice(SINGAPORE_VEHICLE_MAKES)
                models = POPULAR_MODELS.get(make, ["Generic Model"])
                model = random.choice(models)

                # Year range (last 15 years)
                current_year = datetime.now().year
                year_start = random.randint(current_year - 15, current_year - 5)
                year_end = random.randint(year_start, current_year)

                compatibility = PartCompatibilityEnhanced(
                    part_id=part.id,
                    make=make,
                    model=model,
                    year_start=year_start,
                    year_end=year_end,
                    trim="All Trims" if random.random() > 0.3 else "Standard",
                    engine=None,  # Optional
                    notes=f"Compatible with {make} {model} {year_start}-{year_end}"
                )

                db.add(compatibility)
                compatibility_created += 1

        # Commit every category
        db.commit()
        logger.info(f"✅ Created {parts_per_category} parts for {category}")

    logger.info(f"""
    🎉 Synthetic data generation complete!

    📊 Statistics:
    - Parts created: {parts_created}
    - Prices created: {prices_created}
    - Compatibility entries: {compatibility_created}

    🏷️  All data labeled with: data_source='synthetic'

    🗑️  To remove synthetic data later:
        DELETE FROM parts_catalog WHERE data_source = 'synthetic';
    """)


def main():
    """Main execution"""
    db = SessionLocal()

    try:
        # Check if synthetic data already exists
        existing = db.query(PartsCatalog).filter(
            PartsCatalog.data_source == "synthetic"
        ).count()

        if existing > 0:
            logger.warning(f"⚠️  Found {existing} existing synthetic parts")
            response = input("Delete and regenerate? (y/n): ")
            if response.lower() == 'y':
                logger.info("Deleting existing synthetic data...")
                db.query(PartsCatalog).filter(
                    PartsCatalog.data_source == "synthetic"
                ).delete()
                db.commit()
                logger.info("✅ Deleted existing synthetic data")
            else:
                logger.info("Keeping existing data. Exiting.")
                return

        # Generate new synthetic parts
        generate_synthetic_parts(db, num_parts=5000)

        logger.info("✅ Database seeded successfully!")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
