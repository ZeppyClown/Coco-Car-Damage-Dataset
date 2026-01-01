#!/usr/bin/env python
"""
Generate synthetic training data for intent classification and entity extraction

Creates 5,000+ realistic automotive queries with:
- Intent labels
- Entity annotations
- Diverse phrasings
"""

import json
import random
from typing import List, Dict, Tuple
from pathlib import Path

# Seed for reproducibility
random.seed(42)

# Vehicle data
MAKES = ["Honda", "Toyota", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
         "Audi", "Volkswagen", "Subaru", "Mazda", "Hyundai", "Kia", "Tesla", "Jeep"]

MODELS = {
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Tacoma"],
    "Ford": ["F-150", "Mustang", "Explorer", "Escape", "Fusion"],
    "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Camaro"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Maxima"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "M3"],
    "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "S-Class"],
    "Audi": ["A4", "A6", "Q5", "Q7", "TT"],
    "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "Golf"],
    "Subaru": ["Outback", "Forester", "Crosstrek", "Impreza", "Legacy"],
    "Mazda": ["CX-5", "Mazda3", "CX-9", "Mazda6", "MX-5"],
    "Hyundai": ["Sonata", "Elantra", "Tucson", "Santa Fe", "Kona"],
    "Kia": ["Optima", "Forte", "Sportage", "Sorento", "Soul"],
    "Tesla": ["Model 3", "Model S", "Model X", "Model Y"],
    "Jeep": ["Wrangler", "Cherokee", "Grand Cherokee", "Compass", "Renegade"]
}

YEARS = list(range(2010, 2024))

PARTS = [
    "brake pads", "brake rotors", "oil filter", "air filter", "cabin filter",
    "spark plugs", "battery", "alternator", "starter", "radiator",
    "water pump", "fuel pump", "timing belt", "serpentine belt", "wiper blades",
    "headlight bulb", "tail light", "turn signal", "wheel bearing", "ball joint",
    "tie rod", "control arm", "shock absorber", "strut", "coil spring",
    "catalytic converter", "muffler", "exhaust pipe", "O2 sensor", "MAF sensor",
    "throttle body", "fuel injector", "ignition coil", "distributor cap",
    "transmission fluid", "coolant", "brake fluid", "power steering fluid"
]

FAULT_CODES = [
    "P0300", "P0420", "P0171", "P0172", "P0455", "P0442", "P0128", "P0401",
    "P0715", "P0720", "P0700", "C1201", "C0035", "B1342", "U0100",
    "P0301", "P0302", "P0303", "P0304", "P0305", "P0306"
]

SYSTEMS = [
    "engine", "transmission", "brakes", "suspension", "steering",
    "electrical", "cooling", "exhaust", "fuel", "ignition", "HVAC"
]

SYMPTOMS = [
    "rough idle", "check engine light", "grinding noise", "squeaking",
    "vibration", "pulling to one side", "stalling", "hard to start",
    "overheating", "smoke", "burning smell", "rattling", "knocking",
    "hesitation", "poor acceleration", "loss of power", "wobbling"
]

# Sample VINs (format-valid but fictional)
SAMPLE_VINS = [
    "1HGBH41JXMN109186", "1FTFW1ET5BFC10312", "5YFBURHE5HP588522",
    "3VWDX7AJ9CM632919", "1N4AL3AP8JC231472", "19XFB2F59CE000001",
    "4T1BF1FK5CU551169", "2C3CDXHG9FH123456", "5FNRL6H78KB012345"
]

LOCATIONS = [
    "90210", "10001", "60601", "75201", "94102", "98101", "33101",
    "02101", "19101", "85001", "Denver", "Seattle", "Miami", "Boston"
]


def create_entity_annotation(text: str, entity_text: str, label: str) -> Dict:
    """Create entity annotation with start/end positions"""
    start = text.find(entity_text)
    if start == -1:
        return None
    return {
        "text": entity_text,
        "label": label,
        "start": start,
        "end": start + len(entity_text)
    }


def generate_parts_queries() -> List[Dict]:
    """Generate parts identification queries"""
    queries = []
    templates = [
        "I need {part} for my {year} {make} {model}",
        "Where can I get {part} for a {year} {make} {model}",
        "Looking for {part} for {year} {make} {model}",
        "Need to replace {part} on my {year} {make} {model}",
        "{part} for {make} {model} {year}",
        "What {part} fits a {year} {make} {model}",
        "Can you find me {part} for my {make} {model}",
        "I want to buy {part} for {year} {make}",
        "Do you have {part} for {make} {model}",
        "Searching for {part} compatible with {year} {make} {model}",
        "I need new {part}",
        "Looking for {part}",
        "Where to buy {part}",
        "{part} replacement",
        "Best {part} for {make}",
    ]

    for _ in range(1000):
        template = random.choice(templates)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        part = random.choice(PARTS)

        text = template.format(part=part, make=make, model=model, year=year)

        entities = []
        if "{part}" in template:
            ent = create_entity_annotation(text, part, "PART")
            if ent: entities.append(ent)
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "parts_identification",
            "entities": entities
        })

    return queries


def generate_valuation_queries() -> List[Dict]:
    """Generate vehicle valuation queries"""
    queries = []
    templates = [
        "What's my {year} {make} {model} worth",
        "How much is a {year} {make} {model} worth",
        "Value of {year} {make} {model}",
        "Price estimate for {year} {make} {model}",
        "What can I sell my {year} {make} {model} for",
        "Market value of {year} {make} {model}",
        "How much should I pay for a {year} {make} {model}",
        "Fair price for {year} {make} {model} with {mileage} miles",
        "Estimate value of my {year} {make} {model}",
        "What's a {year} {make} going for",
        "Price check on {year} {make} {model}",
        "{make} {model} {year} value",
        "How much is my car worth",
        "What's my vehicle worth",
        "Need a valuation for my {year} {make}",
    ]

    for _ in range(800):
        template = random.choice(templates)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        mileage = random.choice([20000, 30000, 50000, 75000, 100000, 150000])

        text = template.format(make=make, model=model, year=year, mileage=mileage)

        entities = []
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)
        if "{mileage}" in template:
            ent = create_entity_annotation(text, str(mileage), "MILEAGE")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "vehicle_valuation",
            "entities": entities
        })

    return queries


def generate_paint_code_queries() -> List[Dict]:
    """Generate paint code queries"""
    queries = []
    templates = [
        "What's the paint code for my {year} {make} {model}",
        "Paint code for {year} {make} {model}",
        "I need the color code for {make} {model}",
        "What color code does my {year} {make} have",
        "Find paint code for VIN {vin}",
        "Color code lookup for {year} {make}",
        "What's my car's paint code",
        "{make} {model} paint color code",
        "Need touch up paint code for {year} {make}",
        "Paint formula for my {make}",
    ]

    for _ in range(600):
        template = random.choice(templates)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        vin = random.choice(SAMPLE_VINS)

        text = template.format(make=make, model=model, year=year, vin=vin)

        entities = []
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)
        if "{vin}" in template:
            ent = create_entity_annotation(text, vin, "VIN")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "paint_code",
            "entities": entities
        })

    return queries


def generate_specifications_queries() -> List[Dict]:
    """Generate specifications queries"""
    queries = []
    templates = [
        "Decode VIN {vin}",
        "What are the specs for VIN {vin}",
        "Vehicle specifications for {year} {make} {model}",
        "Tell me about VIN {vin}",
        "Get vehicle info for {vin}",
        "Specs for {year} {make} {model}",
        "What engine does a {year} {make} {model} have",
        "Transmission type for {year} {make}",
        "{year} {make} {model} specifications",
        "Vehicle details for VIN {vin}",
        "Lookup VIN {vin}",
        "Information on {year} {make} {model}",
    ]

    for _ in range(800):
        template = random.choice(templates)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        vin = random.choice(SAMPLE_VINS)

        text = template.format(make=make, model=model, year=year, vin=vin)

        entities = []
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)
        if "{vin}" in template:
            ent = create_entity_annotation(text, vin, "VIN")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "specifications",
            "entities": entities
        })

    return queries


def generate_diagnostics_queries() -> List[Dict]:
    """Generate diagnostics queries"""
    queries = []
    templates = [
        "My {year} {make} has code {code}",
        "Check engine light with {code} on my {make} {model}",
        "What does {code} mean",
        "Diagnosing {code} on {year} {make}",
        "My car has {symptom} and code {code}",
        "{symptom} on my {year} {make} {model}",
        "{system} problem on {make} {model}",
        "Troubleshoot {code}",
        "My {make} is {symptom}",
        "{symptom} when driving my {year} {make}",
        "Error code {code} help",
        "{system} issue on my {year} {make}",
    ]

    for _ in range(1000):
        template = random.choice(templates)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        code = random.choice(FAULT_CODES)
        system = random.choice(SYSTEMS)
        symptom = random.choice(SYMPTOMS)

        text = template.format(
            make=make, model=model, year=year,
            code=code, system=system, symptom=symptom
        )

        entities = []
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)
        if "{code}" in template:
            ent = create_entity_annotation(text, code, "FAULT_CODE")
            if ent: entities.append(ent)
        if "{system}" in template:
            ent = create_entity_annotation(text, system, "SYSTEM")
            if ent: entities.append(ent)
        if "{symptom}" in template:
            ent = create_entity_annotation(text, symptom, "SYMPTOM")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "diagnostics",
            "entities": entities
        })

    return queries


def generate_general_queries() -> List[Dict]:
    """Generate general automotive questions"""
    queries = []
    general_questions = [
        "What oil should I use for my {year} {make} {model}",
        "How often should I change oil",
        "When to replace {part}",
        "Best {part} for {make}",
        "How to check {system}",
        "Is it safe to drive with {symptom}",
        "What causes {symptom}",
        "How much does {part} replacement cost",
        "Can I drive with code {code}",
        "How to maintain my {make}",
        "What's normal {system} temperature",
        "How to improve fuel economy",
        "Best tires for {make} {model}",
        "Recommended tire pressure",
        "How to jump start a car",
    ]

    for _ in range(800):
        template = random.choice(general_questions)
        make = random.choice(MAKES)
        model = random.choice(MODELS[make])
        year = random.choice(YEARS)
        part = random.choice(PARTS)
        system = random.choice(SYSTEMS)
        symptom = random.choice(SYMPTOMS)
        code = random.choice(FAULT_CODES)

        text = template.format(
            make=make, model=model, year=year,
            part=part, system=system, symptom=symptom, code=code
        )

        entities = []
        if "{make}" in template:
            ent = create_entity_annotation(text, make, "MAKE")
            if ent: entities.append(ent)
        if "{model}" in template:
            ent = create_entity_annotation(text, model, "MODEL")
            if ent: entities.append(ent)
        if "{year}" in template:
            ent = create_entity_annotation(text, str(year), "YEAR")
            if ent: entities.append(ent)
        if "{part}" in template:
            ent = create_entity_annotation(text, part, "PART")
            if ent: entities.append(ent)
        if "{system}" in template:
            ent = create_entity_annotation(text, system, "SYSTEM")
            if ent: entities.append(ent)
        if "{symptom}" in template:
            ent = create_entity_annotation(text, symptom, "SYMPTOM")
            if ent: entities.append(ent)
        if "{code}" in template:
            ent = create_entity_annotation(text, code, "FAULT_CODE")
            if ent: entities.append(ent)

        queries.append({
            "text": text,
            "intent": "general_question",
            "entities": entities
        })

    return queries


def main():
    """Generate complete training dataset"""
    print("=" * 60)
    print("Generating Synthetic Training Dataset")
    print("=" * 60)

    all_queries = []

    print("\n1. Generating parts identification queries...")
    parts_queries = generate_parts_queries()
    all_queries.extend(parts_queries)
    print(f"   ✓ Generated {len(parts_queries)} queries")

    print("\n2. Generating valuation queries...")
    valuation_queries = generate_valuation_queries()
    all_queries.extend(valuation_queries)
    print(f"   ✓ Generated {len(valuation_queries)} queries")

    print("\n3. Generating paint code queries...")
    paint_queries = generate_paint_code_queries()
    all_queries.extend(paint_queries)
    print(f"   ✓ Generated {len(paint_queries)} queries")

    print("\n4. Generating specifications queries...")
    specs_queries = generate_specifications_queries()
    all_queries.extend(specs_queries)
    print(f"   ✓ Generated {len(specs_queries)} queries")

    print("\n5. Generating diagnostics queries...")
    diag_queries = generate_diagnostics_queries()
    all_queries.extend(diag_queries)
    print(f"   ✓ Generated {len(diag_queries)} queries")

    print("\n6. Generating general questions...")
    general_queries = generate_general_queries()
    all_queries.extend(general_queries)
    print(f"   ✓ Generated {len(general_queries)} queries")

    # Shuffle
    random.shuffle(all_queries)

    # Split into train/val/test
    total = len(all_queries)
    train_size = int(total * 0.7)
    val_size = int(total * 0.15)

    train_data = all_queries[:train_size]
    val_data = all_queries[train_size:train_size + val_size]
    test_data = all_queries[train_size + val_size:]

    # Save datasets
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "train": train_data,
        "val": val_data,
        "test": test_data
    }

    print("\n" + "=" * 60)
    print("Saving Datasets")
    print("=" * 60)

    for name, data in datasets.items():
        filepath = output_dir / f"intent_{name}.json"
        with open(filepath, 'w') as f:
            json.dump({"queries": data}, f, indent=2)
        print(f"✓ Saved {name}: {len(data)} queries → {filepath}")

    # Print statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"\nTotal queries: {total}")
    print(f"Train: {len(train_data)} (70%)")
    print(f"Validation: {len(val_data)} (15%)")
    print(f"Test: {len(test_data)} (15%)")

    print("\nQueries per intent:")
    intent_counts = {}
    for q in all_queries:
        intent = q["intent"]
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    for intent, count in sorted(intent_counts.items()):
        percentage = (count / total) * 100
        print(f"  {intent}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 60)
    print("✓ Dataset Generation Complete!")
    print("=" * 60)

    # Show examples
    print("\nExample queries:")
    for intent in intent_counts.keys():
        example = next((q for q in all_queries if q["intent"] == intent), None)
        if example:
            print(f"\n[{intent}]")
            print(f"  Text: {example['text']}")
            print(f"  Entities: {len(example['entities'])}")


if __name__ == "__main__":
    main()
