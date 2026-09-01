"""Sanity tests for Robo-Teacher V2 adaptive learner memory."""

from unittest.mock import patch

import learner_profile


assert learner_profile.classify_topic("Please explain HCF of 12 and 18") == "Factors/HCF/LCM"
assert learner_profile.classify_topic("How do I add 1/3 and 1/4?") == "Fractions/Decimals"
assert learner_profile.classify_topic("What is 25 percent of 80?") == "Percentages/Ratio"
assert learner_profile.classify_topic("Solve x + 4 = 10") == "Algebra"
assert learner_profile.classify_topic("A trader made a profit of 500 naira") == "Financial Mathematics"
print("Topic classification OK")

base = dict(learner_profile.DEFAULT_PROFILE)
base["topic_counts"] = {}
base["recent_questions"] = []

saved = {}

def fake_load(_pilot_id):
    return {
        **base,
        "topic_counts": dict(base["topic_counts"]),
        "recent_questions": list(base["recent_questions"]),
    }


def fake_save(pilot_id, profile):
    saved[pilot_id] = profile


with patch("learner_profile.load_profile", side_effect=fake_load), \
     patch("learner_profile.save_profile", side_effect=fake_save):
    profile = learner_profile.update_profile_from_message(
        "ISE001",
        "Please explain fractions in a simpler way",
    )

assert profile["last_topic"] == "Fractions/Decimals"
assert profile["topic_counts"]["Fractions/Decimals"] == 1
assert profile["preferred_explanation_style"] == "simple"
assert saved["ISE001"]["recent_questions"][-1].startswith("Please explain fractions")
print("Adaptive profile update OK")

context = learner_profile.profile_prompt_context(profile)
assert "Preferred explanation style: simple" in context
assert "Fractions/Decimals (1)" in context
assert "Do not claim certainty about mastery" in context
print("Profile prompt context OK")

language_profile = {
    **base,
    "topic_counts": {},
    "recent_questions": [],
}
learner_profile._infer_preferences(language_profile, "Please explain this in Yoruba and make it easier")
assert language_profile["language_preference"] == "Yoruba"
assert language_profile["difficulty_level"] == "supportive"
print("Preference inference OK")

print("\nAll V2 learner-profile sanity checks passed.")
