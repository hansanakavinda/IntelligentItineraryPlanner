SYNTHETIC_PROFILES = [
    {
        "profile_name": "nature_lover_low_budget",
        "category": ["Nature"],
        "time_limit": 3,
        "budget": 1000,
        "crowdedness": False,
        "user_location": (6.05, 80.22),
        # Test validation fields
        "max_budget": 1000,
        "expected_keywords": ["Forest", "Reserve", "Sanctuary", "Lake", "Lagoon"],
        "should_be_crowded": False
    },
    {
        "profile_name": "adventure_seeker_time_rich",
        "category": ["Water Activity", "Surf Spot"],
        "time_limit": 10,
        "budget": 10000,
        "crowdedness": None,
        "user_location": (6.1, 80.2),
        # Test validation fields
        "max_budget": 10000,
        "min_total_time": 2,
        "expected_keywords": ["Surf", "Diving", "Water", "PADI", "Dive"]
    },
    {
        "profile_name": "historical_and_cultural_enthusiast",
        "category": ["Historical", "Cultural"],
        "time_limit": 5,
        "budget": 3000,
        "crowdedness": True,
        "user_location": (6.08, 80.22),
        # Test validation fields
        "max_budget": 3000,
        "expected_keywords": ["Fort", "Temple", "Cultural", "Heritage", "Historical", "Tea"],
        "should_be_crowded": True
    },
    {
        "profile_name": "beach_lover_moderate_budget",
        "category": ["Beach"],
        "time_limit": 6,
        "budget": 2000,
        "crowdedness": None,
        "user_location": (5.95, 80.45),
        # Test validation fields
        "max_budget": 2000,
        "expected_keywords": ["Beach", "Sand", "Coast", "Bay", "Swimming"]
    },
    {
        "profile_name": "wildlife_photographer_patient",
        "category": ["Wildlife"],
        "time_limit": 8,
        "budget": 5000,
        "crowdedness": False,
        "user_location": (6.25, 81.0),
        # Test validation fields
        "max_budget": 5000,
        "min_total_time": 3,
        "expected_keywords": ["Safari", "Park", "Wildlife", "Turtle", "Bird"],
        "should_be_crowded": False
    },
    {
        "profile_name": "quick_sightseeing_tourist",
        "category": ["Landmark", "Historical"],
        "time_limit": 2,
        "budget": 500,
        "crowdedness": True,
        "user_location": (6.0, 80.2),
        # Test validation fields
        "max_budget": 500,
        "expected_keywords": ["Lighthouse", "Fort", "Pagoda", "Point"]
    },
    {
        "profile_name": "cultural_immersion_seeker",
        "category": ["Cultural"],
        "time_limit": 4,
        "budget": 1500,
        "crowdedness": None,
        "user_location": (6.0, 80.4),
        # Test validation fields
        "max_budget": 1500,
        "expected_keywords": ["Temple", "Fishermen", "Tea", "Traditional", "Shrine"]
    },
    {
        "profile_name": "extreme_budget_backpacker",
        "category": ["Beach", "Nature", "Cultural"],
        "time_limit": 12,
        "budget": 100,
        "crowdedness": None,
        "user_location": (5.98, 80.3),
        # Test validation fields
        "max_budget": 100,
        "expected_keywords": ["Free", "Beach", "Temple", "Nature"]
    },
    {
        "profile_name": "luxury_traveler_no_time_limit",
        "category": ["Water Activity", "Wildlife", "Historical"],
        "time_limit": 24,
        "budget": 50000,
        "crowdedness": None,
        "user_location": (6.1, 80.5),
        # Test validation fields
        "max_budget": 50000,
        "min_total_time": 2,
        "expected_keywords": ["PADI", "Safari", "Fort", "Diving", "Park"]
    },
    {
        "profile_name": "family_with_kids_safe_places",
        "category": ["Beach", "Nature", "Wildlife"],
        "time_limit": 4,
        "budget": 3500,
        "crowdedness": True,
        "user_location": (6.0, 80.25),
        # Test validation fields
        "max_budget": 3500,
        "expected_keywords": ["Beach", "Turtle", "Sanctuary", "Hatchery", "Family"],
        "should_be_crowded": True
    }
]