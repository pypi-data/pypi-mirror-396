"""This module has been developed in the PollinERA project to deal with time of
death notation and add another import format.

TODO: Surpress warnings for too long sheet names
TODO: Skip files that have locked postprocessing files and give a warning
TODO: Give a Status message, which file is being processed
TODO: Apply these changes also to openguts.py
TODO: Write tests for the imports and produce templates. See test_data_import.py
"""


from typing import List
import os
import warnings
from datetime import timedelta
from guts_base.data.utils import datalad_locked_file_warning

import click
import pandas as pd
import numpy as np

# default columns
DEFAULT_COLUMNS_whitespace = dict(
    id_subject = ["id subject", "subject id", "id", "id bee"],
    id_treatment = ["id treatment", "treatment id", "treatment"],
    id_replicate = ["id replicate", "replicate id", "replicate name", "replicate"],
    n = ["individuals", "n", "number_replicates", "n_individuals", "replicates"],
    censored = ["cenzus", "censoring", "escaped"],
    time_start_experiment = ["date of start", "experiment start", "start experiment"],
    time_end_experiment = ["date of end", "experiment end", "end experiment"],
    time_start_exposure = ["time of exposure start", "start exposure", "exposure start"],
    time_end_exposure = ["time of exposure end", "end exposure", "exposure end"],
    time_death = ["time of death", "survival time", "date of death"],
)

DEFAULT_COLUMNS_underscore = {
    k: [v_.replace(" ", "_") for v_ in v] 
    for k, v in DEFAULT_COLUMNS_whitespace.items()
}

DEFAULT_COLUMNS = {
    k: list(set(DEFAULT_COLUMNS_whitespace[k] + DEFAULT_COLUMNS_underscore[k]))
    for k in DEFAULT_COLUMNS_whitespace.keys()
}

REQUIRED_COLUMNS = dict(
    id_subject = True,
    id_treatment = True,
    id_replicate = False,
    censored = False,
    n = False,
    time_start_experiment = True,
    time_end_experiment = False,
    time_start_exposure = True,
    time_end_exposure = True,
    time_death = True,
)



def clean_column_names(columns: List[str]):
    cleaned_columns = []
    for c in columns:
        c = c.lower()  # convert to lowercase
        c = c.strip()  # strip leading and trailing whitespace
        c = c.replace(" ", "_")
        c = c.replace("[", "")
        c = c.replace("]", "")
        c = c.replace("/", "_")

        cleaned_columns.append(c)

    return cleaned_columns

def standardize_column_names(
        columns: List[str], 
        raise_error=True, 
        ignore_columns=[]
    ):
    column_mapper = invert_dict_of_lists(DEFAULT_COLUMNS)
    standardized_columns = []
    for c in columns:
        c = column_mapper.get(c, c) # try to get a standard value for the column

        standardized_columns.append(c)

    missing_columns = [
        k for k in DEFAULT_COLUMNS.keys() 
        if k not in standardized_columns and k not in ignore_columns
    ]
    if len(missing_columns) > 0 and raise_error:
        raise KeyError(
            f"Not all necessary columns could be found. {missing_columns} "
            "could not identified. Rename columns or add the corresponding "
            "columns in the mapper."
        )

    return standardized_columns


def invert_dict_of_lists(original_dict):
    inverted_dict = {}
    for key, value_list in original_dict.items():
        for value in value_list:
            inverted_dict[value] = key
    return inverted_dict

def long_to_wide(df_long, id_columns, time_column, observation_column):
        df_long["id"] = df_long[id_columns].apply(
            lambda x: '__'.join(x.astype(str)), axis=1
        )
        
        df_wide = df_long.pivot(
            # data=df_long.reset_index(), 
            index=time_column,
            values=observation_column, 
            columns="id", 
        )
        
        return df_wide

def wide_to_long(df_wide, id_columns, time_column, observation_column):
    df_long = pd.melt(
        frame=df_wide.reset_index(), 
        value_vars=df_wide.columns,
        id_vars=time_column,
        var_name="id",
        value_name=observation_column
    )

    df_long[id_columns] = df_long.id.str.split("__", n=1, expand=True)
    df_long = df_long.drop(columns="id")
    return df_long[id_columns+[time_column, observation_column]]


def get_unique_value(series, action_if_not_unique="mean"):
    if series.nunique() == 1:
        return series.drop_duplicates().iloc[0]
    else:
        if action_if_not_unique == "mean":
            return series.mean()
        elif action_if_not_unique == "max":
            return series.max()
        elif action_if_not_unique == "min":
            return series.min()
        elif action_if_not_unique == "error":
            raise ValueError("Start time contains non unique values")
        else:
            raise NotImplementedError("Aggregation action is not implemented.")


def make_openguts_intervention_table(
        df: pd.DataFrame, 
        intervention:str,
        intervention_time_unit:str="d",
        rect_interpolate=True,
    ) -> List[pd.DataFrame]:
    # create exposure tables
    id_columns = ["id_treatment", "id_replicate"]
    time_column = f"time [{intervention_time_unit}]"
    
    df_long = []
    for (tid, rid), group in df.groupby(id_columns):
        intervention_value = float(group[intervention].unique())
        if f"time_start_exposure_{intervention}" in group:
            intervention_start = get_unique_value(group[f"time_start_exposure_{intervention}"])
        else:
            intervention_start = get_unique_value(group["time_start_exposure"])
        if f"time_end_exposure_{intervention}" in group:
            intervention_end = get_unique_value(group[f"time_end_exposure_{intervention}"])
        else:
            intervention_end = get_unique_value(group["time_end_exposure"])

        experiment_start = get_unique_value(group["time_start_experiment"])
        experiment_end = get_unique_value(group["time_end_experiment"])

        time = np.array([
            experiment_start,
            intervention_start,
            intervention_end,
            experiment_end
        ])

        value = np.array([0, intervention_value, 0, 0])

        m = pd.DataFrame(
            data=np.column_stack([
                np.repeat(tid, len(time)), 
                np.repeat(rid, len(time)), 
                time, value
            ]), 
            columns=list(group[id_columns].columns) + [time_column, intervention]
        )
        # this throws the first value out if the time of exposure start is
        # identical to the exposure end
        m = m.drop_duplicates(subset=id_columns + [time_column], keep="last")

        df_long.append(m)

    df_long = pd.concat(df_long)
    df_wide =  long_to_wide(df_long, id_columns, time_column, intervention).reset_index()
    df_wide[time_column] = (df_wide[time_column] - experiment_start)
    df_wide = df_wide.set_index(time_column)
    
    if rect_interpolate:
        df_wide = df_wide.reindex(np.unique(np.concatenate([
            np.array(list(df_wide.index)),
            np.array(list(df_wide.index - pd.Timedelta(1, "s")))[1:]
        ])))
        df_wide = df_wide.fillna(method="ffill")
    
    df_wide.index = df_wide.index / pd.Timedelta(1, "d")
    return df_wide



def make_openguts_observation_table(
        df: pd.DataFrame,
        observation="censored",
        observation_schedule:str="d",
    ) -> List[pd.DataFrame]:
    """returns counts of censored individuals"""
    df = df.copy()
    
    experiment_start = get_unique_value(df["time_start_experiment"])
    experiment_end = get_unique_value(df["time_end_experiment"])

    times_nominal = pd.date_range(experiment_start, experiment_end, freq=observation_schedule)
    timecol_name = f"time [{observation_schedule.lower()}]"


    id_columns = ["id_treatment", "id_replicate"]

    # calculate survival time
    df[timecol_name] = df["time_death"] - df["time_start_experiment"]

    # this seems to have been necessary, because reindexing removed times smaller than
    # the observation_schedule interval. This is now resolved by concatenating true
    # times and nominal times
    # TODO: remove this commented block when there appear no more errors
    # time_remainder = df[timecol_name] % pd.Timedelta(1, observation_schedule)
    # if (time_remainder > pd.Timedelta(0)).any():
    #     raise ValueError(
    #         "Observations should be entered at the same time as the experiment start "+
    #         "df['time_death] - df['time_experiment_start'] should be a multiple of "+
    #         f"the time resolution of the observation schedule. Here: 1{observation_schedule}"
    #     )

    if observation == "censored":
        # sum IDs that were marked as censored at time t
        df_long = df.groupby(id_columns+[timecol_name])["censored"].sum()

    elif observation == "lethality":
        # count IDs that died at time t
        df_long = df.groupby(id_columns+[timecol_name])["time_death"].count()

    else:
        raise NotImplementedError(f"observation {observation} is not implemented.")

    df_long = df_long.rename(observation)
    
    # df to wide frame
    df_wide = long_to_wide(df_long.reset_index(), id_columns, timecol_name, observation)
    
    # get a time vector that contains all nominal observation times and also actually
    # occurred days 
    observation_times = np.unique(np.concatenate([df_wide.index, times_nominal-experiment_start]))

    # reindex wide dataframe on time
    df_wide = df_wide.reindex(index=observation_times, method=None)
    df_wide.index = df_wide.index.set_names(timecol_name)
    df_wide = df_wide.fillna(0)

    return df_wide


# write to excel file
def excel_writer(df: pd.DataFrame, file, sheet):
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore")
        if not os.path.exists(file):
            with pd.ExcelWriter(file, mode="w") as writer:
                df.to_excel(writer, sheet_name=sheet)

        else:
            with pd.ExcelWriter(file, if_sheet_exists="replace", mode="a") as writer:
                df.to_excel(writer, sheet_name=sheet)

def write_data_template(
        notation="time_of_death",
        time_start_experiment=()
    ):
    pass

def time_to_fraction(data, column, experiment_start):
    data


class TimeOfDeathIO:
    def __init__(
        self, 
        file, 
        intervention_columns: List[str],
        sheet:str = "time-of-death",
    ):
        self._file = file
        self.data = self.from_file()

def main(file: str, sheet: str, out:str, intervention_columns: List[str], 
         extra_observation_columns: List[str] = [],
         observation_schedule="d", rect_interpolate=False):
    intervention_columns = clean_column_names(list(intervention_columns))
    extra_observation_columns = clean_column_names(list(extra_observation_columns))
    processed_file = f"{out}/openguts_{os.path.basename(file)}"
    
    print("\n")
    print(f"Processing File: {file}")
    print(f"Converting from time-of-death to openguts")
    print("-----------------------------------------")

    if os.access(processed_file, os.EX_OK):
        if not os.access(processed_file, os.W_OK):
            datalad_locked_file_warning(processed_file)
            return
    else:
        directory = os.path.dirname(processed_file)
        if os.access(directory, os.EX_OK):
            pass
        else:
            os.makedirs(directory)

    # read datafile
    data = pd.read_excel(io=file, sheet_name=sheet)
    data.columns = clean_column_names(data.columns)

    # Assumptions
    # -----------
    # this should not be too small, Bürger and Focks (2025) assume a topical exposure
    # duration of 1 hour. If exposure duration is too small, it will result in
    # problems with k_d
    exposure_duration = timedelta(seconds=3600)
    exposure_start_delay = timedelta(hours=0)
    id_zfill = 2  # number of zeros to pad ID column values with
    
    # standardize columns
    data.columns = standardize_column_names(data.columns, raise_error=False)
    data["id_treatment"] = data["id_treatment"].astype(str).str.zfill(id_zfill)

    # add optional columns to the dataframe if they are not present
    experiment_start = get_unique_value(data["time_start_experiment"])
    if "time_start_exposure" not in data:
        warnings.warn(
            "No column: 'time_start_exposure'. " 
            f"Assuming time_start_exposure=time_start_experiment"
            f"({experiment_start}) + {exposure_start_delay}",
            category=UserWarning
        )
        exposure_start = experiment_start + exposure_start_delay
        data["time_start_exposure"] = exposure_start
    
    if "time_end_exposure" in data:
        if (data["time_start_experiment"] == data["time_end_exposure"]).all():
            warnings.warn(
                "'time_end_exposure' equals 'time_start_exposure'. "+
                "Removing column 'time_end_exposure'"
            )
            data = data.drop("time_end_exposure", axis=1)
    
    if "time_end_exposure" not in data:
        exposure_start = data["time_start_exposure"]
        warnings.warn(
            "No column: 'time_end_exposure'. " 
            f"Assuming time_end_exposure=time_start_exposure + {exposure_duration}",
            category=UserWarning
        )
        exposure_end = exposure_start + exposure_duration
        data["time_end_exposure"] = exposure_end

    if "time_end_experiment" not in data:
        experiment_end = data.time_death.max()
        warnings.warn(
            "No column: 'time_end_experiment' "
            f"Using the time of the last observation: {experiment_end}",
            category=UserWarning
        )
        data["time_end_experiment"] = experiment_end

    if "id_replicate" not in data:
        warnings.warn(
            "No column: 'id_replicate'. " 
            "Assuming all treatments were only carried out with 1 replicate "
            "(containing n individuals).",
            category=UserWarning
        )
        data["id_replicate"] = 0
        
        # check for replicates
        id_columns = ["id_treatment"]
        for rid, (_, group) in enumerate(data[id_columns+intervention_columns]
                                         .groupby(id_columns)):
            data.loc[group.index, "id_replicate"] = rid + 1

        data["id_replicate"] = data["id_replicate"].astype(str).str.zfill(id_zfill)
        id_columns = ["id_treatment", "id_replicate"]

    elif data["id_replicate"].isna().all():
        warnings.warn(
            "column: 'id_replicate' contained only NAN values" 
            "Assuming all treatments were only carried out with 1 replicate "
            "(containing n individuals).",
            category=UserWarning
        )
        data["id_replicate"] = 0
        
        # check for replicates
        id_columns = ["id_treatment"]
        for rid, (_, group) in enumerate(data[id_columns+intervention_columns]
                                         .groupby(id_columns)):
            data.loc[group.index, "id_replicate"] = rid + 1

        data["id_replicate"] = data["id_replicate"].astype(str).str.zfill(id_zfill)
        id_columns = ["id_treatment", "id_replicate"]
    else:
        data["id_replicate"] = data["id_replicate"].astype(str)
        data["id_treatment"] = data["id_treatment"].astype(str)
        id_columns = ["id_treatment", "id_replicate"]

    if "censored" not in data:
        warnings.warn(
            "No column: 'censoring'. " 
            "Assuming all observation are not censored, meaning each "
            "'time of death' indication comes from an individual that was "
            "observed dead at that time (as opposed to escaped or removed from "
            "the experiment)",
            category=UserWarning
        )
        data["censored"] = 0

    data.columns = standardize_column_names(data.columns, raise_error=True, ignore_columns=["n"])

    (data["time_start_experiment"] - experiment_start).dt.seconds
    (data["time_start_experiment"] - experiment_start).dt.seconds

    interventions = []
    for iv in intervention_columns:
        iv_wide = make_openguts_intervention_table(
            data, 
            intervention=iv, 
            intervention_time_unit="d",
            rect_interpolate=rect_interpolate,
        )
        interventions.append(iv_wide)
        excel_writer(iv_wide, file=processed_file, sheet=iv)

    censored = make_openguts_observation_table(
        data,
        observation="censored",
        observation_schedule=observation_schedule,
    )

    lethality = make_openguts_observation_table(
        data,
        observation="lethality",
        observation_schedule=observation_schedule,
    )

    _extra_observations = []
    for eob in extra_observation_columns:
        ob_wide = make_openguts_observation_table(
            data,
            observation=eob,
            observation_schedule=observation_schedule
        )
        _extra_observations.append(ob_wide)
        excel_writer(ob_wide, file=processed_file, sheet=eob)


    deaths = lethality - censored

    # excel export
    excel_writer(censored, file=processed_file, sheet="censored")
    excel_writer(lethality, file=processed_file, sheet="lethality (uncensored)")
    excel_writer(deaths, file=processed_file, sheet="lethality (censored)")


    cens_long = wide_to_long(censored, id_columns, f"time [{observation_schedule}]", "censored")
    leth_long = wide_to_long(lethality, id_columns, f"time [{observation_schedule}]", "lethality")
    
    if "n" in data:
        if data["n"].isna().all():
            warnings.warn(
                "column: 'n' contained only NAN values. "+
                "Removed (so it can be created from scratch)",
                category=UserWarning
            )
            data = data.drop("n", axis=1)
        else:
            pass

    if "n" not in data:
        warnings.warn(
            "No column: 'n'. " 
            "Inferring the number of individuals at the beginning of the "
            "experiment from the uncensored number of dead organisms "
            "(including those escaped and alive at the end of the experiment).",
            category=UserWarning
        )
        n = leth_long.groupby(id_columns)["lethality"].sum().rename("n")
        data = pd.merge(data, n.reset_index(), on=id_columns, how="left")


    # calculate survival 
    n = data.groupby(id_columns)["n"].agg("unique").astype(int)
    survival = pd.merge(leth_long, n, on=id_columns, how="left")
    mortality = survival.groupby(id_columns)["lethality"].cumsum()
    survival["survival"] = survival["n"] - mortality
    survival_wide = long_to_wide(survival, id_columns, f"time [{observation_schedule}]", "survival")
    excel_writer(survival_wide, file=processed_file, sheet="survival")
    
    # Calculate the number of present organisms just after censoring
    # n_observed_after_censoring = survival_wide.copy()
    # n_observed_after_censoring[survival_wide.columns] = np.row_stack([
    #     survival_wide.iloc[0].values,
    #     survival_wide.iloc[:-1].values - censored.iloc[1:].values
    # ])
    # excel_writer(n_observed_after_censoring, file=processed_file, 
    #              sheet="n_observed_after_censoring")


    # Calculate the number of organisms alive after the last observation
    n_observed_after_last_observation = survival_wide.copy()
    n_observed_after_last_observation[survival_wide.columns] = np.row_stack([
        np.full_like(survival_wide.iloc[0].values, np.nan),
        survival_wide.iloc[:-1].values
    ])
    excel_writer(n_observed_after_last_observation, file=processed_file, 
                 sheet="n_observed_after_last_observation")


    data.columns = standardize_column_names(data.columns)
    data_minimal = data[list(DEFAULT_COLUMNS.keys()) + intervention_columns]
    excel_writer(data_minimal.set_index("id_subject"), file=processed_file, 
                 sheet="time_of_death")

    if "meta" in pd.ExcelFile(file).sheet_names:
        excel_writer(
            df=pd.read_excel(file, sheet_name="meta").set_index("Metadata"),
            file=processed_file,
            sheet="meta"
        )
    elif "Info" in pd.ExcelFile(file).sheet_names:
        metadata = pd.read_excel(io=file, sheet_name="Info")
        metadata = metadata.set_index("Experiment information")
        metadata.columns = ["value", "description"]
        metadata.loc["interventions", "value"] = ", ".join(intervention_columns)
        metadata.loc["observations", "value"] = ", ".join(["survival", "censored"])
        excel_writer(metadata, file=processed_file, sheet="meta")
    else:
        warnings.warn("No metadata found in sheets 'meta' or 'Info'.")

    return processed_file

@click.command()
@click.option("--file", "-f", help="Path to the xlsx file")
@click.option("--sheet", "-s", help="Name of the excel sheet")
@click.option("--out", "-o", help="Output directory", default="processed_data")
@click.option("--observation_schedule", help="Schedule of the observations: d - daily, h - hourly", default="d")
@click.option("--intervention_columns", "-c", multiple=True, type=str, help="Names of the columns that carry the exposure information")
@click.option("--extra_observation_columns", "-e", multiple=True, type=str, default=[], help="Names of the columns that carry additional observations beside time-of-death and censoring")
def time_of_death_to_openguts(file, sheet, out, observation_schedule, intervention_columns, extra_observation_columns):
    _ = main(
        file=file, 
        sheet=sheet, 
        out=out, 
        intervention_columns=intervention_columns,
        extra_observation_columns=extra_observation_columns,
        observation_schedule=observation_schedule
    )


if __name__ == "__main__":


    if os.path.basename(os.getcwd()) != "data":
        os.chdir("case_studies/tktd-osmia/data")
        # call the underlying function
        ctx = click.Context(time_of_death_to_openguts)
        ctx.forward(
            time_of_death_to_openguts,
            file="test/template_time_of_death.xlsx",
            sheet="time-of-death",
            intervention_columns=["Substance_A", "Substance B"],
        )
    else:
        time_of_death_to_openguts()
