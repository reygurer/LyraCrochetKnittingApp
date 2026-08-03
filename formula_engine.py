"""
Calculation engine.

Each pattern's computed_fields entries have a "formula" that is a plain
arithmetic expression using only + - * / ( ) and field names
(e.g. "(bust/2) / swatchStretchedAcross * 20"). This is evaluated here in
Python, and the same expression is translated into an Excel formula in
excel_export.py — single source of truth, two outputs.
"""


def eval_expr(expr: str, scope: dict) -> float:
    try:
        # Restricted eval — only sees the given field names, no builtins.
        value = eval(expr, {"__builtins__": {}}, scope)
        return float(value)
    except Exception:
        return 0.0


def apply_round(value: float, rule):
    if rule in (None, "none"):
        return value
    if rule == "even":
        return 2 * round(value / 2)
    if rule == "odd":
        return 2 * round((value - 1) / 2) + 1
    if isinstance(rule, dict):
        if rule.get("type") == "mround":
            m = rule.get("multiple", 1) or 1
            return round(value / m) * m
        if rule.get("type") == "round":
            return round(value, rule.get("digits", 0))
    return value


def compute_all(pattern, inputs: dict):
    """pattern: models.Pattern instance. inputs: {field_id: float}"""
    scope = dict(inputs)
    results = {}

    for f in pattern.computed_fields:
        raw = eval_expr(f["formula"], scope)
        val = apply_round(raw, f.get("round"))
        scope[f["id"]] = val
        results[f["id"]] = val

    yarn = None
    if pattern.yarn_estimate:
        area = eval_expr(pattern.yarn_estimate["area_formula"], scope)
        swatch_area = inputs.get("swatchStretchedAcross", 0) * inputs.get(
            "swatchStretchedDown", 0
        )
        num_swatches = (area / swatch_area) if swatch_area else 0

        swatch_weight = inputs.get("swatchWeight", 0)
        skein_weight = inputs.get("skeinWeight", 0)
        skein_meterage = inputs.get("skeinMeterage", 0)
        swatch_yarn_length = inputs.get("swatchYarnLength", 0)

        if swatch_weight > 0 and skein_weight > 0:
            swatch_meters = (swatch_weight / skein_weight) * skein_meterage
        elif swatch_yarn_length > 0:
            swatch_meters = swatch_yarn_length / 100
        else:
            swatch_meters = 0

        total_meters = num_swatches * swatch_meters
        total_weight = (
            total_meters * (skein_weight / skein_meterage) if skein_meterage else 0
        )
        yarn = {"total_meters": total_meters, "total_weight": total_weight}

    return results, yarn


def render_instructions(pattern, results: dict) -> str:
    text = pattern.instructions_template or ""
    for key, val in results.items():
        text = text.replace("{%s}" % key, str(val))
    return text
