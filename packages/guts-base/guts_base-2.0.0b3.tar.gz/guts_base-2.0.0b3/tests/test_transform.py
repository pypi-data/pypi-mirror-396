from dataclasses import dataclass
import os
import pytest
import numpy as np
import xarray as xr
from scipy.stats import ttest_ind
import arviz
from matplotlib import pyplot as plt
from typing import Type, Tuple
from pymob.sim.config import Modelparameters, Param
from pymob.sim.config import Expression
from guts_base.sim.transformer import (
    GutsTransform,
    GenericTransform,
    DataTransform,
    ParameterTransform,
)
from guts_base import PymobSimulator
from guts_base.sim.utils import GutsBaseError
from guts_base.mod import RED_SD_DA


@dataclass
class TestDataTransform(DataTransform):
    test_factor_1 = 2

    def y(self, x):
        return x * self.test_factor_1
    
    def y_inv(self, x):
        return x / self.test_factor_1

@dataclass
class TestParamTransform(ParameterTransform):
    test_factor_2 = 5

    def x(self, x):
        return x * self.test_factor_2

    def x_inv(self, x):
        return x / self.test_factor_2

@dataclass(repr=False)
class TestTransform(GenericTransform):
    parameter_transformer_class: Type[ParameterTransform] = TestParamTransform
    data_transformer_class: Type[DataTransform] = TestDataTransform
    test_factor_1: float = 2
    test_factor_2: float = 5

def data_and_transform() -> Tuple[Tuple[Modelparameters, xr.Dataset], GenericTransform]:
    transform = TestTransform(test_factor_1=10.0, ignore_keys=["TEST_IGNORE"])
    mp = Modelparameters.model_validate(dict(UNDEFINED=Param(value=10.0), x=Param(value=5.0)))
    data = xr.Dataset({"TEST_IGNORE": 1.0, "y": 823_873_617_231.4127831231231235535567786789})

    return (mp, data), transform


# TODO: Add pytest-fixture for targets [parameters, idata, observations] and inverse [False, True]
def test_transform_check(sim_from_model_and_dataset: PymobSimulator):
    sim_from_model_and_dataset.transformer = GutsTransform(
        time_factor=24.0, x_in_factor=1000.0, ignore_keys=["id", "exposure_path"]
    )

    fts_true, _ = sim_from_model_and_dataset.transformer._check_transform_state(
        target="parameters", transform=True, inverse=False
    )
    fts_false, _ = sim_from_model_and_dataset.transformer._check_transform_state(
        target="parameters", transform=True, inverse=True
    )

    # test whether decisions are taken correctly to transform parameters
    assert fts_true
    assert not fts_false


def test_transform_observations(sim_from_model_and_dataset: PymobSimulator):
    sim_from_model_and_dataset.transformer = GutsTransform(
        time_factor=24.0, x_in_factor=1000.0, ignore_keys=["id", "exposure_path"]
    )

    obs = sim_from_model_and_dataset.observations.copy(deep=True)

    # this transform should not inverse transform observations, because they are already
    # transformed
    sim_from_model_and_dataset.transform(inverse=True, observations=True)

    # test that no transform took place
    np.testing.assert_array_equal(
        sim_from_model_and_dataset.observations.to_array().values, obs.to_array().values
    )

    # this shoudl transform observations
    sim_from_model_and_dataset.transform(inverse=False, observations=True)

    # test if the observations are the same as the deepcopied observations divided by 1000
    np.testing.assert_array_equal(
        sim_from_model_and_dataset.observations.exposure.values,
        obs.exposure.values / 1000,
    )

    # request a transform, which is not granted
    sim_from_model_and_dataset.transform(inverse=False, observations=True)

    sim_from_model_and_dataset.transform(inverse=True, observations=True)

    # test that observations were transformed and inverse transformed
    np.testing.assert_array_almost_equal(
        sim_from_model_and_dataset.observations.to_array().values,
        obs.to_array().values,
        decimal=10,
    )

    # final check. Test a roundtrip of the observations
    sim_from_model_and_dataset.transformer.data_transformer._test_transform_consistency(
        sim_from_model_and_dataset.observations
    )


def test_transform_parameters(sim_from_model_and_dataset: PymobSimulator):
    sim_from_model_and_dataset.transformer = GutsTransform(
        time_factor=24.0, x_in_factor=1000.0, ignore_keys=["id", "exposure_path"]
    )

    # back up model parameters
    model_parameters = sim_from_model_and_dataset.config.model_parameters.model_dump(
        mode="python"
    )

    # assert that model parameters are initially equal
    assert (
        sim_from_model_and_dataset.config.model_parameters
        == Modelparameters.model_validate(model_parameters)
    )

    # this transform should not inverse transform observations, because they are already
    # transformed
    sim_from_model_and_dataset.transform(inverse=True, parameters=True)

    # test that no transform took place
    model_parameters_untransformed = (
        sim_from_model_and_dataset.config.model_parameters.model_dump(mode="json")
    )
    assert Modelparameters.model_validate(
        model_parameters_untransformed
    ) == Modelparameters.model_validate(model_parameters)

    # this shoudl transform observations
    sim_from_model_and_dataset.transform(inverse=False, parameters=True)

    # test if the observations are the same as the deepcopied observations divided by 1000
    model_parameters_transformed = (
        sim_from_model_and_dataset.config.model_parameters.model_dump(mode="json")
    )
    assert Modelparameters.model_validate(
        model_parameters_transformed
    ) != Modelparameters.model_validate(model_parameters)

    # request a transform, which is not granted
    sim_from_model_and_dataset.transform(inverse=False, parameters=True)

    # this should reverse the previously applied transformation, and should consequently
    # raise no error if all transformations have been applied
    sim_from_model_and_dataset.transform(inverse=True, parameters=True)
    model_parameters_transformed = (
        sim_from_model_and_dataset.config.model_parameters.model_dump(mode="json")
    )
    assert Modelparameters.model_validate(
        model_parameters_transformed
    ) == Modelparameters.model_validate(model_parameters)

    # final check. Test a roundtrip of the observations
    sim_from_model_and_dataset.transformer.parameter_transformer._test_transform_consistency(
        sim_from_model_and_dataset.config.model_parameters
    )


def test_partially_undefined_transform():
    (mp, _), transform = data_and_transform()
    try:
        transform.parameter_transformer.transform(mp)
    except GutsBaseError:
        pass

    # define transform at runtime
    TestParamTransform.UNDEFINED = lambda self, x: x * self.test_factor_2  # type: ignore
    mp_transformed = transform.parameter_transformer.transform(mp)

    assert mp.UNDEFINED.value == mp_transformed.UNDEFINED.value / TestParamTransform.test_factor_2  # type: ignore
    assert mp.x.value == mp_transformed.x.value / TestParamTransform.test_factor_2  # type: ignore


def test_ignore_data_variables():
    (_, data), transform = data_and_transform()

    # test is ignored. Should be no transform
    transform.data_transformer.TEST_IGNORE = lambda self, x: x / self.test_factor_1  # type: ignore
    transform.data_transformer._test_transform_consistency(data)

    data_transformed = transform.data_transformer.transform(data)

    # assert ignored variables have not been transformed
    assert data_transformed.TEST_IGNORE == data.TEST_IGNORE
    
    # assert that the data was correctly transformed
    assert data_transformed.y == data.y * transform.data_transformer.test_factor_1  # type: ignore


def test_numeric_precision_limits_of_exact_solutions():
    (_, data), transform = data_and_transform()
    
    # for factors from 1e-100 to 1e+100 test if the parameter values can be precisely recovered
    for factor in np.logspace(-100, 100, 100):
        transform.data_transformer.test_factor_1 = factor  # type: ignore
        transform.data_transformer._test_transform_consistency(data)


@pytest.mark.slow
def test_numeric_precision_limits_of_ode_solutions(sim_from_model_and_dataset: PymobSimulator):
    # copy of original parameters and 
    sim_from_model_and_dataset.model_parameters
    mp = sim_from_model_and_dataset.config.model_parameters.model_dump()
    mp_untransformed = Modelparameters.model_validate(mp)
    theta_old = mp_untransformed.value_dict
    # make an evaluation of the original parameters and input information
    sim_from_model_and_dataset.config.jaxsolver.rtol = 1e-11
    sim_from_model_and_dataset.config.jaxsolver.atol = 1e-60  # ⚠️ This is only necessary 
    # for testing; when extreme conversions are expected. This means, I recommend,
    # Issuing an error, when the exposure is too close to the absolute tolerance of the
    # solver
    sim_from_model_and_dataset.dispatch_constructor()
    
    results_untransformed = sim_from_model_and_dataset.evaluate(parameters=theta_old)

    # set up the transformer and transform TIME coordinates (so that dispatch constructor)
    # has to be called only once.
    sim_from_model_and_dataset.transformer = GutsTransform(
        time_factor=24, x_in_factor=1000.0, ignore_keys=["id", "exposure_path", "substance",]
    )
    
    sim_from_model_and_dataset.coordinates = sim_from_model_and_dataset.transformer.data_transformer.transform(
        sim_from_model_and_dataset.coordinates
    )

    # explicitly transform the xin coordinates, because they may be different than
    # the simulation coordinates.
    _dct = sim_from_model_and_dataset.transformer.data_transformer.transform(
        dict(sim_from_model_and_dataset.model_parameters["x_in"].coords)
    )

    sim_from_model_and_dataset.model_parameters["x_in"]["time"] = _dct["time"].values
    sim_from_model_and_dataset.dispatch_constructor()


    # this is EXTREMELY ROBUST! It can transform easily over 100 orders of magnitude with
    # a precision loss only after the 4th decimal
    x_in_factors = np.logspace(-50, 50, 1001 + 1)
    diffs = []
    res = []
    for x_in_factor in x_in_factors:
        # vary the x_in factor to get a handle on the effect on precision
        sim_from_model_and_dataset.transformer.parameter_transformer.x_in_factor = x_in_factor  # type: ignore
        sim_from_model_and_dataset.transformer.data_transformer.x_in_factor = x_in_factor  # type: ignore

        # transform model parameters
        mp_transformed = sim_from_model_and_dataset.transformer.parameter_transformer.transform(
            mp_untransformed
        )
        theta_transformed = mp_transformed.value_dict

        # transform observations to get new transformed input (exposure)
        obs_transformed = sim_from_model_and_dataset.transformer.data_transformer.transform(
            sim_from_model_and_dataset.observations
        )

        # parse and validate x_in
        x_in_transformed = sim_from_model_and_dataset.parse_input("x_in", reference_data=obs_transformed)
        x_in_transformed = x_in_transformed.reindex(time=np.concatenate([x_in_transformed.time.values, [x_in_transformed.time.values[-1] * 1.1]]))
        x_in_transformed = x_in_transformed.interpolate_na(dim="time", method="linear").ffill(dim="time")
        x_in_transformed_val = sim_from_model_and_dataset.validate_model_input(x_in_transformed)

        # calucalte the model with transformed parameters and input
        results_transformed = sim_from_model_and_dataset.evaluate(parameters=theta_transformed, x_in=x_in_transformed_val)

        # backtransform results 
        results_backtransformed = sim_from_model_and_dataset.transformer.data_transformer.transform_inv(
            x=results_transformed
        )

        diff = results_untransformed - results_backtransformed
        absdiff = np.abs(diff)
        maxabsdiff = absdiff.max()
        maxabsdiff = maxabsdiff.assign_coords({"factor": x_in_factor}).expand_dims("factor")
        diffs.append(maxabsdiff)
        maxres = results_transformed.max()
        maxres = maxres.assign_coords({"factor": x_in_factor}).expand_dims("factor")
        res.append(maxres)

        # # compare untransformed and backtransformed results
        np.testing.assert_array_almost_equal(
            results_untransformed.to_array().values,
            results_backtransformed.to_array().values,
            decimal=4,
        )

    diffs_ds = xr.concat(diffs, dim="factor")
    # maxres_ds = xr.concat(res, dim="factor")
    data = diffs_ds

    fig, ax = plt.subplots(4,1, sharex=True)
    ax[0].plot(data.factor, data.exposure)
    ax[1].plot(data.factor, data.D)
    ax[2].plot(data.factor, data.H)
    ax[3].plot(data.factor, data.survival)
    ax[1].axhline(sim_from_model_and_dataset.config.jaxsolver.rtol, color="black")
    ax[1].axhline(np.sqrt(sim_from_model_and_dataset.config.jaxsolver.atol), color="red")
    ax[1].set_xscale("log")
    ax[1].set_ylabel("Damage")
    ax[2].set_ylabel("Hazard")
    ax[0].set_ylabel("Exposure")
    ax[3].set_ylabel("Survival")
    ax[1].set_yscale("log")
    ax[2].axhline(sim_from_model_and_dataset.config.jaxsolver.rtol, color="black")
    ax[2].axhline(np.sqrt(sim_from_model_and_dataset.config.jaxsolver.atol), color="red")
    ax[0].set_yscale("linear")
    ax[2].set_yscale("log")
    ax[3].set_yscale("log")
    ax[3].set_xlabel("x-in scale factor")
    ax[0].set_title("Maximum absolute difference of round-trip transform")
    os.makedirs("results/testing", exist_ok=True)

    if sim_from_model_and_dataset._model_class is not None:
        _name = sim_from_model_and_dataset._model_class.__name__
    else:
        _name = "test_model"
    fig.savefig(f"results/testing/numeric_precision_of_transforms_{_name}.png")

@pytest.mark.batch4
@pytest.mark.integration
def test_transform_integrity(sim_from_model_and_dataset: PymobSimulator):
    """Tests if parameter distributions generated from transformed simulations and 
    untransformed simulations are equivalent.
    """
    sim_from_model_and_dataset.config.inference_numpyro.svi_iterations = 20_000
    sim_from_model_and_dataset.config.inference_numpyro.svi_learning_rate = 0.0005
    sim_from_model_and_dataset.config.inference_numpyro.draws = 1000
    sim_from_model_and_dataset.config.jaxsolver.throw_exception = False
    sim_from_model_and_dataset.dispatch_constructor()
    sim_from_model_and_dataset.set_inferer("numpyro")

    sim_from_model_and_dataset.inferer.run()

    posterior = sim_from_model_and_dataset.inferer.idata.posterior.copy(deep=True)

    x_in_factor = float(sim_from_model_and_dataset.observations.exposure.max().values)

    # set transformation
    sim_from_model_and_dataset.transformer = GutsTransform(
        time_factor=1.0, x_in_factor=x_in_factor, 
        ignore_keys=["id", "exposure_path",]
    )

    sim_from_model_and_dataset.transform(idata=False, observations=True, parameters=True)


    # transform priors, because it makes sense here

    for key, param in sim_from_model_and_dataset.config.model_parameters.free.items():
        trans_func = getattr(sim_from_model_and_dataset.transformer.parameter_transformer, key)
        arg = param.prior.parameters["scale"] # type: ignore
        arg_new = trans_func(np.array(arg.evaluate())).tolist()
        arg_new_exp = Expression(str(arg_new))
        param.prior.parameters["scale"] = arg_new_exp # type: ignore

    sim_from_model_and_dataset.set_inferer("numpyro")
    sim_from_model_and_dataset.inferer.run()

    # update idata transform status, because the idata was generated with
    # a transformed simulation
    sim_from_model_and_dataset.transformer.is_transformed["idata"] = True
    sim_from_model_and_dataset.transform(idata=True, observations=True, parameters=True, inverse=True)

    posterior_rt = sim_from_model_and_dataset.inferer.idata.posterior.copy(deep=True)

    mu = posterior.mean(("chain", "draw")).to_array().values
    sigma = posterior.std(("chain", "draw")).to_array().values
    mu_bar = posterior.median(("chain", "draw")).to_array().values
    
    # this is the sample mean and std deviation
    x = posterior_rt.mean(("chain", "draw")).to_array().values
    s = posterior_rt.std(("chain", "draw")).to_array().values
    x_bar = posterior_rt.median(("chain", "draw")).to_array().values

    # plot results
    axes = arviz.plot_density(
        data=[posterior, posterior_rt], 
        data_labels=["untransformed", "transformed-backtransformed"], 
        shade=0.2
    )
    fig = axes[0,0].figure
    
    os.makedirs("results/testing", exist_ok=True)

    if sim_from_model_and_dataset._model_class is not None:
        _name = sim_from_model_and_dataset._model_class.__name__
    else:
        _name = "test_model"
    fig.savefig(f"results/testing/transformation_integrity_dist_comparison_{_name}.png")

    for param in sim_from_model_and_dataset.model_parameter_names:
        if len(posterior[param].shape) > 2:
            ttest_result = ttest_ind(posterior[param].sel(chain=0).values, posterior_rt[param].sel(chain=0).values)
        else:
            ttest_result = ttest_ind(posterior[param].sel(chain=0).values, posterior_rt[param].sel(chain=0).values)
        # test if it is likely that the samples come from the same distribution.
        assert np.all(ttest_result.pvalue > 0.05)

    # just test closeness of means and std deviations to a 5% relative tolerance
    np.testing.assert_allclose(mu, x, atol=0.00001, rtol=0.05)
    np.testing.assert_allclose(sigma, s, atol=0.00001, rtol=0.05)
