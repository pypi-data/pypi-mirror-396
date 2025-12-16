import pytest

from guts_base import LPxEstimator, GutsBase
from guts_base.sim import construct_sim_from_config, load_idata

@pytest.mark.slow
def test_lp50(sim_post_inference):
    _id = sim_post_inference.observations.id.values[1]
    lpx_estimator = LPxEstimator(sim=sim_post_inference, id=_id)

    theta_mean = lpx_estimator.sim.inferer.idata.posterior.mean(("chain", "draw"))
    theta_mean = {k: v["data"] for k, v in theta_mean.to_dict()["data_vars"].items()}

    lpx_estimator._loss(log_factor=0.0, theta=theta_mean)

    lpx_estimator.plot_loss_curve(mode="draws", draws=2, force_draws=True)
    lpx_estimator.plot_loss_curve(mode="mean")
    lpx_estimator.plot_loss_curve(mode="manual", parameters=lpx_estimator._posterior_mean())

    lpx_estimator.estimate(mode="mean")
    lpx_estimator.estimate(mode="manual", parameters=lpx_estimator._posterior_mean())
    lpx_estimator.estimate(mode="draws", draws=2, force_draws=True)

    lpx_estimator.results
    lpx_estimator.results_full

def test_copy(sim_post_inference):
    """only tests whether the copied estimator can be evaluated"""
    _id = sim_post_inference.observations.id.values[1]
    lpx_estimator = LPxEstimator(sim=sim_post_inference, id=_id)

    e = lpx_estimator.sim.dispatch()
    e()
    e.results


if __name__ == "__main__":
    test_copy(load_idata(construct_sim_from_config("red_sd_da", GutsBase), "ecx/idata_red_sd_da.nc"))
