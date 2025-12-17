from guts_base.sim import GutsSimulationVariableExposure, GutsSimulationConstantExposure
from pymob.utils.testing import assert_no_infs_in_dataset, assert_no_nans_in_dataset

def test_guts_constant_exposure():
    sim = GutsSimulationConstantExposure()
    sim.initialize_from_script()

    sim.dispatch_constructor()
    e = sim.dispatch(theta={})
    e()
    e.results

    assert_no_nans_in_dataset(e.results)
    assert_no_infs_in_dataset(e.results)


def test_guts_variable_exposure():
    sim = GutsSimulationVariableExposure()
    sim.initialize_from_script()

    sim.dispatch_constructor()
    e = sim.dispatch(theta={})
    e()
    e.results

    assert_no_nans_in_dataset(e.results)
    assert_no_infs_in_dataset(e.results)




if __name__ == "__main__":
    test_guts_variable_exposure()