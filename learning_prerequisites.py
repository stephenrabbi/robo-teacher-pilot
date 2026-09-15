"""Conservative prerequisite graph for Junior Secondary Mathematics.

The graph stays inside the learner's selected JSS class. It is used only to
sequence support when evidence suggests that a harder topic may be blocked by
an earlier foundation. It does not infer failure from curriculum order alone.
"""

from __future__ import annotations

from curriculum import CLASS_TOPICS


# Direct prerequisites only, ordered from the closest/most useful foundation
# to check first. Topics without a meaningful same-class prerequisite are
# intentionally omitted rather than forcing an artificial dependency.
PREREQUISITES: dict[str, dict[str, tuple[str, ...]]] = {
    "JSS1": {
        "Factors, Multiples, LCM & HCF": ("Whole Numbers",),
        "Fractions": ("Factors, Multiples, LCM & HCF",),
        "Estimation": ("Whole Numbers",),
        "Decimals & Approximation": ("Fractions", "Estimation"),
        "Number Bases (Binary)": ("Whole Numbers",),
        "Positive & Negative Integers": ("Whole Numbers",),
        "Introductory Algebra": ("Positive & Negative Integers",),
        "Simple Equations": ("Introductory Algebra",),
        "Plane Shapes & Mensuration": ("Decimals & Approximation",),
        "3D Shapes & Volume": ("Plane Shapes & Mensuration",),
        "Angles & Construction": ("Plane Shapes & Mensuration",),
        "Data Presentation": ("Whole Numbers",),
        "Mean, Median & Mode": ("Data Presentation",),
    },
    "JSS2": {
        "Commercial Arithmetic": ("Fractions, Ratios, Decimals & Percentages",),
        "Algebraic Expressions & Factorisation": ("Directed Numbers",),
        "Algebraic Fractions": (
            "Fractions, Ratios, Decimals & Percentages",
            "Algebraic Expressions & Factorisation",
        ),
        "Simple Equations": ("Algebraic Expressions & Factorisation",),
        "Linear Inequalities": ("Simple Equations", "Directed Numbers"),
        "Linear Graphs": ("Simple Equations",),
        "Plane Shapes & Scale Drawing": ("Fractions, Ratios, Decimals & Percentages",),
        "Angles & Polygons": ("Plane Shapes & Scale Drawing",),
        "Elevation & Depression": ("Angles & Polygons",),
        "Bearings & Distances": ("Angles & Polygons",),
        "Pythagoras & Mensuration": ("Plane Shapes & Scale Drawing",),
        "Probability": (
            "Fractions, Ratios, Decimals & Percentages",
            "Statistics & Data Presentation",
        ),
    },
    "JSS3": {
        "Equations Involving Fractions": ("Factorisation & Quadratic Expressions",),
        "Simultaneous Equations": ("Equations Involving Fractions",),
        "Similar Shapes": ("Ratio, Proportion & Variation",),
        "Trigonometry": ("Similar Shapes",),
        "Geometry & Construction": ("Similar Shapes",),
        "Mensuration & Volumes": ("Similar Shapes",),
        "Pie Charts": ("Statistics & Averages", "Ratio, Proportion & Variation"),
        "Commercial Arithmetic": ("Ratio, Proportion & Variation",),
    },
}


def direct_prerequisites(class_level: str, topic: str) -> tuple[str, ...]:
    """Return only valid same-class direct prerequisites for one topic."""
    if class_level not in CLASS_TOPICS:
        return ()
    topics = set(CLASS_TOPICS[class_level])
    return tuple(
        prerequisite
        for prerequisite in PREREQUISITES.get(class_level, {}).get(topic, ())
        if prerequisite in topics and prerequisite != topic
    )


def validate_prerequisite_graph() -> list[str]:
    """Return graph problems without raising during normal classroom startup."""
    problems: list[str] = []
    for class_level, graph in PREREQUISITES.items():
        if class_level not in CLASS_TOPICS:
            problems.append(f"Unknown class: {class_level}")
            continue
        topics = list(CLASS_TOPICS[class_level])
        for target, prerequisites in graph.items():
            if target not in topics:
                problems.append(f"{class_level}: unknown target {target}")
                continue
            for prerequisite in prerequisites:
                if prerequisite not in topics:
                    problems.append(f"{class_level}: {target} has unknown prerequisite {prerequisite}")
                elif topics.index(prerequisite) >= topics.index(target):
                    problems.append(f"{class_level}: {prerequisite} must occur before {target}")
    return problems
