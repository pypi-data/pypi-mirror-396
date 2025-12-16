from dl2050utils.common import oget, now
from dl2050utils.core import LexIdx

# #############################################################################################################################
# Utils
# #############################################################################################################################

async def get_lseq(db, tbl, col, val):
    """Extracts lseq record from tbl applyng an id filter on col."""
    row = await db.select_one(tbl, filters={col:val})
    lseq = oget(row,['lexseq'])
    return lseq

async def get_lseq_on_reorder(db, tbl, col, id0, id1, id2, insert_mode=False):
    """Produces the new lseq for a re-order operation for tbl."""
    l = LexIdx()
    # If no re-order is required, return None of updates and insert in the end for inserts
    if id1 is None and id2 is None:
        if insert_mode:
            res = await db.execute(f"select max(lexseq) from {tbl} where {col}='{id0}'")
            lseq = oget(res,[0,'max'])
            return l.next(lseq)
        return None
    # Procede with finding the new lseq
    # If id1 is specified and id2 is None, inserts in the end
    if id2 is None:
        res = await db.execute(f"select max(lexseq) from {tbl} where {col}='{id0}'")
        lseq = oget(res,[0,'max'])
        return l.next(lseq)
    # Otherwise interpolates
    lseq1 = await get_lseq(db, tbl, 'item_id',id1)
    lseq2 = await get_lseq(db, tbl, 'item_id',id2)
    return l.interpolate(lseq1, lseq2)

# #############################################################################################################################
# Ulists
# #############################################################################################################################

async def ulists_insert(db, email, ulist_code, ulist_name=None, ulist_payload=None):
    """
    Inserts a new ulist into the database or returns the list if it altready exists.
    Returns the inserted UList or if ulist_code exists returns it along with all items instead of inserting.
    """
    # Check for existing ulist_code
    filters = [{'col':'email', 'val':email}, {'col':'ulist_code', 'val':ulist_code}]
    res = await db.select('ulists', filters=filters, limit=1)
    rows = oget(res,['data'],[])
    if len(rows)!=0:
        row = rows[0]
        filters = [{'col':'email', 'val':email}, {'col':'ulist_code', 'val':row['ulist_code']}]
        res = await db.select('ulist_items', filters=filters, limit=1024)
        row['items'] = oget(res,['data'],[])
        return row
    # Otherwise create the record
    row = {'email':email, 'ulist_code':ulist_code, 'ulist_name':ulist_name, 'ulist_payload':ulist_payload, 'created_at':now()}
    res = await db.insert('ulists', row)
    row['items'] = []
    return row

async def ulists_update(db, email, ulist_code=None, ulist_name=None, ulist_payload=None):
    """
    Returns False on success, True on error.
    """
    # Create the record
    row = {'email':email, 'ulist_code':ulist_code, 'ulist_name':ulist_name, 'ulist_payload':ulist_payload}
    n = await db.update('ulists', ['email','ulist_code'], row, read_only_cols=['ulist_code'])
    return n!=1

async def ulists_delete(db, email, ulist_code):
    """
    Returns False on success, True on error.
    """
    n = await db.delete('ulists', ['email', 'ulist_code'], [email, ulist_code])
    return n!=1

async def ulists_select(db, email, ulist_code=None):
    """
    Selects ulists for user defined by email. If  ulist_code is passed return that UList with all items.
    """
    if ulist_code is not None:
        res = await db.select('ulists', filters={'email':email, 'ulist_code':ulist_code}, limit=1)
        rows = oget(res,['data'],[])
        if len(rows)!=0:
            row = rows[0]
            filters = [{'col':'email', 'val':email}, {'col':'ulist_code', 'val':row['ulist_code']}]
            res = await db.select('ulist_items', filters=filters, limit=1024)
            row['items'] = oget(res,['data'],[])
            return row
        return None
    res = await db.select('ulists', filters={'email':email}, limit=1024)
    rows = oget(res,['data'])
    return rows

# #############################################################################################################################
# Items
# #############################################################################################################################

async def ulist_items_insert(db, email, ulist_code, item_name=None, item_payload=None, item_id_1=None, item_id_2=None):
    """
    Inserts a new item for an ulist.
    Returns False on success, True on error.
    """
    # Create the record
    row = {'email':email, 'ulist_code':ulist_code, 'item_name':item_name, 'item_payload':item_payload}
    # Manage order: either interpolate item_id_1, item_id_2 or insert at the end
    row['lexseq'] = await get_lseq_on_reorder(db, 'ulist_items', 'ulist_code', ulist_code, item_id_1, item_id_2, insert_mode=True)
    await db.insert('ulist_items', row)
    return None

async def ulist_items_update(db, email, item_id, ulist_code, item_name=None, item_payload=None, item_id_1=None, item_id_2=None):
    """
    Returns True on error, False if everything ok.
    """
    # Create the record
    row = {'email':email, 'item_id':item_id, 'item_name':item_name, 'item_payload':item_payload}
    # Re-order if either item_id_1 or item_id_2 is provided
    lexseq = await get_lseq_on_reorder(db, 'ulist_items', 'ulist_code', ulist_code, item_id_1, item_id_2)
    if lexseq is not None: row['lexseq'] = lexseq
    n = await db.update('ulist_items', ['email','item_id'], row, read_only_cols=['item_id'])
    return n!=1

async def ulist_items_delete(db, email, item_id):
    """
    Returns False on success, True on error.
    """
    n = await db.delete('ulist_items', ['email','item_id'], [email,item_id])
    return n!=1

async def ulist_items_select(db, email, ulist_code):
    """
    Selects all items from an ulist with a 1024 limit.
    Returns de selected rows.
    """
    filters = [{'col':'email', 'val':email}, {'col':'ulist_code', 'val':ulist_code}]
    res = await db.select('ulist_items', filters=filters, sort='lexseq', limit=1024)
    rows = oget(res,['data'])
    return rows
