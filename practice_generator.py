"""Generate varied, deterministic-marking JSS2 Maths practice questions."""

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
