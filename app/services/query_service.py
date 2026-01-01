"""
Query Service - Intelligent query processing with ML

Combines intent classification and entity extraction to understand
user queries and route them to appropriate endpoints
"""

import joblib
from pathlib import Path
from typing import Dict, Any, Optional
from app.services.entity_extractor import EntityExtractor
from app.core.logging import get_logger

logger = get_logger(__name__)


class QueryService:
    """Intelligent query processing service"""

    def __init__(self):
        """Initialize query service with trained models"""
        self.model_dir = Path("data/models")

        # Load intent classifier
        try:
            self.intent_model = joblib.load(self.model_dir / "intent_classifier_simple.pkl")
            logger.info("query_service_init", message="Intent classifier loaded successfully")
        except Exception as e:
            logger.error("query_service_init_error", error=str(e))
            self.intent_model = None

        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()
        logger.info("query_service_init", message="Entity extractor initialized")

    def process_query(self, text: str) -> Dict[str, Any]:
        """
        Process a natural language query

        Args:
            text: User query text

        Returns:
            Dictionary containing:
            - intent: Classified intent
            - confidence: Confidence score
            - entities: Extracted entities
            - suggested_action: What endpoint to call
        """
        logger.info("process_query", text=text)

        result = {
            "text": text,
            "intent": None,
            "confidence": 0.0,
            "entities": {},
            "suggested_action": None
        }

        # Classify intent
        if self.intent_model:
            try:
                intent = self.intent_model.predict([text])[0]
                proba = self.intent_model.predict_proba([text])[0]
                confidence = float(max(proba))

                result["intent"] = intent
                result["confidence"] = confidence

                logger.info("intent_classified",
                           intent=intent,
                           confidence=f"{confidence:.3f}")
            except Exception as e:
                logger.error("intent_classification_error", error=str(e))

        # Extract entities
        try:
            entities = self.entity_extractor.extract(text)
            result["entities"] = entities

            logger.info("entities_extracted",
                       count=len(entities),
                       entities=list(entities.keys()))
        except Exception as e:
            logger.error("entity_extraction_error", error=str(e))

        # Suggest action based on intent
        result["suggested_action"] = self._get_suggested_action(
            result["intent"],
            result["entities"]
        )

        return result

    def _get_suggested_action(self,
                              intent: Optional[str],
                              entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest which endpoint to call based on intent and entities

        Args:
            intent: Classified intent
            entities: Extracted entities

        Returns:
            Dictionary with endpoint and parameters
        """
        if not intent:
            return {"endpoint": None, "message": "Unable to determine intent"}

        actions = {
            "parts_identification": {
                "endpoint": "/api/v1/parts/identify",
                "method": "POST",
                "required_entities": ["part"],
                "optional_entities": ["make", "model", "year"]
            },
            "vehicle_valuation": {
                "endpoint": "/api/v1/valuation/estimate",
                "method": "POST",
                "required_entities": [],
                "optional_entities": ["make", "model", "year", "mileage"]
            },
            "paint_code": {
                "endpoint": "/api/v1/paint-code/lookup",
                "method": "POST",
                "required_entities": [],
                "optional_entities": ["make", "model", "year", "vin"]
            },
            "specifications": {
                "endpoint": "/api/v1/specifications/{vin}",
                "method": "GET",
                "required_entities": ["vin"],
                "optional_entities": ["make", "model", "year"]
            },
            "diagnostics": {
                "endpoint": "/api/v1/diagnostics/troubleshoot",
                "method": "POST",
                "required_entities": [],
                "optional_entities": ["fault_code", "symptom", "system", "make", "model", "year"]
            },
            "general_question": {
                "endpoint": "/api/v1/query",
                "method": "POST",
                "required_entities": [],
                "optional_entities": []
            }
        }

        action = actions.get(intent, {})

        if not action:
            return {"endpoint": None, "message": f"Unknown intent: {intent}"}

        # Check if required entities are present
        required = action.get("required_entities", [])
        missing = [e for e in required if e not in entities]

        if missing:
            return {
                "endpoint": action["endpoint"],
                "method": action["method"],
                "status": "missing_entities",
                "missing": missing,
                "message": f"Missing required entities: {', '.join(missing)}"
            }

        # Build parameters from entities
        params = {}
        for entity_type in action.get("optional_entities", []) + required:
            if entity_type in entities:
                params[entity_type] = entities[entity_type]

        return {
            "endpoint": action["endpoint"],
            "method": action["method"],
            "status": "ready",
            "parameters": params
        }


# Global instance (singleton pattern)
_query_service = None


def get_query_service() -> QueryService:
    """Get or create query service instance"""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
