"""Synthetic regression tests for engineering bases, conservation and boundaries."""

import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scr-design-assistant" / "scripts" / "scr_calc.py"
SPEC = importlib.util.spec_from_file_location("scr_calc", SCRIPT)
calc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calc)


class FlowTests(unittest.TestCase):
    def test_state_conversion_round_trip_and_absolute_pressure(self):
        pressure = calc.absolute_pressure(gauge_pressure_kpa=4,
                                          ambient_pressure_kpa_abs=96)["pressure_kpa_abs"]
        self.assertEqual(pressure, 100)
        converted = calc.state_flow(volume_m3_h=1000, from_temperature_c=20,
                                    from_pressure_kpa_abs=100, to_temperature_c=313.15,
                                    to_pressure_kpa_abs=200)["volume_m3_h"]
        self.assertAlmostEqual(converted, 1000)
        restored = calc.state_flow(volume_m3_h=converted, from_temperature_c=313.15,
                                   from_pressure_kpa_abs=200, to_temperature_c=20,
                                   to_pressure_kpa_abs=100)["volume_m3_h"]
        self.assertAlmostEqual(restored, 1000)

    def test_wet_dry_flow_and_inverse(self):
        common = dict(temperature_c=0, pressure_kpa_abs=100,
                      standard_temperature_c=0, standard_pressure_kpa_abs=100,
                      water_mole_fraction_wet=0.2)
        dry = calc.standard_flow(volume_m3_h=1000, gas_basis="wet",
                                 output_gas_basis="dry", **common)["volume_standard_m3_h"]
        wet = calc.standard_flow(volume_m3_h=dry, gas_basis="dry",
                                 output_gas_basis="wet", **common)["volume_standard_m3_h"]
        self.assertAlmostEqual(dry, 800)
        self.assertAlmostEqual(wet, 1000)

    def test_mass_volume_uses_the_supplied_state(self):
        result = calc.mass_to_volume(mass_kg_h=28, molar_mass_kg_per_kmol=28,
                                     temperature_c=0, pressure_kpa_abs=100, gas_basis="dry")
        self.assertAlmostEqual(result["volume_m3_h"], 22.71095464149, places=9)

    def test_invalid_state_and_missing_humidity_are_rejected(self):
        for pressure, temperature in [(0, 0), (-5, 0), (100, -273.15)]:
            with self.subTest(pressure=pressure, temperature=temperature), self.assertRaises(ValueError):
                calc.state_flow(volume_m3_h=1, from_temperature_c=temperature,
                                from_pressure_kpa_abs=pressure,
                                to_temperature_c=0, to_pressure_kpa_abs=100)
        with self.assertRaises(ValueError):
            calc.standard_flow(volume_m3_h=1, temperature_c=0, pressure_kpa_abs=100,
                               gas_basis="wet", output_gas_basis="dry",
                               standard_temperature_c=0, standard_pressure_kpa_abs=100)


class NoxTests(unittest.TestCase):
    def arguments(self):
        return dict(concentration_mg_standard_m3=100,
                    concentration_standard_temperature_c=0,
                    concentration_standard_pressure_kpa_abs=100,
                    concentration_gas_basis="dry", volume_standard_m3_h=10000,
                    flow_standard_temperature_c=0, flow_standard_pressure_kpa_abs=100,
                    flow_gas_basis="dry")

    def test_concentration_and_ef_independent_routes_agree(self):
        concentration_route = calc.nox_from_concentration(**self.arguments())
        ef_route = calc.nox_from_ef(power_kw=500, emission_factor_g_kwh=2)
        self.assertAlmostEqual(concentration_route["mass_nox_as_no2_kg_h"], 1)
        self.assertAlmostEqual(ef_route["mass_nox_as_no2_kg_h"], 1)

    def test_standard_state_and_moisture_are_matched(self):
        # Same gas amount: wet volume is twice as large at twice the absolute T;
        # converting wet->dry then retains 80% of that amount.
        args = self.arguments()
        args.update(volume_standard_m3_h=25000, flow_standard_temperature_c=273.15,
                    flow_gas_basis="wet", water_mole_fraction_wet=0.2)
        self.assertAlmostEqual(calc.nox_from_concentration(**args)["mass_nox_as_no2_kg_h"], 1)

    def test_raw_wet_and_raw_dry_routes_conserve_nox_mass(self):
        dry = self.arguments()
        dry.update(volume_standard_m3_h=12500, flow_gas_basis="wet",
                   water_mole_fraction_wet=0.2)
        wet = dict(dry, concentration_gas_basis="wet", concentration_mg_standard_m3=80)
        self.assertAlmostEqual(calc.nox_from_concentration(**dry)["mass_nox_as_no2_kg_h"],
                               calc.nox_from_concentration(**wet)["mass_nox_as_no2_kg_h"])

    def test_oxygen_reference_is_restored_before_mass_calculation(self):
        args = self.arguments()
        args.update(concentration_mg_standard_m3=200,
                    measured_o2_dry_percent=13, reference_o2_dry_percent=5,
                    oxidant_o2_dry_percent=21)
        result = calc.nox_from_concentration(**args)
        self.assertAlmostEqual(result["concentration_at_actual_o2_mg_standard_m3"], 100)
        self.assertAlmostEqual(result["mass_nox_as_no2_kg_h"], 1)

    def test_oxygen_conventions_must_be_explicit_and_valid(self):
        for updates in [dict(reference_o2_dry_percent=5),
                        dict(reference_o2_dry_percent=5, measured_o2_dry_percent=21,
                             oxidant_o2_dry_percent=21),
                        dict(reference_o2_dry_percent=5, measured_o2_dry_percent=10,
                             oxidant_o2_dry_percent=21, concentration_gas_basis="wet")]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                calc.nox_from_concentration(**dict(self.arguments(), **updates))

    def test_ppm_conversion_has_explicit_state_and_no2_mass_basis(self):
        result = calc.nox_ppm_to_mg_standard_m3(nox_ppm=1,
                    standard_temperature_c=0, standard_pressure_kpa_abs=100, gas_basis="dry")
        self.assertAlmostEqual(result["concentration_mg_standard_m3"], 2.0256964415, places=8)
        self.assertEqual(result["nox_mass_basis"], "NO2_equivalent")

    def test_zero_is_preserved_and_nonfinite_or_boolean_inputs_are_rejected(self):
        self.assertEqual(calc.nox_from_ef(power_kw=0, emission_factor_g_kwh=5)["mass_nox_as_no2_kg_h"], 0)
        for invalid in [math.nan, math.inf, True, "10", -1]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                calc.nox_from_ef(power_kw=invalid, emission_factor_g_kwh=1)


class DosingAndGeometryTests(unittest.TestCase):
    def dosing_arguments(self):
        return dict(inlet_nox_as_no2_kg_h=calc.MW_NO2_KG_PER_KMOL,
                    removal_fraction=0.8, ratio=1,
                    def_urea_mass_fraction=0.5, def_density_kg_l=1.2)

    def test_inlet_anr_does_not_silently_multiply_removal(self):
        result = calc.def_demand(mode="inlet_anr", **self.dosing_arguments())
        self.assertAlmostEqual(result["nh3_equivalent_kmol_h"], 1)
        self.assertAlmostEqual(result["pure_urea_kg_h"], 30.02765)
        self.assertAlmostEqual(result["def_solution_l_h"], 50.0460833333333)
        self.assertAlmostEqual(result["implied_inlet_anr"], 1)

    def test_removed_multiple_and_inlet_anr_have_defined_equivalence(self):
        removed = calc.def_demand(mode="removed_nox_multiple",
                    stoichiometric_nh3_per_nox=1, **self.dosing_arguments())
        inlet = calc.def_demand(mode="inlet_anr", **dict(self.dosing_arguments(), ratio=0.8))
        self.assertAlmostEqual(removed["def_solution_l_h"], inlet["def_solution_l_h"])
        self.assertAlmostEqual(removed["implied_inlet_anr"], 0.8)

    def test_dose_requires_solution_and_reaction_inputs(self):
        for updates in [dict(def_urea_mass_fraction=0), dict(def_density_kg_l=0),
                        dict(removal_fraction=1.1), dict(def_urea_mass_fraction=1.1)]:
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                calc.def_demand(mode="inlet_anr", **dict(self.dosing_arguments(), **updates))
        with self.assertRaises(ValueError):
            calc.def_demand(mode="removed_nox_multiple", **self.dosing_arguments())

    def test_selected_area_recomputes_velocity_and_residence(self):
        result = calc.duct_screen(actual_flow_m3_h=3600, cross_section_m2=0.5,
                                  length_m=4, target_velocity_m_s=4)
        self.assertAlmostEqual(result["mean_velocity_m_s"], 2)
        self.assertAlmostEqual(result["ideal_mean_residence_s"], 2)
        self.assertAlmostEqual(result["required_area_at_target_m2"], 0.25)
        circular = calc.duct_screen(actual_flow_m3_h=3600,
                     inner_diameter_m=math.sqrt(2 / math.pi), length_m=4)
        self.assertAlmostEqual(circular["mean_velocity_m_s"], 2)

    def test_zero_flow_has_no_finite_residence_prediction(self):
        self.assertIsNone(calc.duct_screen(actual_flow_m3_h=0,
                           cross_section_m2=1, length_m=2)["ideal_mean_residence_s"])

    def test_spares_and_unfilled_capacity_never_reduce_operating_ghsv(self):
        common = dict(volume_standard_m3_h=10000, standard_temperature_c=0,
                      standard_pressure_kpa_abs=100, gas_basis="dry",
                      installed_effective_volume_l=500, ghsv_limit_h_inv=12500)
        result = calc.catalyst_screen(purchased_volume_l=700,
                                      empty_reserved_volume_l=300, **common)
        self.assertEqual(result["ghsv_h_inv"], 20000)
        self.assertEqual(result["required_effective_volume_l"], 800)
        self.assertEqual(result["off_line_spare_volume_l"], 200)
        self.assertFalse(result["within_supplied_ghsv_limit"])
        no_spare = calc.catalyst_screen(purchased_volume_l=500, **common)
        self.assertEqual(result["ghsv_h_inv"], no_spare["ghsv_h_inv"])
        with self.assertRaises(ValueError):
            calc.catalyst_screen(purchased_volume_l=100, **common)


class CliTests(unittest.TestCase):
    def test_json_batch_and_pending_checks(self):
        request = {"calculations": [{"id": "synthetic", "operation": "nox_from_ef",
                    "inputs": {"power_kw": 500, "emission_factor_g_kwh": 2}}]}
        process = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                                 input=json.dumps(request), capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        output = json.loads(process.stdout)
        self.assertEqual(output["results"][0]["result"]["mass_nox_as_no2_kg_h"], 1)
        self.assertEqual(output["results"][0]["id"], "synthetic")
        self.assertTrue(output["pending_checks"])

    def test_cli_rejects_nonfinite_json_and_unknown_operation(self):
        for request in ['{"operation":"nox_from_ef","inputs":{"power_kw":NaN,"emission_factor_g_kwh":1}}',
                        '{"operation":"nox_from_ef","inputs":{"power_kw":1,"power_kw":2,"emission_factor_g_kwh":1}}',
                        '{"operation":"eval","inputs":{}}']:
            with self.subTest(request=request):
                process = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                                         input=request, capture_output=True, text=True)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertIn("error", json.loads(process.stderr))


if __name__ == "__main__":
    unittest.main()
