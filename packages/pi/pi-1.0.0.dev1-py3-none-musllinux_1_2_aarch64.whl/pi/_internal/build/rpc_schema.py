from __future__ import annotations
from typing import Any, Literal, TypedDict, NotRequired

import collections

import pydantic

from pi._internal import rpc


def _snake_to_title(snake_str: str) -> str:
    return "".join(word.capitalize() for word in snake_str.split("_"))


def _title_to_snake(title_str: str) -> str:
    """Convert TitleCase to snake_case."""
    import re

    # Handle leading underscores separately
    leading_underscores = ""
    working_str = title_str
    while working_str.startswith("_"):
        leading_underscores += "_"
        working_str = working_str[1:]

    if not working_str:
        return leading_underscores

    # Insert underscores before uppercase letters
    # that are followed by lowercase
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", working_str)
    # Insert underscores before uppercase letters
    # preceded by lowercase or digits
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return leading_underscores + s2.lower()


class _InterfaceSchema(TypedDict):
    type: Literal["object"]
    additionalProperties: bool
    properties: dict[str, Any]
    required: list[str]


class RustTypeSettings(TypedDict):
    crate: str
    version: str
    path_prefix: NotRequired[str | None]


def _interface_schema() -> _InterfaceSchema:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {},
        "required": [],
    }


def _create_rust_type_annotation(
    rust_settings: RustTypeSettings, interface_name: str, type_name: str
) -> dict[str, Any]:
    """Create x-rust-type annotation for a model definition."""
    crate = rust_settings["crate"]
    path = f"{crate}"
    if prefix := rust_settings.get("path_prefix"):
        path = f"{path}::{prefix}"
    path = f"{path}::{interface_name}::{type_name}"
    return {
        "crate": rust_settings["crate"],
        "version": rust_settings["version"],
        "path": path,
    }


def rpc_json_schema(
    *,
    rust_settings: RustTypeSettings | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """
    Merge Pydantic model schemas into a single JSON Schema with $defs.
    We also produce a small RPC manifest describing which request/response
    types correspond to which method.
    """
    interfaces: collections.defaultdict[str, _InterfaceSchema] = (
        collections.defaultdict(_interface_schema)
    )
    schema: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:pi:rpc-schema",
        "title": "PI RPC Schema",
        "type": "object",
        "properties": {
            "interfaces": interfaces,
        },
        "required": ["interfaces"],
        "$defs": {},
    }

    def _update_refs_recursive(obj: Any, ref_mapping: dict[str, str]) -> Any:
        """Recursively update $ref entries in a schema object."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if key == "$ref" and isinstance(value, str):
                    # Update the reference if we have a mapping for it
                    if value in ref_mapping:
                        result[key] = ref_mapping[value]
                    else:
                        result[key] = value
                else:
                    result[key] = _update_refs_recursive(value, ref_mapping)
            return result
        elif isinstance(obj, list):
            return [_update_refs_recursive(item, ref_mapping) for item in obj]
        else:
            return obj

    # Collect individual model schemas and merge $defs.
    def _collect(
        model: type[pydantic.BaseModel], interface_name: str
    ) -> tuple[str, dict[str, Any]]:
        sch = model.model_json_schema(ref_template="#/$defs/{model}")
        # The top-level "title" is the canonical model name Pydantic uses.
        title = sch.get("title") or model.__name__
        defs = sch.get("$defs") or {}

        def qualify(name: str) -> str:
            return f"{interface_name}__{name}"

        # Create mapping of old refs to new namespaced refs
        ref_mapping = {}
        for k in defs.keys():
            old_ref = f"#/$defs/{k}"
            new_ref = f"#/$defs/{qualify(k)}"
            ref_mapping[old_ref] = new_ref

        # Update all $refs in the definitions to use namespaced references
        updated_defs = _update_refs_recursive(defs, ref_mapping)
        updated_sch = _update_refs_recursive(sch, ref_mapping)

        # Merge defs; later collisions should be rare because model names
        # are prefixed.
        for k, v in updated_defs.items():
            namespaced_key = qualify(k)
            if rust_settings is not None:
                v = {**v}
                v["x-rust-type"] = _create_rust_type_annotation(
                    rust_settings, interface_name, k
                )
            if defn := schema["$defs"].get(namespaced_key):
                # identical redefs are fine; structural conflict would be a
                # dev error
                if defn != v:
                    raise ValueError(f"Conflicting $defs for {namespaced_key}")
            else:
                # Add x-rust-type property if rust_settings provided
                schema["$defs"][namespaced_key] = v

        # Move the model schema itself into $defs under its namespaced title
        # so everything is reachable via $ref.
        namespaced_title = qualify(title)
        if namespaced_title in schema["$defs"]:
            if schema["$defs"][namespaced_title] != updated_sch:
                raise ValueError(
                    f"Conflicting top-level model {namespaced_title}"
                )
        else:
            # Remove nested $defs from the top-level schema copy
            sch_no_defs = dict(updated_sch)
            sch_no_defs.pop("$defs", None)

            # Add x-rust-type property if rust_settings provided
            if rust_settings is not None:
                sch_no_defs["x-rust-type"] = _create_rust_type_annotation(
                    rust_settings, interface_name, title
                )

            schema["$defs"][namespaced_title] = sch_no_defs

        return namespaced_title, updated_sch

    sources: list[str] = []

    for mm in rpc.get_exports():
        method_name = _snake_to_title(mm.method)
        req_model_name = f"{method_name}Request"

        params_model = pydantic.create_model(
            req_model_name,
            __module__=mm.module,
            **mm.params,  # pyright: ignore [reportArgumentType]
        )  # type: ignore [call-overload]
        params_title, _ = _collect(params_model, mm.interface)

        iface_schema = interfaces[mm.interface]
        methods = iface_schema["properties"]
        method_names = iface_schema["required"]

        properties = {
            "request": {"$ref": f"#/$defs/{params_title}"},
        }

        required = ["request"]

        if mm.result is not None:
            res_model_name = f"{method_name}Response"
            result_model = pydantic.create_model(
                res_model_name,
                __module__=mm.module,
                result=mm.result,
            )
            result_title, _ = _collect(result_model, mm.interface)
            properties["response"] = {"$ref": f"#/$defs/{result_title}"}
            required.append("response")

        methods[mm.method] = {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required,
        }

        method_names.append(mm.method)

        if mm.source:
            sources.append(mm.source)

    return schema, sources


if __name__ == "__main__":
    import argparse
    import importlib
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Generate RPC JSON schema for PI interfaces"
    )
    parser.add_argument(
        "--interfaces",
        help="Python module to import before generating the schema",
        required=True,
    )
    parser.add_argument(
        "--rust-crate",
        help="Rust crate name (required with --rust-crate-version)",
    )
    parser.add_argument(
        "--rust-crate-version",
        help="Rust crate version (required with --rust-crate)",
    )
    parser.add_argument(
        "--rust-mod-prefix",
        help="Rust module prefix",
    )

    args = parser.parse_args()

    # Validate Rust settings arguments
    if (args.rust_crate is None) != (args.rust_crate_version is None):
        parser.error(
            "--rust-crate and --rust-crate-version must both be specified "
            "or both be omitted"
        )

    # Construct rust_settings if provided
    rust_settings = None
    if args.rust_crate and args.rust_crate_version:
        rust_settings = {
            "crate": args.rust_crate,
            "version": args.rust_crate_version,
        }
        if args.rust_mod_prefix:
            rust_settings["path_prefix"] = args.rust_mod_prefix

    # Import the specified module to register interfaces
    try:
        importlib.import_module(args.interfaces)
    except ImportError as e:
        print(
            f"Error importing module '{args.interfaces}': {e}", file=sys.stderr
        )
        sys.exit(1)

    # Generate and output the schema as JSON
    schema, sources = rpc_json_schema(rust_settings=rust_settings)  # type: ignore [arg-type]
    json.dump(
        {"schema": json.dumps(schema), "sources": sources},
        sys.stdout,
        indent=2,
    )
