from guts_base.data.survival import generate_survival_repeated_observations
from scipy.stats import rv_discrete
from scipy.stats._discrete_distns import _isintegral
import numpy as np
import scipy.stats._boost as _boost
from scipy import stats
from matplotlib import pyplot as plt

def conditional_prob_neglogexp(p, p_init=1.0, eps=1e-12):
    p_ = np.concatenate([p_init, p[:]])
    # p needs to be clipped zero division does not occurr, if the last p values are zero
    p_clipped = np.clip(p_, eps, 1.0)
    # convert to logscale
    neg_log_p = -np.log(p_clipped)
    # exponent substraction is numerically more stable than division
    return np.exp(neg_log_p[:-1] - neg_log_p[1:])
    

def conditional_prob(p, p_init=1.0):
    p_ = np.concatenate([p_init, p[:]])
    # divide later though previous probability
    return p_[1:] / p_[:-1]
    

def conditional_prob_from_neglogp(p, p_init=1.0):
    p_ = np.concatenate([[p_init], p[:]])
    return np.exp(p_[:-1] - p_[1:])
    


class conditional_survival_gen(rv_discrete):
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

    n_init: int
        The starting number of positive observations (e.g. initial number of organisms
        in a survival trial)

    p_init: float
        The starting survival probability in an experiment

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
    >>> S = conditional_survival(p=p[1:], n_init=[n], p_init=[1.0], eps=[1e-12])

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
    def __init__(self, **kwargs):
        # Initialize your custom parameters here
        super().__init__(**kwargs)
        # Set up any custom state needed for sampling

    def _argcheck(self, p, n_init, p_init, eps):
        return (n_init >= 0) & _isintegral(n_init) & (p >= 0) & (p <= 1)# & (np.diff(np.concatenate([p_init, p])) <= 0)

    def _pmf(self, x, p, n_init, p_init, eps):
        # nan filling is not necessary, because nans are thrown out this shifts the 
        # p vector to where it belongs
        n_ = np.concatenate([n_init[[0]], x[:-1]])
        p_conditional = conditional_prob_neglogexp(p, p_init=p_init[[0]], eps=eps[[0]])
        return _boost._binom_pdf(x, n_, p_conditional)
        
    def _rvs(self, p, n_init=10, p_init=[1.0], eps=[1e-12], size=1, random_state=None):
        p_conditional = conditional_prob_neglogexp(p, p_init=p_init[[0]], eps=eps[[0]])
    
        # axis-0 is the batch dimension
        # axis-1 is the time dimension (probability)
        L = np.zeros(shape=(*size,))
        L = np.array(L, ndmin=2)

        for i in range(L.shape[1]):
            # calculate the binomial response of the conditional survival
            # i.e. the probability to die within an interval conditional on 
            # having survived until the beginning of that interval
            L[:, i] = random_state.binomial(
                p=1 - p_conditional[i], 
                n=n_init[i]-L.sum(axis=1).astype(int)
            )

        return n_init-L.cumsum(axis=1)

conditional_survival = conditional_survival_gen(name="conditional_survival", )



