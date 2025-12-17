import pytest
from guts_base import GutsBase


TEST_CONFIGS = [
    # default settings
    dict(),
    dict(
        background_mortality="pre-fit",
        transform_scalings={"time_factor": 2.0, "x_in_factor": 0.1}
    ),
    dict(
        forward_interpolate_exposure_data=False
    ),

]

@pytest.mark.integration
@pytest.mark.batch1
@pytest.mark.parametrize("config",TEST_CONFIGS)
def test_estimate_parameters(sim_from_model_and_dataset: GutsBase, config):
    sim_from_model_and_dataset.config.inference_numpyro.draws = 100
    sim_from_model_and_dataset.config.report.debug_report = True
    sim_from_model_and_dataset.estimate_parameters(**config)

