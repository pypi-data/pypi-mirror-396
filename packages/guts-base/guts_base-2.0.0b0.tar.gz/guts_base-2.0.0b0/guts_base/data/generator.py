import numpy as np
import pandas as pd
import xarray as xr
from typing import TypedDict, Dict, Optional, Sequence, Literal
from numpy.typing import NDArray

class ExposureDataDict(TypedDict):
    start: float
    end: Optional[float]
    exposure: Optional[float|Sequence[float]]

def create_artificial_data(
    t_max, 
    dt, 
    exposure_paths=["oral", "topical", "contact"],
    intensity=[0.1, 0.5, 0.05],
    seed=1,
):
    rng = np.random.default_rng(1)
    time = np.arange(0, t_max, step=dt)  # daily time resolution

    # calculate potential exposure based on a lognormal distribution
    oral = rng.lognormal(mean=np.log(intensity[0]), sigma=0.5, size=len(time))
    # and include a random exposure days
    oral *= rng.binomial(n=1, p=1, size=len(time))


    # calculate potential exposure based on a lognormal distribution
    topical = rng.lognormal(mean=np.log(intensity[1]), sigma=1, size=len(time))
    # and include a random exposure days
    topical *= rng.binomial(n=1, p=0.25, size=len(time))


    # calculate potential exposure based on a lognormal distribution
    contact = rng.lognormal(mean=np.log(intensity[2]), sigma=0.1, size=len(time))
    # and include a random exposure days
    contact *= rng.binomial(n=1, p=0.8, size=len(time))



    exposures = xr.Dataset(
        data_vars={
            "exposure": (("time", "exposure_path"), np.column_stack([oral, topical, contact])),
        },
        coords={"time": time, "exposure_path": ["oral", "topical", "contact"]}
    )

    return exposures.sel(exposure_path=exposure_paths)


def design_exposure_timeseries(time: NDArray, exposure: ExposureDataDict, eps: float):
    if exposure is None:
        return
    
    if exposure["exposure"] is None:
        exposure["exposure"] = 0.0
    
    exposure["end"] = time[-1] if exposure["end"] is None else exposure["end"]

    return np.where(
        np.logical_and(time >= exposure["start"], time < exposure["end"]),
        # compatibility with old version where exposure was named concentration
        exposure["concentration"] if "concentration" in exposure else exposure["exposure"],
        0
    )

def design_exposure_scenario(
    t_max: float, 
    dt: float, 
    exposures: Dict[str,ExposureDataDict],
    eps: float = 1e-8,
    exposure_dimension: str = "exposure_type",
):
    """
    TODO: tmax, dt and eps are probably not necessary
    """
    # add dt so that tmax is definitely inclded
    time = np.arange(0, t_max+dt, step=dt)  # daily time resolution
    time = np.unique(np.concatenate([time] + [
        np.array([time[-1] if vals["end"] is None else vals["end"]])
        for key, vals in exposures.items()

    ]))

    treatments = {}
    for key, expo in exposures.items():
        treat = design_exposure_timeseries(time, expo, eps)
        treatments.update({key: treat})

    data = np.column_stack(list(treatments.values()))
    data = np.expand_dims(data, axis=0)

    coords = {"id": [0], "time": time}
    
    coords.update({exposure_dimension: list(treatments.keys())})

    exposures_dataset = xr.Dataset(
        data_vars={"exposure": (tuple(coords.keys()), data)},
        coords=coords
    )

    return exposures_dataset


def draft_laboratory_experiment(
    treatments: Dict[str, float|Dict[str,float]], 
    experiment_end: pd.Timedelta = pd.Timedelta(10, unit="days"), 
    exposure_pattern: ExposureDataDict|Dict[str,ExposureDataDict] = ExposureDataDict(start=0.0, end=None, exposure=None),
    dt: pd.Timedelta = pd.Timedelta(1, unit="days"), 
    exposure_dimension: str = "exposure_type",
):
    

    time_unit = pd.Timedelta(1, experiment_end.resolution_string) # type: ignore

    dt_float = dt / time_unit
    experiment_end_float = experiment_end / time_unit + dt / time_unit
    exposures = {}
    for treatment_name, treatment in treatments.items():
        if isinstance(treatment, dict):
            dummy_dim = False
            exposure_dict = exposure_pattern.copy()
            for treatment_key, treatment_val in treatment.items():
                if treatment_key not in exposure_dict:
                    raise KeyError(
                        "If `treatments` values contain mutliple keys " +
                        f"({treatment.keys()}), these must be present in the " +
                        "`exposure_pattern` as well; i.e. exposure_pattern must be a dict."
                        
                    )
                exposure_dict[treatment_key]["exposure"] = treatment_val

        else:
            dummy_dim = True
            exposure = exposure_pattern.copy()

            if "exposure" not in exposure:
                raise KeyError(
                    "exposure_pattern did not contain the key `exposure` ",
                    f"but {exposure.keys()}. Make sure the treatments and exposures match."
                )
            exposure["exposure"] = treatment

            exposure_dict = {"dummy_key": exposure}

        for _, vals in exposure_dict.items():
            if vals["end"] is None:
                pass
            elif isinstance(vals["end"], float|int):
                pass
            elif isinstance(vals["end"], pd.Timedelta):
                vals["end"] = vals["end"] / time_unit
            else:
                raise NotImplementedError(
                    f"exposure_data['end']={vals['end']} but must be None, float or pd.Timedelta."
                )

            if vals["start"] is None:
                pass
            elif isinstance(vals["start"], float|int):
                pass
            elif isinstance(vals["start"], pd.Timedelta):
                vals["start"] = vals["start"] / time_unit
            else:
                raise NotImplementedError(
                    f"exposure_data['start']={vals['start']} but must be None, float or pd.Timedelta."
                )

        x_in = design_exposure_scenario(
            t_max=experiment_end_float, dt=dt_float, 
            exposures=exposure_dict,
            exposure_dimension=exposure_dimension,
        )

        if dummy_dim:
            x_in = x_in.isel({exposure_dimension: 0})
            x_in["exposure"] = x_in["exposure"].drop_vars(exposure_dimension)


        x_in = x_in.assign_coords({"id": [treatment_name]})
        exposures.update({treatment_name: x_in})

    experiment = xr.combine_by_coords(exposures.values())
    # sort by id so the order of the treatments remains consistent
    experiment = experiment.sel(
        id=list(exposures.keys()), 
        time=[float(t) for t in  experiment.time if t <= experiment_end / time_unit]
    )

    return experiment

