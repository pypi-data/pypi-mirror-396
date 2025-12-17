from functools import partial
import numpy as np
from pydantic import BeforeValidator, ConfigDict, PlainSerializer
from typing import Literal, Optional, List, Dict, Tuple, Annotated, Mapping
from pymob.sim.config import (
    PymobModel, 
    string_to_list, 
    serialize_list_to_string, 
    nested_dict_to_string, 
    to_nested_dict, 
    string_to_dict, 
    serialize_dict_to_string,
    OptionListStr,
)
from pymob.sim.config.casestudy_registry import register_case_study_config

OptionListMix = Annotated[
    Optional[Tuple[float,float,int]], 
    BeforeValidator(string_to_list), 
    serialize_list_to_string
]

OptionListFloat = Annotated[
    List[float], 
    BeforeValidator(string_to_list), 
    serialize_list_to_string
]

class ExposureDict(PymobModel):
    start: float = 0.0
    end: Optional[float] = None


serialize_datavar_to_string = PlainSerializer(
    partial(nested_dict_to_string, dict_model=ExposureDict), 
    return_type=str, 
    when_used="json"
)

NestedDict = Annotated[
    Dict[str,Dict[str,float|None]], 
    BeforeValidator(partial(to_nested_dict, dict_model=ExposureDict)), 
    serialize_datavar_to_string
]


DictStr = Annotated[
    Mapping[str, str], 
    BeforeValidator(partial(string_to_dict, split_str=" ", sep_str="=")), 
    serialize_dict_to_string
]


AllowedTimeUnits = Literal["day", "hour", "minute", "second",]

class GutsBaseConfig(PymobModel):
    # extra arguments can be passed to the settings file, but they won't be validated
    model_config = ConfigDict(validate_assignment=True, extra="allow", validate_default=True)

    # The default time unit of the simulation. Defaults to day. 
    # If available, the time unit in the observations will be used. It can be 
    # specified with standard day formats in square brackets in the survival and
    # exposure sheets. E.g. "time [d]" or "time [hours]". Note that the unit
    # must be the same in all sheets that are used for the simulation. 
    # Currently this only affects the reported parameter units.
    unit_time: AllowedTimeUnits = "day"
    
    # the input unit of the simulation, by default no unit is given
    # It is however, highly recommended to priovide a unit for each exposure path/substance
    # this would be done by specifiying, e.g. unit_input={"A": "mg", "B": "ng/kg"}
    # if the openguts file consists of two exposure sheets (A and B)
    # In future versions, the unit of exposure might be read directly from the metadata,
    # at the moment it must be provided explicitly
    unit_input: DictStr = {"default": ""}

    # if the units should be converted to a target this will be specified here.
    # The syntax is input->output and {x} is a placeholder for the input unit. 
    # This means, if the unit input of exposure is 'mg', then '{x}->{x}' applies no 
    # transformation. The target unit will also be 'mg'. 
    # To change the target unit, you could apply '{x}->mg'. Provided {x} is a mass quantity,
    # the conversion will work. If however {x} is a concentration (mg/ml), then a more
    # elaborate transformation is necessary: {x}/(1.12g/ml)->mg/mg
    # this will successfully bring the output unit to a mass concentration.
    # Generally, the string accepts any arithmetic operations that can be handled with pint
    # https://pint.readthedocs.io/en/stable/getting/tutorial.html
    # TODO: Write a validation method for the string. I could use pint for this already
    # TODO: Currently not implemented
    unit_target: DictStr = {"default": "{x}->{x}"}

    # If the dataset provided to GutsBase contains additional DataArrays with substance
    # names, that should be used for exposure AND an exposure DataArray does not exist. 
    # Use this instead. A copy of that data array <substance> will be placed in 
    # observations["exposure"]. By default GutsBase assumes that the exposure data is 
    # contained in observations["exposure"]
    substance: Optional[str] = None

    # start, end and the number fo timepoints to interpolate the results for plotting
    # this will be inserted into numpy.linspace
    results_interpolation: OptionListMix = (np.nan, np.nan, 100)
    
    # whether GutsBase should make sure that the exposure profiles are forward 
    # interpolated. This means, if a rectangular profile is not explicitly given,
    # by providing the same exposure (time, value) combination at the moment before the 
    # next recorded change in the exposure profile, the default behavior is to interpolate
    # linearly over the profile. E.g. a profile like (time=0,value=10), (time=2,value=0)
    # would implicitly yield the points, e.g.: (time=1,value=5), (time=1.99, value=~0). 
    # If forward_interpolate_exposure_data = True, then the interpolated point would be
    # (time=1,value=10), (time=1.99,value=10)
    forward_interpolate_exposure_data: bool = False

    # if the IT model is used, the x-dim (time) resolution needs to be increased 
    # (reindexed), because the solution requires numeric integration of the hazard 
    # function in each solve. The default is to increase the temporal resolution to 
    # 100 datapoints. If the simulated time period is very long, 100 points may not be
    # enough to capture the dynamics of the hazard function
    n_reindexed_x: int = 100

    # this is if case_study.observations is an .xlsx file. In this case you are allowed
    # to pass a preprocessing script by the full module path. e.g. 
    # 'guts_base.data.preprocessing.ringtest' where the last element is the function
    # name in a regular python file. The function must have the arguments path and new_path
    # because it will read the file and save a processed file. 
    # create_database_and_import_data_main will try to import this function with 
    # import_module and execute the preprocessing
    # The default behavior is not to pass a string and preprocess the file
    data_preprocessing: Optional[str] = None

    # private option (should only in case of errors be modified by the user)
    # this will skip the data_processing section of GutsBase.initialize
    # >>> if not _skip_data_processing: self.process_data()
    # This option is set to true when simulations are exported with .nc files,
    # which already are processed and do not need (and can't be) processed again
    skip_data_processing: bool = False

    # this parameter is not for user interaction. It is simply set when parsing the model
    background_mortality_parameters: OptionListStr = []

    # GUTS-REPORT Settings
    # ====================

    # Guts base uses pint to parse units. To see which other options are available to 
    # format the resulting strings see:
    # https://pint.readthedocs.io/en/stable/user/formatting.html
    unit_format_pint: str = "~P"

    # Define the exposure scenarios that should be used for ecx computations
    ecx_exposure_scenarios: NestedDict = {
        "acute_1day": {"start": 0.0, "end": 1.0},
        "chronic": {"start": 0.0, "end": None},
    }

    # whether to assess the uncertainty of the ECx estimate (draws) or not (mean)
    ecx_mode: Literal["mean", "draws"] = "mean"
    
    # number of draws from the posterior for assessing the uncertainty of the estimate
    ecx_draws: int = 250

    # if the number of draws is below 100, an error is raised. If ecx_force_draws,
    # this error is supressed
    ecx_force_draws: bool = False
    
    # times after being of the exposure to estimate the ECx for
    ecx_estimates_times: OptionListFloat = [1.0, 2.0]
    
    # effect levels to estimate the ecx for
    ecx_estimates_x: OptionListFloat = [0.1, 0.5]
    
    # whether the background mortality should be set to zero when estimating the ECx
    ecx_set_background_mortality_to_zero: bool = True

    # whether the posterior should be summarized with the mean or the median of the 
    # distribution. Median is more robust
    table_parameter_stat_focus: Literal["mean", "median"] = "median"


register_case_study_config("guts_base", model_cls=GutsBaseConfig)