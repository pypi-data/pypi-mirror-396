import json
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus, unquote_plus
from warnings import catch_warnings

from cyclonedx.model import Property
from cyclonedx.model.bom import Bom
from cyclonedx.model.component import Component
from cyclonedx.output import OutputFormat, make_outputter
from cyclonedx.schema import SchemaVersion

from dt_sbom_scanner.AnsiColors import AnsiColors


def load_bom(file: Path) -> Bom:
    """
    Loads SBOM from file
    """
    # NOTE: This is a hack to fix missing bom_ref in Component
    component_init = Component.__init__

    def component_patched(self, **kwargs):
        if "bom_ref" not in kwargs:
            print(
                f"{AnsiColors.YELLOW}⚠{AnsiColors.RESET} missing 'bom_ref' in component {AnsiColors.HGRAY}{kwargs.get('name')}@{kwargs.get('version')}{AnsiColors.RESET} ({kwargs['type'].value}): fix"
            )
            kwargs["bom_ref"] = kwargs["name"]
        component_init(self, **kwargs)

    Component.__init__ = component_patched

    try:
        with catch_warnings(record=True) as warnings:
            with open(file) as reader:
                if file.suffix == ".xml":
                    bom = Bom.from_xml(reader)
                else:
                    # NOTE: This is a hack to remove conflicting fields
                    # https://github.com/CycloneDX/cyclonedx-python-lib/issues/578
                    raw_json = json.load(reader)
                    for component in raw_json.get("components", []):
                        component.pop("evidence", None)
                    raw_json.pop("annotations", None)
                    raw_json.pop("formulation", None)
                    bom = Bom.from_json(raw_json)

            # Restore original method
            Component.__init__ = component_init

            bom.validate()

        if warnings:
            for w in warnings:
                print(
                    f"{AnsiColors.YELLOW}⚠{AnsiColors.RESET} l#{w.lineno}: {w.message}"
                )
    except Exception as e:
        raise ValueError(f"Error while loading SBOM: {file.name}") from e

    return bom


def trim_purls(sbom: Bom, limit: int = 0) -> None:
    """Tries to trim PURLs by removing longest qualifiers"""
    if limit <= 0:
        return

    for component in sbom.components:
        purl = component.purl
        if not purl:
            continue

        purl_orig = str(purl)
        # url encode params if not already
        for key in purl.qualifiers:
            purl.qualifiers[key] = quote_plus(unquote_plus(purl.qualifiers[key]))

        purl_trunc = str(purl)
        if len(purl_trunc) < limit:
            continue

        while purl.qualifiers and len(purl_trunc) >= limit:
            longest_key = max(
                purl.qualifiers, key=lambda key: len(purl.qualifiers[key])
            )
            purl.qualifiers.pop(longest_key)
            purl_trunc = str(purl)

        if len(str(purl)) >= limit:
            print(
                f"{AnsiColors.YELLOW}⚠{AnsiColors.RESET} trimmed {purl_orig} -> {AnsiColors.HGRAY}{purl_trunc}{AnsiColors.RESET} but still exceeds limit ({limit})"
            )
        else:
            print(
                f"{AnsiColors.GREEN}✓{AnsiColors.RESET} successfully trimmed {purl_orig} -> {AnsiColors.HGRAY}{purl_trunc}{AnsiColors.RESET}"
            )


def serialize(
    bom: Bom, format=OutputFormat.JSON, schema_version=SchemaVersion.V1_5
) -> str:
    return make_outputter(bom, format, schema_version).output_as_string()


def to_json(bom: Bom, schema_version=SchemaVersion.V1_5) -> str:
    return make_outputter(bom, OutputFormat.JSON, schema_version).output_as_string()


def to_xml(bom: Bom, schema_version=SchemaVersion.V1_5) -> str:
    return make_outputter(bom, OutputFormat.XML, schema_version).output_as_string()


def save_bom(bom: Bom, file: Path, schema_version=SchemaVersion.V1_5) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    return make_outputter(
        bom,
        OutputFormat.XML if file.suffix == ".xml" else OutputFormat.JSON,
        schema_version,
    ).output_to_file(file, allow_overwrite=True)


# def cleanup(self, file: TextIO) -> str:
#     """Cleans up a single SBOM for import into Dependency-Track"""
#     bom = self.load(file)
#     return self.output(bom)


def merge_boms(
    root_name: str,
    root_version: Optional[str],
    root_group: Optional[str],
    boms: list[Bom],
) -> Bom:
    """Merges multiple SBOMs into a single SBOM"""
    merged = Bom()
    root = merged.metadata.component = Component(
        name=root_name, version=root_version, group=root_group
    )

    for bom in boms:
        merged.metadata.authors.update(bom.metadata.authors)

        merged.services.update(bom.services)
        merged.vulnerabilities.update(bom.vulnerabilities)

        depended = set()
        for dependency in bom.dependencies:
            if dependency.dependencies:
                merged.register_dependency(
                    Component(name=dependency.ref.value, bom_ref=dependency.ref),
                    [
                        Component(name=d.ref.value, bom_ref=d.ref)
                        for d in dependency.dependencies
                    ],
                )
                depended.update(d.ref for d in dependency.dependencies)

        def add_component(component: Component, parent: Optional[Component]):
            if all(c.bom_ref != component.bom_ref for c in merged.components):
                if component in merged.components:
                    # allow duplicated component by adding an unique metadata
                    component.properties.add(
                        Property(
                            name="dt:merge-deduplicate", value=component.bom_ref.value
                        )
                    )
                merged.components.add(component)
            if parent and component.bom_ref not in depended:
                merged.register_dependency(parent, [component])
            for child in component.components:
                add_component(child, component)
            component.components.clear()

        if bom.metadata.component:
            add_component(bom.metadata.component, root)
        for component in bom.components:
            add_component(component, bom.metadata.component)

    return merged
