# SPDX-FileCopyrightText: 2021 Dalibo
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import json
from pathlib import Path

import pydantic
import pytest
import yaml
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator

from pglift.models import helpers, interface
from pglift.pm import PluginManager
from pglift.prometheus.models.interface import PostgresExporter
from pglift.types import BaseModel

all_plugins = PluginManager.all()


def test_argspec_from_instance_manifest(
    expected_dir: Path,
    write_changes: bool,
    composite_instance_model: type[interface.Instance],
) -> None:
    compare_argspec(composite_instance_model, write_changes, expected_dir)


def test_argspec_from_role_manifest(
    expected_dir: Path,
    write_changes: bool,
    composite_role_model: type[interface.Role],
) -> None:
    compare_argspec(composite_role_model, write_changes, expected_dir)


@pytest.mark.parametrize(
    "model_type",
    [
        PostgresExporter,
        interface.Database,
    ],
)
def test_argspec_from_model_manifest(
    expected_dir: Path, write_changes: bool, model_type: type[BaseModel]
) -> None:
    compare_argspec(model_type, write_changes, expected_dir)


def compare_argspec(
    model_type: type[BaseModel],
    write_changes: bool,
    expected_dir: Path,
    *,
    name: str | None = None,
) -> None:
    actual = helpers.argspec_from_model(model_type)
    if name is None:
        name = model_type.__name__.lower()
    fpath = expected_dir / f"ansible-argspec-{name}.json"
    if write_changes:
        fpath.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
    expected = json.loads(fpath.read_text())
    assert actual == expected


@pytest.mark.parametrize(
    "objtype",
    [
        ("instance", interface.Instance, interface.InstanceApplyResult),
        ("role", interface.Role, interface.ApplyResult),
        ("database", interface.Database, interface.ApplyResult),
        ("postgresexporter", PostgresExporter, interface.ApplyResult),
    ],
    ids=lambda v: v[0],
)
def test_doc_fragments(
    expected_dir: Path,
    objtype: tuple[str, type[pydantic.BaseModel], type[pydantic.BaseModel]],
    write_changes: bool,
) -> None:
    name, m, r = objtype
    if hasattr(m, "composite"):
        model = m.composite(all_plugins)
    else:
        model = m
    options = helpers.argspec_from_model(model)
    validator = ArgumentSpecValidator(copy.deepcopy(options))
    examples = (expected_dir / "ansible-examples" / f"{name}.yaml").read_text()
    for example in yaml.safe_load(examples):
        assert len(example) == 2 and "name" in example
        collection_name = (set(example) - {"name"}).pop()
        assert not validator.validate(example[collection_name]).error_messages
    data = {
        "options": options,
        "return values": helpers.argspec_from_model(r),
        "examples": examples,
    }
    doc_fragments = (
        Path(__file__).parent.parent.parent.parent
        / "ansible"
        / "plugins"
        / "doc_fragments"
    )
    assert doc_fragments.is_dir()
    fpath = doc_fragments / f"{name}.json"
    if write_changes:
        fpath.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    expected = json.loads(fpath.read_text())
    assert data == expected
