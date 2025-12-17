from metrima.math.main import _make_divider
from metrima.core.fx import Fx, fx
from metrima.utils.errors import MissingArgument
from decimal import Decimal

def _create_test(title: str,
                 action: str,
                 expected: int | float,
                 actual: int | float | Fx,
                 _python: int | float | None = None,
                 _show_actual_python: bool = False,
                 _show_divisor: bool = True,
                 _decimal: Decimal | None = None,
                 _show_actual_decimal: bool = False) -> bool | tuple[bool, bool] | tuple[bool, bool, bool]:
    from tinycolors import cprint, color, clib, cinput
    if _python is None and _show_actual_python:
        raise MissingArgument(f"Missing argument for '{_create_test.__name__}': '_python'")
    if _decimal is None and _show_actual_decimal:
        raise MissingArgument(f"Missing argument for '{_create_test.__name__}': '_decimal'")

    cprint(f"{title}", as_="bold yellow")
    cprint(f"{action} is...", as_="bold yellow")

    cprint(_make_divider('- ', 30), as_="bold white")
    cprint("Metrima says: ", as_="bold blue")
    print(f"{color.bg.black}{color.dim}{color.italic}{actual}{clib.reset}")

    cprint(_make_divider('- ', 30), as_="bold white")
    cprint("What we expected: ", as_="bold blue")
    cprint(f"{color.italic}{expected}", as_="bold green on black")

    cprint(_make_divider('- ', 30), as_="bold white")
    cprint("Metrima is..", as_="bold blue", end=" ")
    if actual == expected:
        cprint(f"{color.bold}CORRECT!", as_="italic green")
        cprint(f"{actual} is {expected}", as_="italic green")
    else:
        cprint(f"{color.bold}INCORRECT!", as_="italic red")
        cprint(f"{actual} is NOT {expected}", color="red")

    print()

    if not _show_actual_python and not _show_actual_decimal:
        cprint(_make_divider('='), as_="bold white") if _show_divisor else None
        return actual == expected

    if _show_actual_python:
        cprint("What Python says:", as_="bold cyan")
        _color = "bold red on black" if _python != expected else "bold green on black"
        cprint(f"{color.italic}{_python}", as_=_color)
        print()

    if _show_actual_decimal:
        cprint("What Decimal says:", as_="bold magenta")
        _decimal_float = float(_decimal)
        _color = "bold red on black" if _decimal_float != expected else "bold green on black"
        cprint(f"{color.italic}{_decimal}", as_=_color)

    cprint(_make_divider('='), as_="bold white") if _show_divisor else None

    if _show_actual_python and _show_actual_decimal:
        return actual == expected, _python == expected, _decimal_float == expected
    elif _show_actual_python:
        return actual == expected, _python == expected
    else:
        return actual == expected


def test_main() -> None:
    """
    Test demo for Metrima
    :return:
    """
    from tinycolors import cprint, color, clib, cinput
    cprint(_make_divider('='), as_="bold white")
    cprint("             Metrima v0.1.0 Testing Grounds             ", as_="bold white")
    cprint("        Metrima Demo, Metrima VS Python VS Decimal      ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    total = 0
    passed = 0
    pytotal = 0
    pypassed = 0
    dectotal = 0
    decpassed = 0

    # -- ADDITION -- #
    result = _create_test("Addition", "1.432 + 5.1234", 6.5554,
                          fx(1.432) + fx(5.1234),
                          1.432 + 5.1234, True,
                          True,
                          Decimal('1.432') + Decimal('5.1234'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- SUBTRACTION -- #
    result = _create_test("Subtraction", "10.0 - 2.45", 7.55,
                          fx(10.0) - fx(2.45),
                          10.0 - 2.45, True,
                          True,
                          Decimal('10.0') - Decimal('2.45'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- MULTIPLICATION -- #
    result = _create_test("Multiplication", "7.2 * 41.512", 298.8864,
                          fx(7.2) * fx(41.512),
                          7.2 * 41.512, True,
                          True,
                          Decimal('7.2') * Decimal('41.512'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- DIVISION -- #
    result = _create_test("Division", "3.6 / 1.2", 3.0,
                          fx(3.6) / fx(1.2),
                          3.6 / 1.2, True,
                          True,
                          Decimal('3.6') / Decimal('1.2'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- POWER/EXPONENTIATION -- #
    result = _create_test("Power", "2.5 ** 3", 15.625,
                          fx(2.5) ** fx(3),
                          2.5 ** 3, True,
                          True,
                          Decimal('2.5') ** Decimal('3'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- MODULO -- #
    result = _create_test("Modulo", "10.5 % 3.2", 0.9,
                          fx(10.5) % fx(3.2),
                          10.5 % 3.2, True,
                          True,
                          Decimal('10.5') % Decimal('3.2'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- FLOOR DIVISION -- #
    result = _create_test("Floor Division", "17.8 // 4.0", 4.0,
                          fx(17.8) // fx(4.0),
                          17.8 // 4.0, True,
                          True,
                          Decimal('17.8') // Decimal('4.0'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- NEGATION -- #
    result = _create_test("Negation", "-(-5.75)", 5.75,
                          -fx(-5.75),
                          -(-5.75), True,
                          True,
                          -(-Decimal('5.75')), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- ABSOLUTE VALUE -- #
    result = _create_test("Absolute Value", "abs(-12.345)", 12.345,
                          abs(fx(-12.345)),
                          abs(-12.345), True,
                          True,
                          abs(Decimal('-12.345')), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- COMPLEX EXPRESSION -- #
    result = _create_test("Complex Expression", "(2.5 + 3.5) * 4 - 10 / 2", 19.0,
                          (fx(2.5) + fx(3.5)) * fx(4) - fx(10) / fx(2),
                          (2.5 + 3.5) * 4 - 10 / 2, True,
                          True,
                          (Decimal('2.5') + Decimal('3.5')) * Decimal('4') - Decimal('10') / Decimal('2'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- CHAINED OPERATIONS -- #
    result = _create_test("Chained Addition", "1.1 + 2.2 + 3.3 + 4.4", 11.0,
                          fx(1.1) + fx(2.2) + fx(3.3) + fx(4.4),
                          1.1 + 2.2 + 3.3 + 4.4, True,
                          True,
                          Decimal('1.1') + Decimal('2.2') + Decimal('3.3') + Decimal('4.4'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # -- MIXED OPERATIONS -- #
    result = _create_test("Mixed Operations", "5 * 3 + 12 / 4 - 2", 16.0,
                          fx(5) * fx(3) + fx(12) / fx(4) - fx(2),
                          5 * 3 + 12 / 4 - 2, True, False,
                          Decimal('5') * Decimal('3') + Decimal('12') / Decimal('4') - Decimal('2'), True)
    total += 1
    pytotal += 1
    dectotal += 1
    passed += result[0]
    pypassed += result[1]
    decpassed += result[2]

    # Summary
    cprint("\n" + _make_divider('='), as_="bold white")
    cprint("                    TESTING COMPLETE!                    ", as_="bold green")
    cprint(_make_divider('='), as_="bold white")

    text_color = "bold cyan" if passed != total else "bold blue"
    cprint(f"\nMetrima Results: {passed}/{total} tests passed", as_=text_color)
    metrima_percentage = (passed / total * 100) if total > 0 else 0
    metrima_color = "bold green" if passed == total else "bold yellow" if passed > total * 0.5 else "bold red"
    cprint(f"Success Rate: {metrima_percentage:.1f}%", as_=metrima_color)

    text_color = "bold cyan" if pypassed != total else "bold magenta"
    cprint(f"\nPython Results: {pypassed}/{pytotal} tests passed", as_=text_color)
    python_percentage = (pypassed / pytotal * 100) if pytotal > 0 else 0
    python_color = "bold green" if pypassed == pytotal else "bold yellow" if pypassed > pytotal * 0.5 else "bold red"
    cprint(f"Success Rate: {python_percentage:.1f}%", as_=python_color)

    text_color = "bold cyan" if decpassed != total else "bold magenta"
    cprint(f"\nDecimal Results: {decpassed}/{dectotal} tests passed", as_=text_color)
    decimal_percentage = (decpassed / dectotal * 100) if dectotal > 0 else 0
    decimal_color = "bold green" if decpassed == dectotal else "bold yellow" if decpassed > dectotal * 0.5 else "bold red"
    cprint(f"Success Rate: {decimal_percentage:.1f}%", as_=decimal_color)

    cprint("\n" + _make_divider('='), as_="bold white")

def test_fx():
    from tinycolors import cprint, color, clib, cinput
    cprint(_make_divider('='), as_="bold white")
    cprint("             Metrima v0.1.0 Testing Grounds             ", as_="bold white")
    cprint(f"       Metrima's {color.bg.black}Fx{clib.reset} testing      ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    print()

    test_count = 0
    pass_count = 0

    cprint("Fx class testing", as_="bold white on black")
    print()


    pass_local = 0
    total_local = 6

    cprint("repr(Fx()) and str(Fx())", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1, expected2, expected3 = 'Fx(value=0, scale=0)', 'Fx(value=0, scale=0)', 'Fx(value=0, scale=0)'
    actual1, actual2, actual3 = repr(Fx("0")), repr(Fx(0)), repr(Fx(0.0))

    cprint(f"repr(Fx(\"0\")) = {actual1}", "cyan")
    cprint(f"repr(Fx(0)) = {actual2}", "cyan")
    cprint(f"repr(Fx(0.0)) = {actual3}", "cyan")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    expected4, expected5, expected6 = "3.14", "42", "0.5"
    actual4, actual5, actual6 = str(Fx("3.14")), str(Fx(42)), str(Fx(0.5))

    cprint(f"str(Fx(\"3.14\")) = {actual4}", "cyan")
    cprint(f"str(Fx(42)) = {actual5}", "cyan")
    cprint(f"str(Fx(0.5)) = {actual6}", "cyan")
    cprint('-'*40, as_="bold white")

    if actual4 == expected4:
        pass_local += 1
    if actual5 == expected5:
        pass_local += 1
    if actual6 == expected6:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Addition: 1.432 + 5.1234", as_="bold yellow")
    cprint('-' * 40, as_="bold white")

    expected1 = str(Fx("6.5554"))
    actual1 = str(Fx("1.432") + Fx("5.1234"))
    cprint(f'Fx("1.432") + Fx("5.1234") = {actual1}', "cyan")

    expected2 = str(Fx("5.5"))
    actual2 = str(Fx(2) + Fx(3.5))
    cprint(f'Fx(2) + Fx(3.5) = {actual2}', "cyan")

    expected3 = str(Fx("0.019"))
    actual3 = str(Fx(0.01) + Fx(0.009))
    cprint(f'Fx(0.01) + Fx(0.009) = {actual3}', "cyan")

    cprint('-' * 40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Subtraction: 5.5 - 2.2", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("3.3"))
    actual1 = str(Fx("5.5") - Fx("2.2"))
    cprint(f'Fx("5.5") - Fx("2.2") = {actual1}', "cyan")

    expected2 = str(Fx("7"))
    actual2 = str(Fx(10) - 3)
    cprint(f'Fx(10) - 3 = {actual2}', "cyan")

    expected3 = str(Fx("4.5"))
    actual3 = str(7 - Fx(2.5))
    cprint(f'7 - Fx(2.5) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Multiplication: 1.5 * 2", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("3.0"))
    actual1 = str(Fx("1.5") * Fx("2"))
    cprint(f'Fx("1.5") * Fx("2") = {actual1}', "cyan")

    expected2 = str(Fx("7.5"))
    actual2 = str(Fx(3) * 2.5)
    cprint(f'Fx(3) * 2.5 = {actual2}', "cyan")

    expected3 = str(Fx("8.4"))
    actual3 = str(2 * Fx(4.2))
    cprint(f'2 * Fx(4.2) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Division: 3.6 / 1.2", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("3.0"))
    actual1 = str(Fx("3.6") / Fx("1.2"))
    cprint(f'Fx("3.6") / Fx("1.2") = {actual1}', "cyan")

    expected2 = str(Fx("2.5"))
    actual2 = str(Fx(5) / 2)
    cprint(f'Fx(5) / 2 = {actual2}', "cyan")

    expected3 = str(Fx("3.0"))
    actual3 = str(12 / Fx(4))
    cprint(f'12 / Fx(4) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Floor Division: 2.5 // 1.2", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("2.0"))
    actual1 = str(Fx("2.5") // Fx("1.2"))
    cprint(f'Fx("2.5") // Fx("1.2") = {actual1}', "cyan")

    expected2 = str(Fx("2.0"))
    actual2 = str(Fx(7) // 3)
    cprint(f'Fx(7) // 3 = {actual2}', "cyan")

    expected3 = str(Fx("2.0"))
    actual3 = str(10 // Fx(4))
    cprint(f'10 // Fx(4) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 4

    cprint("Comparisons", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = True
    actual1 = Fx("2.0") == Fx("2")
    cprint(f'Fx("2.0") == Fx("2") = {actual1}', "cyan")

    expected2 = False
    actual2 = Fx(3) != 3
    cprint(f'Fx(3) != 3 = {actual2}', "cyan")

    expected3 = True
    actual3 = Fx("1.5") > Fx("1.4")
    cprint(f'Fx("1.5") > Fx("1.4") = {actual3}', "cyan")

    expected4 = True
    actual4 = Fx("1.2") < 2
    cprint(f'Fx("1.2") < 2 = {actual4}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Modulo: 5.5 % 2", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("1.5"))
    actual1 = str(Fx("5.5") % Fx("2"))
    cprint(f'Fx("5.5") % Fx("2") = {actual1}', "cyan")

    expected2 = str(Fx("1"))
    actual2 = str(Fx(7) % 3)
    cprint(f'Fx(7) % 3 = {actual2}', "cyan")

    expected3 = str(Fx("0"))
    actual3 = str(10 % Fx(2.5))
    cprint(f'10 % Fx(2.5) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 3

    cprint("Power: 2 ** 3", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("8.0"))
    actual1 = str(Fx("2") ** Fx("3"))
    cprint(f'Fx("2") ** Fx("3") = {actual1}', "cyan")

    expected2 = str(Fx("9.0"))
    actual2 = str(Fx(3) ** 2)
    cprint(f'Fx(3) ** 2 = {actual2}', "cyan")

    expected3 = str(Fx("32.0"))
    actual3 = str(2 ** Fx(5))
    cprint(f'2 ** Fx(5) = {actual3}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 5

    cprint("Type Conversions", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = 3.14
    actual1 = float(Fx("3.14"))
    cprint(f'float(Fx("3.14")) = {actual1}', "cyan")

    expected2 = 42
    actual2 = int(Fx("42.7"))
    cprint(f'int(Fx("42.7")) = {actual2}', "cyan")

    expected3 = "5.5"
    actual3 = str(Fx(5.5))
    cprint(f'str(Fx(5.5)) = {actual3}', "cyan")

    expected4 = True
    actual4 = bool(Fx("3.14"))
    cprint(f'bool(Fx("3.14")) = {actual4}', "cyan")

    expected5 = False
    actual5 = bool(Fx(0))
    cprint(f'bool(Fx(0)) = {actual5}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1
    if actual5 == expected5:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 4

    cprint("Unary Operations", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    expected1 = str(Fx("-3.14"))
    actual1 = str(-Fx("3.14"))
    cprint(f'-Fx("3.14") = {actual1}', "cyan")

    expected2 = str(Fx("5.5"))
    actual2 = str(+Fx("5.5"))
    cprint(f'+Fx("5.5") = {actual2}', "cyan")

    expected3 = str(Fx("3.14"))
    actual3 = str(abs(Fx("-3.14")))
    cprint(f'abs(Fx("-3.14")) = {actual3}', "cyan")

    expected4 = str(Fx("3.1"))
    actual4 = str(round(Fx("3.14159"), 1))
    cprint(f'round(Fx("3.14159"), 1) = {actual4}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    pass_local = 0
    total_local = 4

    cprint("In-place Operations", as_="bold yellow")
    cprint('-'*40, as_="bold white")

    x1 = Fx("5")
    x1 += Fx("3")
    expected1 = str(Fx("8"))
    actual1 = str(x1)
    cprint(f'x = Fx("5"); x += Fx("3"); x = {actual1}', "cyan")

    x2 = Fx("10")
    x2 -= 3
    expected2 = str(Fx("7"))
    actual2 = str(x2)
    cprint(f'x = Fx("10"); x -= 3; x = {actual2}', "cyan")

    x3 = Fx("4")
    x3 *= 2.5
    expected3 = str(Fx("10.0"))
    actual3 = str(x3)
    cprint(f'x = Fx("4"); x *= 2.5; x = {actual3}', "cyan")

    x4 = Fx("9")
    x4 //= 2
    expected4 = str(Fx("4.0"))
    actual4 = str(x4)
    cprint(f'x = Fx("9"); x //= 2; x = {actual4}', "cyan")

    cprint('-'*40, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()


    cprint("="*40, as_="bold white")
    cprint(f"TOTAL: {pass_count} out of {test_count} test containers passed", as_="bold white on black")
    if pass_count == test_count:
        cprint("ALL TEST CONTAINERS PASS", as_="bold green")
    else:
        cprint(f"{test_count - pass_count} test containers failed", as_="bold red")
    cprint("="*40, as_="bold white")

def test_decorators():
    """
    Comprehensive unit test for all decorators.
    """
    from tinycolors import cprint, color, clib
    from metrima.utils.decorators import legacy, timed, repeat, memo, mimic, attribute
    import time
    
    cprint(_make_divider('='), as_="bold white")
    cprint("        Metrima v0.1.0 Decorators Testing Suite         ", as_="bold white")
    cprint("   Comprehensive test showcasing all decorators         ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    print()
    
    total_tests = 0
    passed_tests = 0
    
    # ============ TEST 1: @legacy decorator ============
    cprint("TEST 1: @legacy Decorator", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    @legacy(message="old_add is deprecated, use new_add instead")
    def old_add(a: int, b: int) -> int:
        return a + b
    
    cprint("Testing deprecated function:", color="cyan")
    cprint(f'  old_add(5, 3)', as_="italic blue")
    
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = old_add(5, 3)
        
        if len(w) > 0 and issubclass(w[-1].category, DeprecationWarning):
            cprint(f"  ✓ DeprecationWarning raised", color="green")
            passed_tests += 1
        else:
            cprint(f"  ✗ No DeprecationWarning raised", color="red")
    
    cprint(f"  Result: {color.bold}{result}{clib.reset}", as_="bold green on black")
    cprint(f"  Expected: {color.bold}8{clib.reset}", as_="bold green on black")
    total_tests += 1
    print()
    
    # ============ TEST 2: @timed decorator ============
    cprint("TEST 2: @timed Decorator", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    @timed
    def compute_sum(n: int) -> int:
        total = 0
        for i in range(n):
            total += i
        return total
    
    cprint("Testing function timing:", color="cyan")
    cprint(f'  compute_sum(100000)', as_="italic blue")
    
    result, duration = compute_sum(100000)
    cprint(f"  Result: {color.bold}{result}{clib.reset}", as_="bold green on black")
    cprint(f"  Time taken: {color.italic}{duration:.6f} seconds{clib.reset}", color="yellow")
    
    if duration > 0:
        cprint(f"  ✓ Timing captured successfully", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Timing not captured", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 3: @repeat decorator ============
    cprint("TEST 3: @repeat Decorator", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    call_count = [0]  # Use list to allow modification in nested function
    
    def increment_counter() -> int:
        call_count[0] += 1
        return call_count[0]
    
    cprint("Testing function repetition:", color="cyan")
    cprint(f'  Calling repeat(increment_counter)(count=5)', as_="italic blue")
    
    call_count[0] = 0
    repeated_func = repeat(increment_counter)(count=5)
    result = repeated_func()
    
    cprint(f"  Result after 5 iterations: {color.bold}{result}{clib.reset}", as_="bold green on black")
    cprint(f"  Expected: {color.bold}5{clib.reset}", as_="bold green on black")
    cprint(f"  Function called {color.bold}{call_count[0]}{clib.reset} times", as_="italic cyan")
    
    if result == 5 and call_count[0] == 5:
        cprint(f"  ✓ Function executed 5 times correctly", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Function did not execute correctly", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 4: @memo decorator ============
    cprint("TEST 4: @memo Decorator", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    @memo
    def fibonacci_memo(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)
    
    cprint("Testing memoization with fibonacci(25):", color="cyan")
    
    # First call - slow
    cprint(f'  First call: fibonacci_memo(25)', as_="italic blue")
    start = time.perf_counter()
    result1 = fibonacci_memo(25)
    first_time = time.perf_counter() - start
    cprint(f"  Result: {color.bold}{result1}{clib.reset}", as_="bold green on black")
    cprint(f"  Time: {color.italic}{first_time:.6f} seconds{clib.reset}", color="yellow")
    
    # Second call - fast (cached)
    cprint(f'  Second call: fibonacci_memo(25) [cached]', as_="italic blue")
    start = time.perf_counter()
    result2 = fibonacci_memo(25)
    second_time = time.perf_counter() - start
    cprint(f"  Result: {color.bold}{result2}{clib.reset}", as_="bold green on black")
    cprint(f"  Time: {color.italic}{second_time:.9f} seconds{clib.reset}", color="cyan")
    
    speedup = first_time / second_time if second_time > 0 else float('inf')
    cprint(f"  Speedup: {color.bold}{speedup:.0f}x faster{clib.reset}", as_="bold bright green")
    
    if result1 == result2 and second_time < first_time:
        cprint(f"  ✓ Memoization working correctly", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Memoization failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 5: @memo decorator - PARAMETERS ============
    cprint("TEST 5: @memo Decorator (with parameters)", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing memo with cache cleaning (max_cache=3):", color="cyan")
    
    @memo(clean=True, max_cache=3)
    def expensive_func(x: int) -> int:
        return x * x
    
    cprint("  Calling with different arguments to exceed max_cache...", as_="italic blue")
    
    r1 = expensive_func(1)
    r2 = expensive_func(2)
    r3 = expensive_func(3)
    cprint(f"  expensive_func(1) = {color.bold}{r1}{clib.reset}", as_="bold green on black")
    cprint(f"  expensive_func(2) = {color.bold}{r2}{clib.reset}", as_="bold green on black")
    cprint(f"  expensive_func(3) = {color.bold}{r3}{clib.reset}", as_="bold green on black")
    
    r4 = expensive_func(4)
    cprint(f"  expensive_func(4) = {color.bold}{r4}{clib.reset}", as_="bold green on black")
    cprint(f"  Cache exceeded max_cache, oldest entry cleaned", as_="italic cyan")
    
    if r1 == 1 and r2 == 4 and r3 == 9 and r4 == 16:
        cprint(f"  ✓ Memo with cache cleaning works", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Memo cache cleaning failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 5b: @memo decorator - NO CLEANING ============
    cprint("TEST 5b: @memo Decorator (clean=False)", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing memo with clean=False (unlimited cache):", color="cyan")
    
    @memo(clean=False, max_cache=2)
    def square(x: int) -> int:
        return x ** 2
    
    cprint("  Calling with multiple arguments (cache won't be cleaned)...", as_="italic blue")
    
    s1 = square(5)
    s2 = square(6)
    s3 = square(7)
    s4 = square(5)
    
    cprint(f"  square(5) = {color.bold}{s1}{clib.reset}", as_="bold green on black")
    cprint(f"  square(6) = {color.bold}{s2}{clib.reset}", as_="bold green on black")
    cprint(f"  square(7) = {color.bold}{s3}{clib.reset}", as_="bold green on black")
    cprint(f"  square(5) again = {color.bold}{s4}{clib.reset} (from cache)", as_="italic green")
    
    if s1 == 25 and s2 == 36 and s3 == 49 and s4 == 25:
        cprint(f"  ✓ Memo without cleaning works", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Memo without cleaning failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 5c: @memo decorator - NO PARENTHESES ============
    cprint("TEST 5c: @memo Decorator (no parentheses)", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing @memo (auto-detects callable):", color="cyan")
    
    call_counter = [0]
    
    @memo
    def cube(x: int) -> int:
        call_counter[0] += 1
        return x ** 3
    
    cprint("  Calling cube(3) twice to test caching...", as_="italic blue")
    call_counter[0] = 0
    
    c1 = cube(3)
    c2 = cube(3)
    
    cprint(f"  cube(3) first time = {color.bold}{c1}{clib.reset}", as_="bold green on black")
    cprint(f"  cube(3) second time = {color.bold}{c2}{clib.reset}", as_="bold green on black")
    cprint(f"  Function called {color.bold}{call_counter[0]}{clib.reset} time(s) total", as_="italic cyan")
    
    if c1 == 27 and c2 == 27 and call_counter[0] == 1:
        cprint(f"  ✓ @memo (no parentheses) works - cached on second call", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ @memo (no parentheses) failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 5d: @memo decorator - WITH KWARGS ============
    cprint("TEST 5d: @memo Decorator (with kwargs)", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing memo with kwargs:", color="cyan")
    
    @memo
    def power(base: int, exponent: int = 2) -> int:
        return base ** exponent
    
    cprint("  Calling with positional and keyword args...", as_="italic blue")
    
    p1 = power(2, 3)
    p2 = power(2, exponent=3)
    p3 = power(2, 3)
    
    cprint(f"  power(2, 3) = {color.bold}{p1}{clib.reset}", as_="bold green on black")
    cprint(f"  power(2, exponent=3) = {color.bold}{p2}{clib.reset}", as_="bold green on black")
    cprint(f"  power(2, 3) again = {color.bold}{p3}{clib.reset}", as_="bold green on black")
    
    if p1 == 8 and p2 == 8 and p3 == 8:
        cprint(f"  ✓ Memo with kwargs works", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Memo with kwargs failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 6: @mimic decorator ============
    cprint("TEST 6: @mimic Decorator", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    def original_func(x: int, y: int) -> int:
        """Original function documentation."""
        return x + y
    
    cprint("Testing metadata preservation:", color="cyan")
    
    @mimic(original_func)
    def wrapper_func(x: int, y: int) -> int:
        return x + y
    
    cprint(f"  Original function name: {color.bold}{original_func.__name__}{clib.reset}", as_="italic green")
    cprint(f"  Wrapper function name (after @mimic): {color.bold}{wrapper_func.__name__}{clib.reset}", as_="italic green")
    cprint(f"  Original docstring: {color.italic}{original_func.__doc__}{clib.reset}", as_="italic cyan")
    cprint(f"  Wrapper docstring (after @mimic): {color.italic}{wrapper_func.__doc__}{clib.reset}", as_="italic cyan")
    
    if wrapper_func.__name__ == original_func.__name__ and wrapper_func.__doc__ == original_func.__doc__:
        cprint(f"  ✓ Metadata copied correctly", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Metadata not copied", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 7: attribute descriptor ============
    cprint("TEST 7: attribute Descriptor", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    class Person:
        def __init__(self, name: str, age: int):
            self._name = name
            self._age = age
        
        @attribute
        def name(self):
            """Get the person's name."""
            return self._name
        
        @name.setter
        def name(self, value: str):
            if isinstance(value, str):
                self._name = value
        
        @attribute
        def age(self):
            """Get the person's age."""
            return self._age
        
        @age.setter
        def age(self, value: int):
            if isinstance(value, int) and value > 0:
                self._age = value
    
    cprint("Testing descriptor with Person class:", color="cyan")
    
    person = Person("Alice", 30)
    cprint(f"  Created Person instance: name={color.bold}{person.name}{clib.reset}, age={color.bold}{person.age}{clib.reset}", as_="italic green")
    
    person.name = "Bob"
    person.age = 25
    cprint(f"  Updated Person: name={color.bold}{person.name}{clib.reset}, age={color.bold}{person.age}{clib.reset}", as_="italic green")
    
    if person.name == "Bob" and person.age == 25:
        cprint(f"  ✓ Descriptor get/set working correctly", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Descriptor failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ SUMMARY ============
    cprint(_make_divider('='), as_="bold white")
    cprint(f"DECORATORS TEST SUMMARY", as_="bold white on black")
    cprint(_make_divider('='), as_="bold white")
    
    success_color = "bold green" if passed_tests == total_tests else "bold yellow" if passed_tests > total_tests * 0.5 else "bold red"
    cprint(f"\nTests Passed: {passed_tests}/{total_tests}", as_=success_color)
    
    percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    cprint(f"Success Rate: {percentage:.1f}%", as_=success_color)
    
    if passed_tests == total_tests:
        cprint("\n🎉 ALL DECORATOR TESTS PASSED! 🎉", as_="bold bright green")
    else:
        cprint(f"\n⚠️  {total_tests - passed_tests} test(s) failed", as_="bold bright red")
    
    cprint(_make_divider('='), as_="bold white")
    print()

def test_lib():
    """
    Comprehensive unit test for lib module functions.
    """
    from tinycolors import cprint, color, clib
    from metrima.lib import (length, invert, is_whitespace, trim, has, locate, 
                             span, attach, push_back, combinelst, duplicate, 
                             verify, chop, is_whole, indexed)
    
    cprint(_make_divider('='), as_="bold white")
    cprint("          Metrima v0.1.0 Library Functions Testing       ", as_="bold white")
    cprint("   Comprehensive test for lib.py utility functions       ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    print()
    
    total_tests = 0
    passed_tests = 0
    
    # ============ TEST 1: length() ============
    cprint("TEST 1: length()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing string length:", color="cyan")
    result = length("hello")
    cprint(f"  length('hello') = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == 5:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected 5, got {result}", color="red")
    
    cprint("Testing list length:", color="cyan")
    result = length([1, 2, 3, 4])
    cprint(f"  length([1, 2, 3, 4]) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == 4:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected 4, got {result}", color="red")
    
    total_tests += 2
    print()
    
    # ============ TEST 2: invert() ============
    cprint("TEST 2: invert()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing list inversion:", color="cyan")
    result = invert([1, 2, 3, 4, 5])
    expected = [5, 4, 3, 2, 1]
    cprint(f"  invert([1, 2, 3, 4, 5]) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected {expected}", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 3: is_whitespace() ============
    cprint("TEST 3: is_whitespace()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing whitespace detection:", color="cyan")
    result1 = is_whitespace("   ")
    result2 = is_whitespace("hello")
    cprint(f"  is_whitespace('   ') = {color.bold}{result1}{clib.reset}", as_="bold green on black")
    cprint(f"  is_whitespace('hello') = {color.bold}{result2}{clib.reset}", as_="bold green on black")
    if result1 and not result2:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Whitespace detection failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 4: trim() ============
    cprint("TEST 4: trim()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing string trimming:", color="cyan")
    result = trim("   hello world   ")
    expected = "hello world"
    cprint(f"  trim('   hello world   ') = {color.italic}'{result}'{clib.reset}", as_="italic cyan")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected '{expected}'", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 5: has() ============
    cprint("TEST 5: has()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing truthiness check:", color="cyan")
    result1 = has([0, 0, 1, 0])
    result2 = has([0, 0, 0, 0])
    cprint(f"  has([0, 0, 1, 0]) = {color.bold}{result1}{clib.reset}", as_="bold green on black")
    cprint(f"  has([0, 0, 0, 0]) = {color.bold}{result2}{clib.reset}", as_="bold green on black")
    if result1 and not result2:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Truthiness check failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 6: locate() ============
    cprint("TEST 6: locate()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing substring location:", color="cyan")
    result = locate("hello world", "world")
    cprint(f"  locate('hello world', 'world') = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == 6:
        cprint(f"  ✓ Correct (found at index 6)", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected 6, got {result}", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 7: span() ============
    cprint("TEST 7: span()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing span generator:", color="cyan")
    result = list(span(5))
    expected = [0, 1, 2, 3, 4]
    cprint(f"  list(span(5)) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected {expected}", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 8: attach() & push_back() ============
    cprint("TEST 8: attach() & push_back()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing list attachment:", color="cyan")
    lst = [1, 2, 3]
    attach(lst, 4)
    cprint(f"  attach([1, 2, 3], 4) → {color.bold}{lst}{clib.reset}", as_="bold green on black")
    
    result = push_back([1, 2, 3], 4)
    cprint(f"  push_back([1, 2, 3], 4) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if lst == [1, 2, 3, 4] and result == [1, 2, 3, 4]:
        cprint(f"  ✓ Both attach and push_back work correctly", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ List operations failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 9: combinelst() ============
    cprint("TEST 9: combinelst()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing list combination:", color="cyan")
    result = combinelst([1, 2], [3, 4], [5, 6])
    expected = [1, 2, 3, 4, 5, 6]
    cprint(f"  combinelst([1,2], [3,4], [5,6]) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected {expected}", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 10: duplicate() ============
    cprint("TEST 10: duplicate()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing deep duplication:", color="cyan")
    original = [1, [2, 3], {"key": "value"}]
    result = duplicate(original)
    result[1][0] = 99
    cprint(f"  Original after modifying duplicate: {color.bold}{original}{clib.reset}", as_="bold green on black")
    if original[1][0] == 2:
        cprint(f"  ✓ Deep copy works (original unchanged)", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Deep copy failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 11: verify() ============
    cprint("TEST 11: verify()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing element verification:", color="cyan")
    result1 = verify([1, 2, 3, 4])
    result2 = verify([1, 2, 0, 4])
    cprint(f"  verify([1, 2, 3, 4]) = {color.bold}{result1}{clib.reset}", as_="bold green on black")
    cprint(f"  verify([1, 2, 0, 4]) = {color.bold}{result2}{clib.reset}", as_="bold green on black")
    if result1 and not result2:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Verification failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 12: chop() ============
    cprint("TEST 12: chop()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing string splitting:", color="cyan")
    result = chop("hello,world,python", ",")
    expected = ["hello", "world", "python"]
    cprint(f"  chop('hello,world,python', ',') = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected {expected}", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 13: is_whole() ============
    cprint("TEST 13: is_whole()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing whole number detection:", color="cyan")
    result1 = is_whole(5)
    result2 = is_whole(5.0)
    result3 = is_whole(5.5)
    cprint(f"  is_whole(5) = {color.bold}{result1}{clib.reset}", as_="bold green on black")
    cprint(f"  is_whole(5.0) = {color.bold}{result2}{clib.reset}", as_="bold green on black")
    cprint(f"  is_whole(5.5) = {color.bold}{result3}{clib.reset}", as_="bold green on black")
    if result1 and result2 and not result3:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Whole number detection failed", color="red")
    
    total_tests += 1
    print()
    
    # ============ TEST 14: indexed() ============
    cprint("TEST 14: indexed()", as_="bold yellow")
    cprint('-' * 50, as_="bold white")
    
    cprint("Testing indexed iteration:", color="cyan")
    result = list(indexed(['a', 'b', 'c']))
    expected = [(0, 'a'), (1, 'b'), (2, 'c')]
    cprint(f"  list(indexed(['a', 'b', 'c'])) = {color.bold}{result}{clib.reset}", as_="bold green on black")
    if result == expected:
        cprint(f"  ✓ Correct", color="green")
        passed_tests += 1
    else:
        cprint(f"  ✗ Expected {expected}", color="red")
    
    total_tests += 1
    print()
    
    # ============ SUMMARY ============
    cprint(_make_divider('='), as_="bold white")
    cprint(f"LIB FUNCTIONS TEST SUMMARY", as_="bold white on black")
    cprint(_make_divider('='), as_="bold white")
    
    success_color = "bold green" if passed_tests == total_tests else "bold yellow" if passed_tests > total_tests * 0.5 else "bold red"
    cprint(f"\nTests Passed: {passed_tests}/{total_tests}", as_=success_color)
    
    percentage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    cprint(f"Success Rate: {percentage:.1f}%", as_=success_color)
    
    if passed_tests == total_tests:
        cprint("\n🎉 ALL LIB FUNCTION TESTS PASSED! 🎉", as_="bold bright green")
    else:
        cprint(f"\n⚠️  {total_tests - passed_tests} test(s) failed", as_="bold bright red")
    
    cprint(_make_divider('='), as_="bold white")
    print()

def test_timeunits():
    """
    Unit tests for `metrima.timeunits` arithmetic, comparisons,
    and millisecond remainder preservation.
    """
    from tinycolors import cprint
    from metrima.units.time import Hour, Minute, Second, Millisecond

    cprint(_make_divider('='), as_="bold white")
    cprint("            Metrima timeunits Test Suite            ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    print()

    total = 0
    passed = 0

    # TEST 1: Hour + Hour -> Second (3 hours = 10800s)
    cprint('TEST: Hour + Hour -> Second', as_='bold yellow')
    a = Hour(1)
    b = Hour(2)
    res = a + b
    total += 1
    val = getattr(res, 'value', None)
    msval = getattr(res, 'milliseconds', 0) or 0
    try:
        cond = int(val) == 10800 and int(msval) == 0
    except Exception:
        cond = False
    if cond:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint(f'  ✗ Failed — got: {res}', color='red')

    # TEST 2: Millisecond leftover preserved (200ms + 300ms = 0s + 500ms)
    cprint('TEST: Millisecond addition preserves leftover', as_='bold yellow')
    m1 = Millisecond(200)
    m2 = Millisecond(300)
    r2 = m1 + m2
    total += 1
    try:
        cond2 = int(getattr(r2, 'value', 0)) == 0 and int(getattr(r2, 'milliseconds', 0)) == 500
    except Exception:
        cond2 = False
    if cond2:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint(f'  ✗ Failed — got: {r2}', color='red')

    # TEST 3: Numeric addition treated as seconds (30s + 15 -> 45s)
    cprint('TEST: Second + numeric seconds', as_='bold yellow')
    s = Second(30)
    r3 = s + 15
    total += 1
    try:
        cond3 = int(getattr(r3, 'value', None)) == 45
    except Exception:
        cond3 = False
    if cond3:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint(f'  ✗ Failed — got: {r3}', color='red')

    # TEST 4: Comparisons (1 minute > 30 seconds)
    cprint('TEST: Minute(1) > Second(30)', as_='bold yellow')
    total += 1
    cond4 = Minute(1) > Second(30)
    if cond4:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint('  ✗ Failed', color='red')

    # TEST 5: Subtraction (2h - 30m = 5400s)
    cprint('TEST: Hour(2) - Minute(30) -> 5400s', as_='bold yellow')
    total += 1
    r5 = Hour(2) - Minute(30)
    try:
        cond5 = int(getattr(r5, 'value', None)) == 5400
    except Exception:
        cond5 = False
    if cond5:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint(f'  ✗ Failed — got: {r5}', color='red')

    # TEST 6: Multiplication (1 minute * 2 = 120s)
    cprint('TEST: Minute(1) * 2 -> 120s', as_='bold yellow')
    total += 1
    r6 = Minute(1) * 2
    try:
        cond6 = int(getattr(r6, 'value', None)) == 120
    except Exception:
        cond6 = False
    if cond6:
        cprint('  ✓ Passed', color='green')
        passed += 1
    else:
        cprint(f'  ✗ Failed — got: {r6}', color='red')

    # SUMMARY
    cprint(_make_divider('='), as_='bold white')
    success_color = 'bold green' if passed == total else 'bold yellow' if passed > total * 0.5 else 'bold red'
    cprint(f'\nTimeUnits Tests Passed: {passed}/{total}', as_=success_color)
    cprint(_make_divider('='), as_='bold white')
    print()

def test_weight_units():
    """
    Comprehensive test suite for Metrima weight units.
    Tests conversions, arithmetic operations, and cross-system compatibility.
    """
    from metrima.units.weight import oz, lb, kg, mcg, mg, tonne, gram, grain, ton
    from tinycolors import cprint, color, clib
    
    cprint(_make_divider('='), as_="bold white")
    cprint("             Metrima v0.1.0 Testing Grounds             ", as_="bold white")
    cprint(f"       Metrima's {color.bg.black}Weight Units{clib.reset} testing      ", as_="bold white")
    cprint(_make_divider('='), as_="bold white")
    print()

    test_count = 0
    pass_count = 0

    cprint("Weight Unit Testing", as_="bold white on black")
    print()

    pass_local = 0
    total_local = 6

    cprint("Basic Unit Creation", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    expected1 = "1"
    actual1 = str(kg(1).__kilogram__())
    cprint(f'kg(1).__kilogram__() = {actual1}', "cyan")

    expected2 = "1000"
    actual2 = str(kg(1).__gram__())
    cprint(f'kg(1).__gram__() = {actual2}', "cyan")

    expected3 = "2.20462262185"
    actual3 = str(kg(1).__pound__())
    cprint(f'kg(1).__pound__() = {actual3}', "cyan")

    expected4 = "1"
    actual4 = str(lb(1).__pound__())
    cprint(f'lb(1).__pound__() = {actual4}', "cyan")

    expected5 = "0.45359237"
    actual5 = str(lb(1).__kilogram__())
    cprint(f'lb(1).__kilogram__() = {actual5}', "cyan")

    expected6 = "16"
    actual6 = str(lb(1).__ounce__())
    cprint(f'lb(1).__ounce__() = {actual6}', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1
    if actual5 == expected5:
        pass_local += 1
    if actual6 == expected6:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Float Input Handling (Bug Fix Verification)", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = kg(1.5)
    expected1 = "1.5"
    actual1 = str(w1.__kilogram__())
    cprint(f'kg(1.5).__kilogram__() = {actual1}', "cyan")

    expected2 = "1500"
    actual2 = str(w1.__gram__())
    cprint(f'kg(1.5).__gram__() = {actual2}', "cyan")

    expected3 = "1500000"
    actual3 = str(w1.__milligram__())
    cprint(f'kg(1.5).__milligram__() = {actual3}', "cyan")

    expected4 = "1500000000"
    actual4 = str(w1.__microgram__())
    cprint(f'kg(1.5).__microgram__() = {actual4}', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 5

    cprint("Metric System Conversions", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    expected1 = "1000000"
    actual1 = str(kg(1).__microgram__())
    cprint(f'kg(1).__microgram__() = {actual1} mcg', "cyan")

    expected2 = "1000000"
    actual2 = str(kg(1).__milligram__())
    cprint(f'kg(1).__milligram__() = {actual2} mg', "cyan")

    expected3 = "0.001"
    actual3 = str(kg(1).__tonne__())
    cprint(f'kg(1).__tonne__() = {actual3} tonnes', "cyan")

    expected4 = "2500"
    actual4 = str(gram(2.5).__milligram__())
    cprint(f'gram(2.5).__milligram__() = {actual4} mg', "cyan")

    expected5 = "500"
    actual5 = str(tonne(0.5).__kilogram__())
    cprint(f'tonne(0.5).__kilogram__() = {actual5} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1
    if actual5 == expected5:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 5

    cprint("Imperial System Conversions", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    expected1 = "7000"
    actual1 = str(lb(1).__grain__())
    cprint(f'lb(1).__grain__() = {actual1} grains', "cyan")

    expected2 = "437.5"
    actual2 = str(oz(1).__grain__())
    cprint(f'oz(1).__grain__() = {actual2} grains', "cyan")

    expected3 = "0.000446428571428571"
    actual3 = str(grain(1).__pound__())
    cprint(f'grain(1).__pound__() = {actual3} lb', "cyan")

    expected4 = "2240"
    actual4 = str(ton(1).__pound__())
    cprint(f'ton(1).__pound__() = {actual4} lb', "cyan")

    expected5 = "8"
    actual5 = str(oz(0.5).__pound__())
    cprint(f'oz(0.5).__pound__() = {actual5} lb', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1
    if str(float(oz(0.5).__pound__())) == "0.03125":
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 5

    cprint("Cross-System Conversions", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    expected1 = "453.59237"
    actual1 = str(lb(1).__gram__())
    cprint(f'lb(1).__gram__() = {actual1} g', "cyan")

    expected2 = "28.349523125"
    actual2 = str(oz(1).__gram__())
    cprint(f'oz(1).__gram__() = {actual2} g', "cyan")

    expected3 = "0.06479891"
    actual3 = str(grain(1).__gram__())
    cprint(f'grain(1).__gram__() = {actual3} g', "cyan")

    expected4 = "35.27396194958041"
    actual4 = str(kg(1).__ounce__())
    cprint(f'kg(1).__ounce__() = {actual4} oz', "cyan")

    expected5 = "15432.358352941431"
    actual5 = str(kg(1).__grain__())
    cprint(f'kg(1).__grain__() = {actual5} grains', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1
    if actual5 == expected5:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Metric Addition (Same System)", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = kg(2) + kg(3)
    expected1 = "5"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(2) + kg(3) = {actual1} kg', "cyan")

    result2 = gram(500) + gram(250)
    expected2 = "750"
    actual2 = str(result2.__gram__())
    cprint(f'gram(500) + gram(250) = {actual2} g', "cyan")

    result3 = mg(100) + mg(50)
    expected3 = "150"
    actual3 = str(result3.__milligram__())
    cprint(f'mg(100) + mg(50) = {actual3} mg', "cyan")

    result4 = kg(1.5) + gram(500)
    expected4 = "2"
    actual4 = str(result4.__kilogram__())
    cprint(f'kg(1.5) + gram(500) = {actual4} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Imperial Addition (Same System)", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = lb(2) + lb(3)
    expected1 = "5"
    actual1 = str(result1.__pound__())
    cprint(f'lb(2) + lb(3) = {actual1} lb', "cyan")

    result2 = oz(8) + oz(8)
    expected2 = "16"
    actual2 = str(result2.__ounce__())
    cprint(f'oz(8) + oz(8) = {actual2} oz', "cyan")

    result3 = grain(1000) + grain(500)
    expected3 = "1500"
    actual3 = str(result3.__grain__())
    cprint(f'grain(1000) + grain(500) = {actual3} grains', "cyan")

    result4 = lb(1) + oz(8)
    expected4 = "1.5"
    actual4 = str(result4.__pound__())
    cprint(f'lb(1) + oz(8) = {actual4} lb', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 3

    cprint("Cross-System Addition (Returns Metric)", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = kg(1) + lb(1)
    expected1 = "1.45359237"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(1) + lb(1) = {actual1} kg', "cyan")

    result2 = gram(500) + oz(1)
    expected2 = "528.349523125"
    actual2 = str(result2.__gram__())
    cprint(f'gram(500) + oz(1) = {actual2} g', "cyan")

    result3 = lb(2) + kg(1)
    expected3 = "2.20462262185"
    actual3 = str(result3.__kilogram__())
    cprint(f'lb(2) + kg(1) = {actual3} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Subtraction Operations", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = kg(5) - kg(2)
    expected1 = "3"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(5) - kg(2) = {actual1} kg', "cyan")

    result2 = lb(10) - lb(3)
    expected2 = "7"
    actual2 = str(result2.__pound__())
    cprint(f'lb(10) - lb(3) = {actual2} lb', "cyan")

    result3 = kg(2) - gram(500)
    expected3 = "1.5"
    actual3 = str(result3.__kilogram__())
    cprint(f'kg(2) - gram(500) = {actual3} kg', "cyan")

    result4 = kg(2) - lb(1)
    expected4 = "1.54640763"
    actual4 = str(result4.__kilogram__())
    cprint(f'kg(2) - lb(1) = {actual4} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Multiplication Operations", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = kg(2) * kg(3)
    expected1 = "6"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(2) * kg(3) = {actual1} kg', "cyan")

    result2 = lb(4) * lb(2)
    expected2 = "8"
    actual2 = str(result2.__pound__())
    cprint(f'lb(4) * lb(2) = {actual2} lb', "cyan")

    result3 = gram(100) * gram(5)
    expected3 = "500"
    actual3 = str(result3.__gram__())
    cprint(f'gram(100) * gram(5) = {actual3} g', "cyan")

    result4 = kg(2) * lb(2)
    expected4 = "1.8143695"
    actual4 = str(result4.__kilogram__())
    cprint(f'kg(2) * lb(2) = {actual4} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Division Operations", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    result1 = kg(10) / kg(2)
    expected1 = "5"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(10) / kg(2) = {actual1} kg', "cyan")

    result2 = lb(15) / lb(3)
    expected2 = "5"
    actual2 = str(result2.__pound__())
    cprint(f'lb(15) / lb(3) = {actual2} lb', "cyan")

    result3 = gram(1000) / gram(4)
    expected3 = "250"
    actual3 = str(result3.__gram__())
    cprint(f'gram(1000) / gram(4) = {actual3} g', "cyan")

    result4 = kg(10) / lb(2)
    expected4 = "11.0231131092"
    actual4 = str(result4.__kilogram__())
    cprint(f'kg(10) / lb(2) = {actual4} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 3

    cprint("Unit Wrapper Functions", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = gram(1000)
    result1 = kg(w1)
    expected1 = "1"
    actual1 = str(result1.__kilogram__())
    cprint(f'kg(gram(1000)) = {actual1} kg', "cyan")

    w2 = lb(16)
    result2 = oz(w2)
    expected2 = "256"
    actual2 = str(result2.__ounce__())
    cprint(f'oz(lb(16)) = {actual2} oz', "cyan")

    w3 = kg(2.5)
    result3 = lb(w3)
    expected3 = "5.51155655462"
    actual3 = str(result3.__pound__())
    cprint(f'lb(kg(2.5)) = {actual3} lb', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 4

    cprint("Complex Fractional Values", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = kg(2.567)
    expected1 = "2567"
    actual1 = str(w1.__gram__())
    cprint(f'kg(2.567).__gram__() = {actual1} g', "cyan")

    w2 = lb(3.14159)
    expected2 = "50.26544"
    actual2 = str(w2.__ounce__())
    cprint(f'lb(3.14159).__ounce__() = {actual2} oz', "cyan")

    w3 = gram(1.234)
    expected3 = "1234"
    actual3 = str(w3.__milligram__())
    cprint(f'gram(1.234).__milligram__() = {actual3} mg', "cyan")

    w4 = oz(0.5)
    expected4 = "14.1747615625"
    actual4 = str(w4.__gram__())
    cprint(f'oz(0.5).__gram__() = {actual4} g', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1
    if actual4 == expected4:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 3

    cprint("Very Small Units (Precision Test)", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = mcg(500)
    expected1 = "0.5"
    actual1 = str(w1.__milligram__())
    cprint(f'mcg(500).__milligram__() = {actual1} mg', "cyan")

    w2 = mg(0.001)
    expected2 = "1"
    actual2 = str(w2.__microgram__())
    cprint(f'mg(0.001).__microgram__() = {actual2} mcg', "cyan")

    w3 = grain(0.5)
    expected3 = "32.399455"
    actual3 = str(w3.__milligram__())
    cprint(f'grain(0.5).__milligram__() = {actual3} mg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 3

    cprint("Very Large Units", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = tonne(5)
    expected1 = "5000"
    actual1 = str(w1.__kilogram__())
    cprint(f'tonne(5).__kilogram__() = {actual1} kg', "cyan")

    w2 = ton(2)
    expected2 = "4480"
    actual2 = str(w2.__pound__())
    cprint(f'ton(2).__pound__() = {actual2} lb', "cyan")

    w3 = tonne(1)
    expected3 = "1016.0469088"
    actual3 = str(ton(w3).__kilogram__())
    cprint(f'ton(tonne(1)).__kilogram__() = {actual3} kg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    pass_local = 0
    total_local = 3

    cprint("Chained Conversions", as_="bold yellow")
    cprint('-'*60, as_="bold white")

    w1 = kg(1)
    result1 = gram(lb(oz(w1)))
    expected1 = "1000"
    actual1 = str(result1.__gram__())
    cprint(f'gram(lb(oz(kg(1)))).__gram__() = {actual1} g', "cyan")

    w2 = lb(1)
    result2 = kg(gram(mg(w2)))
    expected2 = "0.45359237"
    actual2 = str(result2.__kilogram__())
    cprint(f'kg(gram(mg(lb(1)))).__kilogram__() = {actual2} kg', "cyan")

    w3 = tonne(0.001)
    result3 = mg(gram(w3))
    expected3 = "1000000"
    actual3 = str(result3.__milligram__())
    cprint(f'mg(gram(tonne(0.001))).__milligram__() = {actual3} mg', "cyan")

    cprint('-'*60, as_="bold white")

    if actual1 == expected1:
        pass_local += 1
    if actual2 == expected2:
        pass_local += 1
    if actual3 == expected3:
        pass_local += 1

    test_count += 1
    if pass_local == total_local:
        pass_count += 1
        cprint(f"Pass, {pass_local} out of {total_local}", as_="bold green")
    else:
        cprint(f"Fail, {pass_local} out of {total_local}", as_="bold red")

    print()

    cprint("="*60, as_="bold white")
    cprint(f"TOTAL: {pass_count} out of {test_count} test containers passed", as_="bold white on black")
    if pass_count == test_count:
        cprint("ALL TEST CONTAINERS PASS", as_="bold green")
    else:
        cprint(f"{test_count - pass_count} test containers failed", as_="bold red")
    cprint("="*60, as_="bold white")

def menu():
    from tinycolors import cprint, color, clib, cinput
    cprint(_make_divider('='), as_="bold white")
    cprint("             Metrima v0.1.0 Testing Grounds              ", as_="bold white")
    cprint(" Welcome to Metrima! A small, comprehensive math library.", as_="bold white")
    cprint(_make_divider('='), as_="bold white")

    print()
    cprint(f'{color.italic}1. Competition Demo', as_="bold bright red")
    cprint('2. Fx Class Testing', as_="italic blue")
    cprint('3. Decorators Testing', as_="italic bright magenta")
    cprint('4. Metrimalib Testing', as_="italic bright cyan")
    cprint('5. TimeUnits Testing', as_="italic bright green")
    cprint('6. Weight Unit Testing', as_="italic bright yellow")
    user_choice = cinput(f"{color.italic}Which test would you like to run? ", as_="dim default")
    print()

    _make_divider()
    if user_choice in ["1", "competition", "c", "comp", "main"]:
        test_main()
    elif user_choice in ["2", "fx"]:
        test_fx()
    elif user_choice in ["3", "decorators", "d"]:
        test_decorators()
    elif user_choice in ["4", "lib", "library", "metrimalib", "l"]:
        test_lib()
    elif user_choice in ["5", "timeunits", "time", "t"]:
        test_timeunits()
    elif user_choice in ["6", "weight", "weightunit", "w"]:
        test_weight_units()
    elif user_choice in ["quit", "exit", "q", "x"]:
        exit(0)
    else:
        cprint('x Invalid choice', as_="bold red")

if __name__ == "__main__":
    menu()