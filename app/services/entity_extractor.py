"""
Entity Extraction Service

Extracts automotive entities from text using pattern matching and NLP
"""

import re
from typing import List, Dict, Any
import json
from pathlib import Path


class EntityExtractor:
    """Extract automotive entities from queries"""

    def __init__(self):
        """Initialize entity extractor with automotive vocabularies"""
        # Load automotive vocabularies
        self.makes = self._load_makes()
        self.parts = self._load_parts()
        self.systems = self._load_systems()
        self.symptoms = self._load_symptoms()

        # Compile regex patterns
        self.patterns = {
            "VIN": re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b'),
            "FAULT_CODE": re.compile(r'\b[PCBU][0-9]{4}\b'),
            "YEAR": re.compile(r'\b(?:19|20)\d{2}\b'),
            "MILEAGE": re.compile(r'\b(\d{1,3}[,]?\d{3})\s*(miles?|k|km)\b', re.IGNORECASE),
        }

    def _load_makes(self) -> List[str]:
        """Load vehicle makes"""
        return [
            "Honda", "Toyota", "Ford", "Chevrolet", "Nissan", "BMW",
            "Mercedes-Benz", "Mercedes", "Audi", "Volkswagen", "Subaru",
            "Mazda", "Hyundai", "Kia", "Tesla", "Jeep", "Dodge",
            "Ram", "GMC", "Cadillac", "Lexus", "Acura", "Infiniti",
            "Volvo", "Porsche", "Land Rover", "Jaguar", "Mini", "Fiat"
        ]

    def _load_parts(self) -> List[str]:
        """Load common automotive parts"""
        return [
            "brake pad", "brake pads", "brake rotor", "brake rotors",
            "oil filter", "air filter", "cabin filter", "fuel filter",
            "spark plug", "spark plugs", "battery", "alternator",
            "starter", "radiator", "water pump", "fuel pump",
            "timing belt", "serpentine belt", "wiper blade", "wiper blades",
            "headlight", "tail light", "turn signal", "wheel bearing",
            "ball joint", "tie rod", "control arm", "shock absorber",
            "strut", "coil spring", "catalytic converter", "muffler",
            "exhaust pipe", "O2 sensor", "oxygen sensor", "MAF sensor",
            "throttle body", "fuel injector", "ignition coil",
            "transmission", "clutch", "brake caliper", "brake line",
            "tire", "tires", "rim", "rims", "wheel", "wheels"
        ]

    def _load_systems(self) -> List[str]:
        """Load automotive systems"""
        return [
            "engine", "transmission", "brakes", "brake system",
            "suspension", "steering", "electrical", "cooling",
            "exhaust", "fuel", "fuel system", "ignition", "HVAC",
            "air conditioning", "heating", "drivetrain"
        ]

    def _load_symptoms(self) -> List[str]:
        """Load common symptoms"""
        return [
            "rough idle", "check engine light", "grinding noise",
            "squeaking", "vibration", "pulling", "stalling",
            "hard to start", "overheating", "smoke", "burning smell",
            "rattling", "knocking", "hesitation", "poor acceleration",
            "loss of power", "wobbling", "shaking", "clicking",
            "whining", "humming", "squealing"
        ]

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract all entities from text

        Args:
            text: Input query text

        Returns:
            Dictionary of extracted entities by type
        """
        entities = {}

        # Extract using patterns
        for entity_type, pattern in self.patterns.items():
            if entity_type == "FAULT_CODE":
                # Extract ALL fault codes (can be multiple)
                matches = pattern.findall(text)
                if matches:
                    entities["fault_codes"] = matches  # Store as list with plural key
            else:
                match = pattern.search(text)
                if match:
                    if entity_type == "MILEAGE":
                        # Extract just the number part and convert to int
                        mileage_str = match.group(1).replace(",", "")
                        try:
                            entities[entity_type.lower()] = int(mileage_str)
                        except:
                            entities[entity_type.lower()] = mileage_str
                    else:
                        entities[entity_type.lower()] = match.group(0)

        # Extract make (check before model to avoid conflicts)
        for make in self.makes:
            if re.search(r'\b' + re.escape(make) + r'\b', text, re.IGNORECASE):
                entities["make"] = make
                break

        # Extract model (if make found, look for common models)
        if "make" in entities:
            # Common models (simplified - in production, use make-specific model lists)
            models = [
                "Civic", "Accord", "CR-V", "Pilot", "Odyssey",
                "Camry", "Corolla", "RAV4", "Highlander", "Tacoma", "Prius",
                "F-150", "Mustang", "Explorer", "Escape", "Fusion",
                "Silverado", "Equinox", "Malibu", "Tahoe", "Camaro",
                "Altima", "Sentra", "Rogue", "Pathfinder", "Maxima",
                "3 Series", "5 Series", "X3", "X5", "M3",
                "C-Class", "E-Class", "GLC", "GLE", "S-Class",
                "A4", "A6", "Q5", "Q7", "TT",
                "Jetta", "Passat", "Tiguan", "Atlas", "Golf",
                "Outback", "Forester", "Crosstrek", "Impreza",
                "CX-5", "Mazda3", "CX-9", "Mazda6",
                "Model 3", "Model S", "Model X", "Model Y",
                "Wrangler", "Cherokee", "Grand Cherokee"
            ]

            for model in models:
                if re.search(r'\b' + re.escape(model) + r'\b', text, re.IGNORECASE):
                    entities["model"] = model
                    break

        # Extract parts
        for part in self.parts:
            if re.search(r'\b' + re.escape(part) + r'\b', text, re.IGNORECASE):
                entities["part_name"] = part  # Store as part_name to match query.py
                break

        # Extract system
        for system in self.systems:
            if re.search(r'\b' + re.escape(system) + r'\b', text, re.IGNORECASE):
                entities["system"] = system
                break

        # Extract symptoms (can be multiple)
        symptoms_found = []
        for symptom in self.symptoms:
            if re.search(r'\b' + re.escape(symptom) + r'\b', text, re.IGNORECASE):
                symptoms_found.append(symptom)
        if symptoms_found:
            entities["symptoms"] = symptoms_found

        # Extract color for paint code queries
        colors = ["white", "black", "silver", "gray", "grey", "red", "blue", "green",
                  "yellow", "orange", "brown", "gold", "beige", "pearl", "metallic"]
        for color in colors:
            if re.search(r'\b' + re.escape(color) + r'\b', text, re.IGNORECASE):
                entities["color"] = color
                break

        return entities

    def extract_with_positions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities with their positions in text

        Args:
            text: Input query text

        Returns:
            List of entity dictionaries with start/end positions
        """
        entity_list = []

        # Extract pattern-based entities
        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity_list.append({
                    "text": match.group(0) if entity_type != "MILEAGE" else match.group(1),
                    "label": entity_type,
                    "start": match.start(),
                    "end": match.end()
                })

        # Extract vocabulary-based entities
        vocabularies = {
            "MAKE": self.makes,
            "PART": self.parts,
            "SYSTEM": self.systems,
            "SYMPTOM": self.symptoms
        }

        for label, vocab in vocabularies.items():
            for term in vocab:
                pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                for match in pattern.finditer(text):
                    entity_list.append({
                        "text": match.group(0),
                        "label": label,
                        "start": match.start(),
                        "end": match.end()
                    })

        # Sort by start position
        entity_list.sort(key=lambda x: x["start"])

        # Remove duplicates (keep first occurrence)
        seen_positions = set()
        unique_entities = []
        for entity in entity_list:
            pos_key = (entity["start"], entity["end"])
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_entities.append(entity)

        return unique_entities
