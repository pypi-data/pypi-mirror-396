import pytest
import jax
import jax.numpy as jnp
from pymob import Config

# this should raise an exception when nans are created the computation

def init_guts_casestudy_constant_exposure(scenario="testing_guts_constant_exposure"):
    """This is an external case study used for local testing. The test study
    will eventually added also to the remote as an example, but until this happens
    the test is skipped on the remote.
    """
    config = Config()
    config.case_study.name = "guts_base"
    config.case_study.scenario = scenario
    config.case_study.package = "../pollinator-tktd/case_studies"
    config.case_study.simulation = "GutsSimulationConstantExposure"
    config.import_casestudy_modules(reset_path=True)

    if "sim" in config._modules:       
        Simulation = config.import_simulation_from_case_study()
        sim = Simulation(config)
        return sim
    else:
        pytest.skip()


def init_guts_casestudy_variable_exposure(scenario="testing_guts_variable_exposure"):
    """This is an external case study used for local testing. The test study
    will eventually added also to the remote as an example, but until this happens
    the test is skipped on the remote.
    """
    config = Config()
    config.case_study.name = "guts_base"
    config.case_study.scenario = scenario
    config.case_study.package = "../pollinator-tktd/case_studies"
    config.case_study.simulation = "GutsSimulationVariableExposure"
    config.import_casestudy_modules(reset_path=True)

    if "sim" in config._modules:       
        Simulation = config.import_simulation_from_case_study()
        sim = Simulation(config)
        return sim
    else:
        pytest.skip()

@pytest.mark.slow
def test_guts_constant_exposure():
    sim = init_guts_casestudy_constant_exposure()
    sim.initialize_from_script()

    sim.use_jax_solver()
    sim.dispatch_constructor(rtol=1e-7, atol=1e-8)

    # test gradients
    def test_func(theta):
        k_d, h_b, b, z = theta
        e = sim.dispatch({"k_d": k_d, "h_b": h_b, "b":b, "z": z})
        e()
        return e.Y["survival"][-1]

    val, grads = jax.value_and_grad(test_func)(jnp.array([1, 0.001, 0.2, 1.0]))

    assert all(grads != jnp.nan)

@pytest.mark.slow
def test_guts_variable_exposure():
    sim = init_guts_casestudy_variable_exposure()
    sim.load_modules()
    sim.initialize_from_script()

    sim.use_jax_solver()
    sim.dispatch_constructor(rtol=1e-7, atol=1e-8)

    # test gradients
    def test_func(theta):
        k_d, h_b, b, z = theta
        e = sim.dispatch({"k_d": k_d, "h_b": h_b, "b":b, "z": z})
        e()
        return e.Y["survival"][-1]

    val, grads = jax.value_and_grad(test_func)(jnp.array([1, 0.001, 0.2, 1.0]))

    assert all(grads != jnp.nan)



if __name__ == "__main__":
    test_guts_variable_exposure()