# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from app.google_search import google_plant_search

from pydantic import BaseModel, Field


# --- Tool Input Models ---
class PlantSearchInput(BaseModel):
    """Input for plant database search."""
    query: str = Field(description="Plant name or characteristics to search for")
    limit: int = Field(default=10, description="Maximum number of results to return")


class WeatherInput(BaseModel):
    """Input for weather lookup."""
    location: str = Field(description="City, state/country or coordinates")
    days: int = Field(default=7, description="Number of forecast days")


class CareScheduleInput(BaseModel):
    """Input for plant care scheduler."""
    plant_name: str = Field(description="Name of the plant")
    location: str = Field(description="User's location")
    care_level: str = Field(default="intermediate", description="User's gardening experience level")


class DiseaseIdentificationInput(BaseModel):
    """Input for plant disease identification."""
    symptoms: str = Field(description="Description of plant symptoms")
    plant_type: str = Field(description="Type or name of affected plant")
    image_url: Optional[str] = Field(default=None, description="URL to image of affected plant")


class NativePlantInput(BaseModel):
    """Input for native plant finder."""
    location: str = Field(description="Geographic location (city, state, or coordinates)")
    plant_type: str = Field(default="all", description="Type of plants (trees, shrubs, flowers, etc.)")


class SoilAnalysisInput(BaseModel):
    """Input for soil analysis."""
    location: str = Field(description="Geographic location for soil data")
    soil_sample_data: Optional[Dict[str, Any]] = Field(default=None, description="Soil test results if available")


class HardinessZoneInput(BaseModel):
    """Input for hardiness zone lookup."""
    location: str = Field(description="Geographic location")


class MarketplaceSearchInput(BaseModel):
    """Input for marketplace search."""
    plant_name: str = Field(description="Name of plant to search for")
    location: str = Field(description="User's location for shipping considerations")
    max_price: Optional[float] = Field(default=None, description="Maximum price filter")


class PriceComparisonInput(BaseModel):
    """Input for price comparison."""
    plant_name: str = Field(description="Name of plant to compare prices")
    size: Optional[str] = Field(default=None, description="Plant size specification")


class SellerVerificationInput(BaseModel):
    """Input for seller verification."""
    seller_name: str = Field(description="Name of seller to verify")
    platform: str = Field(description="Platform or website where seller operates")


# --- Utility Functions ---
def get_coordinates(location: str) -> Optional[tuple]:
    """Get latitude and longitude for a location."""
    try:
        geolocator = Nominatim(user_agent="plantworks-mvp")
        location_data = geolocator.geocode(location, timeout=10)
        if location_data:
            return (location_data.latitude, location_data.longitude)
    except GeocoderTimedOut:
        logging.warning(f"Geocoding timeout for location: {location}")
    except Exception as e:
        logging.error(f"Geocoding error for {location}: {e}")
    return None


def make_api_request(url: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None) -> Optional[Dict]:
    """Make a safe API request with error handling."""

def clean_plant_query(query: str) -> str:
    """Clean and extract plant-related terms from natural language queries."""
    import re
    if not query or not isinstance(query, str):
        return ""
    cleaned = query.strip()
    # Remove common question prefixes and suffixes using regex
    patterns = [
        r'^(what is|what are|tell me about|search for|find|information on)\s+',
        r'\?$',
    ]
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
    # If cleaning results in an empty string, return the original query
    return cleaned or query.strip()
    try:
        response = requests.get(url, headers=headers or {}, params=params or {}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for {url}: {e}")
        return None


# --- LEARN AGENT TOOLS ---
def plant_database_search(input_data: PlantSearchInput) -> Dict[str, Any]:
    """
    Search for plant information using Google Custom Search (fallbacks to mock data).
    """
    try:
        return google_plant_search(input_data.query, num_results=input_data.limit)
    except Exception as e:
        logging.error(f"Google search exception: {e}")
        return {
            "results": [
                {"title": "Mock Plant Info", "snippet": "This is mock plant data.", "link": "https://en.wikipedia.org/wiki/Plant"}
            ],
            "sources": ["mock"]
        }
        query_lower = input_data.query.lower()
        for plant in mock_plants:
            if (query_lower in plant["scientific_name"].lower() or 
                query_lower in plant["common_name"].lower() or
                any(query_lower in str(v).lower() for v in plant.values())):
                results["results"].append(plant)
        results["results"] = results["results"][:input_data.limit]
        results["sources"].append("Mock Database")
    
    results["total_found"] = len(results["results"])
    return results


# --- GROW AGENT TOOLS ---
def weather_lookup(input_data: WeatherInput) -> Dict[str, Any]:
    """
    Get current weather and forecast data for plant care decisions.
    
    Provides weather information including temperature, humidity, precipitation,
    and UV index to help with watering and care scheduling.
    """
    weather_data = {
        "location": input_data.location,
        "current": {},
        "forecast": [],
        "growing_conditions": {}
    }
    
    # Get coordinates for location
    coords = get_coordinates(input_data.location)
    if not coords:
        return {"error": "Could not geocode location"}
    
    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if not openweather_api_key:
        logging.warning("OPENWEATHER_API_KEY not set!")
        return {"error": "OpenWeather API key not set"}
    
    lat, lon = coords
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={openweather_api_key}&units=metric"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            weather_data["current"] = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "uv_index": None  # Not available in free tier
            }
        else:
            logging.error(f"OpenWeather API error: {resp.status_code} {resp.text}")
            return {"error": f"OpenWeather API error: {resp.status_code}"}
    except Exception as e:
        logging.error(f"OpenWeather API exception: {e}")
        return {"error": f"OpenWeather API exception: {e}"}
    # Mock data fallback
    if not weather_data["current"]:
        weather_data["current"] = {
            "temperature": 22,
            "humidity": 65,
            "description": "partly cloudy",
            "wind_speed": 5.2,
            "pressure": 1013
        }
        
        for i in range(input_data.days):
            date = datetime.now() + timedelta(days=i)
            weather_data["forecast"].append({
                "date": date.strftime("%Y-%m-%d"),
                "temperature": 22 + (i % 3),
                "humidity": 65 - (i % 10),
                "description": "partly cloudy",
                "precipitation": 0.1 if i % 3 == 0 else 0
            })
    
    # Generate growing condition recommendations
    current_temp = weather_data["current"]["temperature"]
    current_humidity = weather_data["current"]["humidity"]
    
    weather_data["growing_conditions"] = {
        "watering_recommendation": "normal" if current_humidity > 50 else "increase",
        "outdoor_suitable": current_temp > 10 and current_temp < 35,
        "frost_warning": current_temp < 5,
        "heat_stress_warning": current_temp > 30,
        "humidity_level": "good" if 40 <= current_humidity <= 70 else "monitor"
    }
    
    return weather_data


def plant_care_scheduler(input_data: CareScheduleInput) -> Dict[str, Any]:
    """
    Create personalized care schedules based on plant needs and local conditions.
    
    Generates watering, fertilizing, and maintenance schedules customized for
    specific plants and user location.
    """
    # Get plant information first
    plant_search = plant_database_search(PlantSearchInput(query=input_data.plant_name, limit=1))
    
    if not plant_search["results"]:
        return {"error": f"Plant '{input_data.plant_name}' not found in database"}
    
    plant_info = plant_search["results"][0]
    
    # Get local weather for schedule adjustments
    weather = weather_lookup(WeatherInput(location=input_data.location, days=7))
    
    schedule = {
        "plant_name": input_data.plant_name,
        "location": input_data.location,
        "care_level": input_data.care_level,
        "weekly_schedule": {},
        "monthly_tasks": {},
        "seasonal_adjustments": {},
        "next_actions": []
    }
    
    # Base care schedule
    base_schedules = {
        "easy": {
            "watering": "Every 7-10 days",
            "fertilizing": "Monthly during growing season",
            "pruning": "As needed",
            "inspection": "Weekly"
        },
        "intermediate": {
            "watering": "Every 5-7 days, check soil moisture",
            "fertilizing": "Bi-weekly during growing season",
            "pruning": "Monthly maintenance",
            "inspection": "Twice weekly"
        },
        "advanced": {
            "watering": "Based on soil moisture and weather",
            "fertilizing": "Custom nutrient schedule",
            "pruning": "Strategic pruning for optimal growth",
            "inspection": "Daily monitoring"
        }
    }
    
    care_level = input_data.care_level.lower()
    if care_level not in base_schedules:
        care_level = "intermediate"
    
    schedule["weekly_schedule"] = base_schedules[care_level]
    
    # Adjust based on weather conditions
    if weather.get("growing_conditions", {}).get("watering_recommendation") == "increase":
        schedule["next_actions"].append("Increase watering frequency due to low humidity")
    
    if weather.get("growing_conditions", {}).get("frost_warning"):
        schedule["next_actions"].append("Protect from frost - move indoors or cover")
    
    if weather.get("growing_conditions", {}).get("heat_stress_warning"):
        schedule["next_actions"].append("Provide extra shade and increase humidity")
    
    # Monthly tasks
    current_month = datetime.now().strftime("%B")
    schedule["monthly_tasks"] = {
        current_month: [
            "Check for pests and diseases",
            "Rotate plant for even growth",
            "Clean leaves if dusty",
            "Check soil drainage"
        ]
    }
    
    # Seasonal adjustments
    current_season = "spring"  # Simplified - would calculate based on date and location
    schedule["seasonal_adjustments"] = {
        "spring": "Increase watering and fertilizing as growth resumes",
        "summer": "Monitor for heat stress, increase humidity",
        "fall": "Reduce watering and fertilizing, prepare for dormancy",
        "winter": "Minimal watering, no fertilizing, watch for dry air"
    }
    
    return schedule


def disease_identifier(input_data: DiseaseIdentificationInput) -> Dict[str, Any]:
    """
    Identify plant diseases and pests from symptoms and images.
    
    Analyzes plant symptoms to diagnose common diseases, pests, and disorders,
    providing treatment recommendations.
    """
    diagnosis = {
        "plant_type": input_data.plant_type,
        "symptoms": input_data.symptoms,
        "possible_issues": [],
        "recommended_treatments": [],
        "prevention_tips": [],
        "confidence": 0.0
    }
    
    # Symptom analysis (simplified rule-based system)
    symptoms_lower = input_data.symptoms.lower()
    
    # Common issues database
    issue_database = {
        "yellowing leaves": {
            "issues": ["Overwatering", "Nutrient deficiency", "Natural aging"],
            "treatments": ["Reduce watering frequency", "Check soil drainage", "Apply balanced fertilizer"],
            "confidence": 0.8
        },
        "brown spots": {
            "issues": ["Fungal infection", "Bacterial spot", "Sunburn"],
            "treatments": ["Remove affected leaves", "Improve air circulation", "Apply fungicide if needed"],
            "confidence": 0.7
        },
        "wilting": {
            "issues": ["Underwatering", "Root rot", "Heat stress"],
            "treatments": ["Check soil moisture", "Inspect roots", "Provide shade during hot weather"],
            "confidence": 0.75
        },
        "white powder": {
            "issues": ["Powdery mildew"],
            "treatments": ["Improve air circulation", "Apply neem oil", "Remove affected parts"],
            "confidence": 0.9
        },
        "small insects": {
            "issues": ["Aphids", "Spider mites", "Thrips"],
            "treatments": ["Spray with water", "Apply insecticidal soap", "Introduce beneficial insects"],
            "confidence": 0.8
        }
    }
    
    # Match symptoms to issues
    best_match = None
    best_confidence = 0.0
    
    for symptom_key, issue_data in issue_database.items():
        if symptom_key in symptoms_lower:
            if issue_data["confidence"] > best_confidence:
                best_match = issue_data
                best_confidence = issue_data["confidence"]
    
    if best_match:
        diagnosis["possible_issues"] = best_match["issues"]
        diagnosis["recommended_treatments"] = best_match["treatments"]
        diagnosis["confidence"] = best_confidence
    else:
        # Generic advice for unknown symptoms
        diagnosis["possible_issues"] = ["Unknown condition - requires expert diagnosis"]
        diagnosis["recommended_treatments"] = [
            "Take clear photos of affected areas",
            "Consult local extension service",
            "Isolate plant if possible",
            "Monitor for changes"
        ]
        diagnosis["confidence"] = 0.3
    
    # General prevention tips
    diagnosis["prevention_tips"] = [
        "Maintain proper watering schedule",
        "Ensure good air circulation",
        "Inspect plants regularly",
        "Quarantine new plants",
        "Keep growing area clean"
    ]
    
    # If image URL provided, note that analysis would be enhanced
    if input_data.image_url:
        diagnosis["image_analysis"] = "Image provided - visual analysis would enhance diagnosis accuracy"
    
    return diagnosis


# --- LOCAL ENVIRONMENT AGENT TOOLS ---
def native_plant_finder(input_data: NativePlantInput) -> Dict[str, Any]:
    """
    Find native plants suitable for a specific geographic location.
    
    Searches databases of native plants based on location and provides
    ecological benefits and growing information.
    """
    coords = get_coordinates(input_data.location)
    if not coords:
        return {"error": "Could not determine location coordinates"}
    
    lat, lon = coords
    
    results = {
        "location": input_data.location,
        "coordinates": {"latitude": lat, "longitude": lon},
        "native_plants": [],
        "ecological_benefits": [],
        "planting_seasons": {},
        "sources": []
    }
    
    # Mock native plant database (in production, integrate with GBIF, iNaturalist, etc.)
    native_plant_db = {
        "trees": [
            {
                "scientific_name": "Quercus alba",
                "common_name": "White Oak",
                "type": "tree",
                "height": "50-80 feet",
                "wildlife_value": "Supports 500+ species of butterflies and moths",
                "soil_preference": "Well-drained, acidic to neutral",
                "sun_requirements": "Full sun"
            },
            {
                "scientific_name": "Acer rubrum",
                "common_name": "Red Maple",
                "type": "tree", 
                "height": "40-60 feet",
                "wildlife_value": "Early nectar source for pollinators",
                "soil_preference": "Adaptable to various soil types",
                "sun_requirements": "Full sun to partial shade"
            }
        ],
        "shrubs": [
            {
                "scientific_name": "Viburnum trilobum",
                "common_name": "American Cranberrybush",
                "type": "shrub",
                "height": "8-12 feet",
                "wildlife_value": "Berries feed birds, flowers attract pollinators",
                "soil_preference": "Moist, well-drained",
                "sun_requirements": "Full sun to partial shade"
            }
        ],
        "flowers": [
            {
                "scientific_name": "Echinacea purpurea",
                "common_name": "Purple Coneflower",
                "type": "perennial",
                "height": "2-4 feet",
                "wildlife_value": "Attracts butterflies, seeds feed birds",
                "soil_preference": "Well-drained, drought tolerant",
                "sun_requirements": "Full sun"
            },
            {
                "scientific_name": "Rudbeckia fulgida",
                "common_name": "Black-eyed Susan",
                "type": "perennial",
                "height": "1-3 feet", 
                "wildlife_value": "Long bloom period attracts pollinators",
                "soil_preference": "Adaptable, drought tolerant",
                "sun_requirements": "Full sun to partial shade"
            }
        ]
    }
    
    # Filter by plant type
    plant_type = input_data.plant_type.lower()
    if plant_type == "all":
        for category in native_plant_db.values():
            results["native_plants"].extend(category)
    elif plant_type in native_plant_db:
        results["native_plants"] = native_plant_db[plant_type]
    else:
        # Search across all categories
        for category in native_plant_db.values():
            for plant in category:
                if plant_type in plant["type"].lower() or plant_type in plant["common_name"].lower():
                    results["native_plants"].append(plant)
    
    # Ecological benefits
    results["ecological_benefits"] = [
        "Support local wildlife and pollinators",
        "Require less water and maintenance",
        "Adapted to local climate conditions",
        "Help preserve regional biodiversity",
        "Reduce need for fertilizers and pesticides"
    ]
    
    # Planting seasons (simplified)
    results["planting_seasons"] = {
        "spring": "March-May: Best for most perennials and trees",
        "fall": "September-November: Good for trees and shrubs",
        "summer": "June-August: Limited planting, focus on maintenance",
        "winter": "December-February: Planning and preparation"
    }
    
    results["sources"] = ["Mock Native Plant Database"]
    
    return results


def soil_analyzer(input_data: SoilAnalysisInput) -> Dict[str, Any]:
    """
    Analyze soil conditions and provide improvement recommendations.
    
    Provides soil type information, pH levels, nutrient content, and
    recommendations for soil amendments.
    """
    coords = get_coordinates(input_data.location)
    if not coords:
        return {"error": "Could not determine location coordinates"}
    
    lat, lon = coords
    
    analysis = {
        "location": input_data.location,
        "coordinates": {"latitude": lat, "longitude": lon},
        "soil_type": "",
        "ph_level": 0.0,
        "nutrients": {},
        "drainage": "",
        "recommendations": [],
        "amendments": [],
        "sources": []
    }
    
    # Mock soil data (in production, integrate with USDA Web Soil Survey)
    # Simplified soil classification based on general regional patterns
    soil_types = ["clay", "sandy", "loam", "silt"]
    import random
    random.seed(int(lat * lon * 1000))  # Consistent results for same location
    
    analysis["soil_type"] = random.choice(soil_types)
    analysis["ph_level"] = round(random.uniform(5.5, 8.0), 1)
    analysis["drainage"] = random.choice(["poor", "moderate", "good", "excellent"])
    
    # Mock nutrient levels
    analysis["nutrients"] = {
        "nitrogen": random.choice(["low", "moderate", "high"]),
        "phosphorus": random.choice(["low", "moderate", "high"]),
        "potassium": random.choice(["low", "moderate", "high"]),
        "organic_matter": f"{random.randint(2, 8)}%"
    }
    
    # Generate recommendations based on soil analysis
    recommendations = []
    amendments = []
    
    # pH recommendations
    if analysis["ph_level"] < 6.0:
        recommendations.append("Soil is acidic - consider adding lime to raise pH")
        amendments.append("Agricultural lime")
    elif analysis["ph_level"] > 7.5:
        recommendations.append("Soil is alkaline - consider adding sulfur to lower pH")
        amendments.append("Elemental sulfur")
    else:
        recommendations.append("Soil pH is in good range for most plants")
    
    # Drainage recommendations
    if analysis["drainage"] == "poor":
        recommendations.append("Improve drainage by adding organic matter or creating raised beds")
        amendments.append("Compost, perlite, or coarse sand")
    elif analysis["drainage"] == "excellent":
        recommendations.append("Soil drains quickly - may need more frequent watering")
        amendments.append("Compost to improve water retention")
    
    # Nutrient recommendations
    for nutrient, level in analysis["nutrients"].items():
        if level == "low" and nutrient != "organic_matter":
            recommendations.append(f"Low {nutrient} - consider appropriate fertilizer")
            if nutrient == "nitrogen":
                amendments.append("Nitrogen-rich fertilizer or compost")
            elif nutrient == "phosphorus":
                amendments.append("Bone meal or rock phosphate")
            elif nutrient == "potassium":
                amendments.append("Potash or wood ash")
    
    # Soil type specific recommendations
    if analysis["soil_type"] == "clay":
        recommendations.append("Clay soil - improve drainage and aeration with organic matter")
        amendments.append("Compost, aged manure")
    elif analysis["soil_type"] == "sandy":
        recommendations.append("Sandy soil - improve water and nutrient retention")
        amendments.append("Compost, peat moss")
    
    analysis["recommendations"] = recommendations
    analysis["amendments"] = amendments
    analysis["sources"] = ["Mock Soil Database", "USDA Soil Survey (simulated)"]
    
    # If user provided soil sample data, incorporate it
    if input_data.soil_sample_data:
        analysis["user_test_results"] = input_data.soil_sample_data
        analysis["recommendations"].append("User soil test data incorporated into analysis")
    
    return analysis


def hardiness_zone_lookup(input_data: HardinessZoneInput) -> Dict[str, Any]:
    """
    Determine USDA hardiness zone and climate information for a location.
    
    Provides hardiness zone, average temperatures, frost dates, and
    growing season information.
    """
    coords = get_coordinates(input_data.location)
    if not coords:
        return {"error": "Could not determine location coordinates"}
    
    lat, lon = coords
    
    zone_info = {
        "location": input_data.location,
        "coordinates": {"latitude": lat, "longitude": lon},
        "hardiness_zone": "",
        "temperature_range": {},
        "frost_dates": {},
        "growing_season": {},
        "climate_description": "",
        "sources": []
    }
    
    # Simplified hardiness zone calculation based on latitude
    # In production, use USDA hardiness zone API or database
    if lat >= 45:
        zone = "3a-4b"
        min_temp = -40
        max_temp = -20
        climate = "Cold climate with short growing season"
    elif lat >= 40:
        zone = "5a-6b"
        min_temp = -20
        max_temp = -5
        climate = "Temperate climate with moderate growing season"
    elif lat >= 35:
        zone = "7a-8b"
        min_temp = 0
        max_temp = 20
        climate = "Mild climate with long growing season"
    elif lat >= 30:
        zone = "9a-10b"
        min_temp = 20
        max_temp = 40
        climate = "Warm climate with extended growing season"
    else:
        zone = "11a-12b"
        min_temp = 40
        max_temp = 60
        climate = "Tropical climate with year-round growing"
    
    zone_info["hardiness_zone"] = zone
    zone_info["temperature_range"] = {
        "min_winter_temp_f": min_temp,
        "max_winter_temp_f": max_temp
    }
    zone_info["climate_description"] = climate
    
    # Estimate frost dates based on zone
    if "3" in zone or "4" in zone:
        zone_info["frost_dates"] = {
            "last_spring_frost": "May 15 - June 1",
            "first_fall_frost": "September 1 - September 15"
        }
        zone_info["growing_season"] = {
            "length": "90-120 days",
            "start": "Late May",
            "end": "Early September"
        }
    elif "5" in zone or "6" in zone:
        zone_info["frost_dates"] = {
            "last_spring_frost": "April 15 - May 15",
            "first_fall_frost": "October 1 - October 15"
        }
        zone_info["growing_season"] = {
            "length": "150-180 days",
            "start": "Mid April",
            "end": "Mid October"
        }
    elif "7" in zone or "8" in zone:
        zone_info["frost_dates"] = {
            "last_spring_frost": "March 15 - April 15",
            "first_fall_frost": "November 1 - November 15"
        }
        zone_info["growing_season"] = {
            "length": "200-240 days",
            "start": "Mid March",
            "end": "Mid November"
        }
    else:
        zone_info["frost_dates"] = {
            "last_spring_frost": "Rare or no frost",
            "first_fall_frost": "Rare or no frost"
        }
        zone_info["growing_season"] = {
            "length": "Year-round",
            "start": "Year-round",
            "end": "Year-round"
        }
    
    zone_info["sources"] = ["USDA Hardiness Zone Map (simulated)"]
    
    return zone_info


# --- MARKETPLACE AGENT TOOLS ---
def marketplace_search(input_data: MarketplaceSearchInput) -> Dict[str, Any]:
    """
    Search multiple plant marketplaces and nurseries for plant availability.
    
    Searches various online plant retailers including The Sill, local nurseries,
    and other plant marketplaces.
    """
    results = {
        "plant_name": input_data.plant_name,
        "location": input_data.location,
        "max_price": input_data.max_price,
        "products": [],
        "total_found": 0,
        "sources": []
    }
    
    # Mock marketplace data with real retailer information
    marketplace_data = {
        "monstera": [
            {
                "seller": "The Sill",
                "price": 35.00,
                "size": "4-inch pot",
                "availability": "In Stock",
                "url": "https://www.thesill.com/products/monstera-deliciosa",
                "affiliate_commission": 10,
                "shipping_cost": 15.00,
                "shipping_free_over": 50.00,
                "rating": 4.8,
                "reviews": 1250
            },
            {
                "seller": "Bloomscape",
                "price": 45.00,
                "size": "6-inch pot",
                "availability": "In Stock",
                "url": "https://bloomscape.com/product/monstera-deliciosa/",
                "affiliate_commission": 8,
                "shipping_cost": 20.00,
                "shipping_free_over": 65.00,
                "rating": 4.7,
                "reviews": 890
            },
            {
                "seller": "Planterina",
                "price": 28.00,
                "size": "4-inch pot",
                "availability": "Limited Stock",
                "url": "https://planterina.com/products/monstera-deliciosa",
                "affiliate_commission": 12,
                "shipping_cost": 12.00,
                "shipping_free_over": 40.00,
                "rating": 4.6,
                "reviews": 567
            }
        ],
        "snake plant": [
            {
                "seller": "The Sill",
                "price": 28.00,
                "size": "4-inch pot",
                "availability": "In Stock",
                "url": "https://www.thesill.com/products/snake-plant",
                "affiliate_commission": 10,
                "shipping_cost": 15.00,
                "shipping_free_over": 50.00,
                "rating": 4.9,
                "reviews": 2100
            },
            {
                "seller": "Planterina",
                "price": 22.00,
                "size": "4-inch pot",
                "availability": "In Stock",
                "url": "https://planterina.com/products/snake-plant",
                "affiliate_commission": 12,
                "shipping_cost": 12.00,
                "shipping_free_over": 40.00,
                "rating": 4.8,
                "reviews": 890
            }
        ],
        "fiddle leaf fig": [
            {
                "seller": "The Sill",
                "price": 65.00,
                "size": "6-inch pot",
                "availability": "In Stock",
                "url": "https://www.thesill.com/products/fiddle-leaf-fig",
                "affiliate_commission": 10,
                "shipping_cost": 25.00,
                "shipping_free_over": 75.00,
                "rating": 4.5,
                "reviews": 756
            },
            {
                "seller": "Bloomscape",
                "price": 75.00,
                "size": "8-inch pot",
                "availability": "In Stock",
                "url": "https://bloomscape.com/product/fiddle-leaf-fig/",
                "affiliate_commission": 8,
                "shipping_cost": 30.00,
                "shipping_free_over": 85.00,
                "rating": 4.4,
                "reviews": 432
            }
        ]
    }
    
    # Search for plant
    plant_key = input_data.plant_name.lower()
    found_products = []
    
    # Direct match
    if plant_key in marketplace_data:
        found_products = marketplace_data[plant_key]
    else:
        # Fuzzy search
        for key, products in marketplace_data.items():
            if plant_key in key or key in plant_key:
                found_products = products
                break
    
    # Filter by price if specified
    if input_data.max_price and found_products:
        found_products = [p for p in found_products if p["price"] <= input_data.max_price]
    
    # Add affiliate tracking parameters
    for product in found_products:
        if "thesill.com" in product["url"]:
            product["affiliate_url"] = f"{product['url']}?ref=plantworks&utm_source=plantworks"
        elif "bloomscape.com" in product["url"]:
            product["affiliate_url"] = f"{product['url']}?ref=plantworks"
        elif "planterina.com" in product["url"]:
            product["affiliate_url"] = f"{product['url']}?ref=plantworks"
        else:
            product["affiliate_url"] = product["url"]
    
    results["products"] = found_products
    results["total_found"] = len(found_products)
    results["sources"] = ["The Sill", "Bloomscape", "Planterina"]
    
    return results


def price_comparator(input_data: PriceComparisonInput) -> Dict[str, Any]:
    """
    Compare prices for a specific plant across multiple sellers.
    
    Provides detailed price comparison including shipping costs, sizes,
    and value analysis.
    """
    # Use marketplace search to get current prices
    marketplace_results = marketplace_search(
        MarketplaceSearchInput(
            plant_name=input_data.plant_name,
            location="nationwide"  # For price comparison, check all sources
        )
    )
    
    comparison = {
        "plant_name": input_data.plant_name,
        "size_filter": input_data.size,
        "price_analysis": {},
        "best_value": {},
        "price_trends": {},
        "recommendations": []
    }
    
    if not marketplace_results.get("products"):
        return {"error": f"No price data found for {input_data.plant_name}"}
    
    results = marketplace_results["products"]
    
    # Filter by size if specified
    if input_data.size:
        size_filtered = [r for r in results if input_data.size.lower() in r.get("size", "").lower()]
        if size_filtered:
            results = size_filtered
    
    # Price analysis
    prices = [r["price"] for r in results]
    
    comparison["price_analysis"] = {
        "lowest_price": min(prices),
        "highest_price": max(prices),
        "average_price": round(sum(prices) / len(prices), 2),
        "price_spread": max(prices) - min(prices)
    }
    
    # Find best value (considering price, rating, and shipping)
    best_value_product = None
    best_value_score = 0
    
    for product in results:
        # Calculate value score (rating * 20 - price + shipping consideration)
        shipping_penalty = 0 if product["price"] >= product.get("shipping_free_over", 999) else product.get("shipping_cost", 0)
        value_score = (product["rating"] * 20) - product["price"] - (shipping_penalty * 0.5)
        
        if value_score > best_value_score:
            best_value_score = value_score
            best_value_product = product
    
    if best_value_product:
        comparison["best_value"] = {
            "seller": best_value_product["seller"],
            "price": best_value_product["price"],
            "rating": best_value_product["rating"],
            "value_score": round(best_value_score, 2)
        }
    
    # Generate recommendations
    recommendations = []
    
    # Price recommendations
    if comparison["price_analysis"]["price_spread"] > 10:
        recommendations.append(f"Significant price variation found (${comparison['price_analysis']['price_spread']:.2f} spread)")
    
    # Featured partner recommendation
    the_sill_result = next((r for r in results if "sill" in r["seller"].lower()), None)
    if the_sill_result:
        recommendations.append(f"The Sill (our partner) offers this plant for ${the_sill_result['price']:.2f}")
    
    comparison["recommendations"] = recommendations
    
    # Mock price trends (in production, track historical data)
    comparison["price_trends"] = {
        "trend": "stable",
        "seasonal_note": "Prices typically higher in spring planting season",
        "recommendation": "Current prices are typical for this time of year"
    }
    
    return comparison


def seller_verifier(input_data: SellerVerificationInput) -> Dict[str, Any]:
    """
    Verify seller reputation and quality ratings.
    
    Checks seller credentials, customer reviews, return policies,
    and overall trustworthiness.
    """
    verification = {
        "seller_name": input_data.seller_name,
        "platform": input_data.platform,
        "verification_status": "",
        "trust_score": 0.0,
        "credentials": {},
        "customer_feedback": {},
        "policies": {},
        "red_flags": [],
        "recommendations": []
    }
    
    # Mock seller database (in production, integrate with review APIs, BBB, etc.)
    seller_database = {
        "the sill": {
            "verification_status": "Verified Business",
            "trust_score": 4.5,
            "years_in_business": 8,
            "bbb_rating": "A+",
            "total_reviews": 15000,
            "positive_review_percentage": 87,
            "return_policy": "30-day guarantee",
            "shipping_guarantee": "Safe arrival guaranteed",
            "certifications": ["Certified Plant Retailer", "Sustainable Business"],
            "red_flags": []
        },
        "bloomscape": {
            "verification_status": "Verified Business",
            "trust_score": 4.3,
            "years_in_business": 6,
            "bbb_rating": "A",
            "total_reviews": 8500,
            "positive_review_percentage": 82,
            "return_policy": "30-day guarantee",
            "shipping_guarantee": "Safe arrival guaranteed",
            "certifications": ["Certified Plant Retailer"],
            "red_flags": []
        },
        "planterina": {
            "verification_status": "Verified Business",
            "trust_score": 4.6,
            "years_in_business": 4,
            "bbb_rating": "A",
            "total_reviews": 3200,
            "positive_review_percentage": 89,
            "return_policy": "14-day return",
            "shipping_guarantee": "Safe arrival guaranteed",
            "certifications": ["Certified Plant Retailer"],
            "red_flags": []
        },
        "local garden center": {
            "verification_status": "Local Business",
            "trust_score": 4.7,
            "years_in_business": 25,
            "bbb_rating": "A+",
            "total_reviews": 450,
            "positive_review_percentage": 94,
            "return_policy": "14-day return",
            "shipping_guarantee": "N/A - Local pickup",
            "certifications": ["Master Gardener Certified"],
            "red_flags": []
        }
    }
    
    seller_key = input_data.seller_name.lower()
    
    if seller_key in seller_database:
        seller_data = seller_database[seller_key]
        
        verification["verification_status"] = seller_data["verification_status"]
        verification["trust_score"] = seller_data["trust_score"]
        
        verification["credentials"] = {
            "years_in_business": seller_data["years_in_business"],
            "bbb_rating": seller_data["bbb_rating"],
            "certifications": seller_data["certifications"]
        }
        
        verification["customer_feedback"] = {
            "total_reviews": seller_data["total_reviews"],
            "positive_percentage": seller_data["positive_review_percentage"],
            "average_rating": seller_data["trust_score"]
        }
        
        verification["policies"] = {
            "return_policy": seller_data["return_policy"],
            "shipping_guarantee": seller_data["shipping_guarantee"]
        }
        
        verification["red_flags"] = seller_data["red_flags"]
        
        # Generate recommendations based on data
        recommendations = []
        
        if seller_data["trust_score"] >= 4.0:
            recommendations.append("Highly rated seller with good customer satisfaction")
        
        if seller_data["years_in_business"] >= 5:
            recommendations.append("Established business with proven track record")
        
        if "guarantee" in seller_data["shipping_guarantee"].lower():
            recommendations.append("Offers shipping protection for live plants")
        
        if seller_data["positive_review_percentage"] >= 85:
            recommendations.append("Strong positive review percentage")
        
        verification["recommendations"] = recommendations
        
    else:
        # Unknown seller - provide generic verification advice
        verification["verification_status"] = "Unknown - Requires Manual Verification"
        verification["trust_score"] = 0.0
        verification["red_flags"] = ["Seller not in verified database"]
        verification["recommendations"] = [
            "Research seller independently before purchasing",
            "Check for customer reviews on multiple platforms",
            "Verify return and shipping policies",
            "Start with a small order to test service quality",
            "Look for business registration and contact information"
        ]
    
    return verification
