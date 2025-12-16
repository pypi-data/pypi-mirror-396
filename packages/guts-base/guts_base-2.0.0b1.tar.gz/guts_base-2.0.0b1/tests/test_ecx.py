import pytest

from guts_base import LPxEstimator, GutsBase, ECxEstimator, GutsBaseError

@pytest.mark.slow
def test_lp50(sim_post_inference: GutsBase):
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

def test_ecx_manual(sim_post_inference: GutsBase):
    sim = sim_post_inference
    ecx_scenarios = sim.predefined_scenarios()
    parameters = sim.point_estimate(estimate="mean", to="dict")
    assert isinstance(parameters, dict)

    if sim_post_inference.config.guts_base.ecx_set_background_mortality_to_zero:
        conditions = {p: 0.0 for p in sim_post_inference.config.guts_base.background_mortality_parameters}


    for name, x_in in ecx_scenarios.items():
        ecx = ECxEstimator(
            sim, 
            effect="survival",
            x_in=x_in,
            x=0.5,
            time=1.0,
            conditions_posterior=conditions,
        )

        try:
            # this will fail because no parameters are provided
            ecx.plot_loss_curve(mode="manual")
            ecx.estimate(mode="manual")
        except GutsBaseError:
            pass


        ecx.plot_loss_curve(mode="manual", parameters=parameters, log_x0=1.0)
        ecx.figure_loss_curve
        ecx.estimate(mode="manual", parameters=parameters)
        ecx.figure_profile_and_effect

def test_ecx_mean(sim_post_inference: GutsBase):
    """Test ECx generation"""
    sim = sim_post_inference

    ecx_scenarios = sim.predefined_scenarios()
    for name, x_in in ecx_scenarios.items():
        ecx = ECxEstimator(
            sim, 
            effect="survival",
            x_in=x_in,
            x=0.5,
            time=1
        )
        ecx.estimate(mode="mean")
        
