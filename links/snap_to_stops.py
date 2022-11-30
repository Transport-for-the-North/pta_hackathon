"""

API:
https://true-swans-flow-34-89-73-233.loca.lt

Format of request:
Dictionary with 2 keys:
‘lat_long’ = tuple of lat, long
‘acceptable_distance’ = how far from the lat long selection to search within (in meters)

Example request:
requests.post('https://true-swans-flow-34-89-73-233.loca.lt', json={'lat_long': (51.44901, -2.58569), 'acceptable_distance': 1000}).json()

"""