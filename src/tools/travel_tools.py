from typing import Dict, List, Tuple

DESTINATIONS: Dict[str, Dict[str, str]] = {
    "da nang": {
        "region": "central vietnam",
        "highlights": "my khe beach, ba na hills, dragon bridge",
        "best_season": "march to august",
        "food": "mi quang, banh xeo, seafood",
    },
    "phu quoc": {
        "region": "southern island",
        "highlights": "long beach, hon thom, snorkel tours",
        "best_season": "november to april",
        "food": "seafood, bun quay",
    },
    "sapa": {
        "region": "northern highland",
        "highlights": "fansipan, terraced fields, villages",
        "best_season": "september to november",
        "food": "thang co, grilled dishes",
    },
    "hoi an": {
        "region": "central vietnam",
        "highlights": "ancient town, lantern streets, an bang beach",
        "best_season": "february to april",
        "food": "cao lau, chicken rice",
    },
    "nha trang": {
        "region": "south central coast",
        "highlights": "beaches, vinwonders, island hopping",
        "best_season": "january to august",
        "food": "nem nuong, jellyfish noodle",
    },
}

WEATHER_DATA: Dict[Tuple[str, str], str] = {
    ("da nang", "6"): "28-35C, sunny, low rain, great for beach activities.",
    ("phu quoc", "6"): "26-32C, humid, occasional rain, plan indoor backup.",
    ("sapa", "12"): "5-15C, cold and dry, warm clothes recommended.",
    ("hoi an", "6"): "27-34C, sunny, good for walking and river activities.",
    ("nha trang", "7"): "27-34C, sunny, calm sea on most days.",
}

HOTEL_PRICES: Dict[Tuple[str, str], int] = {
    ("da nang", "3"): 500_000,
    ("da nang", "4"): 800_000,
    ("da nang", "5"): 1_800_000,
    ("phu quoc", "3"): 700_000,
    ("phu quoc", "4"): 1_200_000,
    ("phu quoc", "5"): 2_500_000,
    ("hoi an", "3"): 450_000,
    ("hoi an", "4"): 750_000,
    ("hoi an", "5"): 1_600_000,
    ("nha trang", "3"): 550_000,
    ("nha trang", "4"): 850_000,
    ("nha trang", "5"): 1_900_000,
}

FOOD_COSTS: Dict[Tuple[str, str], int] = {
    ("da nang", "low"): 180_000,
    ("da nang", "mid"): 300_000,
    ("da nang", "high"): 600_000,
    ("phu quoc", "low"): 250_000,
    ("phu quoc", "mid"): 380_000,
    ("phu quoc", "high"): 700_000,
    ("hoi an", "low"): 160_000,
    ("hoi an", "mid"): 280_000,
    ("hoi an", "high"): 550_000,
    ("nha trang", "low"): 200_000,
    ("nha trang", "mid"): 320_000,
    ("nha trang", "high"): 620_000,
}

ATTRACTIONS: Dict[Tuple[str, str], List[str]] = {
    ("da nang", "beach"): [
        "My Khe Beach (free)",
        "Ba Na Hills (~900000 VND)",
        "Cham Islands tour (~500000 VND)",
    ],
    ("da nang", "culture"): [
        "Marble Mountains (~40000 VND)",
        "Cham Museum (~60000 VND)",
        "Hoi An day trip (~300000 VND)",
    ],
    ("hoi an", "culture"): [
        "Ancient Town ticket (~120000 VND)",
        "Japanese Bridge (included in town ticket)",
        "Lantern boat on Hoai river (~150000 VND)",
    ],
    ("nha trang", "adventure"): [
        "Scuba intro dive (~1200000 VND)",
        "Island hopping tour (~600000 VND)",
        "VinWonders cable car and park (~950000 VND)",
    ],
    ("phu quoc", "food"): [
        "Duong Dong night market (pay-per-dish)",
        "Ham Ninh seafood village (~300000-600000 VND/meal)",
        "Fish sauce factory visit (free)",
    ],
}


def _normalize_city(city: str) -> str:
    return city.strip().lower()


def search_destination(city: str) -> str:
    """Input: city (string). Output: short destination profile and best season."""
    key = _normalize_city(city)
    info = DESTINATIONS.get(key)
    if not info:
        return f"No destination data found for '{city}'."

    return (
        f"{city.title()} is in {info['region']}. Highlights: {info['highlights']}. "
        f"Best season: {info['best_season']}. Local food: {info['food']}."
    )


def get_weather(city: str, month: str) -> str:
    """Input: city (string), month (string). Output: weather summary and recommendation."""
    key = (_normalize_city(city), month.strip())
    weather = WEATHER_DATA.get(key)
    if not weather:
        return f"No weather data found for city='{city}', month='{month}'."
    return f"Weather in {city.title()} month {month}: {weather}"


def get_hotel_price(city: str, star_level: str, nights: str) -> str:
    """Input: city, star_level ('3'/'4'/'5'), nights. Output: nightly price and total."""
    key = (_normalize_city(city), star_level.strip())
    nightly_price = HOTEL_PRICES.get(key)
    if nightly_price is None:
        return f"No hotel price data for city='{city}', star='{star_level}'."

    try:
        n_nights = int(nights)
    except ValueError:
        return f"Invalid nights value: '{nights}'. Must be an integer string."

    total = nightly_price * n_nights
    return (
        f"Hotel {star_level}-star in {city.title()}: ~{nightly_price:,} VND/night. "
        f"{n_nights} nights total: {total:,} VND."
    )


def estimate_food_cost(city: str, days: str, budget_level: str) -> str:
    """Input: city, days, budget_level ('low'/'mid'/'high'). Output: food/day and total."""
    key = (_normalize_city(city), budget_level.strip().lower())
    cost_per_day = FOOD_COSTS.get(key)
    if cost_per_day is None:
        return f"No food cost data for city='{city}', budget_level='{budget_level}'."

    try:
        n_days = int(days)
    except ValueError:
        return f"Invalid days value: '{days}'. Must be an integer string."

    total = cost_per_day * n_days
    return (
        f"Food cost ({budget_level}) in {city.title()}: ~{cost_per_day:,} VND/day. "
        f"{n_days} days total: {total:,} VND."
    )


def search_attraction(city: str, interest: str) -> str:
    """Input: city, interest ('beach'/'culture'/'adventure'/'food'). Output: top attractions."""
    key = (_normalize_city(city), interest.strip().lower())
    places = ATTRACTIONS.get(key)
    if not places:
        return f"No attraction data for city='{city}', interest='{interest}'."

    lines = [f"Top attractions in {city.title()} for {interest}:"]
    for idx, place in enumerate(places, start=1):
        lines.append(f"{idx}. {place}")
    return "\n".join(lines)


def check_budget(total_cost: str, budget: str) -> str:
    """Input: total_cost (string), budget (string). Output: budget status and recommendation."""
    try:
        total = int(total_cost.replace(",", "").strip())
        cap = int(budget.replace(",", "").strip())
    except ValueError:
        return "Invalid number format for total_cost or budget."

    delta = cap - total
    if delta > 0:
        return f"Total: {total:,} VND. Budget: {cap:,} VND. Remaining: {delta:,} VND."
    if delta == 0:
        return f"Total: {total:,} VND. Budget: {cap:,} VND. Exactly on budget."
    return f"Total: {total:,} VND. Budget: {cap:,} VND. Over budget: {abs(delta):,} VND."
