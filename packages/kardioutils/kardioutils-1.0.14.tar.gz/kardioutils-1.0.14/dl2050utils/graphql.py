"""
    graphql.py

    GraphQL access class and utility functions.
"""

import requests
from tqdm import tqdm
from dl2050utils.common import oget

# #############################################################################################################
# GraphQL
# #############################################################################################################

class GraphQL:
    """
    """
    def __init__(self, cfg=None, api_url=None, api_key=None):
        api_url = api_url or oget(cfg,['graphql','api_url'])
        api_key = api_key or oget(cfg,['graphql','api_key'])
        assert api_url is not None and api_key is not None
        self.api_url = api_url
        self.headers = {'Content-Type':'application/json', 'Accept':'application/json', 'Authorization':api_key}

    def _extract_table_name(self, query):
        """Extract the first table name from a GraphQL query"""
        # Find content between first { and (
        start = query.find("{") + 1
        end = query.find("(", start) if "(" in query else query.find("{", start)
        if end == -1: end = query.find("}", start)
        # Extract and clean table name
        table = query[start:end].strip()
        # Remove _aggregate suffix if present
        return table.replace("_aggregate", "")

    def request(self, payload, extract=False):
        with requests.Session() as session:
            response = session.post(self.api_url, headers=self.headers, json=payload)
            # Check if the request was successful
            if response.status_code == 200:
                json_response = response.json()
                errors = json_response.get("errors", None)
                if errors:
                    raise Exception(f"Request failed with errors: {errors}")
                data = json_response.get("data", {})
                # Check for GraphQL errors
                if "errors" in data: raise Exception(f"GraphQL errors: {data['errors']}")
                # If not extract return raw data
                if not extract: return data
                # Extract table name from query
                tbl = self._extract_table_name(payload["query"])
                # Extract and return rows
                return {
                    "rows": data.get(tbl, []),
                    "nrows": data.get(f"{tbl}_aggregate", {}).get("aggregate", {}).get("count", 0)
                }
            else:
                raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
            
    def exec(self, query, variables={}):
        return self.request({"query":query, "variables":variables})
            
    def fetch(self, tbl, cols=['id'], where=None, cutoff_date=None, limit=None, offset=None, order_by=None):
        columns_str = " ".join(cols)
        # Build where clause
        where_conditions = []
        variables = {}
        # Add cutoff date condition if provided
        if cutoff_date:
            where_conditions.append("updated_at: {_gt: $cutoffDate}")
            variables["cutoffDate"] = cutoff_date
        # Add additional where conditions if provided
        if where:
            for key,value in where.items():
                if isinstance(value, dict):
                    # Handle complex conditions like {"_eq": 11692224}
                    operator,val = next(iter(value.items()))
                    # If val is a string, wrap it in quotes
                    val_str = f"'{val}'" if isinstance(val, str) else val
                    where_conditions.append(f"{key}: {{{operator}: {val_str}}}")
                else:
                    # Handle simple equality conditions
                    val_str = f"'{value}'" if isinstance(value, str) else value
                    where_conditions.append(f"{key}: {{_eq: {val_str}}}")
        # Build combined params string with where, limit, offset and order_by
        params = []
        if where_conditions: params.append(f"where: {{{', '.join(where_conditions)}}}")
        if limit is not None: params.append(f"limit: {limit}")
        if offset is not None: params.append(f"offset: {offset}")
        if order_by:
            order_parts = [f"{k}: {v}" for k, v in order_by.items()]
            params.append(f"order_by: {{{', '.join(order_parts)}}}")
        params_str = f"({', '.join(params)})" if params else ""
        # For aggregate, only use where conditions without limit/offset
        where_str = f"(where: {{{', '.join(where_conditions)}}})" if where_conditions else ""
        query = f"""
            query($cutoffDate: timestamptz) {{
                {tbl}{params_str} {{
                    {columns_str}
                }}
                {tbl}_aggregate{where_str} {{
                    aggregate {{
                        count
                    }}
                }}
            }}
        """
        # print(query)
        variables = {"cutoffDate": cutoff_date} if cutoff_date else {}
        return self.request(payload={"query":query, "variables":variables}, extract=True)
    
# #############################################################################################################
# inspect
# #############################################################################################################

def inspect(gql, tbl):
    Q = """
        query GetTableColumns($tableName: String!) {
          __type(name: $tableName) {
            fields {
              name
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
    """
    variables = {"tableName": tbl}
    res = gql.exec(Q, variables)
    rows = oget(res,['__type','fields'])
    if rows is None: return rows
    return rows

# #############################################################################################################
# read_table_in_chunks
# #############################################################################################################

def build_query_global(tbl, cols):
    q_cols = " ".join(cols)
    Q = f"""
        query Get{tbl.title()}($offset: Int!, $limit: Int!) {{
            {tbl}(
                offset: $offset,
                limit: $limit
            )
            {{
                {q_cols}
            }}
            {tbl}_aggregate
            {{
                aggregate {{
                    count
                }}
            }}
        }}
    """
    return Q

def build_query_cutoff(tbl, cols):
    q_cols = " ".join(cols)
    Q = f"""
    query Get{tbl.title()}($offset: Int!, $limit: Int!, $cutoff: timestamptz!) {{
        {tbl}(
            offset: $offset,
            limit: $limit,
            where: {{ updated_at: {{_gte: $cutoff}} }}
        )
        {{
            {q_cols}
        }}
        {tbl}_aggregate(
            where: {{ updated_at: {{_gte: $cutoff}} }}
        )
        {{
            aggregate {{
                count
            }}
        }}
    }}
    """
    return Q

def read_table_in_chunks(gql, tbl, cols, cutoff_iso=None, chunk_size=1000, show=False):
    """
    Read all rows from a table, optionally filtering by cutoff date, chunk by chunk.
   
    Args:
        gql: GraphQL client instance
        tbl (str): Name of the table to query
        cols (list): List of column names to fetch
        cutoff (datetime.date, optional): Cutoff date to filter rows. If None, no date filtering is applied
        chunk_size (int): Number of rows to fetch per chunk
   
    Yields:
        list: Chunk of rows from the table
    """
    # Get the query from the query template functions
    query = build_query_global(tbl, cols) if cutoff_iso is None else build_query_cutoff(tbl, cols)
    # Prepare variables based on whether cutoff is provided
    variables = {'offset':0, 'limit':chunk_size}
    if cutoff_iso: variables['cutoff'] = cutoff_iso
    # Excute the query
    response = gql.exec(query, variables)
    nrows = response[f'{tbl}_aggregate']['aggregate']['count']
    if show: print(f'Reading {tbl} (nrows: {nrows})')
    # Create progress bar
    pbar = tqdm(total=nrows, desc=f'Reading {tbl}', unit=' rows') if show else None
    chunk = response[tbl]
    if pbar: pbar.update(len(chunk))
    if chunk: yield chunk
    # Fetch remaining chunks
    offset = chunk_size
    while offset < nrows:
        variables['offset'] = offset
        response = gql.exec(query, variables)
        chunk = response[tbl]
        if not chunk: break
        if pbar: pbar.update(len(chunk))
        yield chunk
        offset += chunk_size
