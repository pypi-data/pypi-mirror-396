import os
import arviz as az
from guts_base.sim import GutsBase

def construct_sim_from_config(
    scenario: str, 
    simulation_class: type, 
    output_path=None
) -> GutsBase:
    """Helper function to construct simulations for debugging"""
    sim = simulation_class(f"scenarios/{scenario}/settings.cfg")

    # this sets a different output directory
    if output_path is not None:
        p = output_path / sim.config.case_study.name / "results" / sim.config.case_study.scenario
        sim.config.case_study.output_path = str(p)
    else:
        sim.config.case_study.scenario = "debug_test"
    sim.setup()
    return sim


def load_idata(sim: GutsBase, idata_file: str) -> GutsBase:
    sim.set_inferer("numpyro")

    if os.path.exists(idata_file):
        sim.inferer.idata = az.from_netcdf(idata_file)
    else:
        sim.inferer.idata = None

    return sim