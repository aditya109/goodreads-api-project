try:
    import json
except Exception as e:
    print(e)


def error_provider():
    print(json.dumps({'error': 'Uh Oh ! Sorry Not Found'}))

