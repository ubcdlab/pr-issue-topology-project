import json
from multiprocessing.sharedctypes import Value
import sys
import math
import networkx as nx

def read_json_from_file():
    PATH = f'unified_json/mini_result.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def write_json_to_file(nodes):
    with open(f'unified_json/sampled_result.json', 'w') as f:
        f.write(json.dumps(nodes, sort_keys=False, indent=4))

def component_is_similar(component_1, component_2, all_dimensions):
    components_are_similar = True
    for dimension in all_dimensions:
        similarity = compare_component_dimension_similarity(component_1, component_2, dimension, 0.1)
        components_are_similar = components_are_similar and similarity
    return components_are_similar

def compare_component_dimension_similarity(component_1, component_2, dimension, threshold=0.5):
    numeric = None
    try:
        float(component_1[dimension])
        numeric = True
    except ValueError:
        numeric = False
    if numeric is True:
        difference = component_1[dimension] - component_2[dimension]
        if difference == 0:
            return True
        return math.log10(abs(difference)) <= threshold
    else:
        return component_1[dimension] == component_2[dimension]

def find_similar_components(component, component_universe, dimensions):
    similar_components = []
    for component_in_universe in component_universe:
        if component_is_similar(component, component_in_universe, dimensions):
            similar_components.append(component_in_universe)
    return similar_components

def score_components(sample, universe, space, config):
    coverage = []
    coverage_set = set()
    for component in sample:
        similar_components = find_similar_components(component, universe, config)
        for item in similar_components:
            coverage_set.add(item['key'])
            if item in coverage:
                continue
            coverage.append(item)
    score = len(coverage)/len(universe)
    return score

def next_components(K, preselected_components, component_universe, dimensions, config):
    result = []
    candidates = []
    for item in component_universe:
        if item in preselected_components:
            continue
        candidates.append(item)
    c_space = preselected_components
    for i in range(1, K+1):
        c_best = []
        p_best = None
        for candidate in candidates:
            components_covered_by_candidate = find_similar_components(candidate, candidates, dimensions)
            if len(components_covered_by_candidate) > len(c_best):
                c_best = components_covered_by_candidate
                p_best = candidate
        if p_best is None:
            break
        result.append(p_best)
        candidates.remove(p_best)
        c_space.append(c_best)
    return result

def main():
    condensed_file = read_json_from_file()
    sample = next_components(100, [], condensed_file, ['diameter', 'density'], None)
    score = score_components(sample, condensed_file, ['diameter', 'density'], ['diameter', 'density'])
    print(score)
    write_json_to_file(sample)

if __name__ == '__main__':
    main()