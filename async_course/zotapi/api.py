from django.conf import settings
from zotapi.sql import (
    exec_fetchall,
    get_item_data,
    get_item_ids_and_keys_in_collection,
    get_item_creators,
    get_item_attachments,
)

STRIP_FROM_CITE_KEY = " ’'"

def get_item_ids_and_keys(collection_name):
    ids =  exec_fetchall(get_item_ids_and_keys_in_collection, 
            {"collection_name": collection_name})
    return [{'id': i, 'key': k} for i, k in ids]

def get_creators(item_id):
    data = exec_fetchall(get_item_creators, {'item_id': item_id}) 
    return [
        {'role_id': rid, 'role': r, 'first_name': fn, 'last_name': ln, 'index': i} 
        for rid, r, fn, ln, i in data
    ]

def get_attachments(item_id):
    data = exec_fetchall(get_item_attachments, {'item_id': item_id})
    return [settings.ZOTERO_DATA_DIR / "storage" / p / f.strip("storage:") for p, f in data]

def get_data(item_id):
    data = exec_fetchall(get_item_data, {"item_id": item_id})
    return dict(data)

def parse_extra_data(extra):
    return dict([[val.strip() for val in line.split(':')] for line in extra.split('\n')])

def get_citation_key(item_id):
    data = get_data(item_id)
    if 'extra' in data:
        extra = parse_extra_data(data['extra'])
        if 'Citation Key' in extra:
            return extra['Citation Key']
    creators = get_creators(item_id)
    first_author_last_name = ''
    first_creators = sorted([c for c in creators if c['index'] == 0], 
            key=lambda c: c['role_id'])
    if first_creators: 
        first_author = first_creators[0]['last_name'].lower()
    else:
        first_author = ''
    for char in STRIP_FROM_CITE_KEY:
        first_author = first_author.replace(char, '')
    date = data['date'][:4] if 'date' in data else ''
    return first_author + date
        
