# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: cogito
#     language: python
#     name: python3
# ---

# %%
import glob
import json

# load all json files in the current directory
json_files = glob.glob("*.json")  # noqa: PTH207

try:  # noqa: SIM105
    json_files.remove("iml_func.json")
except ValueError:
    pass

agg_d = {
    "schema": {
        "module": "string",
        "name": "string",
        "type": "string",
        "signature": "string",
        "doc": "string",
        "pattern": "string",
    },
    "data": [],
    "program_prelude": {},
}
for module in json_files:
    d = json.loads(open(module).read())  # noqa: SIM115
    agg_d['data'].extend(d['data'])
    if "program_prelude" in d:
        agg_d['program_prelude'][module.split('.')[0]] = d['program_prelude']
    else:
        print(f"No program_prelude in {module}")
        agg_d['program_prelude'][module.split('.')[0]] = []

# %%
with open('./iml_func.json', 'w') as f:
    json.dump(agg_d, f, indent=4)
