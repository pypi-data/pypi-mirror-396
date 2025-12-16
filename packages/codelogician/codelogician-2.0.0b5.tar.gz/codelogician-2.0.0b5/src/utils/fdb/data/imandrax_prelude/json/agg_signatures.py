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

# %%
modules = glob.glob('*.json')  # noqa: PTH207
modules.remove("Prelude.json")
modules.remove("iml_func.json")

# %%
with open('Prelude.json') as f:
    data = json.load(f)["data"]

# %%
for item in data:
    if item["type"] == "function":
        print(item["signature"])

# %%
for module in modules:
    with open(module) as f:
        data = json.load(f)["data"]

    module_name = module.split('.')[0]
    print(f"- Module: `{module_name}`")
    print("```iml")
    print(f"module type {module_name} = sig")
    for item in data:
        # if item["type"] == "function":
        print("  " + item["signature"])
    print("end")
    print("```")
    print("")
