#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct component {
    int key;
    char repo_name;
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



int main()
{
    FILE *stream = fopen("unified_json/result_test.csv", "r");
    int i = 0;
    int j;
    printf("Choose a line to be given its elements: \n");
    // scanf("%d", &j);
    struct component csv[8635];
    char line[1024];
    while (fgets(line, 1024, stream))
    {
        char* tmp = strdup(line);
        // for (j = 1; j < 6; ++j) {
        //     printf("Element %d would be %s\n", i, getfield(tmp, j));
        // }
        int key = strtol(getfield(tmp, 1), NULL, 10);
        // printf("Element %d would be %d\n", i, key);
        char* repo_name = strdup(getfield(tmp, 2));
        // printf("Element %d would be %s\n", i, repo_name);
        int size = strtol(getfield(tmp, 3), NULL, 10);
        int diameter = strtol(getfield(tmp, 4), NULL, 10);
        float density = strtof(getfield(tmp, 5), NULL);
        printf("Element %d key: %d\n", i, key);
        printf("Element %d size: %d\n", i, size);
        printf("Element %d diameter: %d\n", i, diameter);
        printf("Element %d density: %f\n", i, density);
        i++;
        free(tmp);
    }
}