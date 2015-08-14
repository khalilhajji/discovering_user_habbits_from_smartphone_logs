contains code that evaluates the performances of the different algorithms by computing the perplexity of an unseen test set.
perplexity is the inverse exponential of the log likelihood per sample. exp(-ll/#samples)
the lower the perplexity is, the better the model generalizes to an unseen test set.

#NOTE: THIS METRIC SHOULD NOT BE USED YET BEFORE PERPLEXITY COMPUTATION IS FIXED IN GHCM_MDT and HCM_MDT!!