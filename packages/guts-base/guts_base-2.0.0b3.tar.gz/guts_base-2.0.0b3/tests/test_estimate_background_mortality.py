import pytest
from guts_base import PymobSimulator

@pytest.mark.slow
def test_separate_control_mortality_fit(sim_from_model_and_dataset: PymobSimulator):
    sim_from_model_and_dataset.estimate_background_mortality(
        exclude_controls_after_fixing_background_mortality=False
    )

    for par in sim_from_model_and_dataset.config.guts_base.background_mortality_parameters:
        # test if the parameter is now not free
        assert not sim_from_model_and_dataset.config.model_parameters[par].free

        # test if the value is close to zero
        assert sim_from_model_and_dataset.config.model_parameters[par].value < 0.1

@pytest.mark.slow
def test_separate_control_mortality_fit_falsely_on_treatment(sim_from_model_and_dataset: PymobSimulator):
    highest_exposure_treatment = str(sim_from_model_and_dataset.observations.id[-1].values)
    
    sim_from_model_and_dataset.estimate_background_mortality(
        exclude_controls_after_fixing_background_mortality=False,
        control_ids=highest_exposure_treatment
    )

    for par in sim_from_model_and_dataset.config.guts_base.background_mortality_parameters:
        # test if the parameter is now not free
        assert not sim_from_model_and_dataset.config.model_parameters[par].free

        # test if the value is large (because high mortality was used to fit )
        assert sim_from_model_and_dataset.config.model_parameters[par].value > 0.1

