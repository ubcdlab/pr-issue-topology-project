# An example to get the remaining rate limit using the Github GraphQL API.

import requests

def get_token():
    # get personal access token
    # from a file named token.txt
    token = None
    try:
        with open('.token', 'r') as f:
            token = f.read()
            print('Github token read OK')
    except IOError:
        pass
    return token

def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


headers = {"Authorization": get_token()}

# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query = """
query {
  repository(owner:"vuejs", name:"vue"){
  
  }
}
"""

result = run_query(query) # Execute the query
remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
print("Remaining rate limit - {}".format(remaining_rate_limit))