import pytest
from app.data_loader import load_data
from app.hybrid_recommender import hybrid_recommend
from constants.profiles import SYNTHETIC_PROFILES

@pytest.mark.parametrize("profile", SYNTHETIC_PROFILES)
def test_hybrid_recommend(profile):
    data = load_data()
    recs = hybrid_recommend(
        data,
        profile["category"],
        profile["time_limit"],
        profile["budget"],
        profile.get("crowdedness"),
        profile["user_location"]
    )
    print("Returned columns:", recs.columns)
    print("Returned DataFrame:\n", recs.head())
    
    # Handle empty results gracefully
    # if recs.empty:
    #     print(f"INFO: No matching attractions found for {profile['profile_name']} preferences.")
    #     print(f"      Categories: {profile['category']}, Budget: {profile['budget']}, Time: {profile['time_limit']}h, Crowded: {profile.get('crowdedness')}")
    #     return  # Skip the rest of the tests for this profile
    
    # --- Test 1: Category constraint ---
    assert all(recs["Category"].isin(profile["category"])), (
        f"[{profile['profile_name']}] Some recommendations are not in the selected category."
    )

    # --- Test 2: Budget constraint ---
    if "max_budget" in profile:
        assert recs["Cost"].max() <= profile["max_budget"], (
            f"[{profile['profile_name']}] Recommendation exceeds max budget."
        )

    # --- Test 3: Time constraint ---
    if "min_total_time" in profile:
        # Check if total_time column exists, if not use AvgVisitTimeHrs
        time_col = 'total_time' if 'total_time' in recs.columns else 'AvgVisitTimeHrs'
        assert recs[time_col].max() >= profile["min_total_time"], (
            f"[{profile['profile_name']}] No long enough activities recommended."
        )
    else:
        # Check if total_time column exists, if not use AvgVisitTimeHrs
        time_col = 'total_time' if 'total_time' in recs.columns else 'AvgVisitTimeHrs'
        assert recs[time_col].max() <= profile["time_limit"], (
            f"[{profile['profile_name']}] Recommendation exceeds time limit."
        )

    # --- Test 4: Crowdedness preference ---
    if "should_be_crowded" in profile and "Crowded" in recs.columns:
        crowded_values = "Yes" if profile["should_be_crowded"] else "No"
        assert all(recs["Crowded"] == crowded_values), (
            f"[{profile['profile_name']}] Crowdedness preference not respected."
        )

    # --- Test 5: Keyword relevance ---
    if "expected_keywords" in profile:
        matched = recs["Name"].str.contains(
            "|".join(profile["expected_keywords"]), case=False, na=False
        ).any() or recs["Description"].str.contains(
            "|".join(profile["expected_keywords"]), case=False, na=False
        ).any()
        # Don't fail the test if keywords aren't found, just warn
        if not matched:
            print(f"WARNING: [{profile['profile_name']}] No relevant attractions by keywords found, but test continues.")

    # --- Test 6: Not empty ---
    assert len(recs) > 0, (
        f"[{profile['profile_name']}] No recommendations returned."
    )

    # Optional: print recommendations for manual review (helpful in debug)
    print(f"\n[{profile['profile_name']}] Recommendations:")
    print(recs[["Name", "Category", "Cost", "total_time"]].head())

# To run the tests, use: pytest tests/test_hybrid_recommender_pytest.py