from cycler import cycler
import numpy as np
import arviz as az
from matplotlib import pyplot as plt

from pymob.sim.plot import SimulationPlot
from pymob import SimulationBase

def plot_prior_predictions(
    sim: SimulationBase, 
    data_vars=["survival"],
    title_func=lambda sp, c: f"{sp.observations.id.values[0]}"
):
    idata = sim.inferer.prior_predictions() # type: ignore
    def plot_survival_data_probs(idata):
        return idata["survival"] * sim.observations.sel(id=[id_], time=0).survival
    
    fig, axes = plt.subplots(
        ncols=sim.observations.dims["id"], nrows=len(data_vars), 
        sharex=True, sharey="row", figsize=(30,10), squeeze=False)
    for i, id_ in enumerate(sim.coordinates["id"]):
        simplot = SimulationPlot(
            observations=sim.observations.sel(id=[id_]),
            idata=idata.sel(id=[id_]),  # type: ignore
            rows=data_vars,
            coordinates=sim.coordinates,
            config=sim.config,
            obs_idata_map={
                "survival": plot_survival_data_probs
            },
            idata_groups=["prior_model_fits"],  # type: ignore
        )
        # replace simplot axis
        for j, k in enumerate(simplot.rows):
            simplot.axes_map[k]["all"] = axes[j][i]

        simplot.plot_data_variables()
        simplot.set_titles(title_func)
        for j, k in enumerate(simplot.rows):
            if i != 0:
                simplot.axes_map[k]["all"].set_ylabel("")
            if j != 3:
                simplot.axes_map[k]["all"].set_xlabel("")

        simplot.close()
    
    fig.tight_layout()
    fig.savefig(f"{sim.output_path}/combined_prior_predictions.png")


def plot_posterior_predictions(
    sim: SimulationBase, 
    data_vars=["survival"],
    title_func=lambda sp, c: f"{sp.observations.id.values[0]}",
    groups=["posterior_model_fits", "posterior_predictive"],
):
    fig, axes = plt.subplots(
        ncols=sim.observations.dims["id"], nrows=len(data_vars), 
        sharex=True, sharey="row", figsize=(30,10), squeeze=False
    )

    def plot_survival_data_probs_and_preds(dataset):
        if dataset.attrs["group"] == "posterior_model_fits":
            return dataset["survival"] * sim.observations.sel(id=[id_], time=0).survival
        if dataset.attrs["group"] == "posterior_predictive":
            return dataset["survival"]

    for i, id_ in enumerate(sim.coordinates["id"]):
        simplot = SimulationPlot(
            observations=sim.observations.sel(id=[id_]),
            idata=sim.inferer.idata.sel(id=[id_]),  # type: ignore
            rows=data_vars,
            coordinates=sim.coordinates,
            config=sim.config,
            obs_idata_map={
                "survival": plot_survival_data_probs_and_preds,
            },
            idata_groups=groups,  # type: ignore
        )
        
        # replace simplot axis
        for j, k in enumerate(simplot.rows):
            simplot.axes_map[k]["all"] = axes[j][i]

        simplot.plot_data_variables()
        simplot.set_titles(title_func)
        for j, k in enumerate(simplot.rows):
            if i != 0:
                simplot.axes_map[k]["all"].set_ylabel("")
            if j != 3:
                simplot.axes_map[k]["all"].set_xlabel("")

        simplot.close()
    
    fig.tight_layout()
    fig.savefig(f"{sim.output_path}/combined_posterior_predictions.png")


def plot_survival(sim: SimulationBase, results):
    fig, ax = plt.subplots(1,1)
    obs = sim.observations.survival / sim.observations.subject_count
    ax.plot(sim.observations.time, obs.T, marker="o", color="black")
    ax.plot(results.time, results.survival.T, color="black")


def plot_survival_multipanel(sim: SimulationBase, results, ncols=6, title=lambda _id: _id, filename="survival_multipanel"):

    n_panels = results.sizes["id"]

    nrows = int(np.ceil(n_panels / ncols))

    fig, axes = plt.subplots(nrows, ncols, sharex=True, sharey=True, figsize=(ncols*2+2, nrows*1.5+2))
    axes = axes.flatten()
    mean = results.mean(("chain", "draw"))
    hdi = az.hdi(results, 0.95)
    survival = sim.observations.survival / sim.observations.survival.isel(time=0)

    plot_kwargs = {"color": "black"}
    # param_cycler = plt.rcParams['axes.prop_cycle']
    for _id, ax in zip(sim.observations.id.values, axes):
        ax.set_ylim(-0.05,1.05)

        ax.set_xlabel(f"Time [{sim.config.guts_base.unit_time}]")
        ax.set_ylabel("Survival")
        ax.plot(mean.time, mean.sel(id=_id).survival.T, **plot_kwargs)
        ax.fill_between(hdi.time, *hdi.sel(id=_id).survival.T, alpha=.5, **plot_kwargs) # type: ignore
        ax.plot(survival.time, survival.sel(id=_id).T, ls="", marker="o", alpha=.5, **plot_kwargs)
        ax.set_title(title(_id))

    out = f"{sim.output_path}/{filename}.png"
    fig.tight_layout()
    fig.savefig(out)

    return out

def plot_exposure_multipanel(sim: SimulationBase, results, ncols=6, title=lambda _id: _id, filename="exposure_multipanel"):

    n_panels = results.sizes["id"]

    nrows = int(np.ceil(n_panels / ncols))

    fig, axes = plt.subplots(nrows, ncols, sharex=True, figsize=(ncols*2+2, nrows*1.5+2))
    axes = axes.flatten()
    mean = results

    plot_kwargs = {"color": "black"}
    custom_cycler = (
        cycler(ls=["-", "--", ":", "-."])
    )

    labels = {}
    for _id, ax in zip(sim.observations.id.values, axes):
        ax.set_prop_cycle(custom_cycler)

        ax.set_xlabel(f"Time [{sim.config.guts_base.unit_time}]")
        ax.set_ylabel("Exposure")
        for expo in sim.coordinates[sim._exposure_dimension]: # type: ignore
            line, = ax.plot(
                mean.time, mean.sel({"id":_id, sim._exposure_dimension: expo}).exposure, # type: ignore
                **plot_kwargs, label=f"Exposure: {expo}"
            )
            labels.update({f"Exposure: {expo}": line})
        ax.set_title(title(_id))

    fig.legend(labels.values(), labels.keys(), loc='lower center', fontsize=10, frameon=False)
    out = f"{sim.output_path}/{filename}.png"
    fig.tight_layout(rect=[0,0.05,1.0,1.0], ) # type: ignore
    fig.savefig(out)

    return out

def multipanel_title(sim, _id): 
    oid = sim.observations.sel(id=_id)
    exposure_path = oid.exposure_path.values
    rac = np.round(oid.concentration_closer_x_rac.max().values  * 100, 3)
    return "{ep}\n{c} %RAC".format(ep=str(exposure_path), c=str(rac))

def plot_intermediate_results(sim: SimulationBase, id=0):
    e = sim.dispatch()
    e()
    e.results

    results = e.results.isel(id=[id])

    plot_results(results=results, batch_dim=sim.config.simulation.batch_dimension)

def plot_results(results, batch_dim="id", axes=None, **plot_kwargs):
    datavars = list(results.data_vars.keys())
    if axes is None:
        fig, axes = plt.subplots(len(datavars), 1)

    for ax, dv in zip(axes, datavars):
        res = results[dv]
        if len(res.shape) > 2:
            res_ = res.transpose(..., "time", batch_dim)
            for r in res_:
                ax.plot(r.time, r, **plot_kwargs)
        else:
            ax.plot(results.time, res.transpose("time", batch_dim), **plot_kwargs)

        ax.set_ylabel(dv)
