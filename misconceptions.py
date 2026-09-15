"""Deterministic misconception classification for Junior Secondary Mathematics.

The classifier deliberately stores only a compact category and teaching strategy.
Question text, answer choices, feedback, and lesson text are transient request inputs
and are never persisted by this module.
"""

from __future__ import annotations

import re


MISCONCEPTIONS = {
    "fraction_structure": {
        "label": "Fraction structure confusion",
        "strategy": "Use a visual fraction model, make the denominator meaning explicit, and work one equivalent-fraction step at a time.",
    },
    "sign_direction": {
        "label": "Sign or direction confusion",
        "strategy": "Use a number line or sign table, verbalise the direction of each operation, and check the sign before calculating the magnitude.",
    },
    "place_value_rounding": {
        "label": "Place-value or rounding confusion",
        "strategy": "Write the number in a place-value chart, mark the target digit, and inspect only the next digit before rounding.",
    },
    "algebra_balance": {
        "label": "Equation-balance confusion",
        "strategy": "Use the balance model and perform the same inverse operation on both sides, one line at a time.",
    },
    "factorisation_expansion": {
        "label": "Factorisation or expansion confusion",
        "strategy": "Connect expansion and factorisation as reverse processes, then verify the factorised form by expanding it again.",
    },
    "order_of_operations": {
        "label": "Order-of-operations confusion",
        "strategy": "Mark brackets, powers, multiplication/division, then addition/subtraction before doing any arithmetic.",
    },
    "ratio_percent": {
        "label": "Ratio or percentage interpretation confusion",
        "strategy": "Identify the whole first, convert the comparison to one consistent form, then solve with a bar model or unit-rate step.",
    },
    "formula_substitution": {
        "label": "Formula or substitution confusion",
        "strategy": "List the known values, write the formula separately, substitute with units, then simplify in small steps.",
    },
    "geometry_measurement": {
        "label": "Geometry or measurement confusion",
        "strategy": "Draw and label the figure, mark known lengths or angles, identify the required quantity, then choose the relevant relationship or formula.",
    },
    "graph_coordinate": {
        "label": "Graph or coordinate interpretation confusion",
        "strategy": "Read axes and scale first, plot or trace one coordinate at a time, and connect gradient or position back to the graph visually.",
    },
    "data_interpretation": {
        "label": "Data or statistics interpretation confusion",
        "strategy": "Organise the values in a small table, identify what each statistic represents, then compute or read the required quantity step by step.",
    },
    "probability_sample_space": {
        "label": "Probability or sample-space confusion",
        "strategy": "List the possible outcomes explicitly, count favourable outcomes, then compare them with the total number of equally likely outcomes.",
    },
    "number_base": {
        "label": "Number-base place-value confusion",
        "strategy": "Expand each digit by its base-place value, convert one column at a time, and check the result by converting back.",
    },
    "calculation_accuracy": {
        "label": "Calculation procedure confusion",
        "strategy": "Slow the calculation into one operation per line, estimate the expected size first, and check the final result with an inverse operation where possible.",
    },
    "concept_meaning": {
        "label": "Concept-meaning confusion",
        "strategy": "Start with a concrete familiar example, define the idea in simple language, then connect the example to the mathematical notation.",
    },
    "multi_step_sequence": {
        "label": "Multi-step reasoning confusion",
        "strategy": "Break the problem into numbered micro-steps and require one short learner response before moving to the next step.",
    },
}


_TOPIC_DEFAULTS = {
    "Fractions": "fraction_structure",
    "Fractions, Ratios, Decimals & Percentages": "fraction_structure",
    "Algebraic Fractions": "fraction_structure",
    "Equations Involving Fractions": "fraction_structure",
    "Positive & Negative Integers": "sign_direction",
    "Directed Numbers": "sign_direction",
    "Decimals & Approximation": "place_value_rounding",
    "Approximation": "place_value_rounding",
    "Estimation": "place_value_rounding",
    "Introductory Algebra": "algebra_balance",
    "Simple Equations": "algebra_balance",
    "Linear Inequalities": "algebra_balance",
    "Simultaneous Equations": "algebra_balance",
    "Formulae & Change of Subject": "formula_substitution",
    "Algebraic Expressions & Factorisation": "factorisation_expansion",
    "Factorisation & Quadratic Expressions": "factorisation_expansion",
    "Ratio, Proportion & Variation": "ratio_percent",
    "Commercial Arithmetic": "ratio_percent",
    "Plane Shapes & Mensuration": "geometry_measurement",
    "3D Shapes & Volume": "geometry_measurement",
    "Angles & Construction": "geometry_measurement",
    "Plane Shapes & Scale Drawing": "geometry_measurement",
    "Angles & Polygons": "geometry_measurement",
    "Elevation & Depression": "geometry_measurement",
    "Bearings & Distances": "geometry_measurement",
    "Pythagoras & Mensuration": "geometry_measurement",
    "Similar Shapes": "geometry_measurement",
    "Trigonometry": "geometry_measurement",
    "Geometry & Construction": "geometry_measurement",
    "Mensuration & Volumes": "geometry_measurement",
    "Linear Graphs": "graph_coordinate",
    "Data Presentation": "data_interpretation",
    "Mean, Median & Mode": "data_interpretation",
    "Statistics & Data Presentation": "data_interpretation",
    "Statistics & Averages": "data_interpretation",
    "Pie Charts": "data_interpretation",
    "Probability": "probability_sample_space",
    "Number Bases": "number_base",
    "Number Bases (Binary)": "number_base",
}


_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("fraction_structure", (
        r"\bdenominator\b", r"\bnumerator\b", r"common denominator", r"equivalent fraction",
        r"reciprocal", r"mixed number",
    )),
    ("sign_direction", (
        r"negative sign", r"positive sign", r"different signs", r"same sign", r"number line",
        r"move left", r"move right", r"directed number",
    )),
    ("place_value_rounding", (
        r"decimal place", r"significant figure", r"place value", r"round(?:ed|ing)?", r"tenths?\b", r"hundredths?\b",
    )),
    ("order_of_operations", (
        r"order of operations", r"brackets? first", r"multiply first", r"divide first", r"before (?:adding|subtracting)",
    )),
    ("factorisation_expansion", (
        r"factoris", r"factoriz", r"expand(?:ing|ed)?", r"common factor", r"quadratic expression",
    )),
    ("algebra_balance", (
        r"both sides", r"inverse operation", r"isolate [a-z]", r"solve for [a-z]", r"collect .*terms", r"equation",
    )),
    ("ratio_percent", (
        r"percentage", r"percent\b", r"ratio", r"proportion", r"unit rate", r"discount", r"profit", r"loss",
    )),
    ("formula_substitution", (
        r"substitut", r"formula", r"make .* subject", r"change .* subject", r"known values?",
    )),
    ("graph_coordinate", (
        r"gradient", r"slope", r"coordinate", r"x-axis", r"y-axis", r"plot", r"graph",
    )),
    ("probability_sample_space", (
        r"sample space", r"favourable outcome", r"favorable outcome", r"possible outcomes?", r"probability",
    )),
    ("data_interpretation", (
        r"mean\b", r"median\b", r"mode\b", r"frequency", r"pie chart", r"bar chart", r"histogram", r"statistics",
    )),
    ("geometry_measurement", (
        r"angle", r"perimeter", r"area", r"volume", r"surface area", r"hypotenuse", r"bearing", r"triangle", r"circle",
    )),
    ("number_base", (
        r"base two", r"base 2", r"base ten", r"base 10", r"binary", r"place value in base",
    )),
    ("multi_step_sequence", (
        r"first .* then", r"step 1", r"next step", r"before .* then", r"two-step", r"multi-step",
    )),
)


def misconception_label(category: str | None) -> str | None:
    item = MISCONCEPTIONS.get(category or "")
    return item["label"] if item else None


def teaching_strategy(category: str | None) -> str | None:
    item = MISCONCEPTIONS.get(category or "")
    return item["strategy"] if item else None


def classify_misconception(
    topic: str,
    question: str = "",
    selected_choice: str = "",
    correct_choice: str = "",
    feedback: str = "",
) -> dict:
    """Return one conservative misconception category for an incorrect check.

    The classifier is deterministic and topic-bounded. It never calls a model and
    it never returns or stores the transient learner answer text.
    """
    source = " ".join((question, selected_choice, correct_choice, feedback)).lower()
    source = re.sub(r"\s+", " ", source).strip()
    for category, patterns in _RULES:
        if any(re.search(pattern, source) for pattern in patterns):
            return {
                "category": category,
                "label": MISCONCEPTIONS[category]["label"],
                "strategy": MISCONCEPTIONS[category]["strategy"],
            }

    category = _TOPIC_DEFAULTS.get(topic)
    if category:
        return {
            "category": category,
            "label": MISCONCEPTIONS[category]["label"],
            "strategy": MISCONCEPTIONS[category]["strategy"],
        }

    category = "calculation_accuracy" if re.search(r"calculate|work out|evaluate|simplify|answer", source) else "concept_meaning"
    return {
        "category": category,
        "label": MISCONCEPTIONS[category]["label"],
        "strategy": MISCONCEPTIONS[category]["strategy"],
    }
