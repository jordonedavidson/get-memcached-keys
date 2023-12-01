#!/usr/bin/env python3

from pymemcache.client.base import Client
from urllib.parse import unquote
import json
import argparse

# defaults for memcached server host and port.
host = 'localhost'
port = 11211
outputFileName = 'drupal-keys.json'

# Instantiate cli argument parser
parser = argparse.ArgumentParser(
    description='Retrieve keys from Drupal memcached.')

# Set cli named parameters
parser.add_argument('--host', '-H',
                    help='Memcached server hostname')
parser.add_argument('--port', '-P', type=int,
                    help='Port the memcached server is running on')
parser.add_argument(
    '--file', '-F', help="Filename to write to (without extention)")

# load the cli arguments
args = parser.parse_args()

if args.host:
    host = str(args.host)

if args.port:
    port = int(args.port)

if args.file:
    outputFileName = int(args.file) + '.json'


# Listing of the active slabs that will be used to get the keys
slabNumbers = set()

# dictionary of dictionaries holding the keys in each slab
slabKeys = dict()

# instantiate connecton to client.
client = Client((host, port))

# load all slabs
slabs = client.stats('slabs')

# this loop will provide the active slab numbers needed to get the keys
for key, value in slabs.items():
    # the keys are bytes types so they need to be decoded.
    # the key has the form <slab number>:<name>
    keyParts = key.decode().split(':')
    # add the slab number to the set.
    if keyParts[0].isdigit():
        slabNumbers.add(keyParts[0])

# get all keys from each slab
for slab in slabNumbers:
    keys = list()
    dpkeys = list()
    otherKeys = list()

    # using the cachedump command will provide all the keys for the given slab
    command = f'stats cachedump {slab} 0'
    rawKeys = client.raw_command(command, "END").decode()

    # the rawKeys are a newline delimited string.
    splitKeys = rawKeys.splitlines()

    # the keys we want all start with ITEM
    # test for that then split the key on space and load the 1th element into the new array.
    for item in splitKeys:
        if item.startswith('ITEM'):
            itemParts = item.split(' ')
            # only want the dp_ ones
            if itemParts[1].startswith('dp_'):
                dpkeys.append(unquote(itemParts[1]))
            else:
                # Keep track of any other ITEM keys that are available.
                keys.append(unquote(itemParts[1]))
        else:
            # This picks up any extraneous keys and their values in the cache.
            otherKeys.append(unquote(item))

    # There may be up to 3 types of keys. but we only want to add them if they exist.
    allKeyTypes = [{'dpKeys': dpkeys}]

    if len(keys) > 0:
        allKeyTypes.append({'keys': keys})

    if len(otherKeys) > 0:
        allKeyTypes.append({'other': otherKeys})

    # add the keys to the dictionary.
    slabKeys[slab] = allKeyTypes

# convert the dictionary into a list sorted on the keys.
# sorted looks at the items of the dictionary and orders them based on the value of the lambda function
# in this case sorting by the integer value of the dictionary key.
# json.dumps converts the sorted list into correct JSON format.
output = json.dumps(sorted(slabKeys.items(), key=lambda x: int(x[0])))

# write the results to a file in the same directory.
try:
    with open(outputFileName, 'w') as file:
        file.write(output)
        print(f'The file {outputFileName} is now available')
except IOError as e:
    print(f'An I/O error occurred: {e}')
except Exception as e:
    print(f'An unexpected error occurred: {e}')
