#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int key;
    char* repo_name;
    int size;
    int diameter;
    float density;
} COMPONENT;

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

COMPONENT* read_csv_from_file() {
    FILE *stream = fopen("unified_json/result_test.csv", "r");
    int i = 0;
    int j;
    // scanf("%d", &j);
    // 8632 entries
    COMPONENT* component_list = malloc(8632 * sizeof *component_list);
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

int main()
{
    COMPONENT* component_list = read_csv_from_file();
    for (int counter = 1; counter < 14; ++counter) {
        printf("Element %d key: %d\n", counter, component_list[counter].key);
        printf("Element %d size: %d\n", counter, component_list[counter].size);
        printf("Element %d repo_name: %s\n", counter, component_list[counter].repo_name);
        printf("Element %d diameter: %d\n", counter, component_list[counter].diameter);
        printf("Element %d density: %f\n", counter, component_list[counter].density);
    }

}