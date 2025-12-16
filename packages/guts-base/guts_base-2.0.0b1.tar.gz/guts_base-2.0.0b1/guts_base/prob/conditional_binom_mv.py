from scipy.stats._multivariate import multinomial_frozen, multi_rv_generic
from scipy.stats._discrete_distns import binom
import numpy as np

# TODO: Update example
# TODO: Use forward filling again to deal with nans (these were automatically solved by using rv_discrete)
# TODO: When all is complete delete conditional_bionm.py

def conditional_prob_neglogexp(p, p_init=1.0, eps=1e-12):
    p_ = np.column_stack([p_init, p])
    # p needs to be clipped zero division does not occurr, if the last p values are zero
    p_clipped = np.clip(p_, eps, 1.0)
    # convert to logscale
    neg_log_p = -np.log(p_clipped)
    # exponent substraction is numerically more stable than division
    return np.exp(neg_log_p[:, :-1] - neg_log_p[:, 1:])
    

def conditional_prob(p, p_init=1.0):
    p_ = np.concatenate([p_init, p[:]])
    # divide later though previous probability
    return p_[1:] / p_[:-1]
    

def conditional_prob_from_neglogp(p, p_init=1.0):
    p_ = np.concatenate([[p_init], p[:]])
    return np.exp(p_[:-1] - p_[1:])
    

class conditional_binomial(multi_rv_generic):
    """
    A scipy distribution for a conditional survival probability distribution

    Parameters
    ----------
    k: Array
        Number of repeated positive observations of a quantity that 
        can only decrease. k must be monotonically decreasing (e.g. survivors)
    
    p: Array
        survival function of the repeated observation. 
        p must be monotonically decreasing

    n: int
        The starting number of positive observations (e.g. initial number of organisms
        in a survival trial)

    Example
    -------
    Define a survival function (using a beta cdf and use it to make multinomial draws)
    to simulate survivals from repeated observations
    >>> n = 100
    >>> B = stats.beta(5, 5)
    >>> p = 1 - B.cdf(np.linspace(0, 1))
    >>> s = stats.multinomial(n, p=np.diff(p)*-1).rvs()[0]
    >>> s = n - s.cumsum()

    construct a frozen distribution
    >>> from guts_base.prob import conditional_survival
    >>> S = conditional_survival(n=n, p=p[1:])

    Compute the pmf
    >>> S.pmf(s)

    Compute the logpmf
    >>> S.logpmf(s)

    Draw random samples
    >>> samples = S.rvs(size=(1000, 49))

    Plot the observational variation of a given survival function under repeated
    Observations
    >>> plt.plot(samples.T, color="black", alpha=.02)


    """
    p_init = 1.0
    eps = 1e-12
    shapes = ("n", "p")
    def __call__(self, n, p, seed=None):
        """Create a frozen multinomial distribution.

        See `multinomial_frozen` for more information.
        """
        return conditional_binomial_frozen(n, p, seed)
    
    def _preprocess_params(self, x, n, p):
        x = np.array(x, ndmin=2)
        p = np.array(p, ndmin=2)
        p_init = np.broadcast_to(self.p_init, p[:, [0]].shape)
        n_init = np.broadcast_to(n, x[:,[0]].shape)
        # nan filling is not necessary, because nans are thrown out this shifts the 
        # p vector to where it belongs
        n_ = np.column_stack([n_init[:,[0]], x[:, :-1]])
        p_conditional = conditional_prob_neglogexp(p, p_init=p_init, eps=self.eps)
        return x, n_, p_conditional

    def logpmf(self, x, n, p):
        x, n, p = self._preprocess_params(x, n, p)
        return binom._logpmf(x, n, p)

    def pmf(self, x, n, p):
        x, n, p = self._preprocess_params(x, n, p)
        return binom._pmf(x, n, p)

    def rvs(self, n, p, size=None, random_state=None):
        r"""
        Generate random samples from the conditional binomial distribution.

        The random generation process is described by the following equations:
        
        The lethality matrix is initialized with
        \[
        L \leftarrow \mathbf{0} \in \mathbb{N}_0^{K \times T}
        \]

        where $K$ is the number of treatments and $T$ is the number of observations.
        For each observation $t$ in \( t = 1, \ldots, T \):
        \[
        L_{k,t} \sim \text{Binomial}\left(n=N_{k} - \sum_{t'=0}^{t-1} L_{k,t'},~p=1 - \frac{S_{k,t}}{S_{k,t-1}}\right)
        \]
        Where:
        - \( L_{k,t} \) is the number of organisms dying between $t$ and $t-1$ in each treatment $k$.
        - \( N_{k} \) is the initial number of alive organism in each treatment \( k \) at the start of the observations $t=0$.
        - \( S_{k,t} \) is survival function (the probability of being alive at a given time) computed for each observations $t$ in $T$.

        Finally:
        \[
        S_{k,t}^{obs} = N_{k} - \sum_{t'=0}^{t} L_{k,t'}
        \]


        Parameters
        ----------
        n: int or Array of int
            The initial number of positive observations (e.g. initial number of organisms
            in a survival trial).
        p: Array
            Survival function of the repeated observation.
            p must be monotonically decreasing.
        size: tuple, optional
            Shape of the random variates to generate.
        random_state: RandomState or int, optional
            If seed is not None, it will be used by the RandomState to generate
            random time steps.

        Returns
        -------
        ndarray
            Random samples from the conditional binomial distribution representing the
            number of entities surviving at each time step.


        """
        random_state = self._get_random_state(random_state)

        p = np.array(p, ndmin=2)
        p_init = np.broadcast_to(self.p_init, p[:, [0]].shape)
        n_init = np.broadcast_to(n, p.shape)

        p_conditional = conditional_prob_neglogexp(p, p_init=p_init, eps=self.eps)
    
        if size is None:
            size = p.shape

        # axis-0 is the batch dimension
        # axis-1 is the time dimension (probability)
        L = np.zeros(shape=size)

        for i in range(L.shape[1]):
            # calculate the binomial response of the conditional survival
            # i.e. the probability to die within an interval conditional on 
            # having survived until the beginning of that interval
            L[..., i] = random_state.binomial(
                p=1 - p_conditional[:, i], 
                n=n_init[:, i]-L.sum(axis=-1).astype(int),
                size=size[slice(len(size)-1)]
            )

        return n_init-L.cumsum(axis=-1)
    
conditional_survival = conditional_binomial()


class conditional_binomial_frozen(multinomial_frozen):

    def __init__(self, n, p, seed=None):
        self._dist = conditional_binomial(seed)
        self.n, self.p = n, p
        # self.n, self.p, self.npcond = self._dist._process_parameters(n, p)

        # # monkey patch self._dist
        # def _process_parameters(n, p):
        #     return self.n, self.p, self.npcond

        # self._dist._process_parameters = _process_parameters

    def logpmf(self, x):
        return self._dist.logpmf(x, n=self.n, p=self.p)

    def pmf(self, x):
        return self._dist.pmf(x, n=self.n, p=self.p)

    def rvs(self, n=None, size=None, random_state=None):
        if n is None:
            n = self.n
        return self._dist.rvs(n=self.n, p=self.p, size=size, random_state=random_state)


if __name__ == "__main__":

    S = conditional_survival(n=10, p=[[0.8,0.4,0.2],[0.8,0.4,0.2]])


    prob = S.pmf([[10,5,2], [7,2,0]])
    prob = S.pmf([10,5,2])
    sample = S.rvs()
    sample = S.rvs(size=(10, 2, 3))


    S = conditional_survival(n=10, p=[0.8,0.4,0.2])
    prob = S.pmf([[10,5,2], [7,2,0]])
    prob = S.pmf([10,5,2])
    S.rvs(size=(10,3))
    S.rvs()

    sample

    S = conditional_survival(n=[[10],[2000]], p=[[0.8,0.4,0.2],[0.8,0.4,0.2]])
    prob = S.pmf([[10,5,2], [7,2,0]])
    S.rvs()


