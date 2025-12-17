from typing import List, Optional, Callable, Dict, Any, Tuple
from importlib import import_module
import warnings

import numpy as np
import pandas as pd
from expyDB.database_operations import create_database, experiment_to_db
from pymob.sim.config import dict_to_string

import glob
import os

import click
import pandas as pd

from expyDB.intervention_model import to_expydb, Experiment, PandasConverter
from guts_base.data.utils import datalad_locked_file_warning

def test_equality_of_exposure_patterns_in_treatment(df):
    for _, group in df.groupby("treatment_id"):
        exposures = group.pivot_table(
            # values="value", 
            index=["time", "treatment_id"], 
            columns="replicate_id"
        )

        equal_expo = exposures.values == exposures.values[:, ].reshape((-1, 1))
        if not np.all(equal_expo):
            raise RuntimeError(
                "Replicates in the same treatment ID have different exposure patterns."
            )
        
def create_new_columns_and_test_integrity_of_replicates(
    exposure, survival, n_reps, path
):
    assert np.all(exposure.columns == survival.columns)
    
    columns_new, treatment_reps = identify_replicates(frame=exposure)

    if not np.all(np.array(list(treatment_reps.values())) == n_reps):
        warnings.warn(
            f"Actual treatment replicates are different from "
            f"replicates ({n_reps}), given in Info sheet in file: "
            f"{path}"
        )

    return columns_new

def identify_replicates(frame):
    df = frame.drop(columns="time")

    # Find identical columns and assign group labels
    group_labels = {}
    used_cols = set()
    treatment_map = {}

    for col in df.columns:
        if col not in used_cols:
            # compare the column to each column of the dataframe with 
            # df.apply(func, axis=0) and get the column names
            identical_cols = df.columns[df.apply(lambda x: x.equals(df[col]), axis=0)].tolist()
            group_label = f'{len(group_labels) + 1}'
            group_labels[group_label] = identical_cols
            used_cols.update(identical_cols)

            for icol in identical_cols:
                treatment_map.update({icol: group_label})

    columns_new = [f"{treatment_map[col]}__{col}" for col in df.columns]
    treatment_reps = {key: len(cols) for key, cols in group_labels.items()}

    return columns_new, treatment_reps



def read_timeseries_sheet(path, sheet, sep=None):
    ts = pd.read_excel(path, sheet_name=sheet, index_col=0)  # type: ignore
    multi_index = pd.MultiIndex.from_tuples(
        [tuple(c.split(sep)) for c in ts.columns], names=["treatment_id", "timeseries_id"]
    )
    ts.columns = multi_index
    return ts


class OpenGutsIO:
    # TODO: Use preprocessing here and use map as a class attribute
    def __init__(self, file):
        self._file = file
        self.data = self.from_file(file)

    def _openguts_wide_to_long(self, frame, columns_new):
        frame_wide = frame.copy()

        frame_wide.columns = ["time"] + columns_new
        frame_long = pd.melt(
            frame=frame_wide, 
            id_vars=["time"], 
            value_vars=columns_new,
            var_name="exposure_id"
        )
        # create new index columns from new column names
        frame_long[["treatment_id", "replicate_id"]] = frame_long\
            .exposure_id.str.split("__", n=1, expand=True)
        frame_long = frame_long.drop(columns="exposure_id")
        
        return frame_long


    def _merge_tables(self, tables: List):
        data = tables.pop(0).set_index(["time", "treatment_id", "replicate_id"])

        for expo in tables:
            rdata =expo.set_index(["time", "treatment_id", "replicate_id"])
            data = pd.merge(
                left=data, 
                right=rdata, 
                how="left", 
                left_index=True, 
                right_index=True
            )

        return data

    def _read_timeseries(self, path, sheets):
        # design new columns based on the information about replicates and treatments
        timeseries_long_list = []
        timeseries_column_list = []
        time_units = {}
        for iv in sheets:
            timeseries_df = pd.read_excel(path, sheet_name=f"{iv}") 

            time_column = timeseries_df.columns[0]
            time_unit = time_column.lower().replace("time", "").strip(" []")

            # define replicates based on equality of columns
            timeseries_columns = [c for c in timeseries_df.columns[1:]]
            timeseries_long = self._openguts_wide_to_long(
                frame=timeseries_df, columns_new=timeseries_columns
            )
            intervention_long = timeseries_long.rename(columns={"value": iv})
            timeseries_long_list.append(intervention_long)
            timeseries_column_list.append(timeseries_columns)
            time_units.update({iv: time_unit})

        return self._merge_tables(timeseries_long_list).reset_index(), time_units


    def _read_openguts(self, path, metadata_sheetname="meta"):
        meta = pd.read_excel(path, sheet_name=metadata_sheetname, index_col=0).dropna(how="all")
        interventions = meta.loc["experiment__interventions","Value"]
        if interventions is None:
            raise ValueError("'experiment__interventions' must be defined in metadata")
        else:
            intervention_sheets = [i.strip("[]' ") for i in interventions.split(",")]  # type: ignore
        
        observations = meta.loc["experiment__observations","Value"]
        if observations is None:
            raise ValueError("'experiment__observations' must be defined in metadata")
        else:
            observation_sheets = [i.strip("[]' ") for i in observations.split(",")]  # type: ignore
        
        # survival_df = pd.read_excel(path, sheet_name="survival") 
        # survival_df = survival_df.rename(columns={"time [d]": "time"})

        # design new columns based on the information about replicates and treatments
        interventions_long, interventions_time_units = self._read_timeseries(path, intervention_sheets)
        observations_long, observations_time_units = self._read_timeseries(path, observation_sheets)
        time_unit = {
            "interventions": interventions_time_units,
            "observations": observations_time_units
        }

        # TODO test if all exposures within a treatment (replicates) were nominally the same 
        # test_equality_of_exposure_patterns_in_treatment(df=exposures_long)

        return interventions_long, observations_long, meta, time_unit

    def from_file(self, file) -> None:
        (
            interventions_long, 
            observations_long, 
            meta, 
            time_unit
        ) = self._read_openguts(path=file)

        self.interventions = interventions_long
        self.observations = observations_long
        self.time_unit = time_unit
        self.meta = meta

    def to_file(self, file):
        raise NotImplementedError(
            "This method should implement writing an excel file that corresponds"
            "to the original input file."
        )
    
    def to_experiment(self) -> Experiment:
        return Experiment.from_dict(data=dict(
            interventions=self.interventions, 
            observations=self.observations,
            meta=self.meta,
            time_units=self.time_unit
        ))

    def from_experiment(self, experiment: Experiment) -> None:
        data = experiment.to_dict()
        self.interventions=data["interventions"],
        self.observations=data["observations"],
        self.meta=data["meta"],
        self.time_units=data["time_units"],

    def to_xarray(self):
        return self.to_experiment().to_xarray()


def import_data_to_database(path, database, preprocessing: Optional[Callable] = None, preprocessing_out: Optional[str] = None):
    """This script takes raw data, preprocesses it to contain all 
    necessary metadata for expyDB. Then it creates an experiment Model and 
    processes adds it to the database
    """
    # preprocess path
    if preprocessing is not None:
        if preprocessing_out is None:
            filename = os.path.dirname(path)
            directory = os.path.basename(filename)
            new_path = path.replace(directory, f"processed_{directory}")
        else:
            filename = os.path.basename(path)
            new_path = preprocessing_out.format(filename=filename)

        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        processed_path = preprocessing(path, new_path)
    else:
        processed_path = path

    # Preprocess excel to interventions and observations in Long form and a 
    # metadata Series as well as a default time unit
    openguts = OpenGutsIO(processed_path)
    
    # From excel to an Experiment Model instance
    experiment = openguts.to_experiment()

    # from the Model to the Database
    if not os.access(database, os.W_OK):
        warnings.warn(
            f"Did not write to database. The file '{database}' does "
            "not have write access."
        )
        return
    
    experiment.to_database(database=database)

    print("Import to database successful.")


def create_database_and_import_data_main(datasets_path, database_path, preprocessing=None, preprocessing_out=None):
    print("\n")
    print(f"Creating a database and importing data")
    print(f"======================================")

    if preprocessing is not None:
        module, func = preprocessing.rsplit(".", 1)
        mod = import_module(module)
        preprocessing_func = getattr(mod, func)
    else:
        preprocessing_func = None

    paths = []
    for p in datasets_path:
        if os.path.isfile(p):
            paths.append(p)
        else:
            paths.extend(glob.glob(os.path.join(p, "*.xlsx")))

    create_database(database=database_path, force=True)
    for p in paths:
        print(f"\nPreprocessing and importing file: {p}")
        import_data_to_database(
            path=p, database=database_path, 
            preprocessing=preprocessing_func,
            preprocessing_out=preprocessing_out
        )

@click.command()
@click.option("--datasets_path", type=str, multiple=True, help="The path to the directory where the excel files are located. Alternatively, use multiple times with paths to files")
@click.option("--database_path", type=str, help="The path to the database (should end with .db)")
@click.option("--preprocessing", type=str, help="Function used to preprocess the data", default=None)
@click.option("--preprocessing-out", type=str, help="A pattern that uses {filename} as a placeholder e.g. 'data/processed_data/{filename}. If unset, preprends 'processes_' to the dirname", default=None)
def create_database_and_import_data(datasets_path, database_path, preprocessing, preprocessing_out):
    create_database_and_import_data_main(
        datasets_path=datasets_path,
        database_path=database_path,
        preprocessing=preprocessing,
        preprocessing_out=preprocessing_out
    )