from functools import partial
from pathlib import Path

import jax
import jax.numpy as jnp
import sympy as sp
import numpy as np
from scipy.interpolate import interp1d
from guts_base.prob import likelihood

from pymob.solvers.base import mappar
from pymob.solvers.symbolic import (
    PiecewiseSymbolicODESolver, FunctionPythonCode, get_return_arguments, dX_dt2X
)

_params_info_defaults = {
    "initial": 1.0, 
    "name": None,
    "min": None,
    "max": None,
    "prior": None,
    "dims": None,
    "vary": True,
    "module": None,
    "unit": None,
}

class RED_SD:
    """Simplest guts model, mainly for testing"""
    extra_dim = "substance"
    _likelihood_func_jax = likelihood
    _it_model = False
    _params_info_defaults = _params_info_defaults

    params_info = {
        "hb": dict(name="hb", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, unit="1/{T}", module="background-mortality"),
        "kd": dict(name="kd", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, unit="1/{T}", module="tktd"),
        "m":  dict(name="m", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, unit="{X}", module="tktd"),
        "b":  dict(name="b", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, unit="1/{T}/{X}", module="tktd"),
    }

    state_variables = {
        "exposure": dict(dimensions=["id", "time", "substance"], observed=False),
        "D": dict(dimensions=["id", "time"], observed=False, y0=[0.0]),
        "H": dict(dimensions=["id", "time"], observed=False, y0=[0.0]),
        "survival": dict(dimensions=["id", "time"], observed=True)
    }

    @staticmethod
    def _rhs_jax(t, y, x_in, kd, b, m, hb):
        D, H = y
        dD_dt = kd * (x_in.evaluate(t) - D)
        dH_dt = b * jnp.maximum(0.0, D - m) + hb
        return dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, t, interpolation):
        results["survival"] = jnp.exp(-results["H"])
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)
        return results

class RED_IT:
    """Simplest guts model, mainly for testing"""
    extra_dim = "substance"
    _likelihood_func_jax = likelihood
    _it_model = True
    _params_info_defaults = _params_info_defaults

    params_info = {
        "hb":   dict(name="hb",   min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, module="background-mortality"),
        "kd":   dict(name="kd",   min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, module="tktd"),
        "m":    dict(name="m",    min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, module="tktd"),
        "beta": dict(name="beta", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, module="tktd"),
    }

    state_variables = {
        "exposure": dict(dimensions=["id", "time", "substance"], observed=False),
        "D": dict(dimensions=["id", "time"], observed=False, y0=[0.0]),
        "H": dict(dimensions=["id", "time"], observed=False),
        "survival": dict(dimensions=["id", "time"], observed=True)
    }

    @staticmethod
    def _rhs_jax(t, y, x_in, kd):
        D, = y
        C = x_in.evaluate(t)

        dD_dt = kd * (C - D)

        return (dD_dt, )

    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        """
        TODO: Try alternative formulation. This is computationally simpler and numerically
        more stable:
        log S = log 1.0 + log (1.0 - F) + log exp -hb * t = 0 + log (1.0 - F) - hb * t
        """

        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)

        return results


class RED_SD_DA:
    """Simplest guts model, mainly for testing"""
    extra_dim = "substance"
    _likelihood_func_jax = likelihood
    _it_model = False
    _params_info_defaults = _params_info_defaults
    params_info = {}

    def __init__(self, num_expos = 1):
        for i in range(num_expos):
            self.params_info[f'kd{i+1}'] = {
                'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 
                'vary':True, "dims": "substance", "module": "tktd",
                "unit": "1/{T}"
            }
            if i == 0:
                self.params_info[f'w{i+1}'] = {
                    'name':f'w{i+1}', 'initial':1.0, 'vary':False, 
                    "dims": "substance", "module": "tktd",
                    "unit": "{X}/{X_i}",
                }
            else:
                self.params_info[f'w{i+1}'] = {
                    'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 
                    'vary':True, "dims": "substance", "module": "tktd",
                    "unit": "{X}/{X_i}"
                }

        self.params_info.update({
            "hb": dict(name="hb", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)", dims=None, unit="1/{T}", module="background-mortality"),
            "m":  dict(name="m", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)",  dims=None, unit="{X}", module="tktd"),
            "b":  dict(name="b", min=None, max=None, initial=1.0, vary=True, prior="lognorm(scale=1,s=5)",  dims=None, unit="1/{T}/{X}", module="tktd"),
        })

        self.state_variables = {
            "exposure": dict(dimensions=["id", "time", "substance"], unit="{Xi}", observed=False),
            "D": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H": dict(dimensions=["id", "time"], observed=False, y0=[0.0]),
            "survival": dict(dimensions=["id", "time"], observed=True)
        }

    @staticmethod
    def _rhs_jax(t, y, x_in, kd, w, b, m, hb):
        D, H = y
        dD_dt = kd * (x_in.evaluate(t) - D)
        dH_dt = b * jnp.maximum(0.0, jnp.sum(w * D) - m) + hb
        return dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, t, interpolation):
        results["survival"] = jnp.exp(-results["H"])
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)
        return results

class RED_SD_explicit_units(RED_SD):
    def __init__(self):
        self.params_info["hb"]["unit"] = "1/day"
        self.params_info["b"]["unit"] = "1/mg/day"
        self.params_info["kd"]["unit"] = "1/day"
        self.params_info["m"]["unit"] = "mg"

red_sd = RED_SD._rhs_jax
red_sd_post_processing = RED_SD._solver_post_processing


red_sd_da = RED_SD_DA._rhs_jax
red_sd_da_post_processing = RED_SD_DA._solver_post_processing


def guts_constant_exposure(t, y, C_0, k_d, z, b, h_b):
    # for constant exposure
    D, H, S = y
    dD_dt = k_d * (C_0 - D)
    
    switchDS = 0.5 + (1 / jnp.pi) * jnp.arctan(1e16 * (D - z))
    dH_dt = (b * switchDS * (D - z) + h_b)

    dS_dt = -dH_dt * S

    return dD_dt, dH_dt, dS_dt

def guts_variable_exposure(t, y, x_in, k_d, z, b, h_b):
    # for constant exposure
    D, H, S = y
    C = x_in.evaluate(t)
    dD_dt = k_d * (C - D)
    
    switchDS = 0.5 + (1 / jnp.pi) * jnp.arctan(1e16 * (D - z))
    dH_dt = (b * switchDS * (D - z) + h_b)

    dS_dt = -dH_dt * S

    return dD_dt, dH_dt, dS_dt


class Interpolation:
    def __init__(self, xs, ys, method="previous") -> None:
        self.f = interp1d(
            x=xs,
            y=ys,
            axis=0,
            kind=method
        )

    def evaluate(self, t) -> np.ndarray:
        return self.f(t)


class PiecewiseSymbolicSolver(PiecewiseSymbolicODESolver):
    interpolation_type = "previous"

    def t_jump(self, func_name, compiled_functions={}):
        t, Y, Y_0, theta = self.define_symbols()
        
        D_t = compiled_functions["F"]["algebraic_solutions"]["D"]
        z = theta["z"]
        eq = sp.Eq(D_t.rhs, z).expand()

        t_0 = sp.solve(eq, t)

        assert len(t_0) == 1
        func = sp.simplify(t_0[0])

        python_code = FunctionPythonCode(
            func_name=func_name,
            lhs_0=("Y_0", tuple(Y_0.keys())),
            theta=("theta", tuple(theta.keys())),
            lhs=("Y",),
            rhs=(func,),
            expand_arguments=False,
            modules=("numpy","scipy"),
            docstring=""
        )
        
        tex = self.to_latex(solutions=[sp.Eq(sp.Symbol(func_name), func)])
        code_file = Path(self.output_path, f"{func_name}.tex")
        with open(code_file, "w") as f:
            f.writelines(tex)

        return func, python_code

    def define_symbols(self):
        """Define the necessary symbols solely based on the function"""
        thetanames = mappar(
            self.model, {}, 
            exclude=["t", "dt", "y", "x_in", "Y", "X"], 
            to="names"
        )
        ynames = [dX_dt2X(a) for a in get_return_arguments(self.model)]

        # define symbols for t, Y, Y_0 and theta
        t = sp.Symbol("t", positive=True, real=True)
        Y = {y: sp.Function(y, positive=True, real=True) for y in ynames}
        Y_0 = {
            f"{y}_0": sp.Symbol(f"{y}_0", positive=True, real=True) 
            for y in ynames
        }
        theta = {p: sp.Symbol(p, positive=True, real=True) for p in thetanames}
        
        symbols = (t, Y, Y_0, theta)

        return symbols
        
    @property
    def compiler_recipe(self):
        return {
            "F":self.compile_model,
            "t_jump":self.t_jump,
            "F_piecewise":partial(self.jump_solution, funcnames="F t_jump")
        }

    def solve(self, parameters, y0, x_in):
        odeargs = mappar(
            self.model, 
            parameters, 
            exclude=["t", "dt", "y", "x_in"], 
            to="dict"
        )

        F_piecewise = self.compiled_functions["F_piecewise"]["compiled_function"]

        # get arguments
        time = np.array(self.x)
        Y_0_values = [v for v in y0.values()]

        # handle interpolation
        if "exposure" in self.coordinates_input_vars["x_in"]:
            exposure_interpolation = Interpolation(
                xs=self.coordinates_input_vars["x_in"]["exposure"][self.x_dim],
                ys=x_in["exposure"],
                method=self.interpolation_type
            )
        else:
            exposure_interpolation = Interpolation(
                xs=self.x,
                ys=np.full_like(self.x, odeargs["C_0"]), #type: ignore
                method=self.interpolation_type
            )

        # run main loop
        sol = [Y_0_values]
        for i in range(1, len(time)):
            # parse arguments
            C_0 = exposure_interpolation.evaluate(time[i-1])
            odeargs.update({"C_0": C_0}) # type: ignore
            dt = time[i] - time[i-1]

            # call piecewise function
            y_t = F_piecewise(
                t=dt, 
                Y_0=sol[i-1], 
                θ=tuple(odeargs.values()), # type: ignore
                ε=1e-14
            ) 
            
            sol.append(y_t)

        Y_t = np.array(sol)

        results = {k:y for k, y in zip(y0.keys(), Y_t.T)}
        results["exposure"] = exposure_interpolation.evaluate(np.array(self.x))

        return results