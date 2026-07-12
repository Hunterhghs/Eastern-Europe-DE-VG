"""
Institutional DNA System

Institutions have two dimensions:
- DEPTH: How many years they've been operating (resilience + inertia)
- QUALITY: How well they function (effectiveness)

Deep, high-quality institutions are the ultimate legacy — they persist
across eras and determine what's possible. Deep, low-quality institutions
are traps — hard to reform, actively harmful. Shallow institutions are
fragile but malleable.

Key insight: Institutions built in Era 1 accumulate depth through Eras 2 and 3,
becoming progressively harder to reform but more resilient to shocks.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class InstitutionCategory(Enum):
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    ADMINISTRATIVE = "administrative"


@dataclass
class Institution:
    """A single institution with depth and quality."""
    name: str
    category: InstitutionCategory
    depth_years: int = 0           # How long it's operated
    quality: float = 0.0           # 0.0-1.0 effectiveness
    founded_era: Optional[str] = None
    founded_year: Optional[int] = None
    
    @property
    def resilience(self) -> float:
        """How resistant to degradation during crises. Depth provides resilience."""
        return min(1.0, 0.1 + math.log10(max(1, self.depth_years)) * 0.25)
    
    @property
    def inertia(self) -> float:
        """How resistant to reform. Depth creates inertia — hard to change."""
        return min(1.0, math.log10(max(1, self.depth_years)) * 0.3)
    
    @property
    def effectiveness(self) -> float:
        """Combined measure: quality moderated by depth.
        
        A shallow, high-quality institution is effective but fragile.
        A deep, high-quality institution is both effective and resilient.
        A deep, low-quality institution is actively harmful and hard to fix.
        """
        if self.quality < 0.3 and self.depth_years > 20:
            # Deep dysfunction: the institution actively harms
            return self.quality * 0.5
        return self.quality * (0.7 + 0.3 * self.resilience)


import math


class InstitutionalDNA:
    """Manages all institutions for a nation across eras.
    
    Institutions persist across era transitions. Their depth accumulates
    over time. Quality changes through policy, neglect, or crisis.
    """
    
    # Standard institution templates by category
    TEMPLATES = {
        "land_registry": {
            "name": "Land Registry",
            "category": InstitutionCategory.ECONOMIC,
            "description": "Records property ownership. Foundation of property rights, mortgage markets, and land taxation.",
            "effects": {"property_rights": 0.15, "tax_capacity": 0.10, "investment_climate": 0.10},
        },
        "statistical_office": {
            "name": "Statistical Office",
            "category": InstitutionCategory.ADMINISTRATIVE,
            "description": "Collects and publishes economic and demographic data. Enables evidence-based policy.",
            "effects": {"state_capacity": 0.10, "policy_effectiveness": 0.15},
        },
        "central_bank": {
            "name": "Central Bank",
            "category": InstitutionCategory.ECONOMIC,
            "description": "Manages currency, monetary policy, and financial stability.",
            "effects": {"monetary_sovereignty": 0.20, "inflation_control": 0.15, "investment_climate": 0.10},
        },
        "independent_judiciary": {
            "name": "Independent Judiciary",
            "category": InstitutionCategory.POLITICAL,
            "description": "Resolves disputes and enforces contracts independently of political pressure.",
            "effects": {"property_rights": 0.20, "investment_climate": 0.15, "institutional_trust": 0.15},
        },
        "civil_service": {
            "name": "Professional Civil Service",
            "category": InstitutionCategory.ADMINISTRATIVE,
            "description": "Meritocratic public administration insulated from political patronage.",
            "effects": {"state_capacity": 0.20, "institutional_trust": 0.10, "policy_effectiveness": 0.15},
        },
        "public_education_system": {
            "name": "Public Education System",
            "category": InstitutionCategory.SOCIAL,
            "description": "Universal schooling from primary through secondary.",
            "effects": {"literacy_rate": 0.25, "human_capital": 0.20, "social_mobility": 0.15},
        },
        "public_health_system": {
            "name": "Public Health System",
            "category": InstitutionCategory.SOCIAL,
            "description": "Universal healthcare access, sanitation, and disease prevention.",
            "effects": {"life_expectancy": 0.20, "human_capital": 0.10, "social_cohesion": 0.10},
        },
        "tax_authority": {
            "name": "Tax Authority",
            "category": InstitutionCategory.ECONOMIC,
            "description": "Capacity to assess, collect, and enforce taxation.",
            "effects": {"tax_capacity": 0.25, "state_capacity": 0.15, "fiscal_health": 0.15},
        },
        "regulatory_commission": {
            "name": "Regulatory Commission",
            "category": InstitutionCategory.ECONOMIC,
            "description": "Independent oversight of markets, competition, and consumer protection.",
            "effects": {"investment_climate": 0.10, "institutional_trust": 0.10, "market_efficiency": 0.15},
        },
        "electoral_commission": {
            "name": "Electoral Commission",
            "category": InstitutionCategory.POLITICAL,
            "description": "Administers free and fair elections with trusted results.",
            "effects": {"institutional_trust": 0.20, "political_stability": 0.15},
        },
    }
    
    def __init__(self, initial_quality: float = 0.3, initial_depth: int = 0):
        self.institutions: Dict[str, Institution] = {}
        self.initial_quality = initial_quality
        self.initial_depth = initial_depth
    
    def found(self, institution_key: str, year: int, era: str, 
              quality: Optional[float] = None) -> Institution:
        """Create a new institution (or upgrade existing).
        
        If the institution already exists, this represents a reform/upgrade.
        """
        if institution_key not in self.TEMPLATES:
            raise KeyError(f"Unknown institution template: {institution_key}")
        
        template = self.TEMPLATES[institution_key]
        inst_quality = quality if quality is not None else self.initial_quality
        
        if institution_key in self.institutions:
            # Reform existing — improve quality, depth continues
            existing = self.institutions[institution_key]
            # Reforming deep institutions is harder (inertia)
            reform_effectiveness = 1.0 - existing.inertia * 0.7
            existing.quality = existing.quality + (inst_quality - existing.quality) * reform_effectiveness
            return existing
        
        inst = Institution(
            name=template["name"],
            category=template["category"],
            quality=inst_quality,
            depth_years=0,
            founded_era=era,
            founded_year=year,
        )
        self.institutions[institution_key] = inst
        return inst
    
    def advance_year(self, years: int = 1) -> None:
        """Age all institutions by the given years."""
        for inst in self.institutions.values():
            inst.depth_years += years
    
    def degrade(self, institution_key: str, amount: float) -> None:
        """Degrade an institution's quality (corruption, neglect, crisis).
        
        Deeper institutions resist degradation through resilience.
        """
        if institution_key not in self.institutions:
            return
        
        inst = self.institutions[institution_key]
        effective_degradation = amount * (1.0 - inst.resilience * 0.6)
        inst.quality = max(0.0, inst.quality - effective_degradation)
    
    def improve(self, institution_key: str, amount: float) -> None:
        """Improve an institution's quality (reform, investment).
        
        Deeper institutions resist change through inertia.
        """
        if institution_key not in self.institutions:
            return
        
        inst = self.institutions[institution_key]
        effective_improvement = amount * (1.0 - inst.inertia * 0.7)
        inst.quality = min(1.0, inst.quality + effective_improvement)
    
    def aggregate_quality(self) -> float:
        """Average quality across all institutions."""
        if not self.institutions:
            return 0.0
        return sum(i.quality for i in self.institutions.values()) / len(self.institutions)
    
    def aggregate_effectiveness(self) -> float:
        """Average effectiveness (quality × depth moderation)."""
        if not self.institutions:
            return 0.0
        return sum(i.effectiveness for i in self.institutions.values()) / len(self.institutions)
    
    def aggregate_depth(self) -> float:
        """Average depth in years."""
        if not self.institutions:
            return 0.0
        return sum(i.depth_years for i in self.institutions.values()) / len(self.institutions)
    
    def reform_difficulty(self, institution_key: str) -> float:
        """How hard is it to reform this institution? 0=easy, 1=nearly impossible."""
        if institution_key not in self.institutions:
            return 0.0  # doesn't exist — founding is easier than reforming
        return self.institutions[institution_key].inertia
    
    def crisis_impact_resistance(self, institution_key: str) -> float:
        """How well does this institution weather a crisis? 0=obliterated, 1=untouched."""
        if institution_key not in self.institutions:
            return 0.0
        return self.institutions[institution_key].resilience
    
    def summary(self) -> Dict:
        """Return a summary dictionary for serialization."""
        return {
            key: {
                "name": inst.name,
                "category": inst.category.value,
                "depth_years": inst.depth_years,
                "quality": round(inst.quality, 3),
                "effectiveness": round(inst.effectiveness, 3),
                "resilience": round(inst.resilience, 3),
                "inertia": round(inst.inertia, 3),
                "founded_era": inst.founded_era,
                "founded_year": inst.founded_year,
            }
            for key, inst in self.institutions.items()
        }
    
    def effects_bonus(self) -> Dict[str, float]:
        """Aggregate the policy effects of all institutions.
        
        Returns a dict of effect_name -> total_bonus for use in simulation.
        """
        bonuses: Dict[str, float] = {}
        for key, inst in self.institutions.items():
            if key not in self.TEMPLATES:
                continue
            template = self.TEMPLATES[key]
            for effect_name, max_bonus in template["effects"].items():
                actual_bonus = max_bonus * inst.effectiveness
                bonuses[effect_name] = bonuses.get(effect_name, 0.0) + actual_bonus
        return bonuses


def seed_initial_institutions(legacy_type: str, quality: float, depth: int) -> InstitutionalDNA:
    """Create starting institutions based on inherited imperial legacy.
    
    Different empires left different institutional foundations:
    - austro_hungarian: strong administrative, weak political
    - ottoman: weak all-around but some local communal strength
    - mixed_imperial: inconsistent patchwork
    - extractive_colonial: extractive economic, nothing else
    - alpine_communal: strong local, weak national
    """
    dna = InstitutionalDNA(initial_quality=quality, initial_depth=depth)
    
    # All nations get these baseline institutions pre-founded with their legacy
    base_institutions = {
        "austro_hungarian": {
            "land_registry": 0.55,
            "statistical_office": 0.50,
            "civil_service": 0.48,
            "tax_authority": 0.42,
            "public_education_system": 0.40,
        },
        "mixed_imperial": {
            "land_registry": 0.30,
            "statistical_office": 0.25,
            "civil_service": 0.28,
            "tax_authority": 0.22,
            "public_education_system": 0.30,
        },
        "ottoman": {
            "land_registry": 0.10,
            "tax_authority": 0.12,
            "public_education_system": 0.08,
        },
        "extractive_colonial": {
            "land_registry": 0.20,
            "tax_authority": 0.15,
        },
        "alpine_communal": {
            "public_education_system": 0.45,
            "land_registry": 0.30,
        },
    }
    
    institutions_to_seed = base_institutions.get(legacy_type, {})
    
    for inst_key, inst_quality in institutions_to_seed.items():
        inst = Institution(
            name=InstitutionalDNA.TEMPLATES[inst_key]["name"],
            category=InstitutionalDNA.TEMPLATES[inst_key]["category"],
            quality=inst_quality,
            depth_years=depth,
            founded_era="pre_era1",
            founded_year=1918 - depth,
        )
        dna.institutions[inst_key] = inst
    
    return dna
