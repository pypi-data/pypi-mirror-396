from functools import partial
import numpy as np
import jax
import jax.numpy as jnp
import numpyro
import warnings
from numpyro.infer import Predictive
from numpyro.infer.util import get_transforms
from typing import Literal


def survival_predictions(
    probs, n_trials, 
    eps: float = 0.0,
    seed=1, 
    mode: Literal["survival", "lethality", "deaths"] = "survival"
):
    """Generate predictions for survival based on a multinomial survival distribution

    Parameters
    ----------
    probs : ArrayLike
        2D Array denoting the multinomial probabilities of deaths for each time interval 
        per experiment 
        dims=(experiment, time)
    n_trials : ArrayLike
        1D Array denoting the number of organisms at the beginning in each experiment
        dims = (experiment,)
    seed : int, optional
        Seed for the random number generator, by default 1
    mode : str, optional
        How should the random draws be returned? 
        - survival: Decreasing from n_trials to 0
        - lethality: Increasing from 0 to n_trials
        - deaths: Between 0 and n_trials in each interval. Summing to n_trials
    """

    def survival_to_death_probs(pr_survival):
        # truncate here, because numeric errors below the solver tolerance can
        # lead to negative values in the difference. This needs to be cured here
        pr_survival_ = np.trunc(pr_survival / eps) * eps
        pr_death = pr_survival_[:-1] - pr_survival_[1:]

        pr_death = np.concatenate([
            # concatenate a zero at the beginning in order to "simulate" no
            # deaths at T = 0
            jnp.zeros((1,)),
            # Delta S
            pr_death,
            # The remaining mortility as T -> infinity 
            jnp.ones((1,))-pr_death.sum()
        ])

        # make sure the vector is not zero or 1 (this is always problematic for 
        # probabilities) and make sure the vector sums to 1
        pr_death = np.clip(pr_death, eps, 1-eps)
        pr_death = pr_death / pr_death.sum()
        return pr_death

    rng = np.random.default_rng(seed)
    deaths = jnp.array(list(map(
        lambda n, pr_survival: rng.multinomial(
            n=n, pvals=survival_to_death_probs(pr_survival)
        ), 
        n_trials, 
        probs
    )))

    # remove the last observations to trim off the simulated unobserved mortality
    deaths = deaths[:, :-1]

    if mode == "deaths":
        return deaths
    elif mode == "lethality":
        return deaths.cumsum(axis=1)
    elif mode == "survival":
        return np.expand_dims(n_trials, axis=1) - deaths.cumsum(axis=1)
    else:
        raise NotImplementedError(
            f"Mode {mode} is not implemented."+
            "Use one of 'survival', 'lethality', or 'deaths'."
        )
    
def posterior_predictions(sim, idata, seed=None):
    """Make posterior predictions for survival data"""
    if seed is None:
        seed = sim.config.simulation.seed

    n = idata.posterior.dims["draw"]
    c = idata.posterior.dims["chain"]

    obs, masks = sim.inferer.observation_parser()
    if sim.config.inference_numpyro.user_defined_error_model is not None:
        posterior_model_fits = sim.inferer.posterior_predictions()
        chains = []
        for i in range(c):
            # TODO: Switch to vmap and jit, but it did not work, so if you do it TEST IT!!!!!!!
            predictions = list(map(
                partial(
                    survival_predictions,
                    n_trials=obs["survival"][:, 0].astype(int),
                    eps=obs["eps"],
                    seed=seed,
                    mode="survival",
                ),
                posterior_model_fits["survival"].sel(chain=i).values
            ))
            chains.append(predictions)

        posterior_predictive = {"survival_obs": np.array(chains)}
    elif (
        sim.config.inference_numpyro.user_defined_error_model is None and 
        hasattr(idata, "unconstrained_posterior")
    ):
        model_kwargs = sim.inferer.preprocessing(obs=obs, masks=masks)
        model_kwargs["obs"]["survival"] = None

        # prepare model
        model = partial(
            sim.inferer.inference_model, 
            solver=sim.inferer.evaluator, 
            **model_kwargs
        )    

        posterior_samples = {
            k: np.array(v["data"]) for k, v 
            in idata.unconstrained_posterior.to_dict()["data_vars"].items()
        }

        predictive = Predictive(
            model, posterior_samples=posterior_samples,
            num_samples=n, batch_ndims=2
        )

        key = jax.random.PRNGKey(seed)
        samples = predictive(key)

        posterior_model_fits = sim.inferer.to_arviz_idata(
            posterior=samples,
            n_draws=n,
            n_chains=c
        )["posterior_model_fits"]
        posterior_predictive = {"survival_obs": samples.pop("survival_obs")}
    else:
        warnings.warn(
            "Posterior predictions could not be computed! Either user_defined_error_model "+
            "must be used, or idata must have unconstrained_posterior. Note that the "+
            "unconstrained posterior, currently can't be produced if the simulation is "+
            "transformed."
        )
        return idata


    new_idata = sim.inferer.idata.copy()
    new_idata["posterior_model_fits"] = posterior_model_fits
    new_idata["posterior_predictive"] = sim.inferer.to_arviz_idata(
        posterior_predictive=posterior_predictive,
        n_draws=n,
        n_chains=c
    )["posterior_predictive"]

    # update chain names in case they were subselected (clustering)
    # new_idata = new_idata.assign_coords({"chain": idata.posterior.chain.values})
    new_idata = new_idata.assign_coords({"chain": idata.posterior.chain.values})

    # assert the new posterior matches the old posterior
    tol = sim.config.jaxsolver.atol * 100
    abs_diff_posterior = np.abs(idata.posterior - new_idata.posterior)
    np.testing.assert_array_less(abs_diff_posterior.mean().to_array(), tol)

    fit_tol = tol * sim.coordinates["time"].max()
    abs_diff_fits = np.abs(new_idata.posterior_model_fits - idata.posterior_model_fits)
    np.testing.assert_array_less(abs_diff_fits.mean().to_array(), fit_tol)

    for key, var_orig in idata.posterior_model_fits.items():
        if key == "survival":
            # increase tolerance if survival is looked at
            # this is because. survival is not subject to 
            # solver tolerances (only mediated due to hazard/damage)
            atol = np.sqrt(sim.config.jaxsolver.atol) * 100
            rtol = np.sqrt(sim.config.jaxsolver.rtol) * 100
        else:
            atol = np.sqrt(sim.config.jaxsolver.atol)
            rtol = np.sqrt(sim.config.jaxsolver.rtol)

        var_recalc = new_idata.posterior_model_fits[key]
        np.testing.assert_allclose(
            actual=var_recalc.sel(time=var_orig.time),
            desired=var_orig,
            atol=atol,
            rtol=rtol
        )


    idata.posterior_model_fits = new_idata.posterior_model_fits
    idata.posterior_predictive = new_idata.posterior_predictive

    return idata



