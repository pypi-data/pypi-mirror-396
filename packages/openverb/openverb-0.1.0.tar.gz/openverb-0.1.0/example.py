"""
Simple OpenVerb executor example
Based on examples/python-executor from the OpenVerb repo
"""

from openverb import load_core_library, create_executor

# Simple in-memory database
db = {
    'jobs': []
}

# Load core library and create executor
library = load_core_library()
executor = create_executor(library)

# Register handlers for core verbs
def create_item_handler(params):
    collection = params['collection']
    data = params['data']
    if collection not in db:
        db[collection] = []
    
    item_id = str(len(db[collection]))
    item = {'id': item_id, **data}
    db[collection].append(item)
    
    return {
        'verb': 'create_item',
        'status': 'success',
        'data': item
    }

def list_items_handler(params):
    collection = params['collection']
    items = db.get(collection, [])
    return {
        'verb': 'list_items',
        'status': 'success',
        'items': items
    }

def get_item_handler(params):
    collection = params['collection']
    item_id = params['id']
    items = db.get(collection, [])
    
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return {
            'verb': 'get_item',
            'status': 'error',
            'error_message': f"Item {item_id} not found in {collection}"
        }
    
    return {
        'verb': 'get_item',
        'status': 'success',
        'data': item
    }

def update_item_handler(params):
    collection = params['collection']
    item_id = params['id']
    data = params['data']
    items = db.get(collection, [])
    
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        return {
            'verb': 'update_item',
            'status': 'error',
            'error_message': f"Item {item_id} not found in {collection}"
        }
    
    item.update(data)
    
    return {
        'verb': 'update_item',
        'status': 'success',
        'data': item
    }

def delete_item_handler(params):
    collection = params['collection']
    item_id = params['id']
    
    if collection not in db:
        return {
            'verb': 'delete_item',
            'status': 'error',
            'error_message': f"Collection {collection} not found"
        }
    
    items = db[collection]
    item = next((i for i in items if i['id'] == item_id), None)
    
    if not item:
        return {
            'verb': 'delete_item',
            'status': 'error',
            'error_message': f"Item {item_id} not found in {collection}"
        }
    
    db[collection].remove(item)
    
    return {
        'verb': 'delete_item',
        'status': 'success',
        'success': True
    }

# Register handlers
executor.register('create_item', create_item_handler)
executor.register('list_items', list_items_handler)
executor.register('get_item', get_item_handler)
executor.register('update_item', update_item_handler)
executor.register('delete_item', delete_item_handler)


def demo():
    """Run a demo of the OpenVerb executor."""
    print('🚀 OpenVerb Executor Demo\n')
    print(f'Available verbs: {", ".join(executor.get_verbs())}')
    print()
    
    # Create an item
    print('1️⃣ Creating a job...')
    create_action = {
        'verb': 'create_item',
        'params': {
            'collection': 'jobs',
            'data': {
                'client': 'Smith Construction',
                'job_type': 'Boundary Survey',
                'status': 'pending'
            }
        }
    }
    
    result1 = executor.execute(create_action)
    print('Result:', result1)
    print()
    
    # Create another item
    print('2️⃣ Creating another job...')
    create_action2 = {
        'verb': 'create_item',
        'params': {
            'collection': 'jobs',
            'data': {
                'client': 'Jones Development',
                'job_type': 'Topographic Survey',
                'status': 'active'
            }
        }
    }
    
    result2 = executor.execute(create_action2)
    print('Result:', result2)
    print()
    
    # List all jobs
    print('3️⃣ Listing all jobs...')
    list_action = {
        'verb': 'list_items',
        'params': {'collection': 'jobs'}
    }
    
    result3 = executor.execute(list_action)
    print('Result:', result3)
    print()
    
    # Get single item
    print('4️⃣ Getting job #0...')
    get_action = {
        'verb': 'get_item',
        'params': {
            'collection': 'jobs',
            'id': '0'
        }
    }
    
    result4 = executor.execute(get_action)
    print('Result:', result4)
    print()
    
    # Update item
    print('5️⃣ Updating job #0...')
    update_action = {
        'verb': 'update_item',
        'params': {
            'collection': 'jobs',
            'id': '0',
            'data': {
                'status': 'completed'
            }
        }
    }
    
    result5 = executor.execute(update_action)
    print('Result:', result5)
    print()
    
    # Try invalid action (missing required param)
    print('6️⃣ Testing validation (missing required param)...')
    invalid_action = {
        'verb': 'create_item',
        'params': {
            # Missing 'collection' param
            'data': {'test': 'value'}
        }
    }
    
    result6 = executor.execute(invalid_action)
    print('Result:', result6)
    print()
    
    # Try unknown verb
    print('7️⃣ Testing unknown verb...')
    unknown_action = {
        'verb': 'unknown_verb',
        'params': {}
    }
    
    result7 = executor.execute(unknown_action)
    print('Result:', result7)
    print()
    
    print('✅ Demo complete!')


if __name__ == '__main__':
    demo()
