import os
import glob
import tempfile
import warnings
import numpy as np
import xarray as xr
from diffrax import Dopri5
from typing import Any, Literal, Optional, List, Dict, Mapping, Sequence, Type, Hashable, overload
import pandas as pd

from pymob import SimulationBase
from pymob.sim.config import (
    DataVariable, Param, NumericArray, Numpyro
)

from pymob.solvers import JaxSolver
from pymob.sim.config import Config
from pymob.solvers.base import rect_interpolation
from expyDB.intervention_model import (
    Treatment, Timeseries, select, from_expydb
)


from guts_base.sim.transformer import NoTransform, GenericTransform, GutsTransform
from guts_base.sim.utils import GutsBaseError
from guts_base import mod
from guts_base.data import (
    to_dataset, reduce_multiindex_to_flat_index, create_artificial_data, 
    create_database_and_import_data_main, design_exposure_scenario, ExposureDataDict
)
from guts_base.data.generator import draft_laboratory_experiment
from guts_base.sim.report import GutsReport
from guts_base.sim import units as _units
from guts_base.sim.config import GutsBaseConfig, AllowedTimeUnits

CFG_default = Config()
CFG_numpyro_background = Numpyro(
    kernel="map", 
    svi_iterations=1000, 
    svi_learning_rate=0.01, 
    init_strategy="init_to_median",
    gaussian_base_distribution=True
)

class GutsBase(SimulationBase):
    """
    Base class for GUTS simulations.

    Attributes:
        unit_time (str): The unit of time used for simulation outputs and plots. 
            Can be one of "day", "hour", "minute", or "second". 
            Defaults to "day" if not specified in the simulation configuration.

            
    API methods
    -----------

    - `sim.estimate_parameters` TODO
    - `sim.point_estimate`
    - `sim.draft_laboratory_experiment`
    - `sim.to_openguts`: Export observations as openguts compatible .xlsx file
    - TODO: `sim.load_exposure_scenario`
    - TODO: complete list

    Important pymob methods and attributes
    --------------------------------------

    these methods are inherited from `pymob` and might be important

    - `sim.config` : Configuration of the simulation. 
    - `sim.export` : Export a simulation to disk
    - `sim.from_directory` : Import a simulation from a directory
    - TODO: complete list

    """
    solver = JaxSolver
    Report = GutsReport
    Transform: Type[GenericTransform] = NoTransform

    transformer: GenericTransform = NoTransform()


    _exclude_controls_after_fixing_background_mortality = False
    # results_interpolation: Tuple[float,float,int] = (np.nan, np.nan, 100)
    # _skip_data_processing: bool = False
    # ecx_mode: Literal["mean", "draws"] = "mean"
    # exposure_scenarios = {
    #     "acute_1day": {"start": 0.0, "end": 1.0},
    #     "chronic": {"start": 0.0, "end": None},
    # }

    def initialize(self, input: Optional[Dict] = None):
        """Initiaization goes through a couple of steps:

        1. Configuration: This makes case-study specific changes to the configuration
            file or sets state variables that are relevant for the simulation
            TODO: Ideally everything that is configurable ends up in the config so it
            can be serialized

        2. Import data: This method consists of submethods that can be adapted or 
            overwritten in subclass methods.
            - .read_data
            - .save_observations
            - .process_data
            process_data itself utilizes the submethods _create_indices and 
            _indices_to_dimensions which are empty methods by default, but can be used
            in subclasses if needed

        3. Initialize the simulation input (parameters, y0, x_in). This can 

        By splitting up the simulation init method, into these three steps, modifcations
        of the initialize method allows for higher granularity in subclasses.
        """

        # 1. Configuration
        self.configure_case_study()

        # 2. Import data
        self.observations = self.read_data()
        # FIXME: Saving observations here is not intuituve. If i export a simulation,
        # I want to use the last used state, not some obscure intermediate state
        # self.save_observations(filename="observations.nc", directory=self.output_path, force=True)
        if not self.config.guts_base.skip_data_processing:
            self.process_data()

        # 3. prepare y0 and x_in
        self.prepare_simulation_input()

    def configure_case_study(self):
        """Modify configuration file or set state variables
        """
        if self._model_class is not None:
            self.model = self._model_class._rhs_jax
            self.solver_post_processing = self._model_class._solver_post_processing

    def prepare_simulation_input(self):
        x_in = self.parse_input(input="x_in", reference_data=self.observations, drop_dims=[])
        y0 = self.parse_input(input="y0", reference_data=self.observations, drop_dims=["time"])
        
        # add model components
        if self.config.guts_base.forward_interpolate_exposure_data: # type: ignore
            self.model_parameters["x_in"] = rect_interpolation(x_in)
        else:
            # linear interpolation will be the default assumption, and this will also
            # lead to rect_interpolation, if the exposure_profile was before rectified
            # reindex adds a time point at the end to make sure the exposure profile
            # goes past the observations
            # ffill(dim="time") makes sure that no NaN values are at the end
            x_in_ = x_in.reindex(time=np.concatenate([x_in.time.values, [x_in.time.values[-1] * 1.1]]))
            x_in_ = x_in_.interpolate_na(dim="time", method="linear").ffill(dim="time")
            self.model_parameters["x_in"] = x_in_

        self.model_parameters["y0"] = y0
        self.model_parameters["parameters"] = self.config.model_parameters.value_dict

    def construct_database_statement_from_config(self):
        """returns a statement to be used on a database"""
        substance = self.config.simulation.substance # type:ignore
        exposure_path = self.config.simulation.exposure_path # type:ignore
        return (
            select(Timeseries, Treatment)
            .join(Timeseries)
        ).where(
            Timeseries.variable.in_([substance]),  # type: ignore
            Timeseries.name == {exposure_path}
        )

    def read_data(self) -> xr.Dataset:
        """Reads data and returns an xarray.Dataset. 
        
        GutsBase supports reading data from
        - netcdf (.nc) files
        - expyDB (SQLite databases)
        - excel  (directories of excel files)

        expyDB and excel operate by converting data to xarrays while netcdf directly
        loads xarray Datasets. For highest control over your data, you should always use
        .nc files, because they are imported as-is.
        """
        # TODO: Update to new INTERVENTION MODEL
        dataset = str(self.config.case_study.observations)
        
        # read from a directory
        if os.path.isdir(os.path.join(self.config.case_study.data_path, dataset)):
            # This looks for xlsx files in the folder and imports them as a database and
            # then proceeds as normal
            files = glob.glob(os.path.join(
                self.config.case_study.data_path, 
                dataset, "*.xlsx"
            ))

            tempdir = tempfile.TemporaryDirectory()
            dataset = self.read_data_from_xlsx(data=files, tempdir=tempdir)

        ext = dataset.split(".")[-1]
        
        if not os.path.exists(dataset):
            dataset = os.path.join(self.data_path, dataset)
            
        if ext == "db":
            statement = self.construct_database_statement_from_config()
            observations = self.read_data_from_expydb(dataset, statement)
            
            # TODO: Integrate interventions in observations dataset

        elif ext == "nc":
            observations = xr.load_dataset(dataset)

        else:
            raise NotImplementedError(
                f"Dataset extension '.{ext}' is not recognized. "+
                "Please use one of '.db' (mysql), '.nc' (netcdf)."
            )
        
        return observations
        
    def read_data_from_xlsx(self, data, tempdir):
        database = os.path.join(tempdir.name, "import.db")

        create_database_and_import_data_main(
            datasets_path=data, 
            database_path=database, 
            preprocessing=self.config.guts_base.data_preprocessing,
            preprocessing_out=os.path.join(tempdir.name, "processed_{filename}")
        )

        return database    


    def read_data_from_expydb(self, database, statement) -> xr.Dataset:

        observations_idata, interventions_idata = from_expydb(
            database=f"sqlite:///{database}",
            statement=statement
        )

        dataset = to_dataset(
            observations_idata, 
            interventions_idata,
            unit_time=self.config.guts_base.unit_time
        )
        dataset = reduce_multiindex_to_flat_index(dataset)

        # "Continue here. I want to return multidimensional datasets for data coming "+
        # "from the database. The method can be implemented in any class. Currently I'm looking "+
        # "at guts base"

        filtered_dataset = self.filter_dataset(dataset)

        return filtered_dataset

    def process_data(self):
        """
        Currently these methods, change datasets, indices, etc. in-place.
        This is convenient, but more difficult to re-arragen with other methods
        TODO: Make these methods static if possible
        """
        self._create_indices()
        self._indices_to_dimensions()
        # define tolerance based on the sovler tolerance
        self.observations = self.observations.assign_coords(eps=self.config.jaxsolver.atol * 10)

        self._reindex_time_dim()

        if "survival" in self.observations:
            if "subject_count" not in self.observations.coords:
                self.observations = self.observations.assign_coords(
                    subject_count=("id", self.observations["survival"].isel(time=0).values, )
                )

            if self._data.is_survival_only_nan_except_start(self.observations.survival):
                self.observations = self.observations.assign_coords({
                    "survivors_at_start": (("id", "time"), np.broadcast_to(
                        self.observations.survival.isel(time=0).values.reshape(-1,1), 
                        shape=self.observations.survival.shape
                ).astype(int))})
            else:
                self.observations = self._data.prepare_survival_data_for_conditional_binomial(
                    observations=self.observations
                )

        if "exposure" not in self.observations:
            self.observations["exposure"] = self.observations[self.config.guts_base.substance]
        
        # set 
        self.config.data_structure["exposure"].observed=False

    def _convert_exposure_units(self):
        """
        TODO: Here I need to decide what to do. Work with rescaled units is dangerous
        because fitting might be complicated with weird quantities.
        It would be better to rescale output parameters
        """
        units, unit_conversion_factors = _units._convert_units(
            self.observations.unit.reset_coords("unit", drop=True),
            target_units=self.config.guts_base.unit_target 
        )

        self.observations = self.observations.assign_coords({
            "unit": units,
            "unit_conversion_factors": unit_conversion_factors
        })

        self.observations[self.config.guts_base.substance] =\
              self.observations[self.config.guts_base.substance] * unit_conversion_factors

    @staticmethod
    def _unique_unsorted(values):
        _, index = np.unique(values, return_index=True)
        return tuple(np.array(values)[sorted(index)])


    def _create_indices(self):
        """Use if indices should be added to sim.indices and sim.observations"""
        pass

    def _indices_to_dimensions(self):
        pass

    def filter_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        return dataset

    def _reindex_time_dim(self):
        if self.config.simulation.model_class is not None:
            it_model = "_it" in self.config.simulation.model_class.lower()
        elif self.config.simulation.model is not None:
            it_model =  "_it" in self.config.simulation.model.lower()
        else:
            raise GutsBaseError(
                "GutsBase must have an initialized model or model_class."
            )

        if it_model:
            self.logger.info(msg=(
                "Redindexing time vector to increase resolution, because model has "+
                "'_it' (individual tolerance) in it's name"
            ))

            new_time_index = np.unique(np.concatenate([
                self.coordinates["time"],
                np.linspace(
                    0, np.max(self.coordinates["time"]), 
                    int(self.config.guts_base.n_reindexed_x) # type: ignore
                )
            ]))
            self.observations = self.observations.reindex(time = new_time_index)

        else:
            self.logger.info(msg=(
                "No redindexing of time vector to, because model name did not contain "+
                "'_it' (individual tolerance), or model was not given by name. If an IT model " +
                "is calculated without a dense time resolution, the estimates can be biased!"
            ))


    def reset_observations(self):
        """Resets the observations to the original observations after using .from_mempy(...)
        This also resets the sim.coordinates dictionary.
        """

        self.observations = self._obs_backup


    def recompute_posterior(self):
        """This function interpolates the posterior with a given resolution
        posterior_predictions calculate proper survival predictions for the
        posterior.

        It also makes sure that the new interpolation does not include fewer values
        than the original dataset
        """

        ri = self.config.guts_base.results_interpolation

        # generate high resolution posterior predictions
        if ri is not None:
            time_interpolate = np.linspace(
                start=float(self.observations["time"].min()) if np.isnan(ri[0]) else ri[0],
                stop=float(self.observations["time"].max()) if np.isnan(ri[0]) else ri[1],
                num=ri[2] 
            )

            # combine original coordinates and interpolation. This 
            # a) helps error checking during posterior predictions.
            # b) makes sure that the original time vector is retained, which may be
            #    relevant for the simulation success (e.g. IT model)
            obs = self.observations.reindex(
                time=np.unique(np.concatenate(
                    [time_interpolate, self.observations["time"]]
                )),
            )

            obs["survivors_before_t"] = obs.survivors_before_t.ffill(dim="time").astype(int)
            obs["survivors_at_start"] = obs.survivors_at_start.ffill(dim="time").astype(int)
            self.observations = obs
            
        self.dispatch_constructor()
        _ = self._prob.posterior_predictions(self, self.inferer.idata) # type: ignore


    def prior_predictive_checks(self, **plot_kwargs):
        super().prior_predictive_checks(**plot_kwargs)

        self._plot.plot_prior_predictions(self, data_vars=["survival"])

    def posterior_predictive_checks(self, **plot_kwargs):
        super().posterior_predictive_checks(**plot_kwargs)

        sim_copy: GutsBase = self.copy()
        sim_copy.recompute_posterior()
        # TODO: Include posterior_predictive group once the survival predictions are correctly working
        sim_copy._plot.plot_posterior_predictions(
            sim_copy, data_vars=["survival"], groups=["posterior_model_fits"]
        )


    def plot(self, results):
        self._plot.plot_survival(self, results)

    def predefined_scenarios(self):
        """
        TODO: Fix timescale to observations
        TODO: Incorporate extra exposure patterns (constant, pulse_1day, pulse_2day)
        """
        # get the maximum possible time to provide exposure scenarios that are definitely
        # long enough
        time_max = float(max(
            self.observations[self.config.simulation.x_dimension].max(), 
            *self.config.guts_base.ecx_estimates_times
        ))

        # this produces a exposure x_in dataset with only the dimensions ID and TIME
        standard_dimensions = (
            self.config.simulation.batch_dimension,
            self.config.simulation.x_dimension, 
        )

        # get dimensions different from standard dimensions
        exposure_dimension = [
            d for d in self.observations.exposure.dims if d not in 
            standard_dimensions
        ]

        # raise an error if the number of extra dimensions is larger than 1
        if len(exposure_dimension) > 1:
            raise ValueError(
                f"{type(self).__name__} can currently handle one additional dimension for "+
                f"the exposure beside {standard_dimensions}. You provided an exposure "+ 
                f"array with the dimensions: {self.observations.exposure.dims}"
            )
        else:
            exposure_dimension = exposure_dimension[0]

        # iterate over the coordinates of the exposure dimensions to 
        exposure_coordinates = self.observations.exposure[exposure_dimension].values

        scenarios = {}
        for coord in exposure_coordinates:
            concentrations = np.where(coord == exposure_coordinates, 1.0, 0.0)

            for _name, _expo_scenario in self.config.guts_base.ecx_exposure_scenarios.items():
                if _expo_scenario["start"] is None:
                    _expo_scenario["start"] = 0.0

                exposure_dict = {
                    coord: ExposureDataDict(
                        start=_expo_scenario["start"], 
                        end=_expo_scenario["end"], 
                        exposure=conc
                    )
                    for coord, conc in zip(exposure_coordinates, concentrations)
                }

                scenario = design_exposure_scenario(
                    exposures=exposure_dict,
                    t_max=time_max,
                    dt=1/24,
                    exposure_dimension=exposure_dimension
                )

                scenarios.update({
                    f"{_name}_{coord}": scenario
                })

        return scenarios



    @staticmethod
    def _exposure_data_to_xarray(
        exposure_data: Dict[str, pd.DataFrame], 
        dim: str, 
        default_time_unit: str = "",
        exposure_units: Mapping[str,str] = {"default": ""},
    ) -> xr.Dataset:
        """Creates a Dataset named exposure that has coordinates corresponding to the 
        keys in the exposure_data and a dimension name accordint to dim. It also carries
        an unused coordinate called unit, which carries the unit information of the exposure
        """
        arrays = {}
        _unit_time = []
        _unit_exposure = {}
        for key, df in exposure_data.items():
            # this override is necessary to make all dimensions work out
            unit_time = _units._get_unit_from_dataframe_index(df)
            unit_expo = exposure_units.get(key, exposure_units["default"])

            df.index.name = "time"
            arrays.update({
                key: df.to_xarray().to_dataarray(dim="id", name=key)
            }) 
            _unit_time.append(unit_time)
            _unit_exposure.update({key: f"{_units.ureg.parse_expression(unit_expo).units:C}"})

        # convert exposure units to an xr.Dataarray
        units_arr = pd.Series(_unit_exposure).to_xarray()
        units_arr = units_arr.rename({"index": dim})

        # make sure times of all exposures are identical
        if len(set(_unit_time)) > 1:
            raise GutsBaseError(
                "Different time units were specified in the exposure datasets " +
                f"{set(_unit_time)}. Make sure all exposure datasets have the " +
                "same time unit."
            )
        else:
            unit_time = list(set(_unit_time))[0]

        # if the unit_time was not defined, resort to the default time unit (dimensionless)
        if len(unit_time) == 0:
            unit_time = default_time_unit

        # create the exposure dataset
        exposure_array = xr.Dataset(arrays).to_array(dim=dim, name="exposure")
        exposure_array = exposure_array.transpose("id", "time", ...)
        ds = xr.Dataset({"exposure": exposure_array})
        
        # add the time unit as an attribute (rounttrip ureg, to standardize)
        ds.attrs["unit_time"] = f"{_units.ureg.parse_expression(unit_time).units:C}"
        # add exposure units as coordinates. This is used later on by _convert units
        ds = ds.assign_coords({"unit": units_arr})

        return ds

    @staticmethod
    def _survival_data_to_xarray(
            survival_data: pd.DataFrame,
            default_time_unit: str = ""
        ) -> xr.Dataset:
        # TODO: survival name is currently not kept because the raw data is not transferred from the survival

        unit_time = _units._get_unit_from_dataframe_index(survival_data)
        survival_data.index.name = "time"

        survival_array = survival_data.to_xarray().to_dataarray(dim="id", name="survival")
        survival_array = survival_array.transpose("id", "time", ...)
        arrays = {"survival": survival_array}

        ds = xr.Dataset(arrays)
        if len(unit_time) == 0:
            unit_time = default_time_unit

        ds.attrs["unit_time"] = f"{_units.ureg.parse_expression(unit_time).units:C}"

        return ds

    @classmethod
    def _observations_from_dataframes(
        cls, 
        exposure_data: Dict[str, pd.DataFrame],
        survival_data: Optional[pd.DataFrame] = None,
        exposure_dim: str = "substance",
        unit_input: Mapping[str,str] = {"default": ""}, 
        unit_time: str = "day", 
    ):
        # parse observations
        # obs can be simply subset by selection obs.sel(substance="Exposure-Dime")
        _exposure = cls._exposure_data_to_xarray(
            exposure_data, dim=exposure_dim, 
            exposure_units=unit_input,
            default_time_unit=unit_time,
        )
        arrays = [_exposure]
        if survival_data is not None:
            _survival = cls._survival_data_to_xarray(
                survival_data, 
                default_time_unit=unit_time
            )
            arrays.append(_survival)
            
        observations = xr.combine_by_coords(arrays, combine_attrs="no_conflicts")

        return observations

    @property
    def _exposure_dimension(self):
        return self._get_exposure_dimension(
            dimensions=self.config.data_structure["exposure"].dimensions,
            batch_dim=self.config.simulation.batch_dimension, 
            x_dim=self.config.simulation.x_dimension
        )
    
    @staticmethod
    def _get_exposure_dimension(dimensions, batch_dim: str = "id", x_dim: str = "time"):
        extra_dims = []
        for k in dimensions:
            if k not in (batch_dim, x_dim):
                extra_dims.append(k)
            else:
                pass

        if len(extra_dims) > 1:
            raise GutsBaseError(
                "Guts Base can currently only handle one exposure dimension beside" +
                "the standard dimensions."
            )
        else:
            return extra_dims[0]
        

    def expand_batch_like_coordinate_to_new_dimension(self, coordinate, variables):
        """This method will take an existing coordinate of a dataset that has the same
        coordinate has the batch dimension. It will then re-express the coordinate as a
        separate dimension for the given variables, by duplicating the N-Dimensional array
        times the amount of unique names in the specified coordinate to create an 
        N+1-dimensional array. This array will be filled with zeros along the batch dimension
        where the specified coordinate along the ID dimension coincides with the new (unique)
        coordinate of the new dimension. 

        This process is entirely reversible
        """
        old_coords = self.observations[coordinate]
        batch_dim = self.config.simulation.batch_dimension

        # old coordinate before turning it into a dimension
        obs = self.observations.drop(coordinate)

        # create unique coordinates of the new dimension, preserving the order of the
        # old coordinate
        _, index = np.unique(old_coords, return_index=True)
        coords_new_dim = tuple(np.array(old_coords)[sorted(index)])

        for v in variables:
            # take data variable and extract dimension order
            data_var = obs[v]
            dim_order = data_var.dims

            # expand the dimensionality, then transpose for new dim to be last
            data_var = data_var.expand_dims(coordinate).transpose(..., batch_dim, coordinate)

            # create a dummy dimension to broadcast the new array 
            # dummy_3d = np.ones((1, len(coords_new_dim)))
            dummy_categorical = pd.get_dummies(old_coords).astype(int).values

            # apply automatic broadcasting to increase the size of the new dimension
            # data_var_np1_d = data_var * dummy_3d
            data_var_np1_d = data_var * dummy_categorical
            data_var_np1_d.attrs = data_var.attrs

            # annotate coordinates of the new dimension
            data_var_np1_d = data_var_np1_d.assign_coords({
                coordinate: list(coords_new_dim)
            })

            # transpose back to original dimension order with new dim as last dim
            data_var_np1_d = data_var_np1_d.transpose(*dim_order, coordinate)
            obs[v] = data_var_np1_d

        return obs

    def map_batch_coordinates_to_extra_dim_coordinates(
        self, 
        observations: xr.Dataset, 
        target_dimension: str,
        coordinates: Optional[List[Hashable]] = None
    ) -> xr.Dataset:
        """Iterates over coordinates and reduces those coordinates to the new dimension
        which have the same number of unique coordinates as the new dimension has coordinates
        """
        if coordinates is None:
            coordinates = list(observations.coords.keys())

        for key, coord in observations.coords.items():
            # skips coords, if not specified in coordinates
            if key not in coordinates:
                continue

            if self.config.simulation.batch_dimension in coord.dims and key not in observations.dims:
                if len(coord.dims) == 1:
                    dim_coords = self._unique_unsorted(coord.values)
                    if len(dim_coords) == len(observations[target_dimension]):
                        observations[key] = (target_dimension, list(dim_coords))
                    else:
                        pass
                else:
                    warnings.warn(
                        f"Coordinate '{key}' is has dimensions {coord.dims}. " +
                        "Mapping coordinates with more than 1 dimension to the extra " +
                        f"dimension '{target_dimension}' is not supported yet."
                    )
                    pass

        return observations
                

    def reduce_dimension_to_batch_like_coordinate(self, dimension, variables):
        """This method takes an existing dimension from a N-D array and reduces it to an
        (N-1)-D array, by writing a new coordinate from the reducible dimension in the way
        that the new batch-like coordinate takes the coordinate of the dimension, where
        the data of the N-D array was not zero. After it has been asserted that there is
        only a unique candidate for the each coordinate along the batch dimension 
        (i.e. only one value is non-zero for a given batch-coordinate), the dimension will
        be reduced by summing over the given dimension.

        The method is contingent on having no overlap in batch dimension in the dataset
        """
        pass

    def initialize_from_script(self):
        pass


    @staticmethod
    def _update_model_parameters(model_parameters, params: dict):
        params_stash = {}
        for name, new_values in params.items():
            if not hasattr(model_parameters, name):
                print(f"{name} not in model_parameters, skipping.")
                continue

            param = model_parameters[name]
            stash = param.model_dump(include=list(new_values.keys()))
            params_stash.update({name: stash})

            for k, v in new_values.items():
                setattr(param, k, v)
                
        return params_stash

    ### API methods ###
    

    def estimate_parameters(
        self,
        background_mortality: Literal["pre-fit", "full"] = "full",
        estimate_background_mortality_numpyro_config: Numpyro = CFG_numpyro_background,
        forward_interpolate_exposure_data: bool = CFG_default.guts_base.forward_interpolate_exposure_data,
        ecx_mode: Literal["draws", "mean"] = CFG_default.guts_base.ecx_mode,
        ecx_draws: int = CFG_default.guts_base.ecx_draws,
        ecx_estimates_x: List[float] = CFG_default.guts_base.ecx_estimates_x,
        ecx_estimates_times: List[float] = CFG_default.guts_base.ecx_estimates_times,
        transform_scalings: Optional[Dict[Literal["time_factor", "x_in_factor"],float]] = None,
        transform_ignore_keys: List = ["id", "exposure_path",],
        raise_max_steps_error: bool = False,
        # solver options
        solver_atol: float = 1e-12,
        solver_rtol: float = 1e-10,
        solver_max_steps: int = 1_000_000,
        # inference options
        inference_numpyro_kernel: Literal["nuts", "svi", "map"] = "svi",
        inference_numpyro_draws: int = 2000,
        inference_numpyro_init_strategy: Literal["init_to_median", "init_to_uniform", "init_to_sample"] = "init_to_median",
        inference_numpyro_svi_iterations: int = 20_000,
        inference_numpyro_svi_learning_rate: float = 0.001,
        inference_numpyro_nuts_chains: int = 4,
        inference_numpyro_nuts_warmup: int = 2000,
    ):
        """Estimate the parameters of a GutsBase simulation, generate an automated
        report and export the estimated simulation to disk.
        
        Parameters
        ----------

        background_mortality : Literat['pre-fit', 'full']
            Jointly fit the background mortality parameters with the other free parameters
            ('full') or fit the background mortality prior to estimating other Guts 
            parameters. If 'pre-fit' separately estimates the background mortality 
            parameters based on the control treatments. Defaults to False.
            Afterwards, the background mortality parameters are fixed to the
            estimated maximum-a-posteriori values. Note that in the case of SVI, and NUTS
            the map value is the sample of the posteiror distribution that comes closest to
            the true MAP value

        estimate_background_mortality_numpyro_config : pymob.sim.config.Numpyro
            Configuration options for the separate background mortality estimation.
            Default settings should be fine in most cases.

        forward_interpolate_exposure_data : bool
            whether GutsBase should make sure that the exposure profiles are forward 
            interpolated. This means, if a rectangular profile is not explicitly given,
            by providing the same exposure (time, value) combination at the moment before the 
            next recorded change in the exposure profile, the default behavior is to interpolate
            linearly over the profile. E.g. a profile like (time=0,value=10), (time=2,value=0)
            would implicitly yield the points, e.g.: (time=1,value=5), (time=1.99, value=~0). 
            If forward_interpolate_exposure_data = True, then the interpolated point would be
            (time=1,value=10), (time=1.99,value=10)

        raise_max_steps_error : bool
            Interrupt model evaluation if the solution cannot be reached in the maximum
            number of steps at the required precision (`solver_rtol`, `solver_atol`).
            Defaults to False.
            Especially in Parameter inference settings without hard bounds, it is possible
            that the solver is confronted with extreme parameter combinations that lead
            to highly volatile solutions. In such circumstances it is possible, that 
            a solution cannot be reached in 1,000,000 steps (the default `solver_max_steps`).
            As such parameter combinations are typically nonsense, it is accepted that 
            the solver cannot solve the problem and silently return infinities. The
            default settings typically work for GUTS problems and are a compromise between
            not overly constricting the solvable parameter space and performance. 
            However, it needs to be stressed that there is no guarantee that relevant 
            parameter combinations are rejected because the solver cannot evaluate the 
            problem with the given settings. If this possibility should be guaranteed,
            set `raise_max_steps_error=True` and if necessary increase the `solver_atol`
            and `solver_rtol` tolerances and increase `solver_max_steps`.

        solver_atol : float
            The absolute tolerance of the solver. Defaults to 1e-12.

        solver_rtol : float
            The relative tolerance of the solver. Defaults to 1e-10.

        solver_max_steps : int 
            The maximum number of steps the solver is allowed to reach the solution
            at the required precision (`solver_atol`, `solver_rtol`), before a 
            max-steps-error is raised.

        transform_scalings : Optional, Dict[str, float]
            EXPERIMENTAL FEATURE
            Transforms the simulation with the provided scalings and scaling functions with
            default priors. Defaults to None (no transform).
            Enable py passing a dictionary with transform scalings, e.g.
            `transform_scalings={'time_factor': 1.0, 'x_in_factor': 10.0}`. In this 
            example, all relevant sections of the simulation (observations, parameters,
            idata) will be scaled by 10, as specified in the transform funcitons of
            `GutsTransform`. 
            This might be useful, in situations, where models are fitted "blindly". 
            See the documentation of `GutsBase.transform` for detailed information how
            to use a transform. 

        transform_ignore_keys : List[str]
            Parameters, data variables or coordinates that should be ignored when
            transforming. Takes no effect, when `transform_scalings=None`

        ecx_estimates_x : List[float]
            Effect levels for ecx estimation. Defaults to `GutsBaseConfig.ecx_estimates_x`.

        ecx_estimates_times : List[float]
            Times for ecx estimation. Defaults to `GutsBaseConfig.ecx_estimates_times`.

        ecx_mode : str
            Assess the uncertainty of the ECx estimate ('draws') or not ('mean').
            Defaults to `GutsBaseConfig.ecx_mode`

        ecx_draws: int
            Number of draws from the posterior for assessing the uncertainty of the 
            estimate. Takes no effect, if `ecx_mode='mean'`. Defaults to 
            `GutsBaseConfig.ecx_draws`.
            Note that if a lot of ECx estimates are computed, this can take a lot of time.
            Less draws than 100 draws are not allowed for a reliable estimate. 

        inference_numpyro_kernel : Literal['nuts', 'svi', 'map']
            The algorithm to run inference with. Defaults to 'svi'
            - 'svi' is a stochastic approach, that scales well with large datasets. 
              It frames the problem as an optimization problem and converges on the 
              distribution, whose family is determined by the prior distributon, which
              is closes to the posterior parameter distribution. It is the recommended
              choice for exploring a problem as it is very robust.
            - 'nuts' is the gold standard for bayesian
              inference. But it may take a long time for complex problems. It does not
              scale well with large datasets. Use 'nuts' only if you can get good fits 
              with 'svi'.
            - 'map' Maximum-a-posteriori estimate. Very fast, converges on the best
              estimate, given the prior distributions. Since map is a special case
              of SVI where delta distributions are used, the algorithm also takes
              `svi_...` options.
              TODO: Test uniform prior distributions (currently). If uniform prior
              distributions are used this reduces to a maxmimum likelihood estimate (MLE).

        inference_numpyro_draws : int
            Number of draws from the posterior. Defaults to 2000. Takes no effect with
            'map' kernel. For nuts, these samples are directly sampled from the posterior
            using a MCMC algorithm, For svi, these samples are drawn, after the parametric
            distributions have been found. 

        inference_numpyro_init_strategy : Literal["init_to_median", "init_to_uniform", "init_to_sample"]
        inference_numpyro_svi_iterations : int
        inference_numpyro_svi_learning_rate : float
        inference_numpyro_nuts_chains : int
        inference_numpyro_nuts_warmup : int


        Returns
        -------

        None. Attributes are update in-place. After calling the function the `GutsBase` 
        instance (e.g. `sim`) contains the following attributes:

        - sim.inferer.idata: This is an arviz.InferenceData object that contains the 
          results of the parameter estimation, regardless of the used algorithm
        
        In addition, it generates a number of outputs. These are directed to the directory
        `sim.output_dir


        Examples
        --------

        We start by generating a simulated experiment. Instead of simulating an experiment,
        you could read data in the Openguts format as pandas dataframes or use the 
        mempyguts api (`mempy.input_data).

        >>> from mempy.model import RED_SD
        >>> from guts_base import PymobSimulator
        >>> experiment = PymobSimulator.draft_laboratory_experiment(
        ...     treatments={"C": 0.0, "T1": 1, "T2": 5, "T3": 50, "T4": 100},
        ...     simulate_survival=True,
        ... )
        
        

        >>> survival_data = experiment.survival.to_pandas().T
        >>> exposure_data = {"A": experiment.exposure.to_pandas().T}
        >>> sim = PymobSimulator.from_model_and_dataset(
        ...     model=RED_SD(),
        ...     exposure_data=survival,
        ...     survival_data=exposure,
        ...     output_directory="results/test"
        ... )


        Note
        ----

        Any OTHER configuration options of `pymob` 
        (https://pymob.readthedocs.io/en/latest/api/pymob.sim.html#module-pymob.sim.config)
        or guts_base (`guts_base.sim.config`) that are not controlled by this function 
        can be set before calling `GutsBase.estimate_parameters`. Simply use the config API
        e.g. `sim.config.report.pandoc_output_format = 'latex' or 
        e.g. `sim.config.guts_base.table_parameter_stat_focus = 'median'
        
        """

        # update config options
        self.config.guts_base.forward_interpolate_exposure_data = forward_interpolate_exposure_data
        self.config.guts_base.ecx_mode = ecx_mode
        self.config.guts_base.ecx_draws = ecx_draws
        self.config.guts_base.ecx_estimates_x = ecx_estimates_x
        self.config.guts_base.ecx_estimates_times = ecx_estimates_times

        # set numpyro options
        self.config.inference_numpyro.kernel = inference_numpyro_kernel
        self.config.inference_numpyro.draws = inference_numpyro_draws
        self.config.inference_numpyro.init_strategy = inference_numpyro_init_strategy
        self.config.inference_numpyro.svi_iterations = inference_numpyro_svi_iterations
        self.config.inference_numpyro.svi_learning_rate = inference_numpyro_svi_learning_rate
        self.config.inference_numpyro.chains = inference_numpyro_nuts_chains
        self.config.inference_numpyro.warmup = inference_numpyro_nuts_warmup

        # solver options
        self.config.jaxsolver.throw_exception = raise_max_steps_error
        self.config.jaxsolver.atol = solver_atol
        self.config.jaxsolver.rtol = solver_rtol
        self.config.jaxsolver.max_steps = solver_max_steps

        if background_mortality == "pre-fit":
            self.estimate_background_mortality(
                # uses all treatments where the cumulative exposure is zero
                control_ids=None,
                exclude_controls_after_fixing_background_mortality=True,
                inference_numpyro=estimate_background_mortality_numpyro_config,
            )
        elif background_mortality == "full":
            pass
        else:
            raise NotImplementedError(
                "background_mortality must be one of 'pre-fit', or 'full'"
            )


        # set the transformer and transform the simulation
        # if a transformer is provisioned. Scalings are not a part
        # of the configuration as the scaling of a simulation is intrinsicially
        # something that should be completed at runtime. Saving a 
        if transform_scalings is not None:
            self.transformer = GutsTransform(
                time_factor=transform_scalings["time_factor"],
                x_in_factor=transform_scalings["x_in_factor"],
                ignore_keys=transform_ignore_keys
            )
            self.transform(inverse=False, idata=False)

        self.prepare_simulation_input()
        self.dispatch_constructor()
        self.set_inferer("numpyro")
    
        # prior predictive checks for assessing the plausibility of the priors given
        # the data
        self.prior_predictive_checks()

        # run the actual parameter estimation
        self.inferer.run()

        if transform_scalings is not None:
            # this is something that has to be done manually. The transformer
            # has to be told, that idata is transformed, because it was generated
            # from transformed parameters and data.
            self.transformer.is_transformed["idata"] = True
            self.transform(inverse=True)

        # before exporting or reporting test if all variables are NOT transformed
        assert all([not trans for trans in self.transformer.is_transformed.values()])
        
        # export the simulation to the output directory
        # this dumps config, observations and idata to disk.
        # it can be read with GutsBase.from_directory(...)
        self.export()

        # run posterior predictive checks (plots the observations against the model fits)
        self.posterior_predictive_checks()

        # generate a report. This will fail silently if errors ocurr in the report
        self.report()

    def transform(
        self, 
        inverse=False, 
        idata=True, 
        observations=True, 
        parameters=True,
    ):
        """EXPERIMENTAL FEATURE
        
        Transform with care! Transforming a simulation changes the parameter **values**,
        observations, and results, observations and parameters in the idata object (if
        existing). 
        
        Usage Example
        -------------

        A typical workflow is:

        1. Set up the simulation `sim = PymobSimulator.from_model_and_dataset(...)`
        
        >>> from mempy.model import RED_SD
        >>> from guts_base import PymobSimulator
        >>> experiment = PymobSimulator.draft_laboratory_experiment(
        ...     treatments={"C": 0.0, "T1": 1, "T2": 5, "T3": 50, "T4": 100},
        ...     simulate_survival=True,
        ... )
        >>> survival_data = experiment.survival.to_pandas().T
        >>> exposure_data = {"A": experiment.exposure.to_pandas().T}
        >>> sim = PymobSimulator.from_model_and_dataset(
        ...     model=RED_SD(),
        ...     exposure_data=survival,
        ...     survival_data=exposure,
        ...     output_directory="results/test"
        ... )

        2. Set up the transform `sim.transformer = GutsTransform(x_in_factor=..., time_factor=...)`

        >>> from guts_base.sim.transformer import GutsTransform
        >>> # define a transformation factor
        >>> x_in_factor = float(sim.observations.exposure.max().values)
        >>> # set transformation
        >>> sim.transformer = GutsTransform(
        ...     time_factor=1.0, x_in_factor=x_in_factor, 
        ...     ignore_keys=["id", "exposure_path",]
        ... )
        
        3. Transform the simulation `GutsBase.transform(idata=False)`
        
        >>> sim.transform(idata=False)
        
        4. Run parameter estimation `GutsBase.estimate_parameters(...)`

        >>> sim.estimate_parameters()

        5. Inverse transform the simulation `GutsBase.transform(inverse=True)`
        
        >>> sim.transform(inverse=True)
        
        Explanations
        ------------

        `GutsBase.transform` DOES NOT change the priors. This means, estimating 
        parameters of a transformed simulation will yield different results than 
        estimating parameters of an untransformed simulations. 

        However, this is the whole point. Transformations are meant to make the life of
        a modeller easier. By bringing all data on a unit scale, the problem can be 
        easier solved, using default priors (e.g. lognormal(scale=1, s=5)). Depending
        of the size of the transformation, the effect can be larger or smaller. If 
        for instance I want to scale the exposure to a unit interval [0, 1], and my 
        largest exposure is, e.g. 500, this shifts the relative influence of the prior
        distributions also by a factor of 500, especially the m and b parameters.

        ⚠️ Therefore a word of warning. Before applying transformations to a wide set 
        of different problems, double check your priors and make sure that they behave
        as expected.

        This means, transforming is a double edged sword. If the priors for a transformed
        distribution are chosen well, with one set of priors, many problems of vastly 
        different scales can be solved. If the default priors are not chosen well,
        you will make your life more difficult rather than easier.

        Extending Transform classes
        ---------------------------

        **Note** that forward transform (`inverse=False`) divides by the factors and 
        inverse transform multiplies by the factors. This is how the functions are defined
        in the GutsTransform. 
        
        Also, transforms for all parameters might not exist. If you want to define the
        transforms at runtime, this is relatively easy to do:

        >>> sim.transformer.data_transformer.xxx = lambda self, x: x / self.time_factor
        >>> sim.transformer.data_transformer.xxx_inv = lambda self, x: x * self.time_factor

        This will create new transforms (forward and inverse) for the data variable 'xxx'.
        Similarly this can be done for the `parameter_transformer` attribute of the sim
        transformer.

        If you want to provide your own transform functions, feel free to write your own
        class. See `guts_base.sim.transformer` for inspiration. There the `GutsTransform`
        class is defined.

        Defining Priors
        ---------------

        Some considerations for defining good priors for a simulation transformed to the
        unit scale.

        If the exposure is on the interval [0, 1] (by transforming the data by the max. 
        exposure), for Guts-SD models, the m parameter will be oftentimes within that
        interval. If of course the experiment was conducted in a way that no mortality
        was observed, the m-parameter is likely outside of that interval (m > 1).

        A sensible prior would be for instance:

        >>> sim.config.model_parameters.m.prior = 'lognorm(scale=0.01,s=5)'

        This prior will assign large probability mass to values in the interval [0, 1], 
        but will also cover parts above 1 with quite some probability. 

        For the remaining parameters, a good default is 'lognorm(scale=1.0,s=5)'

        The s-parameter controls the width of the distribution.

        Implementation tasks
        --------------------
        TODO: Currently multi exposure models are only supported for transforming
        the all substances/exposures with the same factor. Theoretically it would be possible 
        to handle each exposure path/substance differently, but this requires more elaborate
        implementations. 
        """
        self.transformer.transform(
            sim=self,
            inverse=inverse,
            idata=idata,
            observations=observations,
            parameters=parameters,
        )

        self.prepare_simulation_input()
        self.dispatch_constructor()

    @overload
    def point_estimate(
        self,
        *,
        estimate: Literal["mean", "map"] = "map",
        to: Literal["xarray"] = "xarray",
    ) -> xr.Dataset: ...
    
    @overload
    def point_estimate(
        self,
        *,
        estimate: Literal["mean", "map"] = "map",
        to: Literal["dict"] = "dict",
    ) -> Dict[str, NumericArray]: ...


    def point_estimate(
        self, 
        estimate: Literal["mean", "map"] = "map",  
        to: Literal["xarray", "dict"] = "xarray"
    ) -> Any:
        """Returns a point estimate of the posterior. If you want more control over the posterior
        use the attribute: sim.inferer.idata.posterior and summarize it or select from it
        using the arviz (https://python.arviz.org/en/stable/index.html) and the 
        xarray (https://docs.xarray.dev/en/stable/index.html) packages

        Parameters
        ----------

        estimate : Literal["map", "mean"]
            Point estimate to return. 
            - map: Maximum a Posteriori. The sample that has the highest posterior probability.
              This sample considers the correlation structure of the posterior
            - mean: The average of all marginal parameter distributions.

        to : Literal["xarray", "dict"]
            Specifies the representation to transform the summarized data to. dict can
            be used to insert parameters in the .evaluate() method. While xarray is the
            standard view. Defaults to xarray

        Example
        -------

        >>> sim.best_estimate(to='dict')
        """
        if estimate == "mean":
            best_estimate = self.inferer.idata.posterior.mean(("chain", "draw"))

        elif estimate == "map":
            loglik = self.inferer.idata.log_likelihood\
                .sum(["id", "time"])\
                .to_array().sum("variable")
            
            sample_max_loglik = loglik.argmax(dim=("chain", "draw"))
            best_estimate = self.inferer.idata.posterior.sel(sample_max_loglik)  # type: ignore
        else:
            raise GutsBaseError(
                f"Estimate '{estimate}' not implemented. Choose one of ['mean', 'map']"
            )


        if to == "xarray":
            return best_estimate
            
        elif to == "dict":
            return {k: np.array(v.values, dtype=float) for k, v in best_estimate.items()}

        else:
            raise GutsBaseError(
                "PymobConverter.best_esimtate() supports only return types to=['xarray', 'dict']" +
                f"You used {to=}"
            )


    def evaluate(
        self, 
        parameters: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
        y0: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
        x_in: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
    ):
        """Evaluates the model along the coordinates of the observations with given
        parameters, x_in, and y0. The dictionaries passed to the function arguments
        only overwrite the existing default parameters; which makes the usage very simple.

        Note that the first run of .evaluate() after calling the .dispatch_constructor()
        takes a little longer, because the model and solver are jit-compiled to JAX for
        highly efficient computations.

        Parameters
        ----------

        theta : Dict[float|Sequence[float]]
            Dictionary of model parameters that should be changed for dispatch.
            Unspecified model parameters will assume the default values, 
            specified under config.model_parameters.NAME.value

        y0 : Dict[float|Sequence[float]]
            Dictionary of initial values that should be changed for dispatch.
        
        x_in : Dict[float|Sequence[float]]
            Dictionary of model input values that should be changed for dispatch.


        Example
        -------

        >>> sim.dispatch_constructor()  # necessary if the sim object has been modified
        >>> # evaluate setting the background mortaltiy to zero
        >>> sim.evaluate(parameters={'hb': 0.0})  

        """
        evaluator = self.dispatch(theta=parameters, x_in=x_in, y0=y0)
        evaluator()
        return evaluator.results

    def estimate_background_mortality(
        self,
        control_ids: Optional[str|List[str]] = None,
        exclude_controls_after_fixing_background_mortality: bool = True,
        inference_numpyro: Numpyro = CFG_numpyro_background,
    ):
        """Separately estimates the background mortality parameters based on the control
        treatments. Afterwards, the background mortality parameters are fixed to the
        estimated maximum-a-posteriori values. Note that in the case of SVI, and NUTS
        the map value is the sample of the posteiror distribution that comes closest to
        the true MAP value. 

        Parameters
        ----------

        control_ids : Optional[str | List [str]]
            The names of the IDs to use for fitting the control mortality parameters
            By default, this selects all IDs that have no exposure throghout the entire
            duration of the provided timeseries.
        exclude_controls_after_fixing_background_mortality : bool
            If the controls should be excluded from fitting after calibration.
        inference_numpyro: Numpyro
            inference_numpyro config section to parameterize background mortality 
            estimation. By default, the MAP kernel is used, which is sufficient
            for a problem, where the uncertainty of the estimate is not propagated to
            the following analysis.
        """

        self._exclude_controls_after_fixing_background_mortality =\
            exclude_controls_after_fixing_background_mortality
        # copy the simulation in order not to mix up anything in the original sim
        sim_control = self.copy()

        if isinstance(control_ids, str):
            control_ids = [control_ids]
        elif control_ids is None:
            cum_expo = sim_control.observations.exposure.sum(
                ("time", sim_control._exposure_dimension)
            )
            control_ids = cum_expo.where(cum_expo == 0, drop=True).id.values
        else:
            pass

        # constrain the observation of the copied object to the control ids
        sim_control.observations = sim_control.observations.sel(id=control_ids)

        # Fix parameters of the background-mortality module at zero
        params_fix_at_zero = {
            k: {"value": 0.0, "free": False } for k in sim_control.model_parameter_names
            if k not in sim_control.config.guts_base.background_mortality_parameters
        }
        
        # update the parameters in the model_parameters dict
        params_backup = sim_control._update_model_parameters(
            sim_control.config.model_parameters, params_fix_at_zero
        )

        # setup inferer
        sim_control.prepare_simulation_input()
        sim_control.dispatch_constructor()
        sim_control.set_inferer("numpyro")

        # run inference 
        sim_control.config.inference_numpyro = Numpyro.model_validate(inference_numpyro)
        sim_control.inferer.run()

        # plot results of background mortality
        sim_control._plot.plot_survival_multipanel(
            sim_control, sim_control.inferer.idata.posterior_model_fits,
            filename="survival_multipanel_control_treatments"
        )

        # optain the maximum a posteriori estiamte from the inferer using the guts-base API
        # and start iterating over the background mortality parameters
        map_estimate = sim_control.point_estimate(estimate="map", to="dict")
        for bgm_param in sim_control.config.guts_base.background_mortality_parameters:
            bgm_param_value = map_estimate[bgm_param]

            # assign the estimated parameter MAP value to the parameters of the original
            # simulation object. Also set them as fixed parameters
            self.config.model_parameters[bgm_param].value = bgm_param_value
            self.config.model_parameters[bgm_param].free = False
        
        # reverse the process from before (this is strictly not necessary)
        _ = sim_control._update_model_parameters(
            sim_control.config.model_parameters, params_backup
        )

        # constrain observations to non-control IDs if flag is set
        if exclude_controls_after_fixing_background_mortality:
            control_mask = [id for id in self.observations.id.values if id not in control_ids]
            self.observations = self.observations.sel(id=control_mask)
            
        # assemble simulation inputs and Evaluator with new fixed parameter values.
        self.prepare_simulation_input()
        self.dispatch_constructor()

    @classmethod
    def draft_laboratory_experiment(
        cls,
        treatments: Dict[str, float|Dict[str,float]],
        n_test_organisms_per_treatment: int = 10, 
        experiment_end: pd.Timedelta = pd.Timedelta(10, unit="days"), 
        exposure_pattern: ExposureDataDict|Dict[str,ExposureDataDict] = ExposureDataDict(start=0.0, end=None, exposure=None),
        exposure_interpolation: Literal["linear", "constant-forward"] = "constant-forward",
        exposure_dimension: str = "substance",
        observation_times: Optional[List[float]] = None,
        dt: pd.Timedelta = pd.Timedelta("1 day"),
        write_to_file: Optional[str] = None 
    ):
        """Simulate a laboratory experiment according to a treatment dictionary

        """

        experiment = draft_laboratory_experiment(
            treatments=treatments,
            experiment_end=experiment_end,
            exposure_pattern=exposure_pattern,
            exposure_dimension=exposure_dimension,
            dt=dt
        )


        survival = np.full(
            [v for k, v in experiment.sizes.items() if k in ("time", "id")], 
            fill_value=np.nan
        )
        # set with the number of test organism at time zerp
        survival[:, 0] = n_test_organisms_per_treatment
        experiment["survival"] = xr.DataArray(survival, coords=[experiment.id,experiment.time])

        if observation_times is None:
            observation_times_safe = experiment.time
        else:
            observation_times_safe = np.unique(np.concatenate([experiment.time,observation_times]))

        experiment = experiment.reindex(time=observation_times_safe)        

        # TODO: This does not year make the exposure profiles openguts ready. I.e. 
        # if concentration changes occurr this will not be completely explicit by
        # making jumps
        # this requires a method that adds a time point before any change if constant-forward
        if exposure_interpolation == "linear":
            experiment["exposure"] = experiment["exposure"].interpolate_na(dim="time", method="linear")
        else:
            experiment["exposure"] = experiment["exposure"].ffill(dim="time",)


        # TODO: What to do with interpolation
        return experiment

    @classmethod
    def to_openguts(cls, observations: xr.Dataset, path: str, time_unit: str):

        experiment = observations.rename({
            "time": f"time [{time_unit}]"
        })

        extra_dim = cls._get_exposure_dimension(observations.dims.keys())

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with pd.ExcelWriter(path) as writer:
            for coord in observations[extra_dim].values:
                experiment.exposure.sel({extra_dim: coord}).to_pandas().T.to_excel(writer, sheet_name=coord)
            experiment.survival.to_pandas().T.to_excel(writer, sheet_name="survival")
    


    def load_exposure_scenario(
        self, 
        data: Dict[str,pd.DataFrame],
        sheet_name_prefix: str = "",
        rect_interpolate=False

    ):

        self._obs_backup = self.observations.copy(deep=True)

        # read exposure array from file
        exposure_dim = [
            d for d in self.config.data_structure["exposure"].dimensions
            if d not in (self.config.simulation.x_dimension, self.config.simulation.batch_dimension)
        ]
        exposure = self._exposure_data_to_xarray(
            exposure_data=data, 
            dim=exposure_dim[0]
        )

        # combine with observations
        new_obs = xr.combine_by_coords([
            exposure,
            self.observations.survival
        ]).sel(id=exposure.id)
        
        self.observations = new_obs.sel(time=[t for t in new_obs.time if t <= exposure.time.max()])  # type: ignore
        self.config.simulation.x_in = ["exposure=exposure"]
        self.model_parameters["x_in"] = self.parse_input("x_in", exposure).ffill("time")  # type: ignore
        self.model_parameters["y0"] = self.parse_input("y0", drop_dims=["time"])

        self.dispatch_constructor()

    def export(self, directory: Optional[str] = None, mode: Literal["export", "copy"] = "export", skip_data_processing=True):
        self.config.simulation.skip_data_processing = skip_data_processing
        super().export(directory=directory, mode=mode)

    def export_to_scenario(self, scenario, force=False):
        """Exports a case study as a new scenario for running inference"""
        self.config.case_study.scenario = scenario
        self.config.case_study.data = None
        self.config.case_study.output = None
        self.config.case_study.scenario_path_override = None
        self.config.simulation.skip_data_processing = True
        self.save_observations(filename=f"observations_{scenario}.nc", force=force)
        self.config.save(force=force)

    @staticmethod
    def _condition_posterior(
        posterior: xr.Dataset, 
        parameter: str, 
        value: float, 
        exception: Literal["raise", "warn"]="raise"
    ):
        """TODO: Provide this method also to SimulationBase"""
        if parameter not in posterior:
            keys = list(posterior.keys())
            msg = (
                f"{parameter=} was not found in the posterior {keys=}. " +
                f"Unable to condition the posterior to {value=}. Have you "+
                "requested the correct parameter for conditioning?"
            )

            if exception == "raise":
                raise GutsBaseError(msg)
            elif exception == "warn":
                warnings.warn(msg)
            else:
                raise GutsBaseError(
                    "Use one of exception='raise' or exception='warn'. " +
                    f"Currently using {exception=}"
                )

        # broadcast value so that methods like drawing samples and hdi still work
        broadcasted_value = np.full_like(posterior[parameter], value)

        return posterior.assign({
            parameter: (posterior[parameter].dims, broadcasted_value)
        })


class GutsSimulationConstantExposure(GutsBase):
    t_max = 10
    def initialize_from_script(self):
        self.config.data_structure.B = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.D = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.H = DataVariable(dimensions=["time"], observed=False)
        self.config.data_structure.survival = DataVariable(dimensions=["time"], observed=False)

        # y0
        self.config.simulation.y0 = ["D=Array([0])", "H=Array([0])", "survival=Array([1])"]
        self.model_parameters["y0"] = self.parse_input(input="y0", drop_dims=["time"])

        # parameters
        self.config.model_parameters.C_0 = Param(value=10.0, free=False)
        self.config.model_parameters.k_d = Param(value=0.9, free=True)
        self.config.model_parameters.h_b = Param(value=0.00005, free=True)
        self.config.model_parameters.b = Param(value=5.0, free=True)
        self.config.model_parameters.z = Param(value=0.2, free=True)

        self.model_parameters["parameters"] = self.config.model_parameters.value_dict
        self.config.simulation.model = "guts_constant_exposure"

        self.coordinates["time"] = np.linspace(0,self.t_max)

    def use_jax_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.coordinates["time"] = np.array([0,self.t_max])
        self.config.simulation.model = "guts_constant_exposure"

        self.solver = JaxSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)

    def use_symbolic_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.coordinates["time"] = np.array([0,self.t_max])
        self.config.simulation.model = "guts_sympy"

        self.solver = mod.PiecewiseSymbolicSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)


class GutsSimulationVariableExposure(GutsSimulationConstantExposure):
    t_max = 10
    def initialize_from_script(self):
        super().initialize_from_script()
        del self.coordinates["time"]
        exposure = create_artificial_data(
            t_max=self.t_max, dt=1, 
            exposure_paths=["topical"]
        ).squeeze()
        self.observations = exposure

        self.config.data_structure.exposure = DataVariable(dimensions=["time"], observed=True)

        self.config.simulation.x_in = ["exposure=exposure"]
        x_in = self.parse_input(input="x_in", reference_data=exposure, drop_dims=[])
        x_in = rect_interpolation(x_in=x_in, x_dim="time")
        self.model_parameters["x_in"] = x_in

        # parameters
        self.config.model_parameters.remove("C_0")

        self.model_parameters["parameters"] = self.config.model_parameters.value_dict
        self.config.simulation.solver_post_processing = "red_sd_post_processing"
        self.config.simulation.model = "guts_variable_exposure"


    def use_jax_solver(self):
        # =======================
        # Define model and solver
        # =======================

        self.model = self._mod.guts_variable_exposure
        self.solver = JaxSolver

        self.dispatch_constructor(diffrax_solver=Dopri5)

    def use_symbolic_solver(self, do_compile=True):
        # =======================
        # Define model and solver
        # =======================

        self.model = self._mod.guts_sympy
        self.solver = self._mod.PiecewiseSymbolicSolver

        self.dispatch_constructor(do_compile=do_compile, output_path=self.output_path)

