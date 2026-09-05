"""Generate varied, deterministic-marking Junior Secondary Maths questions."""

import math
import secrets
from fractions import Fraction


def _pick(values):
    return secrets.choice(tuple(values))


def _int(low: int, high: int) -> int:
    return low + secrets.randbelow(high - low + 1)


def _fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def generate_question(topic: str, difficulty: str):
    generators = {
        "Whole Numbers": _whole_numbers,
        "Fractions": _fractions,
        "Algebra": _algebra,
        "Ratio & Percentage": _ratio_percentage,
        "Factors, Multiples & Roots": _factors_roots,
        "Decimals & Approximation": _decimals,
        "Directed Numbers": _directed,
        "Commercial Arithmetic": _commercial,
        "Inequalities & Graphs": _inequalities_graphs,
        "Geometry & Mensuration": _geometry,
        "Statistics & Probability": _statistics_probability,
        "Factors, Multiples, LCM & HCF": _factors_roots,
        "Estimation": _decimals,
        "Decimals & Approximation": _decimals,
        "Number Bases (Binary)": _number_bases,
        "Number Bases": _number_bases,
        "Positive & Negative Integers": _directed,
        "Introductory Algebra": _algebraic_expressions,
        "Simple Equations": _algebra,
        "Plane Shapes & Mensuration": _geometry,
        "3D Shapes & Volume": _solid_mensuration,
        "Angles & Construction": _angles,
        "Data Presentation": _data_presentation,
        "Mean, Median & Mode": _averages,
        "Standard Form": _standard_form,
        "Prime Factors, Squares & Roots": _factors_roots,
        "Fractions, Ratios, Decimals & Percentages": _ratio_percentage,
        "Approximation": _decimals,
        "Algebraic Expressions & Factorisation": _algebraic_expressions,
        "Algebraic Fractions": _fractions,
        "Linear Inequalities": _inequalities_graphs,
        "Linear Graphs": _inequalities_graphs,
        "Plane Shapes & Scale Drawing": _geometry,
        "Angles & Polygons": _angles,
        "Elevation & Depression": _elevation,
        "Bearings & Distances": _bearings,
        "Pythagoras & Mensuration": _geometry,
        "Statistics & Data Presentation": _data_presentation,
        "Probability": _probability,
        "Rational & Irrational Numbers": _number_types,
        "Ratio, Proportion & Variation": _variation,
        "Factorisation & Quadratic Expressions": _quadratics,
        "Formulae & Change of Subject": _formulae,
        "Equations Involving Fractions": _fraction_equations,
        "Simultaneous Equations": _simultaneous,
        "Similar Shapes": _similar_shapes,
        "Trigonometry": _trigonometry,
        "Geometry & Construction": _angles,
        "Mensuration & Volumes": _solid_mensuration,
        "Statistics & Averages": _averages,
        "Pie Charts": _pie_charts,
    }
    return generators[topic](difficulty)


def _whole_numbers(level):
    if level == "Easy":
        if secrets.randbelow(2):
            a, b = _int(12, 89), _int(11, 79); answer = a + b
            return (f"What is {a} + {b}?", "Add the ones, then the tens.", str(answer), f"Step 1: Add the ones and regroup if needed.\nStep 2: Add the tens.\nTherefore, {a} + {b} = {answer}.")
        a, b = _int(3, 12), _int(3, 12); answer = a * b
        return (f"What is {a} × {b}?", "Use equal groups or your multiplication table.", str(answer), f"Step 1: This means {a} groups of {b}.\nStep 2: Multiply {a} by {b}.\nTherefore, {a} × {b} = {answer}.")
    if level == "Medium":
        if secrets.randbelow(2):
            divisor, answer = _int(4, 15), _int(5, 20); dividend = divisor * answer
            return (f"What is {dividend} ÷ {divisor}?", f"Which number multiplied by {divisor} gives {dividend}?", str(answer), f"Step 1: Use the inverse operation.\nStep 2: {divisor} × {answer} = {dividend}.\nTherefore, {dividend} ÷ {divisor} = {answer}.")
        a, b = _int(200, 900), _int(50, 199); answer = a - b
        return (f"Calculate {a} - {b}.", "Subtract by place value and borrow when necessary.", str(answer), f"Step 1: Align the hundreds, tens and ones.\nStep 2: Subtract each column carefully.\nTherefore, {a} - {b} = {answer}.")
    a, b, c = _int(12, 30), _int(3, 9), _int(10, 60); answer = a * b - c
    return (f"Calculate ({a} × {b}) - {c}.", "Complete the multiplication first.", str(answer), f"Step 1: {a} × {b} = {a*b}.\nStep 2: {a*b} - {c} = {answer}.\nTherefore, the answer is {answer}.")


def _fractions(level):
    if level == "Easy":
        d = _pick((4, 5, 6, 8, 10, 12)); a, b = _int(1, d//2), _int(1, d//2); result = Fraction(a+b, d)
        return (f"Calculate {a}/{d} + {b}/{d}. Give the simplest fraction.", "Keep the common denominator and add the numerators.", _fraction(result), f"Step 1: The denominators are both {d}.\nStep 2: Add the numerators: {a} + {b} = {a+b}.\nStep 3: Simplify {a+b}/{d}. Therefore, the answer is {_fraction(result)}.")
    if level == "Medium":
        d1, d2 = _pick((2, 3, 4, 5, 6)), _pick((4, 6, 8, 10, 12)); a, b = _int(1, d1-1), _int(1, d2-1); result = Fraction(a,d1)+Fraction(b,d2)
        common = math.lcm(d1,d2)
        return (f"Calculate {a}/{d1} + {b}/{d2}. Give the simplest fraction.", f"Use {common} as a common denominator.", _fraction(result), f"Step 1: Use the common denominator {common}.\nStep 2: Convert both fractions and add their numerators.\nStep 3: Simplify the result. Therefore, the answer is {_fraction(result)}.")
    a,b,c,d = _int(2,9),_int(3,10),_int(2,9),_int(3,10); result=Fraction(a,b)*Fraction(c,d)
    return (f"Calculate {a}/{b} × {c}/{d}. Give the simplest fraction.", "Multiply the numerators and denominators, then simplify.", _fraction(result), f"Step 1: Multiply: ({a} × {c})/({b} × {d}) = {a*c}/{b*d}.\nStep 2: Simplify the fraction.\nTherefore, the answer is {_fraction(result)}.")


def _algebra(level):
    x = _int(2, 15)
    if level == "Easy":
        c = _int(2, 12); total=x+c
        return (f"Solve x + {c} = {total}.", f"Subtract {c} from both sides.", str(x), f"Step 1: Subtract {c} from both sides.\nStep 2: x = {total} - {c}.\nTherefore, x = {x}.")
    if level == "Medium":
        a,c=_int(2,7),_int(2,15); total=a*x+c
        return (f"Solve {a}x + {c} = {total}.", f"Subtract {c}, then divide by {a}.", str(x), f"Step 1: Subtract {c}: {a}x = {a*x}.\nStep 2: Divide by {a}.\nTherefore, x = {x}.")
    a,c=_int(2,6),_int(2,10); total=a*(x+c)
    return (f"Solve {a}(x + {c}) = {total}.", f"Divide by {a}, then subtract {c}.", str(x), f"Step 1: Divide by {a}: x + {c} = {x+c}.\nStep 2: Subtract {c}.\nTherefore, x = {x}.")


def _ratio_percentage(level):
    if level == "Easy":
        percent=_pick((10,20,25,50)); base=_pick((40,60,80,100,120,200)); answer=base*percent//100
        return (f"What is {percent}% of {base}?", "Write the percentage over 100, then multiply.", str(answer), f"Step 1: {percent}% = {percent}/100.\nStep 2: {percent}/100 × {base} = {answer}.\nTherefore, the answer is {answer}.")
    if level == "Medium":
        a,b=_int(2,6),_int(3,8); unit=_int(5,20); total=(a+b)*unit; larger=max(a,b)*unit
        return (f"Share {total} in the ratio {a}:{b}. What is the larger share?", f"There are {a+b} parts altogether.", str(larger), f"Step 1: Total parts = {a} + {b} = {a+b}.\nStep 2: One part = {total} ÷ {a+b} = {unit}.\nStep 3: The larger share is {max(a,b)} × {unit} = {larger}.")
    old=_pick((120,160,200,240,300,400)); percent=_pick((10,15,20,25)); increase=old*percent//100; new=old+increase
    return (f"A quantity rises from {old} to {new}. What is the percentage increase?", "Find the increase, divide by the original, then multiply by 100.", str(percent), f"Step 1: Increase = {new} - {old} = {increase}.\nStep 2: {increase} ÷ {old} × 100 = {percent}%.\nTherefore, the increase is {percent}%. ")


def _factors_roots(level):
    if level == "Easy":
        if secrets.randbelow(2):
            root=_int(3,20); square=root*root
            return (f"What is the square root of {square}?", "Find the number that multiplies by itself to give the value.", str(root), f"Step 1: {root} × {root} = {square}.\nTherefore, √{square} = {root}.")
        common=_int(2,10); a=common*_int(2,6); b=common*_int(2,6); answer=math.gcd(a,b)
        return (f"Find the HCF of {a} and {b}.", "List the factors common to both numbers.", str(answer), f"Step 1: List the factors of {a} and {b}.\nStep 2: Choose their highest common factor.\nTherefore, the HCF is {answer}.")
    if level == "Medium":
        common=_int(2,10); a=common*_int(2,8); b=common*_int(2,8); answer=math.gcd(a,b)
        return (f"Find the HCF of {a} and {b}.", "List factors or use prime factorisation.", str(answer), f"Step 1: Find the prime factors of both numbers.\nStep 2: Multiply the shared prime factors.\nTherefore, HCF({a}, {b}) = {answer}.")
    a,b=_int(3,12),_int(4,15); answer=math.lcm(a,b)
    return (f"Find the LCM of {a} and {b}.", "Use the highest powers in their prime factorisations.", str(answer), f"Step 1: Prime-factorise {a} and {b}.\nStep 2: Use each required prime at its highest power.\nTherefore, LCM({a}, {b}) = {answer}.")


def _decimals(level):
    if level == "Easy":
        a,b=_int(10,99),_int(10,99); answer=(a+b)/10
        return (f"Calculate {a/10:.1f} + {b/10:.1f}.", "Align the decimal points.", f"{answer:g}", f"Step 1: Align the decimal points.\nStep 2: Add the tenths and whole numbers.\nTherefore, the answer is {answer:g}.")
    if level == "Medium":
        whole=_int(2,30); hundredths=_int(10,99); value=whole+hundredths/1000; answer=round(value,2)
        return (f"Round {value:.3f} to 2 decimal places.", "Check the third decimal digit.", f"{answer:.2f}", f"Step 1: Look at the third decimal digit in {value:.3f}.\nStep 2: Round the second decimal digit correctly.\nTherefore, the answer is {answer:.2f}.")
    a=_int(101,999)/10; b=_int(11,99)/10; estimate=round(a,-1)*round(b)
    return (f"Estimate {a:.1f} × {b:.1f} by rounding each number to 1 significant figure.", "Round both numbers before multiplying.", f"{estimate:g}", f"Step 1: {a:.1f} rounds to {round(a,-1):g}.\nStep 2: {b:.1f} rounds to {round(b):g}.\nTherefore, the estimate is {estimate:g}.")


def _directed(level):
    if level == "Easy":
        a,b=-_int(2,15),_int(3,20); answer=a+b
        return (f"Calculate {a} + {b}.", "Move right for the positive number.", str(answer), f"Step 1: Start at {a} on a number line.\nStep 2: Move {b} places right.\nTherefore, the answer is {answer}.")
    if level == "Medium":
        a,b=-_int(2,12),_int(2,12); answer=a*b
        return (f"Calculate ({a}) × {b}.", "A negative times a positive is negative.", str(answer), f"Step 1: Multiply the values: {abs(a)} × {b} = {abs(answer)}.\nStep 2: Different signs give a negative result.\nTherefore, the answer is {answer}.")
    a,b,c=-_int(2,10),_int(2,12),_int(3,15); inside=b-c; answer=a*inside
    return (f"Calculate {a} × ({b} - {c}).", "Work inside the brackets first.", str(answer), f"Step 1: {b} - {c} = {inside}.\nStep 2: {a} × {inside} = {answer}.\nTherefore, the answer is {answer}.")


def _commercial(level):
    if level == "Easy":
        cost=_int(5,30)*100; profit=_int(1,10)*50; selling=cost+profit
        return (f"An item costs ₦{cost:,} and sells for ₦{selling:,}. Find the profit.", "Subtract cost price from selling price.", str(profit), f"Step 1: Profit = selling price - cost price.\nStep 2: ₦{selling:,} - ₦{cost:,} = ₦{profit:,}.\nTherefore, the profit is ₦{profit:,}.")
    principal=_int(10,50)*1000; rate=_pick((5,8,10,12)); years=_int(1,4); interest=principal*rate*years//100
    if level == "Medium":
        return (f"Find the simple interest on ₦{principal:,} at {rate}% per year for {years} years.", "Use I = PRT/100.", str(interest), f"Step 1: I = {principal:,} × {rate} × {years} ÷ 100.\nStep 2: I = {interest:,}.\nTherefore, the interest is ₦{interest:,}.")
    price=_int(10,50)*500; discount=_pick((10,15,20,25)); selling=price*(100-discount)//100
    return (f"An item marked ₦{price:,} has a {discount}% discount. Find the selling price.", "Find the discount, then subtract it.", str(selling), f"Step 1: Discount = {discount}% of ₦{price:,} = ₦{price*discount//100:,}.\nStep 2: Subtract the discount.\nTherefore, the selling price is ₦{selling:,}.")


def _inequalities_graphs(level):
    if level == "Easy":
        x,c=_int(1,12),_int(2,10); bound=x+c+1
        return (f"Solve x + {c} < {bound}. What is the greatest whole-number value of x?", f"Subtract {c} from both sides.", str(x), f"Step 1: x < {bound-c}.\nStep 2: The greatest whole number below {bound-c} is {x}.\nTherefore, the answer is {x}.")
    if level == "Medium":
        m,x,c=_int(2,6),_int(1,8),_int(-5,8); y=m*x+c
        return (f"For y = {m}x {'+' if c>=0 else '-'} {abs(c)}, find y when x = {x}.", "Substitute the value of x.", str(y), f"Step 1: Substitute x = {x}.\nStep 2: y = {m}({x}) {'+' if c>=0 else '-'} {abs(c)} = {y}.\nTherefore, y = {y}.")
    x1,y1=_int(0,5),_int(0,8); gradient=_int(2,6); dx=_int(2,6); x2=x1+dx; y2=y1+gradient*dx
    return (f"Find the gradient between ({x1}, {y1}) and ({x2}, {y2}).", "Use change in y divided by change in x.", str(gradient), f"Step 1: Change in y = {y2} - {y1} = {y2-y1}.\nStep 2: Change in x = {x2} - {x1} = {dx}.\nGradient = {y2-y1} ÷ {dx} = {gradient}.")


def _geometry(level):
    if level == "Easy":
        length,width=_int(5,20),_int(3,15); perimeter=2*(length+width)
        return (f"Find the perimeter of a rectangle {length} cm long and {width} cm wide.", "Use 2(length + width).", str(perimeter), f"Step 1: {length} + {width} = {length+width}.\nStep 2: 2 × {length+width} = {perimeter}.\nTherefore, the perimeter is {perimeter} cm.")
    if level == "Medium":
        unit=_int(2,10); distance=_int(3,15); answer=unit*distance
        return (f"A map scale is 1 cm to {unit} km. What distance does {distance} cm represent?", f"Multiply {distance} by {unit} km.", str(answer), f"Step 1: Each centimetre represents {unit} km.\nStep 2: {distance} × {unit} = {answer}.\nTherefore, the distance is {answer} km.")
    triple=_pick(((3,4,5),(5,12,13),(7,24,25),(8,15,17),(9,40,41),(12,35,37),(20,21,29))); scale=_int(1,8); a,b,c=(n*scale for n in triple)
    return (f"A right-angled triangle has shorter sides {a} cm and {b} cm. Find the hypotenuse.", "Use c² = a² + b².", str(c), f"Step 1: c² = {a}² + {b}² = {a*a+b*b}.\nStep 2: c = √{a*a+b*b}.\nTherefore, the hypotenuse is {c} cm.")


def _statistics_probability(level):
    if level == "Easy":
        mean=_int(3,15); gap=_int(1,5); values=(mean-gap,mean,mean+gap)
        return (f"Find the mean of {values[0]}, {values[1]} and {values[2]}.", "Add the values and divide by 3.", str(mean), f"Step 1: The total is {sum(values)}.\nStep 2: {sum(values)} ÷ 3 = {mean}.\nTherefore, the mean is {mean}.")
    if level == "Medium":
        red,blue=_int(1,8),_int(2,10); result=Fraction(red,red+blue)
        return (f"A bag contains {red} red and {blue} blue balls. What is the probability of choosing red?", "Use favourable outcomes divided by total outcomes.", _fraction(result), f"Step 1: Total balls = {red} + {blue} = {red+blue}.\nStep 2: P(red) = {red}/{red+blue}.\nStep 3: Simplify. Therefore, the answer is {_fraction(result)}.")
    mean=_int(5,15)
    while True:
        a,b,c=_int(1,mean+3),_int(1,mean+3),_int(1,mean+3); x=mean*4-a-b-c
        if x > 0:
            break
    return (f"The mean of {a}, {b}, {c} and x is {mean}. Find x.", "Total = mean × number of values.", str(x), f"Step 1: Required total = {mean} × 4 = {mean*4}.\nStep 2: Known total = {a+b+c}.\nStep 3: x = {mean*4} - {a+b+c} = {x}.")


def _number_bases(level):
    if level == "Easy":
        value = _int(4, 31)
        answer = format(value, "b")
        return (f"Write {value} in base two.", "Divide repeatedly by 2 and read the remainders upwards.", answer, f"Step 1: Express {value} as powers of 2.\nStep 2: Put 1 under each power used and 0 under the others.\nTherefore, {value}₁₀ = {answer}₂.")
    if level == "Medium":
        value = _int(8, 63); binary = format(value, "b")
        return (f"Convert {binary}₂ to base ten.", "Multiply each digit by its place value, a power of 2.", str(value), f"Step 1: Expand {binary}₂ using powers of 2.\nStep 2: Add the occupied place values.\nTherefore, {binary}₂ = {value}₁₀.")
    a, b = _int(3, 15), _int(2, 12); result = a + b
    return (f"Calculate {format(a, 'b')}₂ + {format(b, 'b')}₂. Give your answer in base two.", "You may convert to base ten, add, then convert back.", format(result, "b"), f"Step 1: Convert: {format(a, 'b')}₂ = {a} and {format(b, 'b')}₂ = {b}.\nStep 2: Add: {a} + {b} = {result}.\nStep 3: Convert back. Therefore, the answer is {format(result, 'b')}₂.")


def _algebraic_expressions(level):
    x = _int(2, 12); a, b = _int(2, 8), _int(1, 12)
    if level == "Easy":
        answer = a*x+b
        return (f"Find the value of {a}x + {b} when x = {x}.", "Substitute the given value for x.", str(answer), f"Step 1: Substitute x = {x}: {a}({x}) + {b}.\nStep 2: Multiply, then add: {a*x} + {b} = {answer}.\nTherefore, the answer is {answer}.")
    c = _int(2, 7); coefficient = a+c
    if level == "Medium":
        return (f"Simplify {a}x + {c}x + {b}.", "Combine the like terms containing x.", f"{coefficient}x+{b}", f"Step 1: {a}x and {c}x are like terms.\nStep 2: Add their coefficients: {a} + {c} = {coefficient}.\nTherefore, the expression is {coefficient}x + {b}.")
    d = _int(2, 7); constant = a*d
    return (f"Expand {a}(x + {d}).", "Multiply every term inside the bracket by the number outside.", f"{a}x+{constant}", f"Step 1: {a} × x = {a}x.\nStep 2: {a} × {d} = {constant}.\nTherefore, the expansion is {a}x + {constant}.")


def _solid_mensuration(level):
    length, width, height = _int(3, 15), _int(2, 12), _int(2, 10)
    if level == "Easy":
        answer = length*width*height
        return (f"Find the volume of a cuboid {length} cm by {width} cm by {height} cm.", "Use length × width × height.", str(answer), f"Step 1: Volume = {length} × {width} × {height}.\nStep 2: Multiply the dimensions to get {answer}.\nTherefore, the volume is {answer} cm³.")
    if level == "Medium":
        answer = 2*(length*width + length*height + width*height)
        return (f"Find the total surface area of a cuboid {length} cm by {width} cm by {height} cm.", "Add the areas of the six rectangular faces.", str(answer), f"Step 1: Surface area = 2(lw + lh + wh).\nStep 2: Substitute {length}, {width} and {height}.\nTherefore, the surface area is {answer} cm².")
    radius, h = _pick((7, 14, 21)), _int(3, 15); answer = 22*radius*radius*h//7
    return (f"Find the volume of a cylinder of radius {radius} cm and height {h} cm. Use π = 22/7.", "Use V = πr²h.", str(answer), f"Step 1: V = 22/7 × {radius}² × {h}.\nStep 2: Simplify and multiply.\nTherefore, the volume is {answer} cm³.")


def _angles(level):
    if level == "Easy":
        angle = _int(25, 155); answer = 180-angle
        return (f"Two angles on a straight line are {angle}° and x°. Find x.", "Angles on a straight line add to 180°.", str(answer), f"Step 1: x + {angle} = 180°.\nStep 2: x = 180° - {angle}° = {answer}°.\nTherefore, x = {answer}°.")
    sides = _int(4, 30); total = (sides-2)*180
    if level == "Medium":
        return (f"Find the sum of the interior angles of a {sides}-sided polygon.", "Use (n - 2) × 180°.", str(total), f"Step 1: n = {sides}.\nStep 2: ({sides} - 2) × 180° = {total}°.\nTherefore, the sum is {total}°.")
    return (f"The interior angles of a polygon add to {total}°. How many sides does it have?", "Use (n - 2) × 180° and solve for n.", str(sides), f"Step 1: n - 2 = {total} ÷ 180 = {sides-2}.\nStep 2: Add 2, so n = {sides}.\nTherefore, it has {sides} sides.")


def _data_presentation(level):
    categories = _int(4, 12); each = _int(2, 9); total = categories*each
    if level == "Easy":
        return (f"A pictogram uses one symbol for {each} learners. How many learners do {categories} symbols represent?", "Multiply the number of symbols by the key value.", str(total), f"Step 1: One symbol represents {each} learners.\nStep 2: {categories} × {each} = {total}.\nTherefore, the pictogram represents {total} learners.")
    frequencies = [_int(2, 12) for _ in range(4)]; answer = sum(frequencies)
    if level == "Medium":
        values = ", ".join(map(str, frequencies))
        return (f"A frequency table has frequencies {values}. Find the total frequency.", "Add all the frequencies.", str(answer), f"Step 1: Add {values}.\nStep 2: The sum is {answer}.\nTherefore, the total frequency is {answer}.")
    height1, height2 = _int(5, 25), _int(26, 50); difference = height2-height1
    return (f"On a bar chart, Class A has {height1} learners and Class B has {height2}. How many more learners are in Class B?", "Subtract the smaller bar value from the larger one.", str(difference), f"Step 1: Difference = {height2} - {height1}.\nStep 2: The difference is {difference}.\nTherefore, Class B has {difference} more learners.")


def _averages(level):
    middle = _int(4, 20); gap = _int(1, 5); values = [middle-gap, middle, middle+gap]
    if level == "Easy":
        return (f"Find the mean of {values[0]}, {values[1]} and {values[2]}.", "Add the numbers and divide by 3.", str(middle), f"Step 1: Their sum is {sum(values)}.\nStep 2: {sum(values)} ÷ 3 = {middle}.\nTherefore, the mean is {middle}.")
    extra = _int(middle+gap+1, middle+gap+8); ordered = values+[extra]; median = Fraction(values[1]+values[2], 2)
    if level == "Medium":
        return (f"Find the median of {', '.join(map(str, ordered))}.", "For four ordered values, average the two middle values.", _fraction(median), f"Step 1: The values are already ordered.\nStep 2: Average the middle two: ({values[1]} + {values[2]}) ÷ 2.\nTherefore, the median is {_fraction(median)}.")
    x = _int(2, 15); data = [x, _int(1, 20), x, _int(21, 30), x]
    return (f"Find the mode of {', '.join(map(str, data))}.", "The mode is the value that occurs most often.", str(x), f"Step 1: Count how often each value occurs.\nStep 2: {x} occurs three times, more than any other value.\nTherefore, the mode is {x}.")


def _standard_form(level):
    coefficient = _int(11, 99); exponent = _int(2, 6); value = coefficient * 10 ** (exponent-1)
    if level == "Easy":
        return (f"Write {value:,} in standard form.", "Move the decimal point until the first number is between 1 and 10.", f"{coefficient/10:g}*10^{exponent}", f"Step 1: Move the decimal point {exponent} places left.\nStep 2: This gives {coefficient/10:g} × 10^{exponent}.\nTherefore, the answer is {coefficient/10:g} × 10^{exponent}.")
    if level == "Medium":
        return (f"Write {coefficient/10:g} × 10^{exponent} as an ordinary number.", "Move the decimal point to the right by the exponent.", str(value), f"Step 1: The exponent {exponent} means move the decimal point {exponent} places right.\nStep 2: This gives {value}.\nTherefore, the answer is {value:,}.")
    multiplier = _int(2, 8); product = coefficient*multiplier/10
    return (f"Calculate ({coefficient/10:g} × 10^{exponent}) × {multiplier}. Give the answer in standard form.", "Multiply the decimal coefficients and keep the power of ten.", f"{product:g}*10^{exponent}", f"Step 1: {coefficient/10:g} × {multiplier} = {product:g}.\nStep 2: Keep × 10^{exponent}.\nTherefore, the answer is {product:g} × 10^{exponent}.")


def _elevation(level):
    height = _int(3, 30)
    return (f"From a point {height} m from the foot of a pole, the angle of elevation is 45°. Find the pole's height.", "At 45°, tan 45° = opposite/adjacent = 1.", str(height), f"Step 1: tan 45° = height ÷ {height}.\nStep 2: 1 = height ÷ {height}.\nTherefore, the pole is {height} m high.")


def _bearings(level):
    bearing = _int(1, 35)*10 % 360; turn = _pick((30, 45, 60, 90)); answer = (bearing+turn)%360
    return (f"A learner faces bearing {bearing:03d}° and turns {turn}° clockwise. What is the new bearing?", "Add the clockwise turn and reduce values above 360°.", f"{answer:03d}", f"Step 1: Add: {bearing}° + {turn}° = {bearing+turn}°.\nStep 2: Express the result as a three-figure bearing.\nTherefore, the new bearing is {answer:03d}°.")


def _probability(level):
    favourable, other = _int(1, 10), _int(2, 12); result = Fraction(favourable, favourable+other)
    return (f"A bag contains {favourable} red and {other} blue counters. Find the probability of selecting red.", "Use favourable outcomes divided by total outcomes.", _fraction(result), f"Step 1: Total counters = {favourable} + {other} = {favourable+other}.\nStep 2: P(red) = {favourable}/{favourable+other}.\nStep 3: Simplify. Therefore, the answer is {_fraction(result)}.")


def _number_types(level):
    while True:
        root = _int(2, 99)
        if math.isqrt(root) ** 2 != root:
            break
    return (f"Is √{root} rational or irrational?", "A square root of a whole number is rational only when the number is a perfect square.", "irrational", f"Step 1: {root} is not a perfect square.\nStep 2: Its square root cannot be written as a terminating or recurring fraction.\nTherefore, √{root} is irrational.")


def _variation(level):
    x1, y1, x2 = _int(2, 8), _int(3, 12), _int(9, 20); answer = Fraction(y1*x2, x1)
    return (f"y varies directly as x. If y = {y1} when x = {x1}, find y when x = {x2}.", "For direct variation, y/x is constant.", _fraction(answer), f"Step 1: k = y/x = {y1}/{x1}.\nStep 2: y = kx = {y1}/{x1} × {x2}.\nTherefore, y = {_fraction(answer)}.")


def _quadratics(level):
    a, b = _int(1, 12), _int(1, 12); middle=a+b; product=a*b
    if level == "Easy":
        return (f"Factorise x² + {middle}x + {product}.", "Find two numbers whose sum is the x coefficient and product is the constant.", f"(x+{a})(x+{b})", f"Step 1: {a} + {b} = {middle} and {a} × {b} = {product}.\nStep 2: Use these in two brackets.\nTherefore, the factorisation is (x + {a})(x + {b}).")
    return (f"Solve x² + {middle}x + {product} = 0.", "Factorise, then set each bracket equal to zero.", f"-{a},-{b}", f"Step 1: Factorise as (x + {a})(x + {b}) = 0.\nStep 2: x + {a} = 0 or x + {b} = 0.\nTherefore, x = -{a} or x = -{b}.")


def _formulae(level):
    length, width = _int(4, 20), _int(2, 15); perimeter=2*(length+width)
    return (f"Make l the subject of P = 2(l + w), then find l when P = {perimeter} and w = {width}.", "Divide by 2, then subtract w.", str(length), f"Step 1: P/2 = l + w, so l = P/2 - w.\nStep 2: l = {perimeter}/2 - {width} = {length}.\nTherefore, l = {length}.")


def _fraction_equations(level):
    denominator, x = _int(2, 9), _int(2, 20); constant = _int(1, 10); total = x + constant
    return (f"Solve x/{denominator} + {constant} = {total}.", f"Subtract {constant}, then multiply by {denominator}.", str(x*denominator), f"Step 1: x/{denominator} = {total} - {constant} = {x}.\nStep 2: Multiply both sides by {denominator}.\nTherefore, x = {x*denominator}.")


def _simultaneous(level):
    x, y = _int(1, 15), _int(1, 15); total=x+y; difference=x-y
    return (f"Solve x + y = {total} and x - y = {difference}.", "Add the equations to eliminate y.", f"x={x},y={y}", f"Step 1: Add the equations: 2x = {total+difference}.\nStep 2: x = {x}. Substitute into x + y = {total}.\nStep 3: y = {y}. Therefore, x = {x}, y = {y}.")


def _similar_shapes(level):
    scale, side = _int(2, 6), _int(2, 15); image=scale*side
    return (f"Two shapes are similar. A {side} cm side on the smaller shape corresponds to {image} cm on the larger. Find the scale factor.", "Divide the larger corresponding side by the smaller one.", str(scale), f"Step 1: Scale factor = {image} ÷ {side}.\nStep 2: {image} ÷ {side} = {scale}.\nTherefore, the scale factor is {scale}.")


def _trigonometry(level):
    opposite, adjacent, hypotenuse = _pick(((3,4,5),(5,12,13),(8,15,17),(7,24,25))); scale=_int(1,6); opposite*=scale; adjacent*=scale; hypotenuse*=scale
    ratio = _pick(("sin", "cos", "tan"))
    values = {"sin": Fraction(opposite,hypotenuse), "cos": Fraction(adjacent,hypotenuse), "tan": Fraction(opposite,adjacent)}
    names = {"sin":"opposite/hypotenuse", "cos":"adjacent/hypotenuse", "tan":"opposite/adjacent"}
    return (f"In a right-angled triangle, opposite = {opposite} cm, adjacent = {adjacent} cm and hypotenuse = {hypotenuse} cm. Find {ratio} θ.", f"Use {ratio} θ = {names[ratio]}.", _fraction(values[ratio]), f"Step 1: {ratio} θ = {names[ratio]}.\nStep 2: Substitute the given sides and simplify.\nTherefore, {ratio} θ = {_fraction(values[ratio])}.")


def _pie_charts(level):
    total = _pick((20, 24, 30, 36, 40, 45, 60)); category = _int(1, total-1); angle = Fraction(category*360,total)
    return (f"In a survey of {total} learners, {category} chose football. Find the angle for football on a pie chart.", "Use category/total × 360°.", _fraction(angle), f"Step 1: Angle = {category}/{total} × 360°.\nStep 2: Simplify and multiply.\nTherefore, the angle is {_fraction(angle)}°.")
