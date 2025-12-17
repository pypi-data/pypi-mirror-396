import numpy as np
import pytest
from guts_base.sim import GutsSimulationVariableExposure, GutsSimulationConstantExposure

@pytest.mark.slow
def test_guts_constant_exposure_with_symbolic():
    pytest.skip()
    sim = GutsSimulationConstantExposure()
    sim.initialize_from_script()

    sim.use_jax_solver()
    sim.dispatch_constructor(rtol=1e-7, atol=1e-8)
    evaluator = sim.dispatch(theta={})
    evaluator()
    
    sol_numerical = evaluator.results


    sim.use_symbolic_solver()
    evaluator = sim.dispatch(theta={})
    evaluator()

    sol_symbolic = evaluator.results

    diff = (
        sol_numerical.sel(time=[0, 180])
        - sol_symbolic.sel(time=[0, 180])
    )

    max_delta = np.abs(diff).max().to_array()
    np.testing.assert_array_less(max_delta, [1e-2, 1e-2, 1e-2])

    
@pytest.mark.slow
def test_guts_variable_exposure_with_symbolic():
    pytest.skip()
    sim = GutsSimulationVariableExposure()
    sim.initialize_from_script()

    sim.use_symbolic_solver(do_compile=True)
    evaluator = sim.dispatch(theta={})
    evaluator()
    sol_symbolic = evaluator.results

    sim.use_jax_solver()
    sim.dispatch_constructor(rtol=1e-7, atol=1e-8)
    evaluator = sim.dispatch(theta={})
    evaluator()
    sol_numerical = evaluator.results

    # make sure errors are small between exact solution and numerical solution
    # the errors come from:
    # a) integrating not exactly to t_eq
    # b) using a numerical switch in the ODE solution.
    diff = (
        sol_numerical.sel(time=np.arange(0,sim.t_max))
        - sol_symbolic.sel(time=np.arange(0,sim.t_max))
    )[["D", "H", "S"]]
    max_delta = np.abs(diff).max().to_array()
    np.testing.assert_array_less(max_delta, [5e-2, 5e-2, 5e-2])

    axes = sim._plot.plot_multiexposure(sol_numerical, vars=["exposure", "D", "H", "S"], color="tab:blue", label_prefix="ODE")
    axes = sim._plot.plot_multiexposure(sol_symbolic, vars=["exposure", "D", "H", "S"], axes=axes, color="tab:red", linestyle="--", label_prefix="exact")
    fig = axes[0].figure
    fig.savefig(f"{sim.output_path}/solution_comparison.png")


@pytest.mark.slow
def test_guts_variable_exposure_compiled():
    pytest.skip()
    sim = GutsSimulationVariableExposure()
    sim.initialize_from_script()

    sim.use_symbolic_solver(do_compile=False)
    evaluator = sim.dispatch(theta={})
    evaluator()
    sol_symbolic = evaluator.results

    sim.use_jax_solver()
    sim.dispatch_constructor(rtol=1e-7, atol=1e-8)
    evaluator = sim.dispatch(theta={})
    evaluator()
    sol_numerical = evaluator.results

    # make sure errors are small between exact solution and numerical solution
    # the errors come from:
    # a) integrating not exactly to t_eq
    # b) using a numerical switch in the ODE solution.
    diff = (
        sol_numerical.sel(time=np.arange(0,sim.t_max))
        - sol_symbolic.sel(time=np.arange(0,sim.t_max))
    )[["D", "H", "S"]]
    max_delta = np.abs(diff).max().to_array()
    np.testing.assert_array_less(max_delta, [5e-2, 5e-2, 5e-2])
