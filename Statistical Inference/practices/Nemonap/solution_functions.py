import numpy as np
def generate_population(distribution, params, population_size):
    if distribution == "normal" and ('mean' in params.keys()) and ('std' in params.keys()):
        population = np.random.normal(params['mean'], params['std'], population_size)
    elif distribution == "uniform" and ('low' in params.keys()) and ('high' in params.keys()):
        population = np.random.uniform(params['low'], params['high'], population_size)
    else:
        raise ValueError("Invalid distribution or parameters")
    return population

def simple_random_sampling(population, sample_size, num_samples):
    if sample_size > len(population):
            raise ValueError("Sample size must be less than or equal to the population size")
    sampling_data = []
    for _ in range(num_samples):
            sample = np.random.choice(population, sample_size, replace=False)
            sampling_data.append(sample)
    return np.array(sampling_data)

def calculate_bias(population, samples):
    ave_samples = np.mean([np.mean(sample) for sample in samples])
    mean_of_original_data = np.mean(population)
    bias = ave_samples - mean_of_original_data
    return bias
