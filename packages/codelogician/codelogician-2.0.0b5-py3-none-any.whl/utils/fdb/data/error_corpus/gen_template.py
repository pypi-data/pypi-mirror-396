"""
Given a piece of IML that contains errors, generate a template for each error.

- We resort to pydantic for handling all the serialization
    - ItemTemplate(pydantic.BaseModel) -> json string --json.loads -> dict[str, str]
- We use yaml with representer for specific fields to dump the
    dict[str, str] to yaml string
"""
# ruff: noqa: RUF100, F401

import json
from functools import singledispatch
from pathlib import Path
from typing import Final, reveal_type

import typer
import yaml

from utils.fdb.data.error_corpus.schema import ItemTemplate
from utils.imandra.imandrax.client import eval_src, get_imandrax_client
from utils.imandra.imandrax.proto_models import Error, ErrorKind, ErrorMessage, EvalRes

app = typer.Typer()

# ====================
# Yaml dump
# ====================


def dir_to_template(dir_path: Path, name: str) -> ItemTemplate:
    """Generate partial item from a piece of IML.

    Only the first error is returned."""
    repro_iml_p = dir_path / "repro.iml"
    if not repro_iml_p.exists():
        raise ValueError(f"No repro.iml in {dir_path}")
    repro_iml = repro_iml_p.read_text()

    client = get_imandrax_client()

    # Extract error (the first one) from repro.iml
    eval_res = eval_src(client, repro_iml)
    if not eval_res.has_errors:
        raise ValueError(f"No errors for repro.iml in {dir_path}")

    non_po_error = eval_res.errors
    is_po_err = len(non_po_error) == 0
    errors = [*non_po_error, *eval_res.po_errors]
    error = errors[0]
    err_msg = error.msg
    assert err_msg is not None
    data = {
        "name": name,
        "kind": ErrorKind.from_proto_kind(error.kind),
        "msg_str": err_msg.msg,
        "repro_iml": repro_iml,
        "err_msg": err_msg,
        "is_po_err": is_po_err,
    }

    # Validate solution
    if (dir_path / "solution.iml").exists():
        solution_paths = [dir_path / "solution.iml"]
        solution_paths.extend(dir_path.glob("**/solution.iml"))

        for solution_path in solution_paths:
            solution = solution_path.read_text()
            eval_res = eval_src(client, solution)
            if eval_res.has_errors:
                raise ValueError(f"Solution has errors: {solution_path}")
            data[solution_path.stem] = solution

    # Extra info
    if (dir_path / "item.yaml").exists():
        with (dir_path / "item.yaml").open() as f:
            extra = yaml.safe_load(f)
        data.update(extra)

    model = ItemTemplate.model_validate(data)
    return model


class literal_str(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal_str, literal_presenter)


def format_as_multiline_liter(field_name: str) -> bool:
    if field_name in ["repro_iml", "explanation", "msg_str"] or field_name.startswith(
        "solution"
    ):
        return True
    else:
        return False


def models_to_yaml_str(models: list[ItemTemplate]) -> str:
    """Generate YAML string from pydantic.BaseModel"""
    # Sort models by id (uuidv7)
    models = sorted(models, key=lambda x: x.id)

    # model to str dict
    str_dict: list[dict[str, str]] = [
        json.loads(model.model_dump_json()) for model in models
    ]

    # add representer for multiline literal
    for model in str_dict:
        for field in model:
            if format_as_multiline_liter(field):
                model[field] = literal_str(model[field])

    return yaml.dump(str_dict, sort_keys=False)


# ====================
# CLI
# ====================


@app.command(name="eval")
def eval_(
    path_strs: list[str],
    output: str | None = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path",
    ),
):
    paths: list[Path] = []
    for path_str in path_strs:
        if not Path(path_str).is_dir():
            raise ValueError(f"Path must be a directory, got {path_str}")
        paths.append(Path(path_str))

    models: list[ItemTemplate] = []
    for path in paths:
        try:
            model = dir_to_template(path, name=path.name)
            models.append(model)
        except Exception as e:
            typer.echo(f"Error in {path}: {e}")

    yaml_str = models_to_yaml_str(models)

    if output is not None:
        output_path = Path(output)
        output_path.write_text(yaml_str)
        typer.echo(f"Output written to {output_path} (len={len(models)})")
    else:
        typer.echo(yaml_str)


if __name__ == "__main__":
    from utils import configure_logging

    configure_logging("warning")
    app()
