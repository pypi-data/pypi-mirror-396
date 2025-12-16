import re
import xarray as xr
import pandas as pd
from typing import Mapping, Tuple, Optional, Any, Callable
from pint import UnitRegistry
from guts_base.sim.utils import GutsBaseError
from pymob.sim.config import Config
from typing import Dict
from pymob.sim.config import Modelparameters


ureg = UnitRegistry()
ureg.define("ai = 1 = AI")





ASSUMPTIONS = 0
pattern = re.compile(r'\{(?P<content>[^\}]+)\}')

def parse_units(
    model_parameters: Modelparameters,
    units: Dict[str,xr.DataArray|str],
):


    units_explicit = {}
    for key, param in model_parameters.all.items():

        problem_dims = _get_dimensionality_of_the_problem(units, param)

        # if the dimension is not existing, having a list makes no sense
        if len(problem_dims) > 0:
            # forcefully extract only the first element of the list, even
            # if it has more than one element
            # for placeholder, dims in problem_dims.items():
                # for dim in dims:
                    
                    # for i, coord in enumerate(units[placeholder].coords[dim]):
            for dim, coords in problem_dims.items():
                units_explicit_param = {}
                if param.unit is None:
                    _unit = ""
                elif isinstance(param.unit, str):
                    _units = [param.unit] * len(coords)
                else:
                    _units = param.unit

                for i, coord in enumerate(coords):
                    _unit = _units[i]
                    
                    inject_into_template = {}
                    open_placeholders = [p for p in pattern.findall(_unit)]
                    for _placeholder in open_placeholders:
                        if "_i" in _placeholder:
                            placeholder = _placeholder.strip("_i")
                            idx = i
                        else:
                            placeholder = _placeholder
                            idx = ASSUMPTIONS

                        value = _get_placeholder_from_units_dict(
                            placeholder=placeholder, units=units, index=idx
                        )
                        inject_into_template.update({_placeholder: f"({value})"})

                    explicit_unit = _unit.format(**inject_into_template)
                    print(f"{key}[{coord}]: {explicit_unit}")

                    units_explicit_param.update({coord: explicit_unit})
            units_explicit.update({key: units_explicit_param})


        else:
            if param.unit is None:
                _unit = ""
            elif isinstance(param.unit, str):
                _unit = param.unit
            else:
                _unit = param.unit[0]

            open_placeholders = [p for p in pattern.findall(_unit)]

            inject_into_template = {}
            for placeholder in open_placeholders:
                value = _get_placeholder_from_units_dict(
                    placeholder=placeholder, units=units, index=ASSUMPTIONS
                )
                inject_into_template.update({placeholder: f"({value})"})

            explicit_unit = _unit.format(**inject_into_template)

            print(f"{key}: {explicit_unit}")
            
            units_explicit.update({key: explicit_unit})

    return units_explicit



def _get_dimensionality_of_the_problem(units, param):
    if param.unit is None:
        open_placeholders = []
    else:
        open_placeholders = [p for p in pattern.findall(param.unit)]

    dimensionality = {}
    for _placeholder in open_placeholders:
        placeholder = _placeholder.strip("_i")
        _u = units[placeholder]

        if isinstance(_u, xr.DataArray):
            matching_dims = [d for d in _u.dims if d in param.dims]
            dims = {d: _u.coords[d].values for d in matching_dims}

        elif isinstance(_u, str):
            dims = {}

        else:
            raise NotImplementedError
        
        dimensionality.update(dims)
    return dimensionality



def _get_placeholder_from_units_dict(placeholder, units, index):
    _u = units.get(placeholder, None)
    if isinstance(_u, xr.DataArray):
        value = _get_placeholder_value(_u, placeholder, index)
        return value

    elif isinstance(_u, str):
        return _u

    elif _u is None:
        return f"{{{placeholder}}}"



def _get_placeholder_value(_u, placeholder, index=0):
    if len(_u.dims) == 1:
        dim = _u.dims[0]
    else:
        raise GutsBaseError(
            "Currently only 1 dimensional units are supported"
        )
    replaced = False
    if not replaced:
        try:
            # if the replacement is a string, assume that it is a coordinate and
            # should be used. This is of course more explicit, but not good 
            # when using default settings.
            v = str(_u.sel({dim:placeholder}).values)
            replaced = True
        except KeyError:
            pass

    if not replaced:
        try:
            # The placeholder is replaced with the
            # i-th value in the unit dataarray
            v = str(_u[index].values)
            replaced = True
        except IndexError:
            pass

    if not replaced:
        v = f"{{{placeholder}}}"

    return v



def _walk_nested_dict(dct, func):
    """Expects a function that takes key and value as arguments to process the """
    result = {}
    for key, value in dct.items():
        if not isinstance(value, dict):
            _dct = func(key, value)
            result.update(_dct)
        else:
            dct_l1 = {}
            for coord, val in value.items():
                _subdct = func(coord, val)
                dct_l1.update(_subdct)
            result.update({key: dct_l1})
    return result


def derive_explicit_units(config: Config, unit: xr.DataArray, parsing_func: Optional[Callable] = None) -> xr.Dataset:
    # here we have the base units
    T = config.guts_base.unit_time
    fmt_unit = config.guts_base.unit_format_pint
    units_dict = unit.to_pandas().to_dict()



    parsed_units = parse_units(
        model_parameters=config.model_parameters,
        units={"X": unit, "T": T, **units_dict}, # type: ignore
    )

    if parsing_func is None:
        def parse_func(key, value) -> Dict[str, Any]:
            upint = ureg.parse_expression(value)
            assert upint.magnitude == 1.0
            upint = format(upint.u, fmt_unit)
            return {key: upint}
    else:
        parse_func = parsing_func

    pint_parsed_units = _walk_nested_dict(parsed_units, parse_func)

    exposure_dim = [
        k for k in config.data_structure.exposure.dimensions
        if k not in [config.simulation.batch_dimension, config.simulation.x_dimension]
    ]

    if len(exposure_dim) > 1:
        raise NotImplementedError(
            "More than three exposure dimensions are currently not implemented."
        )
    elif len(exposure_dim) == 0:
        raise NotImplementedError(
            "Exposure should have one extra dimension, even if only one coordinate is present"
        )
    else:
        exposure_dim = exposure_dim[0]
    
    units = xr.Dataset({
        "metric": ["unit"],
        exposure_dim: list(units_dict.keys()),
        ** {
            key: ("metric", [val]) if isinstance(val, str)
            else xr.Dataset(val).to_array(exposure_dim, name=key).expand_dims({"metric": ["unit"]}) 
            for key, val in pint_parsed_units.items()
        }
    })
    return units


def _get_unit_from_dataframe_index(df: pd.DataFrame) -> str:
    """Searches the index name in a DataFrame for square parentheses `[...].`
    Extracts the content inside the parentheses
    """
    pattern = re.compile(r'\[(?P<content>[^\]]+)\]')
    match = pattern.search(str(df.index.name))
    if match:
        time_unit = match.group('content')
    else:
        time_unit = ""

    return time_unit


def _convert_units(
    units: xr.DataArray, 
    target_units: Mapping[str,str] = {"default": "{x}->{x}"}
) -> Tuple[xr.DataArray, xr.DataArray]:
    """Converts units of values associated with the exposure dimension
    TODO: Converting before inference could be problem for the calibration, because
    it is usually good if the values are both not too small and not too large 
    """

    if len(units.dims) != 1:
        raise GutsBaseError(
            "GutsBase_convert_exposure_units only supports 1 dimensional exposure units"
        )
    
    _dim = units.dims[0]
    _coordinates = units.coords[_dim]

    converted_units = {}
    _target_units = {}

    for coord in _coordinates.values:
        unit = str(units.sel({_dim: coord}).values)
        
        # get item from config
        # split transformation expression from target expression
        transform, target = target_units.get(coord, target_units["default"]).split("->")
        # insert unit from observations coordinates
        transform = transform.strip(" ").format(x=unit)
        target = target.strip(" ").format(x=unit)

        # parse and convert units
        new_unit = ureg.parse_expression(transform).to(target)
        converted_units.update({coord: new_unit})
        _target_units.update({coord: target})
        
    _units = {k: f"{cu.units:C}" for k, cu in converted_units.items()}

    # assert whether the converted units are the same as the target units
    # so the target units can be used, because the converted units may reduce
    # to dimensionless quantities.
    if not all([
        cu.units == ureg.parse_expression(tu) 
        for cu, tu in zip(converted_units.values(), _target_units.values())
    ]):
        raise GutsBaseError(
            f"Mismatch between target units {_target_units} and converted units " +
            f"{converted_units}."
        )

    _conversion_factors = {k: cu.magnitude for k, cu in converted_units.items()}
    new_unit_coords = xr.Dataset(_target_units).to_array(dim=_dim)
    conversion_factor_coords = xr.Dataset(_conversion_factors).to_array(dim=_dim)



    return new_unit_coords, conversion_factor_coords
