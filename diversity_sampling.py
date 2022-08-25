import json
import sys
import math
import networkx as nx

def component_is_similar(component_1, component_2, all_dimensions):
    components_are_similar = True
    for dimension in all_dimensions:
        similarity = compare_component_dimension_similarity(component_1, component_2, dimension)
        components_are_similar = components_are_similar and similarity

def compare_component_dimension_similarity(component_1, component_2, dimension, threshold=0.5):
    dim_key = dimension['key']
    if dimension['numeric'] == True:
        return math.log10(abs(component_1[dim_key], component_2[dim_key])) <= threshold
    else:
        return component_1[dim_key] == component_2[dim_key]

def find_similar_components(component, component_universe, dimensions):
    similar_components = []
    for component_in_universe in component_universe:
        if component_is_similar(component, component_in_universe, dimensions):
            similar_components.append(component_in_universe)

def score_components(sample, universe, space, config):
    coverage = set()
    for component in sample:
        similar_components = find_similar_components(component, sample, config)
        coverage.update(similar_components)
    score = len(coverage)/len(universe)
    return score

def next_components(K, preselected_components, component_universe, dimensions, config):
    result = []
    candidates = [x1 - x2 for (x1, x2) in zip(component_universe, preselected_components)]
    c_space = preselected_components
    for i in range(1, K+1):
        c_best = []
        p_best = None
        for candidate in candidates:
            assert(1 == 1)
            c_candidate = 
            if len(c_new) > len(c_best):
                c_best = c_new
                p_best = candidate
        if p_best is None:
            break
        candidates = [x1 - x2 for (x1, x2) in zip(candidates, p_best)]
        result.append(p_best)
        candidates.pop(p_best)
        c_space.append(c_best)
    return