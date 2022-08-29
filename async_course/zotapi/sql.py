from sqlite3 import Connection
from django.conf import settings

def exec_fetchall(*args):
    conn = Connection(settings.ZOTERO_DB)
    cursor = conn.cursor()
    cursor.execute(*args)
    values = cursor.fetchall()
    conn.close()
    return values

get_item_ids_and_keys_in_collection = """
SELECT 
    itemID,
    items.key

FROM 
    collectionItems 
    JOIN collections USING (collectionID)
    JOIN items USING (itemID)
WHERE 
    collections.collectionName=:collection_name
"""

get_item_data = """
SELECT 
    fields.fieldName, 
    itemDataValues.value 
FROM 
    itemDataValues 
    JOIN itemData 
    JOIN fields 
WHERE 
    itemData.itemID=:item_id
    AND itemData.valueID=itemDataValues.valueID 
    AND itemData.fieldID=fields.fieldID
"""

get_item_attachments = """
SELECT 
    items.key,
    itemAttachments.path
FROM 
    itemAttachments 
    JOIN items USING (itemID)
WHERE
    parentItemID=:item_id
"""

get_ids_citation_keys_attachments_for_collection = """
SELECT
    items.itemID, 
    itemDataValues.value, 
    itemAttachments.path
FROM
    items
    JOIN collectionItems USING itemID
    JOIN collections USING collectionID
    JOIN itemDataValues USING itemID
    JOIN fields USING fieldID
WHERE 
    collections.collectionName=:collection_name
    AND fields.fieldName="citationKey"
    AND itemDataValues
"""

get_item_creators = """
SELECT 
    creatorTypeID,
    creatorType, 
    firstName, 
    lastName, 
    orderIndex 
FROM 
    itemCreators 
    JOIN creators USING (creatorID) 
    JOIN creatorTypes USING (CreatorTypeID) 
WHERE 
    itemID=:item_id;
"""

get_item_keys = """

"""



# What I want is:
#
# collection_name =>  {
    #"citation_key": "path_to_file"
# }
#
