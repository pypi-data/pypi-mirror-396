import pytest
import pandas as pd
from guts_base import PymobSimulator
from guts_base.data.generator import ExposureDataDict
from pymob.inference.scipy_backend import ScipyBackend
from guts_base.prob import conditional_survival
from guts_base.mod import RED_SD

def test_generate_single_exposure_lab_experiment_simulation(tmp_path):
    # This is the method to be developed for the WP2 task

    experiment = PymobSimulator.draft_laboratory_experiment(
        treatments={
            "control": 0.0, 
            "Treat 1": 1.0, 
            "Treat 2": 5.0, 
            "Treat 3": 50.0, 
            "Treat 4": 100.0,
        },
        n_test_organisms_per_treatment=10,
        experiment_end=pd.Timedelta("10 days"),
        exposure_pattern=ExposureDataDict(start=0, end=None, exposure=None),
        exposure_interpolation="linear",
        dt=pd.Timedelta("1 day"),
    )


    # TODO: this should be a separate classmethod, which includes the interpolation

    model = RED_SD()

    sim = PymobSimulator.from_model_and_dataset(
        model=model, 
        survival_data=experiment.survival.to_pandas().T,
        exposure_data={"A": experiment.exposure.to_pandas().T},
        output_directory=tmp_path
    )

    # update the distribution map
    ScipyBackend._distribution.distribution_map.update({
        "conditional_survival": (conditional_survival, {})
    })

    # set the initial number
    sim.config.error_model.survival = "conditional_survival(p=survival,n=survivors_at_start[:,[0]])"

    # set the inferer to scipy     
    sim.set_inferer("scipy")
    
    # sample from the model
    theta = {"kd": 0.02, "b": 0.3, "m": 0.1, "hb": 0.01}
    results = sim.inferer.inference_model(theta)
    sim.inferer.inference_model(theta=theta)["observations"]["survival"]


    # TODO: [Opt] Results should be idata
    sim.observations.survival.values = results["observations"]["survival"]