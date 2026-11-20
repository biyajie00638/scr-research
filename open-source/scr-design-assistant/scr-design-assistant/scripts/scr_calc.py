#!/usr/bin/env python3
"""Deterministic SCR engineering screening; standard library only.

All volumes use explicitly supplied temperature, absolute pressure and gas basis.
NOx mass is always NO2-equivalent. Water fraction is a wet-gas mole/volume
fraction; it must describe the same operating point as the supplied flow.
Ideal-gas conversions do not model condensation. GHSV uses installed catalyst
block bulk volume, including its channels, excluding unfilled slots and spares.

CLI: python scr_calc.py input.json (or '-' for JSON on stdin).
Request: {"operation": "nox_from_ef", "inputs": {...}}
Batch: {"calculations": [{"id": "optional-label", "operation": ..., "inputs": ...}]}
The CLI only reads input and writes JSON to stdout; it never edits input files.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

R_KPA_M3_PER_KMOL_K = 8.31446261815324
MW_NO2_KG_PER_KMOL = 46.0055
MW_UREA_KG_PER_KMOL = 60.0553

PENDING_CHECKS = [
    "Catalyst conversion, aging, temperature window and ammonia slip require validated supplier data.",
    "Pressure drop and engine backpressure require physical geometry, material and operating inputs.",
    "Mixing, evaporation, equipment suitability and electrical/cabinet certification remain unverified.",
]


def _number(name, value, *, minimum=None, maximum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}")
    return value


def _temperature(name, value):
    value = _number(name, value)
    if value <= -273.15:
        raise ValueError(f"{name} must be above absolute zero")
    return value + 273.15


def _basis(value):
    if value not in ("dry", "wet"):
        raise ValueError("gas basis must be 'dry' or 'wet'")
    return value


def _water(value):
    value = _number("water_mole_fraction_wet", value, minimum=0)
    if value >= 1:
        raise ValueError("water_mole_fraction_wet must be less than one")
    return value


def _basis_flow(flow, source, target, water_mole_fraction_wet):
    _basis(source)
    _basis(target)
    if water_mole_fraction_wet is not None:
        water_mole_fraction_wet = _water(water_mole_fraction_wet)
    if source == target:
        return flow
    if water_mole_fraction_wet is None:
        raise ValueError("water_mole_fraction_wet is required to change dry/wet basis")
    dry_fraction = 1 - water_mole_fraction_wet
    return flow * dry_fraction if source == "wet" else flow / dry_fraction


def absolute_pressure(*, gauge_pressure_kpa, ambient_pressure_kpa_abs):
    """Convert a supplied gauge pressure using the supplied local ambient pressure."""
    gauge = _number("gauge_pressure_kpa", gauge_pressure_kpa)
    ambient = _number("ambient_pressure_kpa_abs", ambient_pressure_kpa_abs, positive=True)
    result = _number("pressure_kpa_abs", gauge + ambient, positive=True)
    return {"pressure_kpa_abs": result}


def state_flow(*, volume_m3_h, from_temperature_c, from_pressure_kpa_abs,
               to_temperature_c, to_pressure_kpa_abs):
    """Convert ideal-gas volume at unchanged composition/basis: Q2=Q1*T2/T1*P1/P2."""
    flow = _number("volume_m3_h", volume_m3_h, minimum=0)
    t1 = _temperature("from_temperature_c", from_temperature_c)
    t2 = _temperature("to_temperature_c", to_temperature_c)
    p1 = _number("from_pressure_kpa_abs", from_pressure_kpa_abs, positive=True)
    p2 = _number("to_pressure_kpa_abs", to_pressure_kpa_abs, positive=True)
    return {"volume_m3_h": flow * t2 / t1 * p1 / p2,
            "temperature_c": to_temperature_c, "pressure_kpa_abs": p2}


def standard_flow(*, volume_m3_h, temperature_c, pressure_kpa_abs, gas_basis,
                  standard_temperature_c, standard_pressure_kpa_abs,
                  output_gas_basis, water_mole_fraction_wet=None):
    """Convert actual flow to an explicit standard state and dry/wet gas basis."""
    result = state_flow(volume_m3_h=volume_m3_h,
                        from_temperature_c=temperature_c,
                        from_pressure_kpa_abs=pressure_kpa_abs,
                        to_temperature_c=standard_temperature_c,
                        to_pressure_kpa_abs=standard_pressure_kpa_abs)
    flow = _basis_flow(result["volume_m3_h"], gas_basis, output_gas_basis,
                       water_mole_fraction_wet)
    return {"volume_standard_m3_h": flow, "gas_basis": output_gas_basis,
            "standard_temperature_c": standard_temperature_c,
            "standard_pressure_kpa_abs": standard_pressure_kpa_abs}


def mass_to_volume(*, mass_kg_h, molar_mass_kg_per_kmol, temperature_c,
                   pressure_kpa_abs, gas_basis):
    """Mass and molar mass must both describe the supplied wet OR dry gas mixture."""
    mass = _number("mass_kg_h", mass_kg_h, minimum=0)
    mw = _number("molar_mass_kg_per_kmol", molar_mass_kg_per_kmol, positive=True)
    tk = _temperature("temperature_c", temperature_c)
    pressure = _number("pressure_kpa_abs", pressure_kpa_abs, positive=True)
    _basis(gas_basis)
    return {"volume_m3_h": mass / mw * R_KPA_M3_PER_KMOL_K * tk / pressure,
            "temperature_c": temperature_c, "pressure_kpa_abs": pressure,
            "gas_basis": gas_basis}


def nox_ppm_to_mg_standard_m3(*, nox_ppm, standard_temperature_c,
                            standard_pressure_kpa_abs, gas_basis):
    """Convert NOx molar ppm to mg/m3 as NO2 at the stated standard state.

    This conversion preserves dry/wet and oxygen basis; it does not correct them.
    """
    ppm = _number("nox_ppm", nox_ppm, minimum=0)
    tk = _temperature("standard_temperature_c", standard_temperature_c)
    pressure = _number("standard_pressure_kpa_abs", standard_pressure_kpa_abs,
                       positive=True)
    _basis(gas_basis)
    return {"concentration_mg_standard_m3": ppm * pressure * MW_NO2_KG_PER_KMOL /
            (R_KPA_M3_PER_KMOL_K * tk), "gas_basis": gas_basis,
            "standard_temperature_c": standard_temperature_c,
            "standard_pressure_kpa_abs": pressure,
            "nox_mass_basis": "NO2_equivalent"}


def nox_from_concentration(*, concentration_mg_standard_m3,
                           concentration_standard_temperature_c,
                           concentration_standard_pressure_kpa_abs,
                           concentration_gas_basis, volume_standard_m3_h,
                           flow_standard_temperature_c,
                           flow_standard_pressure_kpa_abs, flow_gas_basis,
                           water_mole_fraction_wet=None,
                           measured_o2_dry_percent=None,
                           reference_o2_dry_percent=None,
                           oxidant_o2_dry_percent=None):
    """Recover NOx kg/h after matching standard state, moisture and oxygen basis.

    reference_o2_dry_percent=None means concentration at actual exhaust oxygen.
    An oxygen-referenced concentration must be DRY and requires measured dry O2
    and the explicitly chosen oxidant O2 convention (for example 20.9 or 21).
    C_actual = C_ref * (O2_oxidant-O2_measured)/(O2_oxidant-O2_ref).
    Allowed maximum engine backpressure must not be used as actual flow pressure.
    """
    concentration = _number("concentration_mg_standard_m3",
                             concentration_mg_standard_m3, minimum=0)
    _basis(concentration_gas_basis)
    if reference_o2_dry_percent is not None:
        if concentration_gas_basis != "dry":
            raise ValueError("oxygen-referenced concentration must be supplied on dry gas basis")
        if measured_o2_dry_percent is None or oxidant_o2_dry_percent is None:
            raise ValueError("oxygen correction requires measured and oxidant dry O2 percentages")
        oxidant = _number("oxidant_o2_dry_percent", oxidant_o2_dry_percent,
                          positive=True, maximum=100)
        measured = _number("measured_o2_dry_percent", measured_o2_dry_percent, minimum=0)
        reference = _number("reference_o2_dry_percent", reference_o2_dry_percent, minimum=0)
        if measured >= oxidant or reference >= oxidant:
            raise ValueError("measured and reference O2 must be below oxidant O2")
        concentration *= (oxidant - measured) / (oxidant - reference)
    else:
        if measured_o2_dry_percent is not None:
            _number("measured_o2_dry_percent", measured_o2_dry_percent,
                    minimum=0, maximum=100)
        if oxidant_o2_dry_percent is not None:
            _number("oxidant_o2_dry_percent", oxidant_o2_dry_percent,
                    positive=True, maximum=100)
    flow = standard_flow(
        volume_m3_h=volume_standard_m3_h,
        temperature_c=flow_standard_temperature_c,
        pressure_kpa_abs=flow_standard_pressure_kpa_abs, gas_basis=flow_gas_basis,
        standard_temperature_c=concentration_standard_temperature_c,
        standard_pressure_kpa_abs=concentration_standard_pressure_kpa_abs,
        output_gas_basis=concentration_gas_basis,
        water_mole_fraction_wet=water_mole_fraction_wet)["volume_standard_m3_h"]
    return {"mass_nox_as_no2_kg_h": concentration * flow / 1_000_000,
            "concentration_at_actual_o2_mg_standard_m3": concentration,
            "matched_volume_standard_m3_h": flow,
            "matched_gas_basis": concentration_gas_basis,
            "matched_standard_temperature_c": concentration_standard_temperature_c,
            "matched_standard_pressure_kpa_abs": concentration_standard_pressure_kpa_abs,
            "nox_mass_basis": "NO2_equivalent"}


def nox_from_ef(*, power_kw, emission_factor_g_kwh):
    """Power and EF must represent the same operating point and power definition."""
    power = _number("power_kw", power_kw, minimum=0)
    ef = _number("emission_factor_g_kwh", emission_factor_g_kwh, minimum=0)
    return {"mass_nox_as_no2_kg_h": power * ef / 1000,
            "nox_mass_basis": "NO2_equivalent"}


def def_demand(*, inlet_nox_as_no2_kg_h, removal_fraction, mode, ratio,
               def_urea_mass_fraction, def_density_kg_l,
               stoichiometric_nh3_per_nox=None):
    """Theoretical urea demand, with no catalyst performance or control-setting claim.

    inlet_anr: ratio is NH3/INLET NOx molar ratio; removal is not multiplied in.
    removed_nox_multiple: ratio multiplies REMOVED NOx stoichiometric demand;
    stoichiometric_nh3_per_nox must be supplied for the chosen reaction basis.
    Both modes assume one mole urea yields two moles NH3 quantitatively.
    """
    inlet = _number("inlet_nox_as_no2_kg_h", inlet_nox_as_no2_kg_h, minimum=0)
    removal = _number("removal_fraction", removal_fraction, minimum=0, maximum=1)
    ratio = _number("ratio", ratio, minimum=0)
    fraction = _number("def_urea_mass_fraction", def_urea_mass_fraction,
                       positive=True, maximum=1)
    density = _number("def_density_kg_l", def_density_kg_l, positive=True)
    inlet_kmol_h = inlet / MW_NO2_KG_PER_KMOL
    if mode == "inlet_anr":
        if stoichiometric_nh3_per_nox is not None:
            raise ValueError("inlet_anr is already a molar ratio; do not supply stoichiometric_nh3_per_nox")
        nh3 = inlet_kmol_h * ratio
    elif mode == "removed_nox_multiple":
        stoich = _number("stoichiometric_nh3_per_nox", stoichiometric_nh3_per_nox,
                         positive=True)
        nh3 = inlet_kmol_h * removal * ratio * stoich
    else:
        raise ValueError("mode must be 'inlet_anr' or 'removed_nox_multiple'")
    urea = nh3 / 2 * MW_UREA_KG_PER_KMOL
    solution = urea / fraction
    return {"mode": mode, "removed_nox_as_no2_kg_h": inlet * removal,
            "nh3_equivalent_kmol_h": nh3, "pure_urea_kg_h": urea,
            "def_solution_kg_h": solution, "def_solution_l_h": solution / density,
            "implied_inlet_anr": nh3 / inlet_kmol_h if inlet_kmol_h else None,
            "scope": "theoretical_demand_only"}


def duct_screen(*, actual_flow_m3_h, length_m, cross_section_m2=None,
                inner_diameter_m=None, target_velocity_m_s=None):
    """Use actual hot-gas flow and exactly one supplied internal geometry.

    cross_section_m2 also supports rectangular ducts. Selected diameter/area is
    always used to recompute actual velocity and ideal mean residence time.
    """
    flow = _number("actual_flow_m3_h", actual_flow_m3_h, minimum=0) / 3600
    length = _number("length_m", length_m, minimum=0)
    if (cross_section_m2 is None) == (inner_diameter_m is None):
        raise ValueError("supply exactly one of cross_section_m2 or inner_diameter_m")
    if inner_diameter_m is not None:
        diameter = _number("inner_diameter_m", inner_diameter_m, positive=True)
        area = math.pi * diameter ** 2 / 4
    else:
        area = _number("cross_section_m2", cross_section_m2, positive=True)
    velocity = flow / area
    result = {"cross_section_m2": area, "mean_velocity_m_s": velocity,
              "duct_internal_volume_m3": area * length,
              "ideal_mean_residence_s": length / velocity if velocity else None}
    if target_velocity_m_s is not None:
        target = _number("target_velocity_m_s", target_velocity_m_s, positive=True)
        required_area = flow / target
        result.update({"required_area_at_target_m2": required_area,
                       "equivalent_circular_diameter_at_target_m": math.sqrt(4 * required_area / math.pi)})
    return result


def catalyst_screen(*, volume_standard_m3_h, standard_temperature_c,
                    standard_pressure_kpa_abs, gas_basis,
                    installed_effective_volume_l, purchased_volume_l,
                    empty_reserved_volume_l=0, ghsv_limit_h_inv=None):
    """Volume accounting and GHSV screening against a user-supplied design limit.

    Effective volume is INSTALLED active block geometric bulk volume, including
    channels. Purchased volume includes installed blocks and off-line spares.
    Empty reserved capacity is reported separately and never enters GHSV.
    A supplied GHSV limit is a design constraint, not a conversion guarantee.
    """
    flow = _number("volume_standard_m3_h", volume_standard_m3_h, minimum=0)
    _temperature("standard_temperature_c", standard_temperature_c)
    pressure = _number("standard_pressure_kpa_abs", standard_pressure_kpa_abs,
                       positive=True)
    _basis(gas_basis)
    installed = _number("installed_effective_volume_l", installed_effective_volume_l,
                        positive=True)
    purchased = _number("purchased_volume_l", purchased_volume_l, minimum=0)
    reserved = _number("empty_reserved_volume_l", empty_reserved_volume_l, minimum=0)
    if purchased < installed:
        raise ValueError("purchased_volume_l must include all installed effective volume")
    ghsv = flow / (installed / 1000)
    result = {"installed_effective_volume_l": installed, "purchased_volume_l": purchased,
              "off_line_spare_volume_l": purchased - installed,
              "empty_reserved_volume_l": reserved, "ghsv_h_inv": ghsv,
              "gas_basis": gas_basis, "standard_temperature_c": standard_temperature_c,
              "standard_pressure_kpa_abs": pressure}
    if ghsv_limit_h_inv is not None:
        limit = _number("ghsv_limit_h_inv", ghsv_limit_h_inv, positive=True)
        result.update({"required_effective_volume_l": flow / limit * 1000,
                       "within_supplied_ghsv_limit": ghsv <= limit})
    return result


OPERATIONS = {function.__name__: function for function in (
    absolute_pressure, state_flow, standard_flow, mass_to_volume,
    nox_ppm_to_mg_standard_m3, nox_from_concentration, nox_from_ef,
    def_demand, duct_screen, catalyst_screen)}


def run_request(request):
    """Evaluate a single or batch JSON request using an explicit operation allowlist."""
    if not isinstance(request, dict):
        raise ValueError("request must be a JSON object")
    if "calculations" in request:
        if set(request) != {"calculations"}:
            raise ValueError("batch request must contain only calculations")
        calculations = request["calculations"]
        if not isinstance(calculations, list) or not calculations:
            raise ValueError("calculations must be a nonempty list")
    else:
        calculations = [request]
    results = []
    for calculation in calculations:
        if not isinstance(calculation, dict) or set(calculation) - {"id", "operation", "inputs"}:
            raise ValueError("each calculation permits only id, operation and inputs")
        operation = calculation.get("operation")
        if not isinstance(operation, str) or operation not in OPERATIONS:
            raise ValueError(f"unsupported operation: {operation!r}")
        inputs = calculation.get("inputs")
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be a JSON object")
        item = {"operation": operation, "result": OPERATIONS[operation](**inputs)}
        if "id" in calculation:
            if not isinstance(calculation["id"], str):
                raise ValueError("calculation id must be a string")
            item["id"] = calculation["id"]
        results.append(item)
    return {"scope": "deterministic_engineering_screening", "results": results,
            "pending_checks": list(PENDING_CHECKS)}


def _reject_nonfinite_json(value):
    raise ValueError(f"non-finite JSON number is not allowed: {value}")


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON input path, or '-' for stdin")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8-sig")
        request = json.loads(raw, parse_constant=_reject_nonfinite_json,
                             object_pairs_hook=_unique_json_object)
        result = run_request(request)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, OverflowError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
