"""
django-slots: Generate bookable slot candidates without persisting them.
"""

from .engine import Slot, generate_slots

__all__ = ["Slot", "generate_slots"]
