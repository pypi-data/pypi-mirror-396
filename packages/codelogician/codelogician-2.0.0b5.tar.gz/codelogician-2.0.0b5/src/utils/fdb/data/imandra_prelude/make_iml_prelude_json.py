# %% [markdown]
# ### Aggregate all module json files into one

# %%
import json
import os

# %%
iml_prelude_modules = [
    "iml_List_module.json",
    "iml_Option_module.json",
    "iml_Set_module.json",
    "iml_Map_module.json",
    "iml_LChar_module.json",
    "iml_LString_module.json",
    "iml_Multiset_module.json",
    "iml_arithmetic.json",
    "iml_Result_module.json",
]

# %%
agg_d = {
    "title": "Imandra Prelude",
    "level": "Low",
    "elements": [],
    "metadata": {
        "source": []
    }
}
for module in iml_prelude_modules:
    d = json.loads(open(os.path.join('json', module)).read())  # noqa: SIM115, PTH118
    agg_d['elements'].extend(d['elements'])
    agg_d['metadata']['source'].append(module)


# %%
with open('../table/iml_prelude.json', 'w') as f:
    json.dump(agg_d, f)
