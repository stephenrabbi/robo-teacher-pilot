"""NERDC/Lagos-aligned Junior Secondary Mathematics practice curriculum."""

CURRICULUM = {
    "JSS1": {
        "First Term": (
            "Whole Numbers", "Factors, Multiples, LCM & HCF", "Fractions",
            "Estimation",
        ),
        "Second Term": (
            "Decimals & Approximation", "Number Bases (Binary)",
            "Positive & Negative Integers", "Introductory Algebra",
        ),
        "Third Term": (
            "Simple Equations", "Plane Shapes & Mensuration",
            "3D Shapes & Volume", "Angles & Construction",
            "Data Presentation", "Mean, Median & Mode",
        ),
    },
    "JSS2": {
        "First Term": (
            "Standard Form", "Prime Factors, Squares & Roots",
            "Fractions, Ratios, Decimals & Percentages",
            "Commercial Arithmetic", "Approximation", "Directed Numbers",
            "Algebraic Expressions & Factorisation", "Algebraic Fractions",
        ),
        "Second Term": (
            "Simple Equations", "Linear Inequalities", "Linear Graphs",
            "Plane Shapes & Scale Drawing",
        ),
        "Third Term": (
            "Angles & Polygons", "Elevation & Depression",
            "Bearings & Distances", "Pythagoras & Mensuration",
            "Statistics & Data Presentation", "Probability",
        ),
    },
    "JSS3": {
        "First Term": (
            "Number Bases", "Rational & Irrational Numbers",
            "Ratio, Proportion & Variation", "Approximation",
            "Factorisation & Quadratic Expressions",
            "Formulae & Change of Subject",
        ),
        "Second Term": (
            "Equations Involving Fractions", "Simultaneous Equations",
            "Similar Shapes", "Trigonometry", "Geometry & Construction",
        ),
        "Third Term": (
            "Mensuration & Volumes", "Statistics & Averages",
            "Pie Charts", "Commercial Arithmetic",
        ),
    },
}

CLASS_TOPICS = {
    class_level: tuple(
        topic for term_topics in terms.values() for topic in term_topics
    )
    for class_level, terms in CURRICULUM.items()
}

TOPIC_TERM = {
    class_level: {
        topic: term
        for term, topics in terms.items()
        for topic in topics
    }
    for class_level, terms in CURRICULUM.items()
}

ALL_TOPICS = tuple(dict.fromkeys(
    topic for topics in CLASS_TOPICS.values() for topic in topics
))
