import warnings
from functools import partial
import numpy as np
import xarray as xr
from typing import Literal, Optional, Dict, List, TYPE_CHECKING, Mapping
import pandas as pd
from scipy.optimize import minimize
from matplotlib import pyplot as plt
from tqdm import tqdm

from pymob import SimulationBase
from pymob.sim.config import NumericArray
from guts_base.sim.utils import GutsBaseError

if TYPE_CHECKING:
    from guts_base.sim import GutsBase

class ECxEstimator:
    """Estimates the exposure level that corresponds to a given effect. The algorithm 
    operates by varying a given exposure profile (x_in). For each new estimation, a new
    estimator is initialized.

    Parameters
    ----------

    sim : SimulationBase
        This must be a pymob.SimulationBase object. If the ECxEstimator.estimate method
        is used with the modes 'draw' or 'mean'    
    
    effect : str
        The data variable for which the effect concentration is computed. This is one
        of sim.observations and sim.results

    x : float
        Effect level. This is the level of the effect, for which the concentration is 
        computed.

    time : float
        Time at which the ECx is computed

    x_in : xr.Dataset
        The model input 'x_in' for which the effect is computed.
    
    conditionals_posterior : Dict
        Dictionary that overwrites values in the posterior. This is useful if for instance
        background mortality should be set to a fixed value (e.g. zero). Consequently this
        setting does not take effect in estimation mode 'manual' but only for mean and 
        draws. Defaults to an empty dict (no conditions applied).
    """
    _name = "EC"
    _parameter_msg = (
        "Manual estimation (mode='manual', without using posterior information) requires " +
        "specification of parameters={...}. You can obtain and modify " +
        "parameters using the pymob API: `sim.config.model_parameters.value_dict` " +
        "returns a dictionary of DEFAULT PARAMETERS that you can customize to your liking " +
        "(https://pymob.readthedocs.io/en/stable/api/pymob.sim.html#pymob.sim.config.Modelparameters.value_dict)."
    )                

    def __init__(
        self, 
        sim: "GutsBase", 
        effect: str, 
        x: float,
        time: float, 
        x_in: xr.Dataset, 
        conditions_posterior: Dict[str, float] = {}
    ):
        self.sim = sim.copy()
        self.time = time
        self.x = x
        self.effect = effect
        self._mode = None
        self._conditions_posterior = conditions_posterior

        # creates an empty observation dataset with the coordinates of the
        # original observations (especially time), except the ID, which is overwritten
        # and taken from the x_in dataset
        pseudo_obs = self.sim.observations.isel(id=[0])
        pseudo_obs = pseudo_obs.drop([v for v in pseudo_obs.data_vars.keys()])
        pseudo_obs["id"] = x_in["id"]
        
        self.sim.config.data_structure.survival.observed = False
        self.sim.observations = pseudo_obs

        # overwrite x_in to make sure that parse_input takes x_in from exposure and
        # does not use the string that is tied to another data variable which was
        # originally present
        self.sim.config.simulation.x_in = ["exposure=exposure"]

        # ensure correct coordinate order with x_in and raise errors early
        self.sim.model_parameters["x_in"] = self.sim.parse_input("x_in", x_in)


        # fix time after observations have been set. The outcome of the simulation
        # can dependend on the time vector, because in e.g. IT models, the time resolution
        # is important. Therefore the time at which the ECx is computed is just inserted
        # into the time vector at the right position.
        self.sim.coordinates["time"] = np.unique(np.concatenate([
            self.sim.coordinates["time"], np.array(time, ndmin=1)
        ]))

        self.sim.model_parameters["y0"] = self.sim.parse_input("y0", drop_dims=["time"])
        self.sim.dispatch_constructor()

        self.results: pd.Series[float|str] = pd.Series({
            "mean": np.nan,
            "q05": np.nan,
            "q95": np.nan,
            "std": np.nan,
            "cv": np.nan,
            "msg": None
        })

        self.figure_profile_and_effect = None
        self.figure_loss_curve = None

        self.condition_posterior_parameters(conditions=conditions_posterior)

    def _assert_posterior(self):
        try:
            p = self.sim.inferer.idata.posterior
        except AttributeError:
            raise GutsBaseError(
                "Using mode='mode' or mode='draws', but sim did not contain a posterior. " + 
                "('sim.inferer.idata.posterior'). " + self._parameter_msg
            )

    def condition_posterior_parameters(self, conditions: Dict[str, float]):
        for parameter, value in conditions.items():
            if self.sim.config.model_parameters[parameter].free:
                self.sim.inferer.idata.posterior = self.sim._condition_posterior(
                    posterior=self.sim.inferer.idata.posterior,
                    parameter=parameter,
                    value=value,
                    exception="raise",
                )
            else:
                self.sim.config.model_parameters[parameter].value = value
                self.sim.model_parameters["parameters"] = self.sim.config.model_parameters.value_dict
                self.sim.dispatch_constructor()
    
    def _evaluate(self, factor, theta):
        evaluator = self.sim.dispatch(
            theta=theta, 
            x_in=self.sim.validate_model_input(self.sim.model_parameters["x_in"] * factor)
        )
        evaluator()
        return evaluator

    def _loss(self, log_factor, theta):
        # exponentiate the log factor
        factor = np.exp(log_factor)

        e = self._evaluate(factor, theta)
        s = e.results.sel(time=self.time)[self.effect].values

        return (s - (1 - self.x)) ** 2

    def _posterior_mean(self):
        mean = self.sim.inferer.idata.posterior.mean(("chain", "draw"))
        mean = {k: v["data"] for k, v in mean.to_dict()["data_vars"].items()}
        return mean

    def _posterior_sample(self, i):
        posterior_stacked = self.sim.inferer.idata.posterior.stack(
            sample=("chain", "draw")
        )
        sample = posterior_stacked.isel(sample=i)
        sample = {k: v["data"] for k, v in sample.to_dict()["data_vars"].items()}
        return sample

    def plot_loss_curve(self, 
        mode: Literal["draws", "mean", "manual"] = "draws", 
        draws: Optional[int] = None, 
        parameters: Optional[Mapping[str,float|List[float]|NumericArray]] = None,
        log_x0: float = 0.0, 
        log_interval_radius: float = 2.0,
        log_interval_num: int = 100,
        force_draws: bool = False
    ):
        """
        Parameters
        ----------

        mode : Literal['draws', 'mean', 'manual']
            mode of estimation. mode='mean' takes the mean of the posterior and estimate
            the ECx for this singular value. mode='draws' takes samples from the posterior
            and estimate the ECx for each of the parameter draws. mode='manual' takes
            a parameter set (Dict) in the parameters argument and uses that for estimation. 
            Default: 'draws'
        
        draws : int
            Number of draws to take from the posterior. Only takes effect if mode='draw'.
            Raises an exception if draws < 100, because this is insufficient for a 
            reasonable uncertainty estimate. Default: None (using all samples from the
            posterior)
        
        parameters : Dict[str,float|list[float]]
            a parameter dictionary passed used as model parameters for finding the ECx
            value. Default: None

        log_x0 : float
            the starting value for the multiplication factor of the exposure profile for
            the minimization algorithm. This value is on the log scale. This means, 
            exp(log_x0=0.0) = 1.0, which means that the log_x0=0.0 will start at an
            unmodified exposure profile. Default: 0.0
        
        log_interval_radius : float
            the radius of the interval around the starting value log_x0, within which the
            loss function is evaluated. For example, log_interval_radius=2.0 will evaluate
            the loss function at log_factor values ranging from log_x0 - 2.0 to log_x0 + 2.0.
            Default: 2.0

        log_interval_num : int
            the number of points at which the loss function is evaluated within the interval
            defined by log_x0 and log_interval_radius. For example, log_interval_num=100 will
            evaluate the loss function at 100 evenly spaced points between log_x0 - log_interval_radius
            and log_x0 + log_interval_radius. Default: 100

        force_draws : bool
            Force the estimate method to accept a number of draws less than 100. Default: False

        """
        draws = self._check_mode_and_draws_and_parameters(mode, draws, parameters, force_draws)


        factor = np.linspace(-log_interval_radius, log_interval_radius, log_interval_num) + log_x0
        fig, ax = plt.subplots(1,1, sharey=True, figsize=(4, 3))
        
        X_lowest = []

        for i in tqdm(range(draws)):
            if mode == "draws":
                sample = self._posterior_sample(i)
            elif mode == "mean":
                sample = self._posterior_mean()
            elif mode == "manual":
                sample = parameters
            else: 
                raise NotImplementedError(
                    f"Bad mode: {mode}. Mode must be one 'mean' or 'draws'"
                )
            
            y = list(map(partial(self._loss, theta=sample), factor))

            x_lowest = factor[np.array(y).argmin()]
            X_lowest.append(x_lowest)

            ax.plot(
                np.exp(factor), y, 
                color="black",
            )

        self.ecx_candidates = X_lowest

        ax.plot(
            [], [], color="black",
            label=f"$\ell = S(t={self.time},x_{{in}}=C_{{ext}} \cdot \phi) - {self.x}$"
        )
        ax.set_ylabel("Loss ($\ell$)")
        ax.set_xlabel("Multiplication factor ($\phi$)")
        ax.set_title(f"ID: {self.sim.coordinates['id'][0]}")
        ax.set_ylim(0, ax.get_ylim()[1] * 1.25)
        ax.set_xscale("log")
        ax.legend(frameon=False)
        fig.tight_layout()

        self.figure_loss_curve = fig

    def _check_mode_and_draws_and_parameters(self, mode, draws, parameters, force_draws):

        if mode == "draws":
            self._assert_posterior()

            if draws is None:
                draws = (
                    self.sim.inferer.idata.posterior.sizes["chain"] * 
                    self.sim.inferer.idata.posterior.sizes["draw"]
                )
            elif draws < 100 and not force_draws:
                raise GutsBaseError(
                    "draws must be larger than 100. Preferably > 1000. " +
                    f"If you don't want uncertainty assessment of the {self._name} " +
                    "estimates, use mode='mean'. If you really want to use less than " +
                    "100 draws, use force_draws=True at your own risk."
                )
            else:
                pass
            
            if parameters is not None:
                warnings.warn(
                    "Values passed to 'parameters' don't have an effect in mode='draws'"
                )

        elif mode == "mean":
            self._assert_posterior()

            draws = 1

            if parameters is not None:
                warnings.warn(
                    "Values passed to 'parameters' don't have an effect in mode='draws'"
                )

        elif mode == "manual":
            draws = 1
            if parameters is None:
                raise GutsBaseError(self._parameter_msg)
            
            if self._conditions_posterior is not None:
                warnings.warn(
                    "Conditions applied to the posterior do not take effect in mode 'manual'"
                )

        else:
            raise GutsBaseError(
                f"Bad mode: {mode}. Mode must be one 'mean' or 'draws'"
            )

        return draws


    def estimate(
        self, 
        mode: Literal["draws", "mean", "manual"] = "draws", 
        draws: Optional[int] = None, 
        parameters: Optional[Mapping[str,float|List[float]|NumericArray]] = None,
        log_x0: float = 0.0, 
        x0_retries: List[float] = [0.0, -1.0, 1.0, -2.0, 2.0],
        accept_tol: float = 1e-5, 
        optimizer_tol: float = 1e-5,
        method: str = "cobyla", 
        show_plot: bool = True,
        force_draws: bool = False,
        **optimizer_kwargs
    ):
        """The minimizer for the EC_x operates on the unbounded linear scale, estimating 
        the log-modification factor. Converted to the linear scale by factor=exp(x), the 
        profile modification factor is obtained.

        Using x0=0.0 means optimization will start on the linear scale at the unmodified 
        exposure profile. Using the log scale for optimization will provide much smoother
        optimization performance because multiplicative steps on the log scale require 
        much less adaptation.

        Parameters
        ----------

        mode : Literal['draws', 'mean', 'manual']
            mode of estimation. mode='mean' takes the mean of the posterior and estimate
            the ECx for this singular value. mode='draws' takes samples from the posterior
            and estimate the ECx for each of the parameter draws. mode='manual' takes
            a parameter set (Dict) in the parameters argument and uses that for estimation. 
            Default: 'draws'
        
        draws : int
            Number of draws to take from the posterior. Only takes effect if mode='draw'.
            Raises an exception if draws < 100, because this is insufficient for a 
            reasonable uncertainty estimate. Default: None (using all samples from the
            posterior)
        
        parameters : Dict[str,float|list[float]]
            a parameter dictionary passed used as model parameters for finding the ECx
            value. Default: None

        log_x0 : float
            the starting value for the multiplication factor of the exposure profile for
            the minimization algorithm. This value is on the log scale. This means, 
            exp(log_x0=0.0) = 1.0, which means that the log_x0=0.0 will start at an
            unmodified exposure profile. Default: 0.0
        
        x0_retries : List[int]
            a list of values to use as starting points for the minimization algorithm if 
            the initial optimization attempt does not converge. The values are added to 
            log_x0. For example, if log_x0=0.0 and x0_retries=[-1.0, 1.0], the minimization 
            algorithm will first try to start at exp(0.0), then at exp(-1.0) and finally 
            at exp(1.0) if the previous attempts do not converge. Default: [0.0, -1.0, 1.0, -2.0, 2.0]
        
        accept_tol : float
            After optimization is finished, accept_tol is used to assess if the loss
            function for the individual draws exceed a tolerance. These results are
            discarded and a warning is emitted. This is to assert that no faulty optimization
            results enter the estimate. Default: 1e-5
        
        optimizer_tol : float
            Tolerance limit for the minimzer to stop optimization. Default 1e-5

        method : str
            Minization algorithm. See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
            Default: 'cobyla'

        show_plot : bool
            Show the results plot of the lpx. Default: True
        
        force_draws : bool
            Force the estimate method to accept a number of draws less than 100. Default: False

        optimizer_kwargs :
            Additional arguments to pass to the optimizer

        """
        x0_tries = np.array(x0_retries) + log_x0
        draws = self._check_mode_and_draws_and_parameters(mode, draws, parameters, force_draws)

        self._mode = mode
        mult_factor = []
        loss = []
        iterations = []
        for i in tqdm(range(draws)):
            if mode == "draws":
                sample = self._posterior_sample(i)
            elif mode == "mean":
                sample = self._posterior_mean()
            elif mode == "manual":
                sample = parameters
            else: 
                raise NotImplementedError(
                    f"Bad mode: {mode}. Mode must be one 'mean' or 'draws'"
                )

            success = False
            iteration = 0
            while not success and iteration < len(x0_tries):
                opt_res = minimize(
                    self._loss, x0=x0_tries[iteration], 
                    method=method,
                    tol=optimizer_tol,
                    args=(sample,),
                    **optimizer_kwargs
                ) 

                success = opt_res.fun < accept_tol
                iteration += 1

            # convert to linear scale from log scale
            factor = np.exp(opt_res.x)

            mult_factor.extend(factor)
            iterations.append(iteration)
            loss.append(opt_res.fun)

        res_full = pd.DataFrame(dict(factor = mult_factor, loss=loss, retries=iterations))
        self.results_full = res_full

        metric = "{name}_{x}".format(name=self._name, x=int(self.x * 100),)

        successes = sum(res_full.loss < accept_tol)
        if successes < draws:
            warnings.warn(
                f"Not all optimizations converged on the {metric} ({successes/draws*100}%). " +
                "Adjust starting values and method")
            print(res_full)

        short_msg = f"Estimation success rate: {successes/draws*100}%"
        self.results["msg"] = short_msg
        
        res = res_full.loc[res_full.loss < accept_tol,:]

        if len(res) == 0:
            self.msg = (
                f"{metric} could not be found. Two reasons typically cause this problem: "+
                f"1) no expoure before the time at which the {metric} is calculated. "+
                "Check the the exposure profile. " + 
                f"2) Too high background mortality. If the time at which the {metric} is "+
                f"calculated is large and background mortality is high, the {metric}, " +
                "may be reached independent of the effect and optimization cannot succeed."
            )

            print(self.msg)
            return

        self.results["mean"] = float(np.round(np.mean(np.array(res.factor.values)), 4))
        self.results["q05"] = float(np.round(np.quantile(np.array(res.factor.values), 0.05), 4))
        self.results["q95"] = float(np.round(np.quantile(np.array(res.factor.values), 0.95), 4))
        self.results["std"] = float(np.round(np.std(np.array(res.factor.values)), 4))
        self.results["cv"] = float(np.round(np.std(np.array(res.factor.values))/np.mean(np.array(res.factor.values)), 2))

        if show_plot:
            self.plot_profile_and_effect(parameters=parameters)

        print("{name}_{x}".format(name=self._name, x=int(self.x * 100),))
        print(self.results)
        print("\n")

    def plot_profile_and_effect(
        self,
        parameters: Optional[Mapping[str,float|List[float]|NumericArray]] = None
    ):
        coordinates_backup = self.sim.coordinates["time"].copy()

        self.sim.coordinates["time"] = np.linspace(0, self.time, 100)
        self.sim.dispatch_constructor()

        if self._mode is None:
            raise GutsBaseError(
                "Run .estimate() before plot_profile_and_effect()"
            )
        elif self._mode == "mean" or self._mode == "draws":
            e_new = self._evaluate(factor=self.results["mean"], theta=self._posterior_mean())
            e_old = self._evaluate(factor=1.0, theta=self._posterior_mean())
        elif self._mode == "manual":
            if parameters is None:
                raise RuntimeError(
                    f"If {self._name}_x was estimated using manual mode, parameters must "+
                    "also be provided here."
                )
            e_new = self._evaluate(factor=self.results["mean"], theta=parameters)
            e_old = self._evaluate(factor=1.0, theta=parameters)
    
        extra_dim = [k for k in list(e_old.results.coords.keys()) if k not in ["time", "id"]]

        if len(extra_dim) > 0:
            labels_old = [
                f"{l} (original)" for l 
                in e_old.results.coords[extra_dim[0]].values
            ]
            labels_new = [
                f"{l} (modified)" for l 
                in e_new.results.coords[extra_dim[0]].values
            ]
        else:
            labels_old = "original"
            labels_new = "modified"



        fig, (ax1, ax2) = plt.subplots(2,1, height_ratios=[1,3], sharex=True)
        ax1.plot(
            e_old.results.time, e_old.results.exposure.isel(id=0), 
            ls="--", label=labels_old,
        )
        ax1.set_prop_cycle(None)
        ax1.plot(
            e_new.results.time, e_new.results.exposure.isel(id=0), 
            label=labels_new
        )


        ax2.plot(
            e_new.results.time, e_new.results.survival.isel(id=0), 
            color="black", ls="--", label="modified"
        )
        ax1.set_prop_cycle(None)

        ax2.plot(
            e_old.results.time, e_old.results.survival.isel(id=0), 
            color="black", ls="-", label="original"
        )
        ax2.hlines(self.x, e_new.results.time[0], self.time, color="grey")
        ax1.set_ylabel("Exposure")
        ax2.set_ylabel("Survival")
        ax2.set_xlabel("Time")
        ax1.legend()
        ax2.legend()
        ax2.set_xlim(0, None)
        ax1.set_ylim(0, None)
        ax2.set_ylim(0, None)
        fig.tight_layout()

        self.figure_profile_and_effect = fig

        self.sim.coordinates["time"] = coordinates_backup
        self.sim.dispatch_constructor()

    

class LPxEstimator(ECxEstimator):
    """
    the LPx is computed, using the existing exposure profile for 
    the specified ID and estimating the multiplication factor for the profile that results
    in an effect of X %
    """
    _name = "LP"

    def __init__(
        self, 
        sim: "GutsBase", 
        id: str,
        x: float=0.5
    ):
        x_in = sim.model_parameters["x_in"].sel(id=[id])
        time = sim.coordinates["time"][-1]
        super().__init__(
            sim=sim, 
            effect="survival", 
            x=x, 
            time=time, 
            x_in=x_in
        )