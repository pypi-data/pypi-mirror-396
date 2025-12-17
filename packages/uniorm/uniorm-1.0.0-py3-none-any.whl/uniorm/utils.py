"""Utility functions"""

from typing import Any, Dict, List
import re


def snake_case(name: str) -> str:
    """Convert CamelCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def dict_to_model(data: Dict[str, Any], model_class) -> Any:
    """Convert dictionary to model instance"""
    return model_class(**data)


def models_to_dict(models: List[Any]) -> List[Dict[str, Any]]:
    """Convert list of models to list of dictionaries"""
    return [model.to_dict() for model in models]