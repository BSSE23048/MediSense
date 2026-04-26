"""
Medicine Service - Extract medicine names and resolve details/alternatives
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List


class MedicineService:
    """Hybrid medicine intelligence: local catalog + external fallback."""

    def __init__(self):
        # Pakistan-oriented starter catalog. Expand over time.
        self.local_catalog = {
            "panadol": {
                "generic_name": "Paracetamol",
                "ingredients": ["Paracetamol 500mg"],
                "uses": ["Fever", "Headache", "Body pain"],
                "alternatives": ["Calpol", "Tylenol (generic equivalent)"],
            },
            "calpol": {
                "generic_name": "Paracetamol",
                "ingredients": ["Paracetamol 500mg"],
                "uses": ["Fever", "Mild pain"],
                "alternatives": ["Panadol", "Paracetamol generic"],
            },
            "augmentin": {
                "generic_name": "Amoxicillin + Clavulanic Acid",
                "ingredients": ["Amoxicillin", "Clavulanic acid"],
                "uses": ["Bacterial infections", "Sinus infections"],
                "alternatives": ["Curam", "Amoclav"],
            },
            "brufen": {
                "generic_name": "Ibuprofen",
                "ingredients": ["Ibuprofen 400mg"],
                "uses": ["Pain", "Inflammation", "Fever"],
                "alternatives": ["Nurofen", "Ibuprofen generic"],
            },
        }

    def extract_medicines_from_report(self, text: str, llm_medications: List[str] = None) -> List[str]:
        candidates = set()
        if llm_medications:
            for med in llm_medications:
                if med and med.strip():
                    candidates.add(med.strip().split()[0].lower())
        for token in re.findall(r"\b[A-Za-z][A-Za-z0-9\-]{2,}\b", text or ""):
            lower = token.lower()
            if lower in self.local_catalog:
                candidates.add(lower)
        return sorted(candidates)

    def get_medicine_details(self, medicine_name: str) -> Dict:
        key = (medicine_name or "").strip().lower()
        if not key:
            return {}
        local = self.local_catalog.get(key)
        if local:
            return {
                "name": medicine_name,
                "source": "local_dataset",
                **local,
            }
        external = self._fetch_external_details(key)
        if external:
            return external
        return {
            "name": medicine_name,
            "source": "fallback",
            "generic_name": "Unknown",
            "ingredients": [],
            "uses": ["Consult pharmacist/doctor for verified local usage"],
            "alternatives": [],
        }

    def _fetch_external_details(self, medicine_name: str) -> Dict:
        # OpenFDA is generic and may have partial coverage; used as best-effort.
        try:
            query = urllib.parse.quote(f'openfda.brand_name:"{medicine_name}"')
            url = f"https://api.fda.gov/drug/label.json?search={query}&limit=1"
            with urllib.request.urlopen(url, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
            results = data.get("results", [])
            if not results:
                return {}
            item = results[0]
            generic = (item.get("openfda", {}).get("generic_name", ["Unknown"]) or ["Unknown"])[0]
            ingredients = item.get("active_ingredient", [])[:5]
            uses = item.get("indications_and_usage", [])[:3]
            return {
                "name": medicine_name,
                "source": "external_api",
                "generic_name": generic,
                "ingredients": ingredients,
                "uses": uses if uses else ["Usage details unavailable from source"],
                "alternatives": self._alternatives_by_generic(generic, medicine_name),
            }
        except Exception:
            return {}

    def _alternatives_by_generic(self, generic_name: str, exclude_name: str) -> List[str]:
        matches = []
        for brand, info in self.local_catalog.items():
            if info["generic_name"].lower() == (generic_name or "").lower() and brand.lower() != exclude_name.lower():
                matches.append(brand.title())
        return matches

    def get_alternative_medicines(self, medicine_name: str) -> List[str]:
        details = self.get_medicine_details(medicine_name)
        if details.get("alternatives"):
            return details["alternatives"]
        generic_name = details.get("generic_name", "")
        return self._alternatives_by_generic(generic_name, medicine_name)
