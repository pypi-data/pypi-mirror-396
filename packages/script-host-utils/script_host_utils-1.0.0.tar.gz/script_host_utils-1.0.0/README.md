# script_host_utils

Script host utils.

## Installation

```bash
pip install script_host_utils
```

## Usage

```python
from script_host_utils import filtered_json_dumps, levenshtein_distance
import json

assert(
    json.loads(filtered_json_dumps(
        # obj
        {
            "key_for_extract_1": {
                "subkey_for_extract_11": 1,
                "subkey_for_extract_12": 2,
                "subkey_for_EXCLUDE_13": 3
            },
            "key_for_extract_2": {
                "subkey_for_extract_21": 1,
                "subkey_for_EXCLUDE_22": 2
            },
            "key_as_is_3": 1
        },
        # filter_obj
        {
            "key_for_extract_1": ["subkey_for_extract_11", "subkey_for_extract_12"],
            "key_for_extract_2": ["subkey_for_extract_21"]
        },
        # mapping_obj
        {
            "subkey_for_extract_21": "zzz"
        }
    )) == {
        "key_for_extract_1": {
            "subkey_for_extract_11": 1,
            "subkey_for_extract_12": 2
        },
        "key_for_extract_2": {
            "zzz": 1
        },
        "key_as_is_3": 1
    }
)

assert(levenshtein_distance("q123wer456", "zq823wer456z") == 3)
```
