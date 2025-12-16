#
# dbutils.py
#

from dl2050utils.core import oget, check_str, is_numeric_str, check

# ####################################################################################################
# Utils
# ####################################################################################################

def str_to_int_or_float(s):
    """
    Convert a string to an int or float depending on the contetent.
    If not a numeric string return the string as is.
    """
    if not is_numeric_str(s): return s
    v = float(s)
    if int(v)==v: return int(v)
    return v

def is_valid_list(l):
    """Returns True if l is a list and all elements are basic elements, False otherwise"""
    if type(l)!=list: return False
    allowed_types = (int, float, str, bool, type(None))
    return True if all(isinstance(e, allowed_types) for e in l) else False

def convert_filter_val(val, max_sz=1024, none_val='NULL'):
    """
    """
    if val is None: return none_val
    if type(val) in [bool,int,float]: return val
    # if is_numeric_str(val): return  str_to_int_or_float(val)
    if type(val)==str: return val[:max_sz]
    return None

# ####################################################################################################
# parse_filter
# ####################################################################################################

def parse_filter(f, max_sz=1024):
    """
    Checks if a filter is valid.
    The filter is valid if it contains col,val attributes.
    col attribute must be string.
    val attributes can be string, int, float or lists of basic elements, only for IN and NOT IN operators.
    String attributes are enforce to max lengh of max_sz.
    Returns the filter cleared of extra attributes or None if error.
    """
    # Check for valid filter structure
    if type(f)!=dict: return None
    if 'col' not in f or 'val' not in f: return None
    if type(f['col'])!=str: return None
    col,val = f['col'][:max_sz],f['val']
    op = oget(f,['op'],'=').upper()
    if op=='NOT IN': op = 'NOT_IN'
    # Check basic filters (not lists)
    if type(val)!=list:
        if op not in ['=', '!=', '>', '>=', '<', '<=']: return None
        val = convert_filter_val(val, max_sz=max_sz)
        if val=='NULL':
            if op=='!=': val = 'NOT NULL'
            op = ' IS '
        return {'col':col, 'val':val, 'op':op}
    # List values are only allowed for IN and NOT_IN ops
    if op not in ['IN', 'NOT_IN']: return None
    # List must contain only base elements
    if not is_valid_list(val): return None
    # Convert all list value elements
    val = [convert_filter_val(e) for e in val]
    return {'col':col, 'val':val, 'op':op}

# ####################################################################################################
# parse_filters
# ####################################################################################################

def parse_filters(fs, max_sz=1024):
    """
    Filters can be either a list of dicts or a dict with key/vals representing filter conditions.
    A dict filter is converted into a list filters.
    All list filter elements are dicts with one filter condition defined by key/val and optionally the op attributes.
    The op attribut can be =, < , > , <=, >=, !=, IN, NOT_IN
    Examples:
        - Dict filter: {'id':1, 'name':'name1'}
        - List filter: [{'col':'id', 'val':1 'op':'='}, {'col':'name', 'val':'name1' 'op':'='}]
    """
    # Filters must be either dict or list
    if type(fs)!=dict and type(fs)!=list: return []
    # Dict filters are converted into list filters
    if type(fs)==dict:
        fs = [{'col':check_str(e, n=1024), 'val':check(fs[e]), 'op':'='} for e in fs]
    # List filters
    fs2 = []
    for f in fs:
        f2 = parse_filter(f, max_sz=max_sz)
        if f2 is None: continue
        fs2.append(f2)
    return fs2
