"""
    db.py
    DB Class

    ...

    json types are possible as inputs, just pass a python dict as field value

    asyncpg:
    https://github.com/MagicStack/asyncpg
    https://magicstack.github.io/asyncpg/current/installation.html
"""
import asyncio
import asyncpg
from datetime import datetime, date, time
import re
from pathlib import Path
import orjson
import numpy as np
from dl2050utils.core import listify, oget, is_numeric_str, now
from dl2050utils.log import BaseLog
from dl2050utils.fs import pickle_save, pickle_load
from dl2050utils.dbutils import parse_filters

# ####################################################################################################
# Helper functions
# ####################################################################################################

def strip(s):
    """
    Removes single and double quotes, and newlines from a string.
    Args: e (str): String to process.
    Returns: str: Cleaned string.
    """
    if type(s)!=str: return s
    s.replace("'", "")
    s.replace('"', "")
    s.replace("\n", " ")
    return s

# ####################################################################################################
# Types
# ####################################################################################################

def convert_type(v, max_sz=int(1e6)):
    """
    Converts values to their corresponding Python types to be compatible with PostgreSQL.
    Handles None, NumPy types, datetime objects, and ensures NULL representation for None.
    Also handle dicts with conversion to JSON strings.
    # TODO: consider lists?
    """
    # Explicitly return 'NULL' for compatibility with SQL statements
    if v is None: return None
    # Normal types returned as is
    if type(v) in [int, float, bool]: return v
    # Strins checked for max_sz
    if type(v)==str: return v[:max_sz]
    # Convert NumPy scalars to Python scalars
    if isinstance(v, np.generic): return v.item()
    # Handle datetime, date, and time types, format as ISO 8601 string for PostgreSQL compatibility
    if isinstance(v, (datetime, date, time)): return v
    # For dicts, convert into JSON string, potentially dealing with numpy
    if type(v) == dict: return orjson.dumps(v, option=orjson.OPT_SERIALIZE_NUMPY).decode()
    # Default case: return None
    return None

# ####################################################################################################
# Parsers
# ####################################################################################################

def parse_cols(tbl, cols, max_sz=1024):
    if cols is None: return None
    if type(cols)!=list or not len(cols): return None
    cols2 = []
    for c in cols:
        if type(c)!=str or len(c)>max_sz: return None
        cols2.append(f'{c}')
    return cols2

def parse_join(join, max_sz=1024):
    """
    Used to filter the results based on a condition col=val in a join tbl.
    join is a dict with attrs:
        tbl2: the join tbl
        key1: the master tbl join col
        key2: the join tbl key
        col: col where condition is testes
        val: val of the condition
        op: default to '=', can be '!=', '>', '>=', '<', '<='
    Example:
        {'tbl2':'orgs', 'key1':'org', 'key2':'id', 'col':'name', 'val':'MHR', op:'!='}
    """
    attrs = ["tbl2", "key1", "key2", "col", "val"]
    if type(join)!= dict: return None
    join2 = {}
    for k in attrs:
        if k not in join: return None
        val = join[k]
        if type(val)!=str: return None
        join2[k] = join[k][:max_sz]
    join2['op'] = oget(join,['op'],'=')
    if not join2['op'] in ['=', '!=', '>', '>=', '<', '<=']: return None
    return join2

def parse_lookups(lookups, max_sz=1024):
    """
    Used to join with lookup tbls on lookup cols and extract lookup vals.
    lookups is a list of dicts with attrs:
        col: the lookup col from the master tbl
        tbl: the lookup tbl
        key: the key col of the lookup tbl, optional, defaults to id
        val: the val col of the lookup tbl, optional, defaults to name
    Example:
        [{'col':'org', 'tbl':'orgs', 'key':'id', 'val':'name'}]
    """
    if type(lookups)!=list or not len(lookups): return []
    lookups2 = []
    for l in lookups:
        col,tbl =  oget(l,['col']),oget(l,['tbl'])
        if col is None or tbl is None: continue
        key,val = oget(l,['key'],'id'),oget(l,['val'],'name')
        if type(col)!=str or type(tbl)!=str or type(key)!=str or type(key)!=str: continue
        if "col" not in l or "tbl" not in l: continue
        if type(l['col'])!=str or type(l['tbl'])!=str: continue
        key,val = oget(l,["key"],"id"),oget(l,["val"],"name")
        if type(key)!=str or type(val)!=str: continue
        l2 = {'col':col[:max_sz], 'tbl':tbl[:max_sz], 'key':key[:max_sz], 'val':val[:max_sz]}
        lookups2.append(l2)
    return lookups2

# ####################################################################################################
# parse_select_query_result
# ####################################################################################################

def strip_row(row):
    """Strips right spaces from all strings in the dict row"""
    if type(row)!=dict: return row
    for key,value in row.items():
        if isinstance(value, str): row[key] = value.rstrip()

def strip_rows(rows):
    """Strips right spaces from all strings in all rows returned by a query"""
    if rows is None or type(rows)!=list: return
    for i in range(len(rows)):
        strip_row(rows[i])
    return rows

def parse_select_query_result(res):
    if res is None: return None
    if type(res)==list:
        rows = [dict(row) for row in res]
        strip_rows(rows)
        return rows
    row = dict(res)
    strip_row(row)
    return row

# ####################################################################################################
# get_select_query_and_params
# ####################################################################################################

def get_select_query_and_params(tbl, cols=None, filters=None, sfilters=None, join=None, lookups=None,
                                sort=None, ascending=True, offset=None, limit=None):
    """
    Constructs an SQL SELECT.
    Includes optional filters, sfilters, join and lookups, and sorting.
    Enforces a LIMIT clause.
    Args:
        tbl (str): Table name.
        cols (list[str], optional): Columns to select.
        filters, sfilters, join, lookups: refer to parser functions.
        sort (str, optional): Column to sort by.
        ascending (bool, optional): Sort direction.
        offset, limit (int, optional for offset): Pagination.
    Returns: str: SQL query string.
    """
    # Parse cols
    cols = parse_cols(tbl, cols, max_sz=1024)
    # Default to <tbl>.* if cols are not defined
    qcols = f'{tbl}.*'
    if type(cols)==list: qcols =  ', '.join([f'{tbl}.{c}' for c in cols])
    # Parse filters and sfilters, apply positional parameterization and get params
    fs1,sfs1 = parse_filters(filters),parse_filters(sfilters)
    fs,sfs = [],[]
    params = []
    k = 1
    for f in fs1:
        col,op,val = f"{tbl}.{f['col']}",f['op'],f['val']
        # For NULL dont use params
        if op==' IS ':
            fs.append({'col':col, 'op':op, 'val':val})
            continue
        # Set value to paramenter ($1,...)
        val = f'${k}'
        # Convert IN, NOT IN to ==ANY, !=ALL
        if op=='IN': op,val = '=',f'ANY(${k})'
        if op=='NOT IN': op,val = '!=',f'ALL(${k})'
        fs.append({'col':col, 'op':op, 'val':val})
        # Append param
        params.append(f['val'])
        k += 1
    for f in sfs1:
        col,op,val = f"{tbl}.{f['col']}",f['op'],f'${k}'
        # IN,NOT IN not valid for pattern matching (for now)
        if op=='IN' or op=='NOT IN': continue
        sfs.append({'col':col, 'op':op, 'val':val})
        # Append param
        params.append(f"%{f['val']}%")
        k += 1
    # Parse join
    join,lookups = parse_join(join),parse_lookups(lookups)
    qjoins = ''
    if join is not None:
        qjoins += f" JOIN {join['tbl2']} ON {tbl}.{join['key1']}={join['tbl2']}.{join['key2']}"
        # Append filter with join condition
        val = join['val']
        if type(val)==str and not is_numeric_str(val): val = f"'{val}'"
        fs.append({'col':f"{join['tbl2']}.{join['col']}", 'val':val, 'op':'='})
    # Parse lookups
    lookups = parse_lookups(lookups)
    for l in lookups:
        # Append lookup cols (_id and _name suffixes)
        qcols += f", {tbl}.{l['col']} as {l['col']}_id, {l['tbl']}.{l['val']} as {l['col']}_name"
        # Append a new join clause
        qjoins += " LEFT OUTER JOIN "
        key_col = 'id' if 'key' not in l else l['key']
        qjoins += f"{l['tbl']} ON {tbl}.{l['col']}={l['tbl']}.{key_col} "
    # Prepare full filters and sfilters
    qwhere = ' WHERE ' if len(fs)+len(sfs)>0 else ''
    if len(fs):
        qwhere += " AND ".join([f"{e['col']}{e['op']}{e['val']}" for e in fs])
    if len(sfs):
        if len(fs): qwhere += ' AND '
        qwhere += " AND ".join([f"{e['col']} ILIKE {e['val']}" for e in sfs])
    # Insert order
    qorder = ''
    if isinstance(sort, str): qorder = f" ORDER BY {sort} " + ("ASC" if ascending else "DESC")
    # Insert offset and limit
    offset,limit = offset or 0,limit if limit is not None else 32
    if offset is not None: qpag = f" OFFSET {offset} LIMIT {limit}"
    # Final query
    query_string = f"SELECT {qcols} FROM {tbl}{qjoins}{qwhere}{qorder}{qpag}"
    return query_string,params

# ####################################################################################################
# Count query rows
# ####################################################################################################

async def count_query_rows(conn, query, *params):
    """Returns the exepected number of rows in a query."""
    # Exclude the OFFSET and LIMIT subclauses
    pattern = r"(?i)\s+(LIMIT\s*(=|\s)\s*\d+|OFFSET\s*\d+)"
    query = re.sub(pattern, " ", query).strip()
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"
    nrows = await conn.fetchval(count_query, *params)
    return nrows

# async def count_query_rows(con, q):
#     """
#     Returns the exepected number of rows in a query.
#     The number of rows is obtained by changing the query to count(*) and dropping the sort.
#     TODO: Implement Explain/Query Plan approach, currently faliling on joins
#     """
#     q1 = re.sub(r"SELECT .*? FROM", "SELECT count(*) FROM", q, flags=re.IGNORECASE)
#     q1 = re.sub(r"ORDER BY .*?$", "", q1, flags=re.IGNORECASE)
#     q1 = re.sub(r"OFFSET \d+", "", q1, flags=re.IGNORECASE)
#     q1 = re.sub(r"LIMIT \d+", "", q1, flags=re.IGNORECASE)
#     res = await con.fetchrow(q1)
#     if res is None: return None
#     res = dict(res)
#     return oget(res, ["count"])
#     # db.sync_select('pg_class', cols=['reltuples'], filters={'relname': 'diagsg'})
#     # res = await con.fetchrow(f'explain(format json) {q}')
#     # if res is None: return None
#     # res = json.loads(res['QUERY PLAN'])
#     # if res is None or not len(res): return None
#     # return oget(res[0],['Plan','Plan Rows'])

# ####################################################################################################
# DB Class
#
#   startup
#   shutdown
#
#   query
#   select
#   select_one
#   select_key
#   insert
#   update
#   update_or_insert
#   delete
#   get_seq
#
# ####################################################################################################

class DB:
    """
    Class for managing interactions with a PostgreSQL database.
    Constructor Parameters:
            - cfg (dict, optional): DB connection parameters (default: None, and a basic connection is provided).
            - log (BaseLog, optional): Logging mechanism for error and status messages (default: None).
            - dbname (str, optional): Name of the database to connect to (default: None).
    Methods:
        - async startup(min_size=5, max_size=20, loop=None)
            Initiates the database connection pool with optional size and loop parameters.
        - shutdown()
            Gracefully closes the database connection pool.
        - async execute(query_string)
            Executes SQL queries from query string (SELECT and non-SELECT) and returns the result.
        - async select(tbl, join=None, filters=None, sfilters=None, cols='*', sort=None, ascending=True, offset=None, limit=None, one=False)
            Query interface for python. Retrieves data, manage paginatiom, provide options for one row fecth and full rows count.
        - async select_one(tbl, filters=[])
            Retrieves a single row from a table with optional filters.
        - async insert(tbl, d, return_key=None)
            Inserts data into a table and optionally returns the inserted key.
        - async update(tbl, ks, d)
            Updates rows in a table based on provided keys.
        - async update_or_insert(tbl, ks, d)
            Updates rows if they exist, otherwise inserts new rows.
        - async delete(tbl, k, v)
            Deletes rows from a table based on a key-value pair.
        - update_stats()
            Performs a vacuum analyze operation for database statistics update (needed for query planner to work properly)
        - async get_trows(tbl) (Internal)
            Retrieves the total number of rows that will result in a querty (through query planner).
        - async get_trows(tbl) (Internal)
        - enqueue
        - dequeue

        The DB class assumes the use of a PostgreSQL database and proper configuration parameters for connection.
        Error messages and context information are logged for debugging purposes, enhancing reliability and maintainability.
        Ensures data integrity and security by validating and sanitizing input data.
        The filtering in define by two optional distint ways:
            1) As an array of dict objects of the for {'col':col, 'val':val, 'op':op.} Op can be wither =,>,>=,<,<=,!=.
            2) Single dict with all the keys/vals.
    """

    def __init__(self, cfg=None, log=None, dbname=None, passwd=None):
        """
        Initializes database connection with optional configuration and logging.
        Args:
            cfg (dict, optional): Database connection configuration.
            log (BaseLog, optional): Logging mechanism.
            dbname (str, optional): Database name.
            passwd (str, optional): Password for database.
        """
        if cfg is None:
            cfg = {"db": {
                "host": "db",
                "port": 5432,
                "user": "postgres",
                "passwd": "rootroot",
                "dbname": "postgres",
            }}
        self.cfg, self.LOG = cfg, log or BaseLog()
        host = oget(cfg, ["db", "host"], "db")
        port = oget(cfg, ["db", "port"], 5432)
        user = oget(cfg, ["db", "user"], "postgres")
        passwd = oget(cfg, ["db", "passwd"], passwd)
        if dbname is None: dbname = oget(cfg, ["db", "dbname"], "postgres")
        self.url = f"postgres://{user}:{passwd}@{host}:{port}/{dbname}"
        self.dbname = dbname

    async def startup(self, min_size=5, max_size=20, loop=None):
        """
        Starts a connection pool with specified min and max sizes.
        Args:
            min_size (int): Minimum pool size.
            max_size (int): Maximum pool size.
            loop (asyncio.AbstractEventLoop, optional): Event loop.
        Returns: bool: True if startup fails, otherwise False.
        """
        try:
            self.pool = await asyncpg.create_pool(self.url, min_size=min_size, max_size=max_size, loop=loop)
        except Exception as e:
            self.LOG(4, 0, label="DBPG", label2="STARTUP", msg=str(e))
            return True
        self.LOG(2, 0, label="DBPG", label2="STARTUP", msg=f"CONNECTED POOL to {self.dbname}")
        return False

    def shutdown(self):
        """Terminates the connection pool and logs the shutdown."""
        self.pool.terminate()
        self.LOG(2, 0, label="DBPG", label2="shutdown", msg="DISCONNECTED")
        return False

    async def execute(self, query, *params, fetchval=False):
        """
        Executes any SQL query.
        The arguments are SQL query string and optionally the parameters to safely pass to the query.
        If query starts with SELECT returns fetched rows, otherwise result of query execution.
        On execution error return None.
        """
        try:
            async with self.pool.acquire() as con:
                # Return rows for SELECT queries
                if fetchval:
                    return await con.fetchval(query, *params)
                elif query.strip().upper().startswith('SELECT'):
                    res = await con.fetch(query, *params)
                    return parse_select_query_result(res)
                # Return execution result for other queryes
                else:
                    return await con.execute(query, *params)
        except Exception as err:
            self.LOG(4, 0, label="DBPG", label2="execute", msg={"error_msg":str(err), "query":query, "params":params})
            return None
        
    async def select(self, tbl, cols=None, filters=None, sfilters=None, join=None, lookups=None,
                     sort=None, ascending=True, offset=None, limit=None,
                     one=False, count=False):
        """
        Executes a SELECT query on a table with various options.
        Args:
            tbl (str): Table name.
            lookups (list[dict], optional): Lookup table configurations.
            join (dict, optional): Join conditions.
            filters (list[dict] or dict, optional): Exact match filters.
            sfilters (list[dict] or dict, optional): Search filters with wildcards.
            cols (str or list[str], optional): Columns to retrieve.
            sort (str, optional): Column to sort by.
            ascending (bool, optional): Sort direction.
            offset (int, optional): Query offset for pagination.
            limit (int, optional): Query limit for pagination.
            one (bool, optional): If True, returns a single row.
        Returns:
            list[dict] or dict: Query results as a list of dictionaries, or a single dictionary if `one=True`.
        """
        if not tbl: return None
        query,params = get_select_query_and_params(tbl, cols=cols, filters=filters, sfilters=sfilters, join=join, lookups=lookups,
                                                   sort=sort, ascending=ascending, offset=offset, limit=limit)
        try:
            async with self.pool.acquire() as conn:
                res = await conn.fetchrow(query, *params) if one else await conn.fetch(query, *params)
                rows = parse_select_query_result(res)
                nrows = await count_query_rows(conn, query, *params) if count and not one else None
        except Exception as e:
            self.LOG(4, 0, label="DBPG", label2="select", msg={"error_msg":str(e), "query":query, "params":params})
            return None
        if one:
            row = rows
            return row
        if count: return {'data':rows, 'nrows':nrows}
        return {'data':rows}

    async def select_one(self, tbl, filters=[]):
        """
        Retrieves a single row from a table based on filters.
        Args:
            tbl (str): Table name.
            filters (list[dict], optional): Filters for the selection.
        Returns: dict: A single row from the table that matches the filters, or None if not found.
        """
        return await self.select(tbl, filters=filters, one=True)
    
    async def select_key(self, tbl, key_col, key_val):
        """Retrieves a single row as dict from a table based on key cols and key value."""
        return await self.select(tbl, filters={key_col:key_val}, one=True)

    async def insert(self, tbl, d, return_key=None):
        """
        Inserts a new row into a table and optionally returns the primary key.
        Args:
            tbl (str): Table name.
            d (dict): Data to insert.
            return_key (str, optional): Column name of the key to return.
        Returns False on success, True on error. If return_key is specified, returns the key.
        """
        cols = list(d.keys())
        params = [convert_type(e) for e in d.values()]
        vals = [f'${k}' for k in range(1,len(params)+1)]
        query = f"INSERT INTO {tbl} ({', '.join(cols)}) VALUES ({', '.join(vals)})"
        if return_key is not None: query += f" RETURNING {return_key}"
        res = await self.execute(query, *params, fetchval=return_key is not None)
        if res is None: return True
        if return_key is not None: return res
        inserted_rows = int(res.split()[-1])
        if inserted_rows==1: return False
        return True

    async def update(self, tbl, ks, d, read_only_cols=[]):
        """
        Updates rows in a table based on specified keys.
        Args:
            tbl (str): Table name.
            ks (str or list[str]): Key column(s) to match.
            d (dict): Row data for updating.
        Returns the number of updated rows.
        """
        ks = listify(ks)
        # If there is a filter not present in the row, abort
        for k in ks:
            if k not in d: return 0
        cols = list(d.keys())
        cols = [e for e in cols if e not in read_only_cols]
        params = [convert_type(v) for k,v in d.items() if k not in read_only_cols]
        qset = ', '.join([f'{c}=${i+1}' for i,c in enumerate(cols)])
        query = f"UPDATE {tbl} SET {qset}"
        # Build filters clause
        qfilters = []
        for k in ks:
            val = d[k]
            if type(val)==str and not is_numeric_str(val): val = f"'{val[:1024]}'"
            qfilters.append(f'{k}={val}')
        if len(qfilters): query += f" WHERE {' AND '.join(qfilters)}"
        res = await self.execute(query, *params)
        if res is None: return 0
        rows_updated = int(res.split()[-1])
        return rows_updated

    async def update_or_insert(self, tbl, ks, d):
        """
        Updates an existing row if it exists, or inserts a new row otherwise.
        Args:
            tbl (str): Table name.
            ks (str or list[str]): Key column(s) to check for existing row.
            d (dict): Data for updating or inserting.
        Returns:
            bool: True if operation was successful, False otherwise.
        """
        ks = listify(ks)
        row = await self.select_one(tbl, filters={e:d[e] for e in ks})
        if row is None: return await self.insert(tbl, d) == False
        return await self.update(tbl, ks, d) > 0

    async def delete(self, tbl, ks, vs):
        """
        Deletes rows from a table based on a key-value pair.
        Args:
            tbl (str): Table name.
            k (str): Column name to match.
            v: Value to match for deletion.
        Returns:
            bool: True if deletion fails, False otherwise.
        """
        if ks is None or vs is None: return True
        ks,vs = listify(ks),listify(vs)
        ks = listify(ks)
        filters = " AND ".join([f"{k}='{v}'" for k,v in zip(ks,vs)])
        q = f"DELETE FROM {tbl} WHERE {filters}"
        res = await self.execute(q)
        if res is None: return 0
        rows_deleted = int(res.split()[-1])
        return rows_deleted

    # ################################################################################################################################
    # Admin
    # ################################################################################################################################

    def update_stats(self):
        """Updates database statistics using VACUUM ANALYZE."""
        self.sync_execute('VACUUM ANALYZE')

    async def get_trows(self, tbl):
        """
        Retrieves the estimated total number of rows in a table using PostgreSQL's `pg_class`.
        Args: tbl (str): Table name.
        Returns: int: Estimated row count for the specified table.
        """
        q = f"SELECT RELTUPLES AS NROWS FROM PG_CLASS WHERE RELNAME='{tbl}'"
        con = await self.pool.acquire()
        res = await con.fetchrow(q)
        if res is None: return -1
        return int(dict(res)["nrows"])
    
    async def get_seq(self, seqname):
        """
        Gets the next value of a specified sequence.
        Args: seqname (str): Sequence name.
        Returns: int: Next sequence value, or None if fails.
        """
        res = await self.execute(f"SELECT NEXTVAL('{seqname}')")
        return oget(res,[0,"nextval"])

    def set_seq(self, seqname):
        pass

    # ################################################################################################################################
    # Queue management
    # ################################################################################################################################

    async def enqueue(self, tbl, rec, status_col='qstatus', order_col='qts'):
        """"""
        if type(rec)!=dict: rec = {}
        rec[status_col],rec[order_col] = 0,now()
        return await self.insert(tbl, rec)

    def dequeue(self, tbl, uid_col, status_col='qstatus', order_col='qts'):
        """
        Implements a queue system with the table tbl.
        Fetches a task with status 0 (unprocessed) from the table.
        Locks the task by updating its status to 1. If the update fails, another process has locked the task.
        Returns the task id if successfully locked, or None if no task is available or already locked.
        If `order_col` is provided, it ensures tasks are fetched in a defined order, useful when external
          processing of tasks might be time-consuming, to avoid repeatedly checking the same task.
        When the task is complete its qstatus is set to 2 (DONE) or 99 (ERROR).
        """
        # Get a task with status 0
        res = self.sync_select(tbl, filters={status_col:0}, sort=order_col, ascending=True, limit=1)
        uid = oget(res,['data',0,uid_col])
        # If uid is None, no task is available
        if uid is None: return None
        # Otherwise update status to 1
        # If update fails to update any row, a concurrent process picked the same task, and the task is no longer available
        if self.sync_update(tbl, uid_col, {uid_col:uid, status_col:1})==0: return None
        # Task is safelly locked
        return uid
    
    # ################################################################################################################################
    # Sync version of main methods
    # ################################################################################################################################

    def sync_startup(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.startup(*args, **kwargs))
    def sync_execute(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.execute(*args, **kwargs))
    def sync_select(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.select(*args, **kwargs))
    def sync_select_one(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.select_one(*args, **kwargs))
    def sync_insert(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.insert(*args, **kwargs))
    def sync_update(self,  *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.update(*args, **kwargs))
    def sync_update_or_insert(self,  *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.update_or_insert(*args, **kwargs))
    def sync_delete(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.delete(*args, **kwargs))
    def sync_get_seq(self, *args, **kwargs): return asyncio.get_event_loop().run_until_complete(self.get_seq(*args, **kwargs))

# ####################################################################################################
# Utility DB functions
# ####################################################################################################


def row_to_rec(row, lookup_cols):
    """
    Adapts DB output to for front-end consuption.
    Row is produced in the DB Class and has _id and _name suffixes on lookups.
    Rec converts the suffix into an object to be sent to the front-end.
    row_to_rec converts a Row dict into a Rec dict, colapsing the id and name attrs into dicts with id,name attrs,
    for all cols with prefix incuded in lcols.
    Example for lcols=['org']:
        {'id':247, 'org_id':3215,'org_name':'RP'} -> {'id':247, 'org':{'id': 3215, 'name': 'RP'}}
    """
    exclude = [f"{e}_id" for e in lookup_cols] + [f"{e}_name" for e in lookup_cols]
    rec = {k: row[k] for k in row if k not in exclude}
    for e in lookup_cols:
        rec[e] = {"id": row[f"{e}_id"], "name": row[f"{e}_name"]}
    return rec


def res_to_recs(res, lookup_cols):
    """Applies row_to_rec to a list of res."""
    if type(lookup_cols)!=list: return res
    if type(res)==dict:
        if not "data" in res: return None
        res = res["data"]
    if type(res)!=list: return None
    return [row_to_rec(e, lookup_cols) for e in res]


def rec_to_row(rec):
    """
    Converts Front-end Rows with object columns with id,name attrs by colapsing all the lookup dicts into the id attr.
    Example:
        {'id':247, 'org': {'id':3215, 'name':'RP'}} -> {'id':247, 'org':3215}
    """
    return {k: rec[k]["id"] if type(rec[k]) == dict else rec[k] for k in rec}


def run_slq_cmds(db, q):
    """
    Executes multiple SQL commands sequentially from a string with semicolons.
    Args:
        db (DB): Database instance.
        q (str): SQL command string.
    """
    for q in q.split(";"):
        if len(q) < 10: continue
        db.sync_execute(q + ";")

def run_sql_file(db, fname):
    """
    Executes SQL commands from a file.
    Args:
        db (DB): Database instance.
        fname (str): File path containing SQL commands.
    """
    f = open(fname, "r")
    qs = f.read()
    for q in [q for q in qs.split(";")]:
        db.sync_execute(q)

def db_insert_df(db, tbl, df, dmap=None, delete=False):
    """
    Inserts a DataFrame into a database table.
    Args:
        db (DB): Database instance.
        tbl (str): Table name.
        df (pd.DataFrame): Data to insert.
        dmap (dict, optional): Column mapping dictionary.
        delete (bool, optional): If True, deletes existing rows in the table before insertion.

    Returns:
        bool: False if successful, True if an error occurs.
    """
    if delete: db.sync_execute(f"DELETE FROM {tbl}")
    if dmap is None:
        dmap = {c: c for c in df.columns}
    else:
        df = df.rename(columns=dmap)
    cols = [dmap[c] for c in dmap]
    df = df[cols]
    for i in range(len(df)):
        row = df.iloc[i]
        d = {c: row[c] for c in cols}
        if db.sync_insert(tbl, d):
            print("DB insert error")
    return False

def log_and_return(msg):
    print(msg)
    return msg

def db_export_tbl(db, p, tbl):
    """
    Exports a table to a pickle file.
    Args:
        db (DB): Database instance.
        p (str): Path to save the file.
        tbl (str): Table name.

    Returns:
        int: 0 if successful, 1 if an error occurs.
    """
    res = db.sync_select(tbl, limit=int(1e9))
    if res is None or not "data" in res: return 1
    return pickle_save(p, res["data"])

def db_import_tbl(db, p, tbl, delete=False):
    """
    Imports data from a pickle file into a table.
    Args:
        db (DB): Database instance.
        p (str): Path to the pickle file.
        tbl (str): Table name.
        delete (bool, optional): If True, deletes existing rows before import.
    Returns:
        int: 0 if successful, otherwise 1.
    """
    p = Path(p)
    if not p.with_suffix(".pickle").is_file():
        return log_and_return(f"Error importing {tbl}: file {p} not found")
    rows = pickle_load(p)
    if rows is None:
        return log_and_return(f"Cant read {p}")
    if delete:
        if db.sync_execute(f"delete from {tbl}"):
            return log_and_return(f"Error deleting tbl {tbl}")
    n = 0
    for row in rows:
        res = db.sync_insert(tbl, row)
        if res:
            return log_and_return(f"Error inserting record into {tbl}: {row}")
        n += 1
    print(f"Imported {n} records into {tbl}")
    return 0

def db_disable_serial(db, tbl, col):
    """
    Disables auto-increment on a table column.
    Args:
        db (DB): Database instance.
        tbl (str): Table name.
        col (str): Column name.
    """
    db.sync_execute(f"ALTER TABLE {tbl} ALTER COLUMN {col} DROP DEFAULT")

def db_enable_serial(db, tbl, col):
    """
    Enables auto-increment on a table COLUMN.
    Args:
        db (DB): Database instance.
        tbl (str): Table name.
        col (str): Column name.
    """
    n = db.sync_execute(f"SELECT max({col}) FROM {tbl}")[0]["max"]
    db.sync_execute(f"SELECT pg_catalog.setval('public.{tbl}_{col}_seq', {n}, true)")
    db.sync_execute(
        f"ALTER TABLE {tbl} ALTER COLUMN {col} SET DEFAULT nextval('{tbl}_{col}_seq')"
    )
