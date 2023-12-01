# Script for retreiving the keys from MtA website Memcached server

All keys are output into a JSON document which is in the form:

```json
[
  [
    "Slab number",
    [
      {
        "dpkeys": [["array of ITEM keys beginning with dp_"]],
        "keys": [["array of remaing ITEM keys", "if any exist"]],
        "other": [
          ["array keys and values that did not begin with ITEM", "if any exist"]
        ]
      }
    ]
  ]
]
```

## How to use

Call the `get-keys.py` command from the command line.

By default this will connect to the memcached server running on localhost at port 11211. The resulting JSON data will be output to the file `drupal-keys.json` in the same directory.

### Optional flags

The following flags may be used to modify the defaults.

- --host, -H : Specify the hostname or IP address of the memcached server
- --port, -P : Specify the port the memcached server is running on.
- --file, -F : Specify the name of the file to output to. (The .json extention will be added by the script.)
