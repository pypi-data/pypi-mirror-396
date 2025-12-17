import pathlib
from typing import Dict, Optional, Literal, Protocol, TypedDict, List, Tuple, Mapping
import re
import os
import numpy as np
from numpy.ma.core import MaskedConstant
import pandas as pd
import xarray as xr
from pymob.sim.config import Config, DataVariable, Datastructure
from pymob.sim.config import Param
from guts_base.sim import GutsBase

__all__ = [
    "PymobSimulator",
]

class ParamsInfoDict(TypedDict):
    name: str
    min: float
    max: float
    initial: float
    vary: bool
    prior: str
    dims: Tuple[str]
    unit: str|List[str]
    module: str

class StateVariablesDict(TypedDict):
    dimensions: List[str]
    observed: bool
    y0: List[float]

class Model(Protocol):
    extra_dim: str
    params_info: Dict[str, ParamsInfoDict]
    state_variables: Dict[str, StateVariablesDict]
    _params_info_defaults: Dict[str, ParamsInfoDict]
    _it_model: bool

    @staticmethod
    def _rhs_jax():
        raise NotImplementedError
        
    @staticmethod
    def _solver_post_processing():
        raise NotImplementedError

    @staticmethod
    def _likelihood_func_jax():
        raise NotImplementedError


class PymobSimulator(GutsBase):

    @classmethod
    def from_model_and_dataset(
        cls,
        model: Model,
        exposure_data: Dict[str, pd.DataFrame],
        survival_data: pd.DataFrame,
        info_dict: Dict = {},
        pymob_config: Optional[Config] = None,
        output_directory: str|pathlib.Path = pathlib.Path("output/pymob"),
        default_prior: Literal["uniform", "lognorm"] = "lognorm",
    ) -> GutsBase:
        """Construct a GutsBase simulation from a model instance and datasets.

        Example
        -------

        >>> from mempy.model import RED_SD
        >>> from guts_base import Constructor

        We start by simulating some data.
        
        >>> experiment = Constructor.draft_laboratory_experiment(
        ...     treatments={"C": 0.0, "T1": 1, "T2": 5, "T3": 50, "T4": 100},
        ...     simulate_survival=True,
        ...     experiment_end=pd.Timedelta("3 days")
        ... )
        
        >>> survival_data = experiment.survival.to_pandas().T
        >>> survival_data

        >>> exposure_data = {"A": experiment.exposure.to_pandas().T}
        >>> exposure_data

        Here we created an artificial laboratory experiment with simulated survival 
        data from scratch.

        Alternatively you can use the `mempy.input_data.read_exposure_survival` tool
        to read a openguts ready .xlsx file or simply use `pandas` to parse sheets in 
        an excel file or read your openguts data in any way you want.

        >>> sim = Constructor.from_model_and_dataset(
        ...     model=RED_SD(),
        ...     exposure_data=survival,
        ...     survival_data=exposure,
        ...     output_directory="results/test"
        ... )

        `sim` is now a GutsBase instance and is ready to do inference on your problem.

        ```{note}
        See also: GutsBase
        ```

        Development Tasks
        -----------------

        TODO: Process info_dict
        """

        if pymob_config is None:
            cfg = Config()
            # Configure: The configuration can be overridden in a subclass to override the 
            # configuration
            cls._configure(config=cfg)
        else:
            cfg = pymob_config

        if isinstance(output_directory, str):
            output_directory = pathlib.Path(output_directory)

        cfg.case_study.output = str(output_directory)

        # overrides scenario path. This means the scenario is also expected in the
        # same folder
        cfg.case_study.scenario_path_override = str(output_directory)
        cfg.case_study.scenario = output_directory.stem
        cfg.case_study.data = cfg.case_study.output_path
        cfg.case_study.observations = "observations.nc"
        cfg.create_directory(directory="results", force=True)
        
        obs = cls._observations_from_dataframes(
            exposure_data=exposure_data,
            survival_data=survival_data,
            exposure_dim=model.extra_dim,
            unit_input=cfg.guts_base.unit_input,
            unit_time=cfg.guts_base.unit_time,
        )

        obs.to_netcdf(os.path.join(cfg.case_study.output_path, cfg.case_study.observations))
        

        # configure model and likelihood function
        # extract the fully qualified name of the model module.name
        if isinstance(model, type):
            raise TypeError(
                f"model '{model.__name__}' must be initialized. Initialize with "+
                f"{model.__name__}(). Dont forget to specifiy the number of exposures "+
                "with e.g. RED_SD_DA(num_expos=2) if your model has two exposures."
            )
        else:
            pass

        cfg.simulation.model_class = "{module}.{name}".format(
            module=model.__module__, name=type(model).__name__
        )
        cfg.inference_numpyro.user_defined_error_model = "{module}.{name}".format(
            module=model._likelihood_func_jax.__module__, 
            name=model._likelihood_func_jax.__name__
        )

        # derive data structure and params from the model instance
        cls._set_data_structure(config=cfg, model=model)
        cls._set_params(config=cfg, model=model, default_prior=default_prior)

        # configure starting values and input
        cfg.simulation.x_in = ["exposure=exposure"]
        cfg.simulation.y0 = [f"{k}={v['y0']}" for k, v in model.state_variables.items() if "y0" in v]

        cfg.guts_base.background_mortality_parameters = cls._get_background_mortality_params(model)

        # create a simulation object
        # It is essential that all post processing tasks are done in self.setup()
        # which is extended below. This ensures that the simulation can also be run
        # from automated tools like pymob-infer
        sim = cls(config=cfg)
        sim.setup()
        return sim


    def setup(self, **evaluator_kwargs):
        super().setup(**evaluator_kwargs)
        self._obs_backup = self.observations.copy(deep=True)


    @classmethod
    def _configure(cls, config: Config):
        """This is normally set in the configuration file passed to a SimulationBase class.
        Since the mempy to pymob converter initializes pymob.SimulationBase from scratch
        (without using a config file), the necessary settings have to be specified here.
        """
        config.case_study.output = "results"
        config.case_study.simulation = "PymobSimulator"

        # this must be named guts_base,  whihc is the name of the pip package and
        # this regulates which packages are loaded.
        config.case_study.name = "guts_base"

        config.simulation.x_dimension = "time"
        config.simulation.batch_dimension = "id"
        config.simulation.solver_post_processing = None

        # this is the registered guts-base section
        # No longer necessary, because these are saved as defaults
        # config.simulation.unit_time = "day"
        # config.simulation.n_reindexed_x = 100
        # config.simulation.forward_interpolate_exposure_data = True
        
        config.inference.extra_vars = ["eps", "survivors_before_t", "survivors_at_start"]
        config.inference.n_predictions = 100

        config.jaxsolver.diffrax_solver = "Tsit5"
        config.jaxsolver.rtol = 1e-10
        config.jaxsolver.atol = 1e-12
        config.jaxsolver.throw_exception = True
        config.jaxsolver.pcoeff = 0.3
        config.jaxsolver.icoeff = 0.3
        config.jaxsolver.dcoeff = 0.0
        config.jaxsolver.max_steps = 1000000
        config.jaxsolver.throw_exception = True


        config.inference_numpyro.gaussian_base_distribution = True
        config.inference_numpyro.kernel = "svi"
        config.inference_numpyro.init_strategy = "init_to_median"
        config.inference_numpyro.svi_iterations = 10_000
        config.inference_numpyro.svi_learning_rate = 0.001

    @classmethod
    def _set_data_structure(cls, config: Config, model: Model):
        """Takes a dictionary that is specified in the model and uses only keys that
        are fields of the DataVariable config-model"""
        
        state_dict = model.state_variables

        config.data_structure = Datastructure.model_validate({
            key: DataVariable.model_validate({
                k: v for k, v in state_info.items()
                if k in DataVariable.model_fields
            })
            for key, state_info in state_dict.items()
        })

    @staticmethod
    def _get_background_mortality_params(model: Model):
        return [k for k, v in model.params_info.items() if v["module"] == "background-mortality"]


    @classmethod
    def _set_params(cls, config: Config, model: Model, default_prior: str):
        params_info = model.params_info

        if model._it_model:
            eps = config.jaxsolver.atol * 10
            params_info["eps"] = {'name':'eps', 'initial':eps, 'vary':False}


        for par, param_dict in params_info.items():
            for k, v in model._params_info_defaults.items():
                if k not in param_dict:
                    param_dict.update({k:v})

        param_df = pd.DataFrame(params_info).T
        param_df["param_index"] = param_df.name.apply(lambda x: re.findall(r"\d+", x))
        param_df["param_index"] = param_df.param_index.apply(lambda x: int(x[0])-1 if len(x) == 1 else None)
        param_df["name"] = param_df.name.apply(lambda x: re.sub(r"\d+", "", x).strip("_"))

        for (param_name, ), group in param_df.groupby(["name"]):

            dims = list(dict.fromkeys(group["dims"]))
            dims = tuple([]) if dims == [None] else tuple(dims)

            prior = list(dict.fromkeys(group["prior"]))
            prior = prior[0] if len(prior) == 1 else prior
            
            _min = np.min(np.ma.masked_invalid(group["min"].values.astype(float)))
            _max = np.max(np.ma.masked_invalid(group["max"].values.astype(float)))
            _init = np.array(group["initial"].values.astype(float))
            _free = np.array(group["vary"].values)

            unit = list(dict.fromkeys(group["unit"]))
            unit = unit[0] if len(unit) == 1 else unit

            if isinstance(_min, MaskedConstant):
                _min = None
            if isinstance(_max, MaskedConstant):
                _max = None
            
            # TODO: allow for parsing one N-D prior from multiple priors
            # TODO: Another choice would be to parse vary=False priors as deterministic
            #       and use a composite prior from a deterministic and a free prior as
            #       the input into the model

            if prior is None:
                if _min is None or _max is None:
                    prior = None
                elif default_prior == "uniform":
                    _loc = _init * np.logical_not(_free) + _min * _free - config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _scale = _init * np.logical_not(_free) + _max * _free + config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _loc = _loc[0] if len(_loc) == 1 else _loc
                    _scale = _scale[0] if len(_scale) == 1 else _scale
                    prior = f"uniform(loc={_loc},scale={_scale})"
                elif default_prior == "lognorm":
                    _s = 3 * _free + config.jaxsolver.atol * 10 * np.logical_not(_free)
                    _init = _init[0] if len(_init) == 1 else _init
                    _s = _s[0] if len(_s) == 1 else _s

                    prior = f"lognorm(scale={_init},s={_s})"
                else:
                    raise ValueError(
                        f"Default prior: '{default_prior}' is not implemented. "+
                        "Use one of 'uniform', 'lognorm' or specify priors for each "+
                        "parameter directly with: "+
                        f"`model.params_dict['prior'] = {default_prior}(...)`"
                    )

                if prior is not None:
                    prior = prior.replace(" ", ",")

            # if isinstance(value,float):
            param = Param.model_validate(dict(
                value=_init,
                free=np.max(_free),
                min=_min,
                max=_max,
                prior=prior,
                dims=dims,
                unit=unit,
            ))

            setattr(config.model_parameters, param_name, param)

