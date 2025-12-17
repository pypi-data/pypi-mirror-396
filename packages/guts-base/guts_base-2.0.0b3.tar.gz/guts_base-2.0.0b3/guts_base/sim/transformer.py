"""Transformer utilities for GUTS base simulations.

Provides classes to transform parameter and result units, and functions to apply these
transformations to InferenceData objects.
"""
from typing import Dict, Tuple, List, Any, Type
from dataclasses import dataclass, field
from guts_base.sim.utils import GutsBaseError
import numpy as np
import xarray as xr
from pymob.sim.config import Modelparameters
from pymob import SimulationBase

@dataclass
class TransformBase:
    """Base class for transformation utilities.

    Attributes
    ----------
    ignore_keys : Tuple
        Keys that should be ignored during transformation.

    Methods
    -------
    _transform_value(key, value, func_template)
        Apply a specific transformation function to a given value.
    _transform_dataset(x, func_template)
        Transform all data variables in an xarray.Dataset.
    _transform_dict(x, func_template)
        Transform all items in a dictionary.
    _transform_modelparameters(x, func_template)
        Transform model parameter values in a Modelparameters instance.
    _transform(x, func_template)
        Dispatch transformation based on input type.
    transform(x)
        Transform using the default function template.
    transform_inv(x)
        Inverse transformation using the ``*_inv`` function template.
    """
    ignore_keys: Tuple = ()

    def _transform_value(self, key, value, func_template):
        # skips transform if apply_transform is false. This basically ensures that
        # the default NoTransform will not do anything and also not raise a warning
        if key in self.ignore_keys:
            return value
        
        # does not transform if the key was not found
        if hasattr(self, key):
            func = getattr(self, func_template.format(key=key))
            return func(value) 
        else:
            raise GutsBaseError(
                f"'{key}' was not found in '{type(self).__name__}'. All values "+
                "must have an associated transform function or be explicitly excluded. "+
                f"If necessary, define a transform method in '{type(self).__name__}' "+
                f"named '{key}' to transform it:\n" +
                f">>> {type(self).__name__}.{key} = lambda self, x: ... \nAlternatively, "+
                f"use `{type(self).__name__}(..., ignore_keys=[..., '{key}'])` to "+ 
                "suppress this error"
            )
            
    def _transform_dataset(self, x: xr.Dataset, func_template: str) -> xr.Dataset:
        x_transformed = xr.Dataset({
            key: self._transform_value(key, value, func_template)
            for key, value in x.data_vars.items()
        })
        x_transformed.attrs = x.attrs
        return x_transformed

    def _transform_dict(self, x: Dict, func_template: str) -> Dict:
        x_transformed = {
            key: self._transform_value(key, value, func_template)
            for key, value in x.items()
        }
        return x_transformed
    
    def _transform_modelparameters(self, x: Modelparameters, func_template: str) -> Modelparameters:
        """Transform model parameter values of a ``Modelparameters`` instance.

        The method dumps the Modelparameters object and updates each parameter's ``value``
        in the dumpled dict using the appropriate
        transformation function and returns the a newly validated ``Modelparameters`` object.

        Parameters
        ----------
        x : Modelparameters
            The model parameters container whose values will be transformed.
        func_template : str
            Template string used to locate the correct transformation method.

        Returns
        -------
        Modelparameters
            A new ``Modelparameters`` instance after transformation and validation.
        """
        model_parameters = x.model_dump(mode="python")

        for key, param_dict in model_parameters.items():
            transformed_value = self._transform_value(
                key, param_dict["value"], func_template
            )
            param_dict.update({"value": transformed_value})

        # return a validated model parameters dict with updated values
        # this is no in-place transform any longer
        return Modelparameters.model_validate(model_parameters)
    

    def _transform(self, x: xr.Dataset|Dict|Modelparameters, func_template: str) -> xr.Dataset|Dict|Modelparameters:
        if isinstance(x, dict):
            x_transformed = self._transform_dict(x, func_template)

        elif isinstance(x, Modelparameters):
            x_transformed = self._transform_modelparameters(x, func_template)

        elif isinstance(x, xr.Dataset):
            x_transformed = self._transform_dataset(x, func_template)
        else:
            raise NotImplementedError(
                "Use one of dict or xr.Dataset"
            )

        return x_transformed

    def transform(self, x: Any) -> Any:
        """Transform the provided object using the appropriate per-key function.

        The method accepts an ``xarray.Dataset``, a ``dict`` of values, or a
        ``Modelparameters`` instance. The actual transformation is delegated to
        :meth:`_transform`, which dispatches based on the object's type.
        """
        return self._transform(x, func_template="{key}")

    def transform_inv(self, x: Any) -> Any:
        """Inverse transform the provided object using the appropriate per-key
        function.

        Mirrors :meth:`transform` but uses the ``*_inv`` variants of the
        transformation methods.
        """
        return self._transform(x, func_template="{key}_inv")
    

@dataclass
class ParameterTransform(TransformBase):
    """Contains methods that define the transformation for each parameter. Coefficients
    for storing the required transformations are defined as class attributes
    """
    
    def _test_transform_consistency(self, x: Modelparameters):
        _roundtrip_x = self.transform(self.transform_inv(x))
        for key in x.all.keys():
            np.testing.assert_array_almost_equal(
                np.array(x[key].value),
                np.array(_roundtrip_x[key].value)
            )



@dataclass 
class DataTransform(TransformBase):
    def _transform_dataset(self, x: xr.Dataset, func_template):
        x_transformed = super()._transform_dataset(x, func_template)
        if hasattr(x, "time"):
            x_transformed = x_transformed.assign_coords({
                "time": getattr(self, func_template.format(key="time"))(x.time)
            })

        return x_transformed

    def _test_transform_consistency(self, arr: xr.Dataset):
        np.testing.assert_array_almost_equal(
            self.transform(self.transform_inv(arr)).to_array(),
            arr.to_array(),
            decimal=4
        )



@dataclass
class GenericTransform:
    """High-level interface to transform simulation objects and associated InferenceData.



    Parameters
    ----------
    ignore_keys : List[str], optional
        Keys to ignore during transformation.

    Attributes
    ----------
    par_transformer : ParameterTransform
        Transformer for model parameters.
    obs_transformer : ResultsTransform
        Transformer for observations/results.
    is_transformed : dict
        Tracks which components have been transformed.
    """
    # USER ATTRIBUTES
    # transformer classes can be injected – defaults keep the current behaviour
    # By default the SimTransform is not transforming anything
    parameter_transformer_class: Type[ParameterTransform] = field(init=False, repr=False, default=ParameterTransform)
    data_transformer_class: Type[DataTransform] = field(init=False, repr=False, default=DataTransform)

    # keys to ignore when transforming
    ignore_keys: List[str] = field(default_factory=list)
    
    # INTERNAL ATTRIBUTES
    # internal state – created per instance
    # the fields below are initialised in __post_init__
    
    parameter_transformer: ParameterTransform = field(init=False)
    data_transformer: DataTransform = field(init=False)
    is_transformed: Dict[str, bool] = field(init=False)
    apply_transform: bool = field(init=False, default=True)

    def __post_init__(self) -> None:
        """Automatically assign the required keyword arguments to the parameter classes"""
        init_kwargs_par = {
            k: getattr(self, k) for k in 
            self.parameter_transformer_class.__dataclass_fields__.keys()
        }
        self.parameter_transformer = self.parameter_transformer_class(**init_kwargs_par)
        
        init_kwargs_obs = {
            k: getattr(self, k) for k in 
            self.data_transformer_class.__dataclass_fields__.keys()
        }
        self.data_transformer = self.data_transformer_class(**init_kwargs_obs)
        
        # set status
        self.is_transformed = {"idata": False, "observations": False, "parameters": False}

    def __repr__(self) -> str:
        """Represent the SimTransform with its current transformation state."""
        _it = [f'{k}={v}' for k, v in self.is_transformed.items()]
        return (
            f"{type(self).__name__}("
            f"\n    {', '.join(_it)}, "+
            f"\n    data_transformer={self.data_transformer}, "+
            f"\n    parameter_transformer={self.parameter_transformer}"+
            "\n)"
        )


    def _check_transform_state(self, target: str, transform: bool, inverse: bool):
        """Determine whether a transformation should be performed.

        Parameters
        ----------
        target : str
            Component name ('idata', 'observations', 'parameters').
        transform : bool
            Whether a transformation is requested.
        inverse : bool
            Whether the inverse transformation is requested.

        Returns
        -------
        tuple (bool, str)
            ``(flip_transform_status, msg)`` where ``flip_transform_status`` indicates
            if the transformation should be executed and ``msg`` contains a diagnostic
            message.
        """
        if not transform:
            msg = f"No transform requested for '{target}'."
            flip_transform_status = False
        elif self.is_transformed[target] and transform and inverse:
            msg = f"'{target}' is transformed and inverse-transforme was requested. OK: executed"
            flip_transform_status = True
        elif self.is_transformed[target] and transform and not inverse:
            msg = f"'{target}' is transformed and transform was requested. Invalid: skipped."
            flip_transform_status = False
        elif not self.is_transformed[target] and transform and inverse:
            msg = f"'{target}' is not transformed and inverse-transform was requested. Invalid: skipped."
            flip_transform_status = False
        elif not self.is_transformed[target] and transform and not inverse:
            msg = f"'{target}' is not transformed and transform was requested. OK: executed."
            flip_transform_status = True

        return flip_transform_status, msg
    
    def _update_transform_state(self, target, fts, msg):
        """Update internal transformation state and optionally print a message.

        Parameters
        ----------
        target : str
            Component name.
        fts : bool
            Whether the transformation was performed.
        msg : str
            Message to print.
        """
        if fts:
            self.is_transformed[target] = not self.is_transformed[target]
        if msg:
            print(msg)


    def _transform_idata(self, idata, inverse=False):
        """Apply parameter and data transformations to an InferenceData object.
        Needs to be in the transform sim, because it needs both parameter transformer
        and data transformer.

        Parameters
        ----------
        idata : InferenceData
            The arviz InferenceData to transform.
        inverse : bool, optional
            If ``True``, apply the inverse transformation. Default is ``False``.
        """
        if inverse:
            transform_params = self.parameter_transformer.transform_inv
            transform_data = self.data_transformer.transform_inv
        else:
            transform_params = self.parameter_transformer.transform
            transform_data = self.data_transformer.transform


        # this makes sure that idata is not edited inplace 
        groups = {
            "posterior": transform_params(idata.posterior),
            "posterior_model_fits": transform_data(idata.posterior_model_fits),
            "posterior_predictive": transform_data(idata.posterior_predictive),
            "observed_data": transform_data(idata.observed_data),
            "log_likelihood": idata.log_likelihood.assign_coords(
                transform_data({"time": idata.log_likelihood.coords["time"]})
            )
        }

        # transform parameters
        idata.posterior = groups["posterior"]
        # transform results
        idata.posterior_model_fits = groups["posterior_model_fits"]
        idata.posterior_predictive = groups["posterior_predictive"]
        idata.observed_data = groups["observed_data"]
        idata.log_likelihood = groups["log_likelihood"]

        # remove unconstrained_posterior, because it cannot be transformed,
        # therefore it also shouldn't be part of idata
        del idata["unconstrained_posterior"]

    def transform(
        self, 
        sim: SimulationBase, 
        inverse: bool = False, 
        idata: bool = True, 
        observations: bool = True, 
        parameters=True
    ) -> None:
        """Transform simulation data and/or parameters.

        Parameters
        ----------
        sim : object
            Simulation instance containing ``inferer``, ``config``, and ``observations``.
        inverse : bool, optional
            Apply inverse transformation if ``True``.
        idata : bool, optional
            Transform the InferenceData in ``sim.inferer``.
        observations : bool, optional
            Transform ``sim.observations``.
        parameters : bool, optional
            Transform model parameters in ``sim.config``.
        """

        # simply exit without applying any changes if apply transform is False
        if not self.apply_transform:
            return

        # transform idata
        fts, msg = self._check_transform_state(target="idata", transform=idata, inverse=inverse)
        if fts:
            if not hasattr(sim, "inferer"):
                pass

            else:
                if not hasattr(sim.inferer, "idata"):
                    pass
                else:
                    self._transform_idata(
                        idata=sim.inferer.idata, 
                        inverse=inverse
                    )
        
        self._update_transform_state(target="idata", fts=fts, msg=msg)


        fts, msg = self._check_transform_state(target="parameters", transform=parameters, inverse=inverse)
        if fts:
            if inverse:
                sim.config.model_parameters = self.parameter_transformer.transform_inv(
                    sim.config.model_parameters
                )
            else:
                sim.config.model_parameters = self.parameter_transformer.transform(
                    sim.config.model_parameters
                )
                
        self._update_transform_state(target="parameters", fts=fts, msg=msg)

        
        fts, msg = self._check_transform_state(target="observations", transform=observations, inverse=inverse)
        if fts:
            if inverse:
                sim.observations = self.data_transformer.transform_inv(sim.observations)
            else:
                sim.observations = self.data_transformer.transform(sim.observations)

        self._update_transform_state(target="observations", fts=fts, msg=msg)



@dataclass(repr=False)
class NoTransform(GenericTransform):
    data_transformer_class: Type[DataTransform] = DataTransform
    parameter_transformer_class: Type[ParameterTransform] = ParameterTransform
    # update apply_transform field to not apply transforms. This is critical
    # for the NoTransform Class, but will default to True in any other classese
    # inheriting from GenericTransform
    apply_transform: bool = field(init=False, default=False)




@dataclass(repr=False)
class GutsDataTransform(DataTransform):
    """Transformer for GUTS Model datasets. If additional data variables are recorded in the
    observations, these must be in a subclass of GutsRedDataTransform, otherwise they will
    not be transformed.

    Can transform
    RED_SD, RED_IT
    BufferGUTS_SD, BufferGUTS_IT

    """
    x_in_factor: float = 1.0
    time_factor: float = 1.0

    def exposure(self, x):
        return x / self.x_in_factor
    
    def exposure_inv(self, x):
        return x * self.x_in_factor

    def D(self, x):
        return x / self.x_in_factor
    
    def D_inv(self, x):
        return x * self.x_in_factor

    def B(self, x):
        return x / self.x_in_factor
    
    def B_inv(self, x):
        return x * self.x_in_factor

    def H(self, x):
        return x
    
    def H_inv(self, x):
        return x

    def survival(self, x):
        return x
    
    def survival_inv(self, x):
        return x
    
    def time(self, x):
        return x / self.time_factor

    def time_inv(self, x):
        return x * self.time_factor
    


@dataclass
class GutsParameterTransform(ParameterTransform):
    """Transformer for model parameters.

    Scales time-related parameters by ``time_factor`` and concentration-related
    parameters by ``x_in_factor``.
    """
    time_factor: float = 1.0
    x_in_factor: float = 1.0

    # in some beautiful future world. These transformation can be automatized based
    # on the ODE system and the input and output quantities.
    # generally parameter units can be parsed
    def hb(self, x):
        return x * self.time_factor

    def hb_inv(self, x):
        return x / self.time_factor

    def kd(self, x):
        return x * self.time_factor    

    def kd_inv(self, x):
        return x / self.time_factor    

    def m(self, x):
        return x / self.x_in_factor    

    def m_inv(self, x):
        return x * self.x_in_factor    

    def b(self, x):
        return x * self.x_in_factor * self.time_factor

    def b_inv(self, x):
        return x / self.x_in_factor / self.time_factor

    def beta(self, x):
        """beta is scale invariant"""
        return x
    
    def beta_inv(self, x):
        return x
    
    def w(self, x):
        return x
    
    def w_inv(self, x):
        return x

    def eps(self, x):
        """eps is a small value added to D in the computation of the IT model
        Scaling it is required, so that extremely small exposures (leading to small
        damages, do not get disproportionally large by adding small eps values)
        """
        return x / self.x_in_factor

    def eps_inv(self, x):
        return x * self.x_in_factor

@dataclass(repr=False)
class GutsTransform(GenericTransform):
    # the transformation classes
    data_transformer_class: Type[DataTransform] = GutsDataTransform
    parameter_transformer_class: Type[ParameterTransform] = GutsParameterTransform

    # Necessary coefficients for performing the transformation default values of 1.0 
    # will result in no applied transform. The true values will be passed during 
    # initialization (see example.py)
    time_factor: float = 1.0
    x_in_factor: float = 1.0