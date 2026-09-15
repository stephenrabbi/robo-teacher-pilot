"""Deterministic misconception classification for Junior Secondary Mathematics.

The classifier deliberately stores only a compact category and allowlisted teaching
strategy. Question text, answer choices, feedback, and lesson text are transient
request inputs and are never persisted by this module.
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

# Each misconception has a small, auditable strategy set. The first strategy is
# the existing default; later strategies are alternatives selected only when
# learner evidence shows that a different approach is warranted.
_STRATEGY_ALTERNATIVES = {
    "fraction_structure": (
        MISCONCEPTIONS["fraction_structure"]["strategy"],
        "Use equal-size fraction bars or circles to compare the parts first, then translate the picture into numerator and denominator notation.",
        "Start from a simple same-denominator example, ask what stays unchanged, then bridge to equivalent fractions before calculating.",
    ),
    "sign_direction": (
        MISCONCEPTIONS["sign_direction"]["strategy"],
        "Use a temperature or money-debt context to give positive and negative values meaning before returning to the symbols.",
        "Separate sign from magnitude: decide the sign first with a short rule table, then calculate the absolute values.",
    ),
    "place_value_rounding": (
        MISCONCEPTIONS["place_value_rounding"]["strategy"],
        "Underline the rounding place, circle the deciding digit immediately to its right, and ignore all later digits until the decision is made.",
        "Use a number-line midpoint between the two possible rounded values so the learner can see which value the number is closer to.",
    ),
    "algebra_balance": (
        MISCONCEPTIONS["algebra_balance"]["strategy"],
        "Represent the equation as two equal piles, remove or divide the same amount on both sides, then translate each move back into algebra.",
        "Work backwards from the final operation on the unknown, undo one operation at a time, and check by substituting the answer into the original equation.",
    ),
    "factorisation_expansion": (
        MISCONCEPTIONS["factorisation_expansion"]["strategy"],
        "Use an area-box model to show how factors create the expanded terms, then read the side lengths back as factors.",
        "List factor pairs for the constant term and test the middle-term sum before writing the final factorised expression.",
    ),
    "order_of_operations": (
        MISCONCEPTIONS["order_of_operations"]["strategy"],
        "Rewrite the expression with one operation highlighted at a time and evaluate only the highlighted part before copying the rest unchanged.",
        "Use a worked-example comparison showing two different operation orders and let the learner identify why only the standard order preserves the expression.",
    ),
    "ratio_percent": (
        MISCONCEPTIONS["ratio_percent"]["strategy"],
        "Use a 100-square or double number line to connect fractions, ratios and percentages to the same whole visually.",
        "Reduce the situation to one unit first, then scale that unit up to the required quantity or percentage.",
    ),
    "formula_substitution": (
        MISCONCEPTIONS["formula_substitution"]["strategy"],
        "Use a substitution table with symbol, meaning, value and unit columns before putting any numbers into the formula.",
        "Colour-code or verbally match each given value to its symbol, substitute inside brackets, then evaluate only after every symbol has been replaced.",
    ),
    "geometry_measurement": (
        MISCONCEPTIONS["geometry_measurement"]["strategy"],
        "Decompose the figure into familiar shapes, solve one labelled part at a time, then combine the results with units.",
        "Begin from the required quantity, ask which measurements are needed for it, and work backwards to identify the correct theorem or formula.",
    ),
    "graph_coordinate": (
        MISCONCEPTIONS["graph_coordinate"]["strategy"],
        "Use a coordinate-walk routine: horizontal movement first, vertical movement second, then verify the point against the axis scales.",
        "Choose two clear points, build a rise-over-run table, and connect the numerical gradient to the visible steepness of the line.",
    ),
    "data_interpretation": (
        MISCONCEPTIONS["data_interpretation"]["strategy"],
        "Ask the learner to state what one row, bar or sector represents before doing any calculation, then extract only the values needed.",
        "Sort the raw data first and physically mark the middle, repeated or total values before introducing mean, median or mode notation.",
    ),
    "probability_sample_space": (
        MISCONCEPTIONS["probability_sample_space"]["strategy"],
        "Build a small table or tree diagram of every outcome, tick the favourable outcomes, then form the probability from the two counts.",
        "Use an everyday chance experiment, predict the result first, then compare experimental outcomes with the equally likely theoretical sample space.",
    ),
    "number_base": (
        MISCONCEPTIONS["number_base"]["strategy"],
        "Use a place-value table labelled with powers of the base and expand the numeral as a sum before converting it.",
        "Group physical or drawn counters into bundles of the base, record each bundle count as a digit, then reverse the process to check.",
    ),
    "calculation_accuracy": (
        MISCONCEPTIONS["calculation_accuracy"]["strategy"],
        "Estimate first, calculate second, then compare the exact answer with the estimate to catch an unreasonable result immediately.",
        "Use the inverse operation as a compulsory final check and locate the first line where the forward and inverse calculations stop agreeing.",
    ),
    "concept_meaning": (
        MISCONCEPTIONS["concept_meaning"]["strategy"],
        "Use one example and one non-example, ask the learner what changes between them, then derive the concept rule from that contrast.",
        "Ask the learner to explain the idea in everyday words first, then map each part of that explanation to the formal mathematical symbols.",
    ),
    "multi_step_sequence": (
        MISCONCEPTIONS["multi_step_sequence"]["strategy"],
        "Use a short plan-before-solving routine: identify the goal, list the two or three needed steps, then execute only the first step.",
        "Turn the problem into chained mini-questions where each answer becomes the input for the next step, with a quick check between steps.",
    ),
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
    options = strategy_options(category)
    return options[0] if options else None


def strategy_options(category: str | None) -> tuple[str, ...]:
    return _STRATEGY_ALTERNATIVES.get(category or "", ())


def valid_intervention(category: str | None, strategy: str | None) -> bool:
    return bool(category and strategy and strategy in strategy_options(category))


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
                "strategy": teaching_strategy(category),
            }

    category = _TOPIC_DEFAULTS.get(topic)
    if category:
        return {
            "category": category,
            "label": MISCONCEPTIONS[category]["label"],
            "strategy": teaching_strategy(category),
        }

    category = "calculation_accuracy" if re.search(r"calculate|work out|evaluate|simplify|answer", source) else "concept_meaning"
    return {
        "category": category,
        "label": MISCONCEPTIONS[category]["label"],
        "strategy": teaching_strategy(category),
    }
