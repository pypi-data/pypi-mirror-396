#
# dbdf.py
#
import polars as pl
from dl2050utils.dbutils import parse_filters

# ####################################################################################################
# df_filter
# ####################################################################################################

def df_filter(df, filters, sfilters=None):
    """
    Filters a Polars DataFrame based on a filters structure.
        - df: Polars DataFrame to filter.
        - filters: A list of filter dictionaries or a dictionary of filters.
    Return the filtered DataFrame.
    """
    # Check inputs
    if df is None or not len(df): return df
    if filters is None and sfilters is None: return df
    # If it is a simple filter of type {'col':<col>, 'val':<val>}} convert into list
    if type(filters)==dict and 'col' in filters and 'val' in filters: filters = [filters]
    if type(sfilters)==dict and 'col' in sfilters and 'val' in sfilters: sfilters = [sfilters]
    # Parse filters
    filters = parse_filters(filters)
    sfilters = parse_filters(sfilters)
    # If no valid filters, return the original DataFrame
    if not filters and not sfilters: return df
    # Apply the filters
    for f in filters:
        # Cast the val to the same type as the col in the dataframe
        try:
            col,val,op = f['col'],f['val'],f['op']
            # Apply type conversion, ignore filter on failure
            try:
                if df.schema[col]==pl.String:
                    val = [str(e) for e in val] if type(val)==list else str(val)
                if df.schema[col] in [pl.Int16,pl.Int32,pl.Int64]:
                    val = [int(e) for e in val] if type(val)==list else int(val)
                if df.schema[col] in [pl.Float32,pl.Float64]:
                    val = [float(e) for e in val] if type(val)==list else float(val)
            except Exception as exc:
                print(exc)
                continue
            # Handle operations
            if op == '=' or op == '==': df = df.filter(pl.col(col)==val)
            elif op == '!=': df = df.filter(pl.col(col)!=val)
            elif op == '>': df = df.filter(pl.col(col)>val)
            elif op == '>=': df = df.filter(pl.col(col)>=val)
            elif op == '<': df = df.filter(pl.col(col)<val)
            elif op == '<=': df = df.filter(pl.col(col)<=val)
            elif op == 'IN':
                df = df.filter(pl.col(col).is_in(val))
            elif op == 'NOT_IN':
                df = df.filter(~pl.col(col).is_in(val))
            elif op == 'IS':
                if val=='NOT NULL': df.filter(pl.col(col).is_not_null(val))
                else:  df.filter(pl.col(col).is_null(val))
        except Exception as exc:
            print('Exception', exc)
            continue
    # Handle string containment filters
    if sfilters:
        for sf in sfilters:
            col,val = sf['col'],sf['val']
            val = str(val)
            words = val.split()
            for word in words:
                word = word.lower()
                df = df.filter(pl.col(col).str.to_lowercase().str.contains(word))
    return df

# #########################################################################################################################
# df_sort
# #########################################################################################################################

def df_sort(df, sort, ascending=None):
    """
    """
    ascending = False if ascending==False else True
    if sort and sort in df.columns: return df.sort(sort, descending=not ascending)
    return df

# #########################################################################################################################
# df_get_tbl
# #########################################################################################################################

def df_get_tbl(df, cols=None, filters=None, sfilters=None, sort=None, ascending=True, offset=None, limit=None, excel=False,
               join=None):
    """
    Processes a Polars DataFrame by applying filters, sorting, column selection, and pagination, 
    and prepares the result as a dictionary suitable for JSON serialization with orjson.
    Parameters:
    - df (pl.DataFrame): The DataFrame to process. Returns an empty result if None.
    - cols (list, optional): Subset of column names to include in the result. Defaults to all columns.
    - filters (list/dict, optional): Filters to apply (e.g., `=`, `!=`, `>`, `<`, `IN`).
    - sfilters (list/dict, optional): String filters matching all words in the specified columns.
    - sort (str, optional): Column name to sort the DataFrame by.
    - ascending (bool, default=True): Whether to sort in ascending order (False for descending).
    - offset (int, optional): Starting index for row slicing. Defaults to 0.
    - limit (int, default=64): Maximum number of rows to include in the result.
    - one (bool, optional): Unused, placeholder for returning single-row results.
    - excel (bool, optional): Used for exporting to Excel, returns the filtered dataframe for conversion.
    - join (str, optional): Unused, placeholder for joining tables.
    - lookups (dict, optional): Unused, placeholder for enriching data with lookups.
    Returns:
    dict: {
        'data': List of dictionaries (rows in the DataFrame),
        'nrows': Total rows in the filtered DataFrame before slicing,
        'cols': List of included column names.
    }
    """
    if df is None: return None
    df = df_filter(df, filters, sfilters)
    df = df_sort(df, sort, ascending)
    cols = [e for e in cols if e in df.columns] if cols else df.columns
    df = df.select(cols)
    if excel: return df
    nrows = len(df)
    offset,limit = 0 if offset is None else int(offset),64 if limit is None else int(limit)
    df = df[offset:offset+limit]
    rows = df.to_dicts()
    return {'data':rows, 'nrows':nrows, 'cols':cols}
