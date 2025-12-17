import pytest
from guts_base import GutsBase
from guts_base.sim import construct_sim_from_config

# run tests with the Simulation fixtures
def setup(sim):
    """Tests the construction method"""
    assert True

def simulation(sim):
    """Tests if a forward simulation pass can be computed"""
    sim.dispatch_constructor()
    evaluator = sim.dispatch()
    evaluator()
    evaluator.results

    assert True
            
def copy(sim):
    sim.dispatch_constructor()
    e_orig = sim.dispatch()
    e_orig()
    e_orig.results

    sim_copy = sim.copy()
    
    sim_copy.dispatch_constructor()
    e_copy = sim_copy.dispatch()
    e_copy()

    assert (e_copy.results == e_orig.results).all().to_array().all().values

def inference(sim: GutsBase, backend):
    """Tests if prior predictions can be computed for arbitrary backends"""
    sim.dispatch_constructor()
    sim.set_inferer(backend)

    sim.config.inference.n_predictions = 2
    sim.prior_predictive_checks()
    
    sim.config.inference_numpyro.kernel = "svi"
    sim.config.inference_numpyro.svi_iterations = 100
    sim.config.inference_numpyro.svi_learning_rate = 0.05
    sim.config.inference_numpyro.draws = 10
    sim.config.inference.n_predictions = 10

    sim.inferer.run()

    sim.posterior_predictive_checks()

    # configure ecx mode
    sim.config.guts_base.ecx_mode = "draws"
    sim.config.guts_base.ecx_draws = 3
    sim.config.guts_base.ecx_force_draws = True
    sim.config.guts_base.ecx_estimates_x = [0.5]
    sim.config.guts_base.ecx_estimates_times = [2]
    sim.config.report.debug_report = True
    sim.report()



def test_copy_from_config(sim_from_config):
    copy(sim=sim_from_config)

def test_copy_from_model_and_dataset(sim_from_model_and_dataset):
    copy(sim=sim_from_model_and_dataset)

def test_simulation_from_config(sim_from_config):
    simulation(sim=sim_from_config)

def test_simulation_from_model_and_dataset(sim_from_model_and_dataset):
    simulation(sim=sim_from_model_and_dataset)

@pytest.mark.batch3
@pytest.mark.integration
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference_from_config(sim_from_config, backend):
    inference(sim=sim_from_config, backend=backend)

@pytest.mark.batch2
@pytest.mark.integration
@pytest.mark.parametrize("backend", ["numpyro"])
def test_inference_from_model_and_dataset(sim_from_model_and_dataset, backend):
    inference(sim=sim_from_model_and_dataset, backend=backend)

