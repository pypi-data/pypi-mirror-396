import os

import pandas as pd

from expyDB.intervention_model import (
    Experiment, Treatment, Timeseries, 
    PandasConverter,
)

def read_timeseries_sheet(path, sheet, sep=None):
    ts = pd.read_excel(path, sheet_name=sheet, index_col=0)  # type: ignore
    multi_index = pd.MultiIndex.from_tuples(
        [tuple(c.split(sep)) for c in ts.columns], names=["treatment_id", "timeseries_id"]
    )
    ts.columns = multi_index
    return ts

def ringtest(path, new_path):
    exposure = read_timeseries_sheet(path, sheet="Exposure", sep=" ")
    exposure.index.name = "time"
    survival = read_timeseries_sheet(path, sheet="Survival", sep=" ")
    survival.index.name = "time"

    # TODO: possibly using a normal index would also be acceptable
    template = PandasConverter(Experiment())
    # template.meta.index = template.meta_multiindex

    # extract information from the meta that is needed elsewhere
    data = {}
    data.update({"exposure": exposure})
    data.update({"survival": survival})


    map = [
        # new keys
        (None, ("experiment", "name"), lambda x: "Ring test"),
        (None, ("experiment", "interventions"), lambda x: ["exposure"]),
        (None, ("experiment", "observations"), lambda x: ["survival"]),
        (None, ("experiment", "public"), lambda x: True),

        (None, ("treatment", "medium"), lambda x: "water"),

        (None, ("observation", "unit"), lambda x: "-"),
        (None, ("observation", "time_unit"), lambda x: "day"),

        (None, ("intervention", "unit"), lambda x: "-"),
        (None, ("intervention", "time_unit"), lambda x: "day"),
    ]

    template.map_to_meta(map=map)
    template.data = data
    template.to_excel(new_path)

    return new_path

