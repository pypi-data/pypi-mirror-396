from chain_harvester.utils.graphql import call_graphql


def _get_blocks_query(to_block=None):
    base_query = """
        query ($first: Int!, $skip: Int!, $from_block: Int!{to_block_var}) {{
            blocks (orderBy: number, first: $first, skip: $skip, where:
                {{number_gt: $from_block{to_block_filter}}}) {{
                number
                timestamp
                id
            }}
        }}
    """

    to_block_var = ", $to_block: Int!" if to_block is not None else ""
    to_block_filter = ", number_lte: $to_block" if to_block is not None else ""

    query = base_query.format(to_block_var=to_block_var, to_block_filter=to_block_filter)
    return query


def get_blocks(url, from_block, to_block=None, limit=10000, timeout=30, retries=3):
    first = limit
    skip = 0
    while True:
        query = _get_blocks_query(to_block)
        response = call_graphql(
            url,
            query,
            variables={
                "first": first,
                "skip": skip,
                "from_block": from_block,
                "to_block": to_block,
            },
            timeout=timeout,
            max_retries=retries,
        )
        if not response.get("data", {}).get("blocks"):
            break
        yield from response["data"]["blocks"]
        skip += first
