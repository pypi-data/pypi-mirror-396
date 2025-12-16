- Data is stored as `data.yaml` files in the `data` directory.

- `gen_template.py` provides a way to generate a YAML item from a directory of files.
- `unzip_yaml.py` generates a directory of files from a YAML item.

- `agg.py` aggregates all the data into a single object that can be used by FDB.


For adding new data, the general procedure is:
1. Add a new directory to the `data` directory.
2. For each item, create a subdir
    - `repro.iml` for the repro IML, which generates the error message
    - `solution.iml` for the solution IML, which should fix the error and has no other errors
    - `solution_([1-9]+).iml` for the alternative solutions
    - other fields are optional in a `item.yaml` file. normally we have "explanation" and "solution_description".
    - the subdir name will be used as the `name` field in the YAML item
