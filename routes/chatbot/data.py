"""
Data Loader - Support both list JSON and object JSON
"""

import json
import os
from typing import List, Dict, Optional, Union

class DataLoader:
    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.data = self._load_json()

        # Detect structure
        if isinstance(self.data, list):
            # JSON is a list -> treat as "places"
            self.places = self.data
            self.restaurants = []
            self.foods = []
            self.tours = []
        elif isinstance(self.data, dict):
            # JSON is an object with collections
            self.places = self.data.get("places", [])
            self.restaurants = self.data.get("restaurants", [])
            self.foods = self.data.get("foods", [])
            self.tours = self.data.get("tours", [])
        else:
            self.places = []
            self.restaurants = []
            self.foods = []
            self.tours = []

    def _load_json(self):
        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                print(f"✅ Loaded JSON: {self.json_file_path}")
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
            return []

    # ======================================================
    # SEARCH FUNCTIONS
    # ======================================================

    def search_foods(self, region: Optional[str] = None, name: Optional[str] = None, limit: int = 10):
        """If your JSON has no foods -> always return empty"""
        results = []

        for food in self.foods:
            if not isinstance(food, dict):
                continue

            match = True
            if region and region.lower() not in food.get("region", "").lower():
                match = False
            if name and name.lower() not in food.get("name", "").lower():
                match = False

            if match:
                results.append(food)

            if len(results) >= limit:
                break

        return results

    def search_restaurants(self, location=None, cuisine=None, name=None, limit=10):
        results = []

        for item in (self.restaurants or self.places):  # fallback to places
            if not isinstance(item, dict):
                continue

            match = True

            # LOCATION match - search in address and tags
            if location:
                address = item.get('address', '')
                tags = str(item.get('tags', []))
                loc_text = f"{address} {tags}".lower()
                
                # Normalize location search terms (Hồ Chí Minh = HCMC = Sài Gòn = TP. Hồ Chí Minh)
                location_lower = location.lower()
                location_variants = {
                    "hồ chí minh": ["hồ chí minh", "sài gòn", "tp. hồ chí minh", "hcmc"],
                    "hà nội": ["hà nội", "hanoi"],
                    "đà nẵng": ["đà nẵng", "da nang"],
                }
                
                # Check if location matches any variant
                found = False
                for key, variants in location_variants.items():
                    if location_lower in key or key in location_lower:
                        for variant in variants:
                            if variant in loc_text:
                                found = True
                                break
                
                # If not found in variants, do direct search
                if not found and location_lower not in loc_text:
                    match = False

            # CUISINE match
            if cuisine:
                if cuisine.lower() not in str(item.get("tags", [])).lower():
                    match = False

            # NAME match
            if name:
                if name.lower() not in item.get("name","").lower():
                    match = False

            if match:
                results.append(item)

            if len(results) >= limit:
                break

        return results

    def search_places(self, query: str, location: Optional[str] = None, limit: int = 10):
        results = []
        query = query.lower()

        for place in self.places:
            if not isinstance(place, dict):
                continue

            name = place.get("name","").lower()
            address = place.get("address","").lower()
            tags = ",".join(place.get("tags", [])).lower()

            match = query in name or query in address or query in tags

            if location and location.lower() not in address:
                match = False

            if match:
                results.append(place)

            if len(results) >= limit:
                break

        return results

    def get_top_rated(self, collection_name: str, min_rating=4.0, limit=10):
        # If your JSON doesn't have restaurants -> fallback to places
        items = self.restaurants if collection_name == "restaurants" else self.places

        valid_items = [p for p in items if isinstance(p, dict) and p.get("rating", 0) >= min_rating]

        return sorted(valid_items, key=lambda x: x.get("rating", 0), reverse=True)[:limit]

    def reload(self):
        self.data = self._load_json()
        print("🔄 Data reloaded")
