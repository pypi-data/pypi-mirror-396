from guts_base import LPxEstimator, GutsBase

def test_copy(sim_post_inference: GutsBase):
    """only tests whether the copied estimator can be evaluated"""
    _id = sim_post_inference.observations.id.values[1]
    lpx_estimator = LPxEstimator(sim=sim_post_inference, id=_id)

    e = lpx_estimator.sim.dispatch()
    e()
    e.results


def test_export_import_sim_inferer(sim_post_inference: GutsBase):
    sim_post_inference.export()
    imported_sim = GutsBase.from_directory(directory=sim_post_inference.output_path)

    # just try accessing the posterior object
    imported_sim.inferer.idata.posterior