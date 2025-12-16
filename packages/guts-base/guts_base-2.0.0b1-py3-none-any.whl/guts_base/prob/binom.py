import numpyro

def likelihood(theta, simulation_results, indices, observations, masks, make_predictions):
    """Uses lookup and error model from the local function context"""
    if make_predictions:
        obs = None
    else:
        obs = observations["survival"]
    
    _ = numpyro.sample(
        name="survival" + "_obs",
        fn=numpyro.distributions.Binomial(
            probs=simulation_results["survival"],
            total_count=observations["survivors_at_start"],
        ).mask(masks["survival"]),
        obs=obs
    )

