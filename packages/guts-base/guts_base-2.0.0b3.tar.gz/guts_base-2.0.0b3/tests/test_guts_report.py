import pytest
from guts_base import GutsBase
from guts_base.sim.report import GutsReport
from guts_base.sim import units
from guts_base.mod import RED_SD, RED_IT, RED_SD_DA, RED_SD_explicit_units
from pymob.inference.numpyro_backend import NumpyroBackend
import numpy as np

@pytest.fixture
def report(sim_from_model_and_dataset: GutsBase):
    yield GutsReport(
        sim_from_model_and_dataset.config, 
        backend=NumpyroBackend,
        observations=sim_from_model_and_dataset.observations,
        idata=sim_from_model_and_dataset.inferer.idata,
    )



exposure_units = [
    {
        # use default units (X: dimensionless, T: day)
        RED_SD: (None, {"b": "1/{T}", "hb": "1/{T}", "kd": "1/{T}", "m": ""}),
        # for RED IT no units are defined, therefore the units are not declared
        RED_IT: (None, {"beta": "", "hb": "", "kd": "", "m": "", "eps": ""}),
        RED_SD_DA: (None, {"b": "1/{T}", "hb": "1/{T}", "kd": "1/{T}", "m": "", "w": ["", ""]}),
        RED_SD_explicit_units: (None, {"b": "1/d/mg", "hb": "1/d", "kd": "1/d", "m": "mg"})
    },
    {
        RED_SD: (['ng/milliliter'],  {"b": "ml/{T}/ng", "hb": "1/{T}", "kd": "1/{T}", "m": "ng/ml"}),
        RED_IT: (['g'], {"beta": "", "hb": "", "kd": "", "m": "", "eps": ""}),
        RED_SD_DA: (['ug/dl', 'ng/l'], {"b": "dl/{T}/µg", "hb": "1/{T}", "kd": "1/{T}", "m": "µg/dl", "w": ["", "l·µg/dl/ng"]}),
        RED_SD_explicit_units: (['ng/milliliter'], {"b": "1/d/mg", "hb": "1/d", "kd": "1/d", "m": "mg"})
    },
    {
        RED_SD: (['kg'],  {"b": "1/kg/{T}", "hb": "1/{T}", "kd": "1/{T}", "m": "kg"}),
        RED_IT: (['g'], {"beta": "", "hb": "", "kd": "", "m": "", "eps": ""}),
        # test simplification in weights 
        RED_SD_DA: (['ug/ml', 'ng/ml'], {"b": "ml/µg/{T}", "hb": "1/{T}", "kd": "1/{T}", "m": "µg/ml", "w": ["", "µg/ng"]}),
        RED_SD_explicit_units: (['kg'], {"b": "1/d/mg", "hb": "1/d", "kd": "1/d", "m": "mg"})
    },
]

time_unit = ["day", "hour", "second"]

combis = list(zip(exposure_units, time_unit))


@pytest.mark.parametrize("exposure_units,time_unit", combis)
def test_unit(sim_from_model_and_dataset: GutsBase, exposure_units, time_unit):
    _units = sim_from_model_and_dataset.observations.unit.copy(deep=True)
    _exposure_units = exposure_units[sim_from_model_and_dataset._model_class]
    sim_from_model_and_dataset.config.guts_base.unit_time = time_unit

    if _exposure_units[0] is None:
        pass
    else:
        _units.values = _exposure_units[0]

    parsed_units = units.derive_explicit_units(
        config=sim_from_model_and_dataset.config,
        unit=_units,
    )

    _tu = format(
        units.ureg.parse_expression(time_unit).u, 
        sim_from_model_and_dataset.config.guts_base.unit_format_pint
    )

    for key, var in parsed_units.data_vars.items():
        expected = _exposure_units[1][key]
        if isinstance(expected, list):
            expected = [e.format(T=_tu) for e in expected]
        else:
            expected = [expected.format(T=_tu)]

        result = var.sel(metric="unit")
        np.testing.assert_array_equal(result, expected)