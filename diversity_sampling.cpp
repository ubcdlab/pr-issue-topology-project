#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <iostream>
#include <vector>

using namespace std;

struct Component {
    int key;
    std::string repo_name;
    int size;
    int diameter;
    float density;
};

const char* getfield(char* line, int num)
{
    const char* tok;
    char* line_dup = strdup(line);
    for (tok = strtok(line_dup, ",");
        tok && *tok;
        tok = strtok(NULL, ",\n"))
    {
        if (!--num)
            return tok;
    }
    return NULL;
}

bool component_is_similar(Component* component_1, Component* component_2) {
    return component_1->diameter == component_2->diameter && 
    component_1->density == component_2->density; 
}

// vector<Component> find_similar_components(Component* component, vector<Component> component_universe) {
//     std::vector<Component> similar_components;
//     for (auto i = component_universe.begin(); i != component_universe.end(); ++i) {
//         if (component_is_similar(component, i)) {
//             similar_components.emplace_back(i);
//         }
//     }
//     return similar_components;
// }

Component* read_csv_from_file() {
    FILE *stream = fopen("unified_json/result_test.csv", "r");
    int i = 0;
    // 8632 entries within the CSV
    Component *component_list = (Component *) malloc(8633 * sizeof *component_list);

    char line[1024];
    while (fgets(line, 1024, stream))
    {
        char* tmp = strdup(line);

        int key = strtol(getfield(tmp, 1), NULL, 10);
        char* repo_name = strdup(getfield(tmp, 2));
        int size = strtol(getfield(tmp, 3), NULL, 10);
        int diameter = strtol(getfield(tmp, 4), NULL, 10);
        float density = strtof(getfield(tmp, 5), NULL);

        component_list[i].key = key;
        component_list[i].size = size;
        component_list[i].repo_name = repo_name;
        component_list[i].diameter = diameter;
        component_list[i].density = density;

        // printf("Element %d key: %d\n", i, key);
        // printf("Element %d size: %d\n", i, size);
        // printf("Element %d repo_name: %s\n", i, repo_name);
        // printf("Element %d diameter: %d\n", i, diameter);
        // printf("Element %d density: %f\n", i, density);

        i++;

        free(tmp);
    }

    return component_list;
}

// Component* next_components(int K, vector<Component> component_universe) {
//     std::vector<Component> result;
//     std::vector<Component> candidates;
//     candidates = component_universe;
//     for (int i = 0; i < K; i++) {
//         std::vector<Component> c_best;
//         std::vector<Component> p_best;

//     }
//     return NULL;
// }

int main()
{
    cout << "Start\n";
    Component* component_list = read_csv_from_file();
    cout << "Read OK\n";
    cout << sizeof(*component_list)/sizeof(Component*) << "\n";
    for (int counter = 1; counter < sizeof(*component_list)/sizeof(Component); counter++) {
        cout << "Element " << counter << " key: " << component_list[counter].key << "\n";
        // cout<<"Element %d size: %d\n", counter, component_list[counter].size);
        // printf("Element %d repo_name: %s\n", counter, component_list[counter].repo_name);
        // printf("Element %d diameter: %d\n", counter, component_list[counter].diameter);
        // printf("Element %d density: %f\n", counter, component_list[counter].density);
    }

    // COMPONENT* sample = next_components();
    return 0;
}