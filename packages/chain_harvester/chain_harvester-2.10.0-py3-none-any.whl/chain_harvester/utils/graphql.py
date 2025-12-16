import requests


def call_graphql(url, query, variables=None, timeout=10, max_retries=3):
    payload = {"query": query, "variables": variables}
    headers = {"accept": "application/json", "content-type": "application/json"}
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(
                    f"GraphQL request failed after {max_retries} attempts: {e!s}"
                ) from e
            continue
