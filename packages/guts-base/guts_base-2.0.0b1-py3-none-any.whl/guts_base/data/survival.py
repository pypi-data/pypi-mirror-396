import numpy as np
import xarray as xr
from scipy.stats import binom
from matplotlib import pyplot as plt
from pymob.utils.testing import assert_no_nans_in_dataset

def prepare_survival_data_for_conditional_binomial(observations: xr.Dataset) -> xr.Dataset:
    """This is a convenience method for preparing survival data for a 
    conditional binomial model. The method simply prepares an array of the
    same size as survival just shifted by one time step to determine the
    number of survivers at the beginning of the next time step to consider
    conditional surviving of repeated observations.
    
    The additional dataset fills NaN values which may occurr in the observations
    but not in the parameters of the distribution by forward filling and
    then fills remaining nans (which can only ocurr in the initial times t)
    with the nominal number of used organisms.
    """
    survival = observations["survival"]
    # fill nan values forward in time with the last observation 
    # until the next observation. Afterwards leading nans are replaced with 
    # the subject count (no lethality observed before the first observation)
    nsurv = survival.ffill(dim="time").fillna(observations.subject_count)

    # Test if the observations that were filled into the dataframe at the beginning
    # are equal to the subject count if available.
    np.testing.assert_array_equal(
        nsurv.isel(time=0, id=~observations.subject_count.isnull()), 
        observations.subject_count.sel(id=~observations.subject_count.isnull())
    )

    assert_no_nans_in_dataset(nsurv.to_dataset())

    # create a convenience observation survivors before t, which gives the
    # number of living organisms at the end of time interval t-1
    # this is used for calculating conditional survival
    observations = observations.assign_coords({
        "survivors_before_t": (("id", "time"), np.column_stack([
            nsurv.isel(time=0).values, 
            nsurv.isel(time=list(range(0, len(nsurv.time)-1))).values
    ]).astype(int))})

    observations = observations.assign_coords({
        "survivors_at_start": (("id", "time"), np.broadcast_to(
            nsurv.isel(time=0).values.reshape(-1,1), 
            shape=nsurv.shape
    ).astype(int))})

    return observations


def is_survival_only_nan_except_start(survival: xr.DataArray):
    is_not_nan_at_start = survival.isel(time=0).notnull().all().values
    is_nan_at_rest = survival.sel(time=survival.time[1:]).isnull().all().values
    return bool(is_not_nan_at_start and is_nan_at_rest)


def survivors_at_start_of_interval(survival: xr.DataArray, ):    
    # create a convenience observation survivors before t, which gives the
    # number of living organisms at the end of time interval t-1
    # this is used for calculating conditional survival
    return np.column_stack([
        survival.isel(time=0).values, 
        survival.isel(time=list(range(0, len(survival.time)-1))).values
    ]).astype(int)


def generate_survival_repeated_observations(
    S, 
    N=10, 
    time=None,
    reps=1, 
    incidence=True,
    seed=1,
    ax=None,
    tol=None
):
    """Generate observations from a survival function S, with N individuals

    For this the conditional survival probability is used. This means that 
    for each time-interval the probability of dying in that interval, conditional
    on having lived until the beginning of that interval.

    S_cond[i] = (S[i-1] - S[i]) / S[i-1] where i are the intervals in T
    
    L[i] = Binom(p=S_cond[i], N=N_alive[i-1])

    L[i] is the death incidence in the interval i. So the number of deceased 
    individuals in the interval.

    For the binomial trials also N changes over time, with 
    
    N_alive[i] = N - sum(L[:i])

    This means the number of alive individuals gets reduced by the cumulative
    number of deceased individuals.

    Parameters
    ----------
    S : ArrayLike
        values from the survival function must be monotonically decreasing
    N : int
        The number of individuals in one experiment that is repeatedly observed
    reps: int
        The number of repeats of the same experiment

    incidence: bool
        If true, returns the number of deaths in each interval. If False returns 
        the number of cumulative deaths until the interval (including the 
        interval).
    """
    rng=np.random.default_rng(seed)

    if time is None:
        time = np.arange(len(S))

    T = len(time)

    if tol is not None: 
        S = np.clip(S, tol, 1-tol)

    L = np.zeros(shape=(reps, T))
    for i in range(T):
        if i == 0: 
            S_0 = 1
        else:
            S_0 = S[i-1]

        # calculate the binomial response of the conditional survival
        # i.e. the probability to die within an interval conditional on 
        # having survived until the beginning of that interval
        L[:, i] = binom(p=(S_0-S[i])/S_0, n=N-L.sum(axis=1).astype(int)).rvs(random_state=rng)


    # observations
    if ax is None:
        fig, ax = plt.subplots(1,1)
    ax.plot(time, S * N, color="black")
    ax.plot(time, N - L.cumsum(axis=1).T, 
            marker="o", color="tab:red", ls="", alpha=.75)
    ax.set_xlabel("Time [h]")
    ax.set_ylabel("Survival")
    ax.set_ylim(N-N*1.02,N*1.02)

    if incidence:
        return L
    else:
        return L.cumsum(axis=1)