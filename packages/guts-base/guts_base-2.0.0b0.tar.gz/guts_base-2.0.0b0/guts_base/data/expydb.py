from typing import List, Optional, Literal
import numpy as np
import xarray as xr
import pandas as pd
import arviz as az
import datetime

import pandas as pd
import numpy as np

from expyDB.intervention_model import (
    Experiment,
    Treatment, 
    Timeseries,
    TsData,
    from_expydb
)

from guts_base.sim.config import AllowedTimeUnits

def prepare_dataset(
    idata, 
    variable="survival", 
    unit_time: AllowedTimeUnits = "day"
):
    """Get interventions from idata storage with respect ot the treatment 
    ids of the observations and move non indexing-related metadata (unique metadata)
    to the attrs container.
    """
    # this test is guaranteed when prepare dataset is used together with from_expydb
    # because from_expydb organizes the data into datasets with 1 variable,
    # which is the timeseries variable with the coordinates timeseries_id and time
    # for treatments and replicates. Other variables receive their 'own' dataset
    assert len(idata[variable].data_vars) == 1
    array: xr.DataArray = idata[variable][variable]
    array = array.swap_dims(timeseries_id="treatment_id")
    array = array.drop_vars("id")
    # assuming that each timeseries of one variable in each treatment has 
    # a unique name the resulting index should be unique
    array = array.set_index(id=("treatment_id", "timeseries_name"))
    array = array.drop_vars("timeseries_id")
    assert array.indexes["id"].is_unique

    # format time to h and set as float
    time_h = array.time.values / pd.Timedelta(1, unit_time)
    array = array.assign_coords(time=time_h)

    array = move_unique_coordinates_to_attrs(array)

    array.attrs["unit_time"] = unit_time

    # add a unique id for the selected dataset which is only relevant for
    # the scope of modelling
    return array

def move_unique_coordinates_to_attrs(array:xr.DataArray) -> xr.DataArray:
    key: str
    for key, coord in array.coords.items(): # type:ignore
        if key in ["id", "treatment_id", "timeseries_id", "experiment_id", "subject_count", "timeseries_name"]:
            continue
        
        if coord.isnull().all():
            unique_values = [None]
        else:
            unique_values = np.unique(coord.data)

        if len(unique_values) == 1:
            array.attrs.update({key: unique_values[0]})
            array = array.drop_vars(key)
    return array

# def prepare_interventions_dataset(interventions_idata, observations, ivs:Optional[List[str]]=None):
#     """Get interventions from idata storage with respect ot the treatment 
#     ids of the observations"""
#     if ivs is None:
#         ivs = list(interventions_idata.keys())
#     ds_ivs = get_interventions(
#         interventions_idata,
#         observations=observations,
#         ivs=ivs
#     )

#     time_h = ds_ivs.time.values / np.timedelta64(1, "h")
#     ds_ivs = ds_ivs.assign_coords(time=time_h)
#     ds_ivs.attrs["unit_time"] = "hours (h)"

#     return ds_ivs

def to_dataset(
    observations_idata, 
    interventions_idata,
    unit_time: Literal["day", "hour", "minute", "second"] = "hour"
) -> xr.Dataset:
    """Combines intervention and observation datasets, assuming that there is 
    a unique multiindex that can be constructed from 
      - treatment_id
      - timeseries_name

    This way interventions and observations can be combined into a single dataset,
    """
    data_arrays = {}
    for variable in observations_idata.groups():
        # prepare observations
        da = prepare_dataset(
            idata=observations_idata,
            variable=variable,
            unit_time=unit_time,
        )
        data_arrays.update({variable: da})

    # prepare interventions
    for variable in interventions_idata.groups():
        da = prepare_dataset(
            idata=interventions_idata,
            variable=variable,
            unit_time=unit_time,
        )
        data_arrays.update({variable: da})

    return xr.combine_by_coords(data_arrays.values())  # type: ignore


def reduce_multiindex_to_flat_index(dataset):
    multi_index = dataset.id.indexes["id"]
    
    # create a flat index from the multi index
    flat_index = multi_index.map(lambda x: "__".join([str(x_) for x_ in x]))
    
    # remove multi index from dimension 'id'
    dataset = dataset.reset_index("id")
    
    # assign flat index to dimension 'id'
    dataset = dataset.assign_coords(id=flat_index)

    return dataset    

def combine_coords_to_multiindex(
        dataset: xr.Dataset, 
        coordinates: List[str], 
        index_name: str, 
        sep: str = "__"
    ) -> xr.Dataset:
    """Simply combines a list of coordinates into a joint string

    Parameters
    ----------
    dataset : xr.Dataset
        The observations dataset
    coordinates : List[str]
        The coordinates that should be joined
    index_name : str
        The name of the new, joined, coordinate
    sep : str, optional
        The string to separate the coordinate components, by default "__"

    Returns
    -------
    xr.Dataset
        Dataset with a new coordinate composed of the listed coordinates
    """
    try:
        multi_index = pd.MultiIndex.from_arrays([dataset[c].values for c in coordinates])
    except KeyError as err:
        raise KeyError(
            f"Did not find key {err} in the dataset. "
            f"This is probably because the key {err} is equal for all treatments."
        )
    multi_index = multi_index.map(lambda x: "__".join([str(x_) for x_ in x]))
    return dataset.assign_coords({index_name: ("id", multi_index)})

# def get_interventions(interventions_idata, observations, ivs: List[str]) -> xr.Dataset:
#     """Get the interventions according to the treatment ids of the observation
#     dataset.
    
#     Works only for single interventions
#     """
#     X_in = {}
#     for data_var in ivs:
#         x_in = interventions_idata[data_var]\
#             .swap_dims(timeseries_id="treatment_id")\
#             .sel(treatment_id=observations.treatment_id.values)
        
#         x_in = x_in.assign_coords(
#             _id=("treatment_id", range(x_in.sizes["treatment_id"]))
#         )
#         x_in = x_in.swap_dims(treatment_id="_id")
#         X_in.update({data_var: x_in[data_var]})


#     X_in_dataset = xr.concat(X_in.values(), dim="variable")\
#         .assign_coords(variable=ivs)\
#         .to_dataset(dim="variable")
    
#     if "variable" in X_in_dataset.dims:
#         X_in_dataset = X_in_dataset.drop_dims("variable")

#     return X_in_dataset




# def combine_interventions(
#     interventions: az.InferenceData, 
#     force: bool=False
# ) -> xr.DataArray:
#     """Combining interventions into a single dataset is only possible,
#     if there is only a single timeseries for each intervention.

#     Parameters
#     ----------
#     interventions : az.InferenceData
#         Interventions InferenceData. Contains multiple datasets with at
#         least one timeseries
#     force : bool, optional
#         Override restrictions to combine interventions only when the number
#         of timeseries is 1, by default False

#     Returns
#     -------
#     xr.DataArray
#         Interventions, combined into a single dataset

#     Raises
#     ------
#     ValueError
#         If the number of timeseries is larger than 1 and force is not True
#     """
#     assert isinstance(interventions, az.InferenceData)
#     arrays = []
#     for variable, dataset in interventions.items():
#         if dataset.sizes["timeseries_id"] > 1:
#             if force:
#                 arr = dataset.to_array()
#             else:
#                 raise ValueError(
#                     "Combining interventions is only allowed when the number of "
#                     "Timeseries for each variable is 1. This is to avoid blowing "
#                     "Up the size of the dataset with nans, because timeseries ids "
#                     "are different for each variable. You can override this error "
#                     "By using `force=True`"
#                 )
#         else:
#             arr = dataset.squeeze("timeseries_id").to_array()
        
#         arrays.append(arr)

#     return xr.concat(arrays, dim="variable")
    
