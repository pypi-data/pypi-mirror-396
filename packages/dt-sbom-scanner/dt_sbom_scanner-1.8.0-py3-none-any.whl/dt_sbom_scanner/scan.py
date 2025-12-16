import argparse
import glob
import json
import os
import re
import ssl
import sys
from dataclasses import dataclass
from enum import Enum
from functools import cache
from logging import Logger
from pathlib import Path
from time import sleep
from typing import Optional

import requests
from cyclonedx.model.bom import Bom
from cyclonedx.schema import SchemaVersion

from dt_sbom_scanner import sbom_utils
from dt_sbom_scanner.AnsiColors import AnsiColors

LOGGER = Logger(__name__)


INSECURE_SSL_CTX = ssl.create_default_context()
INSECURE_SSL_CTX.check_hostname = False
INSECURE_SSL_CTX.verify_mode = ssl.CERT_NONE

MIME_APPLICATION_JSON = "application/json"

IS_STR_TRUE = ["true", "yes", "1"]


@dataclass
class DtSeverity:
    """Dependency Track severity level"""

    name: str
    risk_score: int
    """See: https://docs.dependencytrack.org/terminology/#risk-score"""
    color: str


SEVERITY_RANKS = [
    DtSeverity("Critical", 10, AnsiColors.HRED),
    DtSeverity("High", 5, AnsiColors.RED),
    DtSeverity("Medium", 3, AnsiColors.YELLOW),
    DtSeverity("Low", 1, AnsiColors.GREEN),
    DtSeverity("Informational", 0, AnsiColors.RESET),
    DtSeverity("Unassigned", 5, AnsiColors.PURPLE),
]


class CollectionLogic(str, Enum):
    """Dependency Track collection logics.

    See: https://github.com/DependencyTrack/dependency-track/blob/master/src/main/java/org/dependencytrack/model/ProjectCollectionLogic.java#L30
    """

    NONE = "NONE"
    "Project is not a collection project"
    ALL = "AGGREGATE_DIRECT_CHILDREN"
    "Project aggregate all direct children"
    TAG = "AGGREGATE_DIRECT_CHILDREN_WITH_TAG"
    "Project aggregate direct children with a specific tag"
    LATEST = "AGGREGATE_LATEST_VERSION_CHILDREN"
    "Project aggregate only direct children marked as latest"

    def __str__(self) -> str:
        return self.name


class DtPermission(str, Enum):
    """Dependency Track permissions.

    See: https://github.com/DependencyTrack/dependency-track/blob/master/src/main/java/org/dependencytrack/auth/Permissions.java#L27"""

    BOM_UPLOAD = "BOM_UPLOAD"
    """Allows the ability to upload CycloneDX Software Bill of Materials (SBOM)"""
    VIEW_PORTFOLIO = "VIEW_PORTFOLIO"
    """Provides the ability to view the portfolio of projects, components, and licenses"""
    PORTFOLIO_MANAGEMENT = "PORTFOLIO_MANAGEMENT"
    """Allows the creation, modification, and deletion of data in the portfolio"""
    VIEW_VULNERABILITY = "VIEW_VULNERABILITY"
    """Provides the ability to view the vulnerabilities projects are affected by"""
    VULNERABILITY_ANALYSIS = "VULNERABILITY_ANALYSIS"
    """Provides the ability to make analysis decisions on vulnerabilities"""
    VIEW_POLICY_VIOLATION = "VIEW_POLICY_VIOLATION"
    """Provides the ability to view policy violations"""
    VULNERABILITY_MANAGEMENT = "VULNERABILITY_MANAGEMENT"
    """Allows management of internally-defined vulnerabilities"""
    POLICY_VIOLATION_ANALYSIS = "POLICY_VIOLATION_ANALYSIS"
    """Provides the ability to make analysis decisions on policy violations"""
    ACCESS_MANAGEMENT = "ACCESS_MANAGEMENT"
    """Allows the management of users, teams, and API keys"""
    SYSTEM_CONFIGURATION = "SYSTEM_CONFIGURATION"
    """Allows the configuration of the system including notifications, repositories, and email settings"""
    PROJECT_CREATION_UPLOAD = "PROJECT_CREATION_UPLOAD"
    """Provides the ability to optionally create project (if non-existent) on BOM or scan upload"""
    POLICY_MANAGEMENT = "POLICY_MANAGEMENT"
    """Allows the creation, modification, and deletion of policy"""

    def __str__(self) -> str:
        return self.name


class DtProjectDef:
    """Dependency Track project definition (either a UUID or name/version)."""

    def __init__(
        self,
        definition: str,
    ):
        self.definition = definition

    @property
    def is_uuid(self) -> bool:
        return self.definition.startswith("#")

    @property
    def uuid(self) -> Optional[str]:
        return self.definition[1:] if self.is_uuid else None

    @property
    def name(self) -> Optional[str]:
        return None if self.is_uuid else self.definition.split("@")[0]

    @property
    def version(self) -> Optional[str]:
        if self.is_uuid:
            return None
        return self.definition.split("@")[1] if "@" in self.definition else None

    @property
    def params(self) -> dict[str, str]:
        params = {}
        if self.is_uuid:
            # target project definition is a UUID: nothing more is required
            params["project"] = self.uuid
        else:
            # target project definition is a project name: assume exists or set autoCreate with parent if permission PROJECT_CREATION_UPLOAD
            params["projectName"] = self.name
            params["projectVersion"] = self.version
        return params


class Version:
    def __init__(self, version_str):
        self.version_str = version_str
        self.major, self.minor, self.patch, self.prerelease, self.build = self._parse(
            version_str
        )

    def _parse(self, version_str):
        regex = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        match = re.match(regex, version_str)
        if match:
            major = int(match.group("major"))
            minor = int(match.group("minor"))
            patch = int(match.group("patch"))
            prerelease = match.group("prerelease")
            build = match.group("build")
            return major, minor, patch, prerelease, build
        else:
            raise ValueError(f"Invalid semantic version: {version_str}")

    def __str__(self):
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version_str += f"-{'.'.join(self.prerelease)}"
        if self.build:
            version_str += f"+{'.'.join(self.build)}"
        return version_str

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def _compare(self, other):
        if not isinstance(other, Version):
            other = Version(str(other))

        if self.major != other.major:
            return 1 if self.major > other.major else -1
        if self.minor != other.minor:
            return 1 if self.minor > other.minor else -1
        if self.patch != other.patch:
            return 1 if self.patch > other.patch else -1

        # Handle pre-release versions
        if self.prerelease and other.prerelease:
            self_prerelease = [
                self._parse_prerelease(x) for x in self.prerelease.split(".")
            ]
            other_prerelease = [
                self._parse_prerelease(x) for x in other.prerelease.split(".")
            ]
            for i in range(min(len(self_prerelease), len(other_prerelease))):
                if self_prerelease[i] != other_prerelease[i]:
                    return 1 if self_prerelease[i] > other_prerelease[i] else -1
            if len(self_prerelease) != len(other_prerelease):
                return 1 if len(self_prerelease) > len(other_prerelease) else -1
        elif self.prerelease:
            return -1
        elif other.prerelease:
            return 1

        # Handle build metadata
        if self.build and other.build:
            self_build = [int(x) if x.isdigit() else x for x in self.build.split(".")]
            other_build = [int(x) if x.isdigit() else x for x in other.build.split(".")]
            for i in range(min(len(self_build), len(other_build))):
                if self_build[i] != other_build[i]:
                    return 1 if self_build[i] > other_build[i] else -1
            if len(self_build) != len(other_build):
                return 1 if len(self_build) > len(other_build) else -1
        elif self.build:
            return 1
        elif other.build:
            return -1

        return 0

    def _parse_prerelease(self, prerelease_str):
        digits = "".join(c for c in prerelease_str if c.isdigit())
        alpha = "".join(c for c in prerelease_str if not c.isdigit())
        if digits:
            return int(digits), alpha
        else:
            return 0, alpha


class ApiClient:
    def __init__(self, base_api_url: str, api_key: str, verify_ssl: bool):
        self.base_api_url = base_api_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-Key": api_key,
                "accept": MIME_APPLICATION_JSON,
            }
        )
        self.session.verify = verify_ssl

    def get(self, path, **kwargs):
        url = f"{self.base_api_url}{path}"
        return self.session.get(url, **kwargs)

    def post(self, path, **kwargs):
        url = f"{self.base_api_url}{path}"
        return self.session.post(url, **kwargs)

    def put(self, path, **kwargs):
        url = f"{self.base_api_url}{path}"
        return self.session.put(url, **kwargs)


class Scanner:
    def __init__(
        self,
        base_api_url: str,
        api_key: str,
        project_path: str,
        path_separator: str = "/",
        purl_max_len: int = -1,
        merge: bool = False,
        merge_output: str = None,
        verify_ssl: bool = True,
        show_findings: bool = False,
        risk_score_threshold: int = -1,
        tags: str = "",
        parent_collection_logic: str = CollectionLogic.ALL.name,
        parent_collection_logic_tag: str = "",
        upload_vex: bool = False,
        merged_vex_file=None,
        **_: None,
    ):
        self.api_client = ApiClient(base_api_url, api_key, verify_ssl)
        self.project_path = project_path
        self.path_separator = path_separator
        self._purl_max_len = purl_max_len
        self.merge = merge
        self.merge_output = merge_output
        self.show_findings = show_findings
        self.risk_score_threshold = risk_score_threshold
        self.tags = list(filter(None, map(str.strip, tags.split(",")))) if tags else []
        self.parent_collection_logic = parent_collection_logic
        self.parent_collection_logic_tag = parent_collection_logic_tag
        self.sbom_count = 0
        self.sbom_scan_failed = 0
        self.upload_vex = upload_vex
        self.merged_vex_file = merged_vex_file

    @property
    @cache
    def dt_version(self) -> Version:
        """Determines the DT server version."""
        return Version(self.api_client.get("/version").json()["version"])

    @property
    @cache
    def cdx_schema_version(self) -> SchemaVersion:
        """Determines the most suitable CycloneDX schema version depending on the DT server version."""
        return SchemaVersion.V1_5

    @property
    @cache
    def purl_max_len(self) -> int:
        """Determines the PURL max length depending on the DT server version."""
        if self._purl_max_len < 0:
            # see: https://github.com/DependencyTrack/dependency-track/pull/3560
            ver = self.dt_version
            self._purl_max_len = 255 if ver < Version("4.11.0") else 786
            print(
                f"Max PURLs length: {AnsiColors.BLUE}{self._purl_max_len}{AnsiColors.RESET} (server version {ver})"
            )

        return self._purl_max_len

    @property
    @cache
    def event_token_path(self) -> str:
        """Determines the DT bom/token or event/token path depending on the DT server version."""
        return "bom/token" if self.dt_version < Version("4.11.0") else "event/token"

    @property
    @cache
    def need_findings(self) -> bool:
        return self.show_findings or self.risk_score_threshold >= 0

    @cache
    def get_permissions(self) -> list[DtPermission]:
        return [
            permission["name"]
            for permission in self.api_client.get("/v1/team/self").json()["permissions"]
        ]

    def has_permission(self, perm: DtPermission) -> bool:
        return perm in self.get_permissions()

    # rewinds the given project path and creates a DT project for each non-UUID defined project
    # returns the tail project UUID
    @cache
    def get_or_create_project(
        self, project_path: str, classifier="application", is_parent: bool = False
    ) -> str:
        project_path_parts = project_path.split(self.path_separator)
        project_def = DtProjectDef(project_path_parts[-1])
        if project_def.is_uuid:
            print(
                f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} is UUID: assume exists..."
            )
            return project_def.uuid

        # project is defined by name/version...
        resp = self.api_client.get(
            "/v1/project",
            params={"name": project_def.name},
        )
        resp.raise_for_status()
        # find project with matching name/version
        project_versions: list[dict] = resp.json()
        exact_match = next(
            filter(
                lambda prj: prj["name"] == project_def.name
                and prj.get("version") == project_def.version,
                project_versions,
            ),
            None,
        )
        if exact_match:
            # project already exists: replace name with found UUID
            print(
                f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} found (by name/version): {exact_match['uuid']}..."
            )
            return exact_match["uuid"]
        # if project exists but not the version, we have to CLONE it
        name_match = next(
            filter(
                lambda prj: prj["name"] == project_def.name,
                project_versions,
            ),
            None,
        )
        if name_match:
            print(
                f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} found sibling (version: {name_match.get('version')}): {name_match['uuid']}..."
            )
            # now create a clone of the project
            resp = self.api_client.put(
                "/v1/project/clone",
                headers={
                    "content-type": MIME_APPLICATION_JSON,
                },
                json={
                    "project": name_match["uuid"],
                    "version": project_def.version,
                    "includeTags": True,
                    "includeProperties": True,
                    "includeComponents": True,
                    "includeServices": True,
                    "includeAuditHistory": True,
                    "includeACL": True,
                },
            )
            try:
                resp.raise_for_status()
                # TODO: clone doesn't return UUID :(
                resp = self.api_client.get(
                    "/v1/project/lookup",
                    headers={
                        "accept": MIME_APPLICATION_JSON,
                    },
                    params={"name": project_def.name, "version": project_def.version},
                )
                resp.raise_for_status()
                # retrieve UUID from response and return
                created_uuid = resp.json()["uuid"]
                print(
                    f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} {AnsiColors.HGREEN}successfully{AnsiColors.RESET} cloned (from sibling): {created_uuid}"
                )
                return created_uuid
            except requests.exceptions.HTTPError as he:
                print(
                    f"- create {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} {AnsiColors.HRED}failed{AnsiColors.RESET} (err {he.response.status_code}): {AnsiColors.HGRAY}{he.response.text}{AnsiColors.RESET}",
                )
                raise

        # project does not exist: create it
        data = {
            "name": project_def.name,
            "version": project_def.version,
            "classifier": classifier.upper(),
            "active": True,
        }

        # Set up collection logic if supported
        if is_parent and self.dt_version >= Version("4.13.0"):
            data["collectionLogic"] = CollectionLogic[
                self.parent_collection_logic
            ].value
            if data["collectionLogic"] == CollectionLogic.TAG:
                data["collectionTag"] = {
                    "name": self.parent_collection_logic_tag.strip()
                }

        # TODO: externalReferences
        # data["externalReferences"] = [{"type":"vcs","url":project_url}],
        if len(project_path_parts) > 1:
            # project to create is not a root project: retrieve parent
            parent_def = DtProjectDef(project_path_parts[-2])
            if not parent_def.is_uuid:
                # create parent project
                parent_uuid = self.get_or_create_project(
                    self.path_separator.join(project_path_parts[:-1]),
                    classifier=classifier,
                    is_parent=True,
                )
                # now parent def must be a UUID
                parent_def = DtProjectDef("#" + parent_uuid)
            # add parent UUID to params
            data["parent"] = {"uuid": parent_def.uuid}

        if self.tags:
            data["tags"] = self.tags

        print(
            f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} not found: create with params {AnsiColors.HGRAY}{json.dumps(data)}{AnsiColors.RESET}..."
        )
        resp = self.api_client.put(
            "/v1/project",
            headers={
                "content-type": MIME_APPLICATION_JSON,
            },
            json=data,
        )
        try:
            resp.raise_for_status()
            # retrieve UUID from response and return
            created_uuid = resp.json()["uuid"]
            print(
                f"- {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} {AnsiColors.HGREEN}successfully{AnsiColors.RESET} created: {created_uuid}"
            )
            return created_uuid
        except requests.exceptions.HTTPError as he:
            print(
                f"- create {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET} {AnsiColors.HRED}failed{AnsiColors.RESET} (err {he.response.status_code}): {AnsiColors.HGRAY}{he.response.text}{AnsiColors.RESET}",
            )
            raise

    def publish(self, sbom: Bom, file_prefix: str, vex_file_path: Path):
        sbom_type = None
        sbom_name = None
        sbom_version = None
        if sbom.metadata and sbom.metadata.component:
            sbom_md_cmp = sbom.metadata.component
            sbom_type = sbom_md_cmp.type.value
            sbom_name = sbom_md_cmp.name
            sbom_version = sbom_md_cmp.version
        print(
            f"- file_prefix: {AnsiColors.HGRAY}{file_prefix}{AnsiColors.RESET}; sbom_type: {AnsiColors.HGRAY}{sbom_type}{AnsiColors.RESET}; sbom_name: {AnsiColors.HGRAY}{sbom_name}{AnsiColors.RESET}; sbom_version: {AnsiColors.HGRAY}{sbom_version}{AnsiColors.RESET}"
        )

        # compute the target project path
        project_path = str.format(
            self.project_path,
            file_prefix=file_prefix,
            sbom_type=sbom_type or "unk",
            sbom_name=sbom_name or "unk",
            sbom_version=sbom_version or "",
        )
        print(f"- target project: {AnsiColors.YELLOW}{project_path}{AnsiColors.RESET}")

        # finally trim purls
        if self.purl_max_len > 0:
            print(
                f"- trim PURLs to {AnsiColors.HGRAY}{self.purl_max_len}{AnsiColors.RESET} charaters..."
            )
            sbom_utils.trim_purls(sbom, self.purl_max_len)

        self.do_publish(
            sbom_utils.to_json(sbom, self.cdx_schema_version),
            project_path,
            sbom_type,
            vex_file_path,
        )

    def do_publish(
        self,
        sbom_json: str,
        project_path: str,
        sbom_type: str,
        vex_file_path: Path,
        allow_retry=True,
    ):
        project_path_parts = project_path.split(self.path_separator)
        # determine publish params
        project_def = DtProjectDef(project_path_parts[-1])
        params = project_def.params

        if self.has_permission(DtPermission.PROJECT_CREATION_UPLOAD):
            params["autoCreate"] = "true"
            if len(project_path_parts) > 1:
                parent_def = DtProjectDef(project_path_parts[-2])
                if parent_def.is_uuid:
                    params["parentUUID"] = parent_def.uuid
                else:
                    params["parentName"] = parent_def.name
                    params["parentVersion"] = parent_def.version
            if self.tags:
                params["projectTags"] = self.tags

        # publish SBOM
        print(
            f"- publish params: {AnsiColors.HGRAY}{json.dumps(params)}{AnsiColors.RESET}..."
        )
        resp = self.api_client.post(
            "/v1/bom",
            files={"bom": sbom_json},
            data=params,
        )
        try:
            resp.raise_for_status()
            print(
                f"- publish {AnsiColors.HGREEN}succeeded{AnsiColors.RESET}: {AnsiColors.HGRAY}{resp.text}{AnsiColors.RESET}"
            )
        except requests.exceptions.HTTPError as he:
            print(
                f"- publish {AnsiColors.HRED}failed{AnsiColors.RESET} (err {he.response.status_code}): {AnsiColors.HGRAY}{he.response.text}{AnsiColors.RESET}",
            )
            if (
                he.response.status_code == 404
                and self.has_permission(DtPermission.PORTFOLIO_MANAGEMENT)
                and self.has_permission(DtPermission.VIEW_PORTFOLIO)
                and allow_retry
            ):
                # try to create parent projects
                print("- create projects...")
                # replace last path part with project UUID
                # TODO: retrieve classifier from SBOM
                project_path_parts[-1] = "#" + self.get_or_create_project(
                    project_path, sbom_type, is_parent=False
                )
                # then retry
                print("- retry publish...")
                self.do_publish(
                    sbom_json,
                    self.path_separator.join(project_path_parts),
                    sbom_type,
                    vex_file_path,
                    allow_retry=False,
                )
                # to prevent do_scan one more time (must have been done in the retried do_publish())
                return
            else:
                raise

        event_id = resp.json().get("token")

        # import VEX file
        if self.upload_vex:
            event_id = self.do_vex_publish(project_def, vex_file_path, event_id)

        if self.need_findings:
            self.do_scan(project_def, event_id)

    def do_vex_publish(
        self, project_def: DtProjectDef, vex_file_path: Path, event_id: str
    ):
        self.wait_for_event_processing(event_id)

        if not vex_file_path.exists():
            print(
                f"- VEX file {AnsiColors.YELLOW}not found, skipping upload{AnsiColors.RESET}: {AnsiColors.HGRAY}{vex_file_path}{AnsiColors.RESET}"
            )
            return event_id

        with open(vex_file_path, "r") as vex_file:
            params = project_def.params
            resp = self.api_client.post(
                "/v1/vex",
                files={"vex": vex_file},
                data=params,
            )
            try:
                resp.raise_for_status()
                print(
                    f"- VEX import {AnsiColors.HGREEN}succeeded{AnsiColors.RESET}: {AnsiColors.HGRAY}{resp.text}{AnsiColors.RESET}"
                )
            except requests.exceptions.HTTPError as he:
                print(
                    f"- VEX import {AnsiColors.HRED}failed{AnsiColors.RESET} (err {he.response.status_code}): {AnsiColors.HGRAY}{he.response.text}{AnsiColors.RESET}",
                )
                raise

            return resp.json().get("token")

    def do_scan(self, project_def: DtProjectDef, event_id: str):
        print(f"- scan: {AnsiColors.HGRAY}{event_id}{AnsiColors.RESET}...")
        if project_def.is_uuid:
            project_id = project_def.uuid
        else:
            params = {}
            params["name"] = project_def.name
            if project_def.version:
                params["version"] = project_def.version
            resp = self.api_client.get(
                "/v1/project/lookup",
                params=params,
            )
            project_id = resp.json().get("uuid")

        self.wait_for_event_processing(event_id)
        # MAYBE: get SBOM with VEX curl -sSf f"{self.base_api_url}/v1/bom/cyclonedx/project/{project_id}?variant=withVulnerabilities"
        resp = self.api_client.get(
            f"/v1/finding/project/{project_id}",
        )
        resp.raise_for_status()
        risk_score = 0
        findings = sorted(
            resp.json(),
            key=lambda o: o.get("vulnerability", {}).get("cvssV3BaseScore", 0),
            reverse=True,
        )
        for o in findings:
            vuln = o.get("vulnerability", {})
            component = o.get("component", {})
            severity = SEVERITY_RANKS[vuln.get("severityRank", 5)]
            cwes = (cwe["name"] for cwe in vuln.get("cwes", []))
            risk_score += severity.risk_score
            if self.show_findings:
                print(
                    f"  - {vuln['vulnId']} {severity.color}{severity.name}{AnsiColors.RESET}: {component.get('group', '')}:{component.get('name')}:{component.get('version', '')} - {' '.join(cwes)}"
                )
                print(re.sub("\n+", "\n", vuln.get("description", "").strip()))
                print()
        if self.risk_score_threshold < 0 or risk_score < self.risk_score_threshold:
            print(
                f"- scan {AnsiColors.HGREEN}succeeded{AnsiColors.RESET}: {len(findings)} vulnerabilities found {AnsiColors.HGRAY}risk score: {risk_score}{AnsiColors.RESET}"
            )
        else:
            self.sbom_scan_failed += 1
            print(
                f"- scan {AnsiColors.HRED}failed{AnsiColors.RESET}: risk score {risk_score} exceeds threshold {self.risk_score_threshold} - failing the scan: {AnsiColors.HGRAY}{len(findings)} vulnerabilities found{AnsiColors.RESET}"
            )

    def wait_for_event_processing(self, event_id: str):
        for n in range(8):  # ~5 minutes
            sleep(2**n)
            resp = self.api_client.get(
                f"/v1/{self.event_token_path}/{event_id}",
            )
            if not resp.json().get("processing", False):
                break

    def scan(self, sbom_patterns: list[str]):
        try:
            # try to connect to Dependency Track server
            self.dt_version
        except requests.exceptions.RequestException as err:
            fail(
                f"Unable to connect to Dependency Track server - check the API URL and network configuration: {err}"
            )
        try:
            # try an authenticated request to Dependency Track server
            self.get_permissions()
        except requests.exceptions.RequestException as err:
            fail(
                f"Unable to authenticate to Dependency Track server - check the API key: {err}"
            )

        print(
            f"🗝 API key has permissions: {AnsiColors.BLUE}{', '.join(self.get_permissions())}{AnsiColors.RESET}"
        )
        print()
        if not self.has_permission(DtPermission.BOM_UPLOAD):
            fail(
                "BOM_UPLOAD permission is mandatory to publish SBOM files to Dependency Track server"
            )
        if self.need_findings:
            if not self.has_permission(DtPermission.VIEW_VULNERABILITY):
                fail(
                    "VIEW_VULNERABILITY permission is mandatory to show finding or compute risk score after SBOM analysis"
                )
            if not self.has_permission(DtPermission.VIEW_PORTFOLIO):
                fail(
                    "VIEW_PORTFOLIO permission is mandatory to show finding or compute risk score after SBOM analysis"
                )
        if self.upload_vex and not self.has_permission(
            DtPermission.VULNERABILITY_ANALYSIS
        ):
            fail("VULNERABILITY_ANALYSIS permission is mandatory to import VEX files")

        # scan for SBOM files
        sboms = []
        for pattern in sbom_patterns:
            for file in glob.glob(pattern, recursive=True):
                print(
                    f"{AnsiColors.BOLD}📄 SBOM: {AnsiColors.BLUE}{file}{AnsiColors.RESET}"
                )
                # load the SBOM and VEX content
                sbom_file_path = Path(file)
                sbom_file_prefix = sbom_file_path.name.split(".")[0]
                vex_file_path = sbom_file_path.with_name(f"{sbom_file_prefix}.vex.json")

                sbom = sbom_utils.load_bom(sbom_file_path)
                if self.merge:
                    sboms.append(sbom)
                else:
                    self.publish(sbom, sbom_file_prefix, vex_file_path)

                print()
                self.sbom_count += 1

        if self.sbom_count == 0:
            print(
                f"- {AnsiColors.YELLOW}WARN{AnsiColors.RESET} no SBOM file found - nothing to publish",
            )
        elif self.merge:
            # extract name and version from path
            print(
                f"{AnsiColors.BOLD}📄 Merge SBOMs: {AnsiColors.BLUE}{self.merge_output or 'in memory'}{AnsiColors.RESET}"
            )
            project_path = str.format(
                self.project_path,
                file_prefix="merged",
                sbom_type="unk",
                sbom_name="unk",
                sbom_version="",
            )
            project_path_parts = project_path.split(self.path_separator)
            project_def = DtProjectDef(project_path_parts[-1])
            if project_def.is_uuid:
                sbom_name = "merged"
                sbom_version = None
            else:
                sbom_name = project_def.name
                sbom_version = project_def.version

            merged_sbom = sbom_utils.merge_boms(
                sbom_name, sbom_version, root_group=None, boms=sboms
            )
            if self.merge_output:
                sbom_utils.save_bom(
                    merged_sbom, Path(self.merge_output), self.cdx_schema_version
                )
            vex_file_path = Path(self.merged_vex_file) if self.merged_vex_file else None

            self.publish(merged_sbom, "merged", vex_file_path)


def fail(msg: str) -> None:
    print(f"{AnsiColors.HRED}ERROR{AnsiColors.RESET} {msg}")
    sys.exit(1)


def run() -> None:
    # define command parser
    parser = argparse.ArgumentParser(
        prog="sbom-scanner",
        description="This tool scans for SBOM files and publishes them to a Dependency Track server.",
    )
    dt_platform_group = parser.add_argument_group("Dependency Track connection")
    dt_platform_group.add_argument(
        "-u",
        "--base-api-url",
        default=os.getenv("DEPTRACK_BASE_API_URL"),
        help="Dependency Track server base API url (includes '/api')",
    )
    dt_platform_group.add_argument(
        "-k",
        "--api-key",
        default=os.getenv("DEPTRACK_API_KEY"),
        help="Dependency Track API key",
    )
    dt_platform_group.add_argument(
        "-i",
        "--insecure",
        action="store_true",
        default=os.getenv("DEPTRACK_INSECURE") in IS_STR_TRUE,
        help="Skip SSL verification",
    )

    project_selection_group = parser.add_argument_group("Project settings")
    project_selection_group.add_argument(
        "-p",
        "--project-path",
        default=os.getenv("DEPTRACK_PROJECT_PATH"),
        help="Dependency Track target project path to publish SBOM files to (see doc)",
    )
    project_selection_group.add_argument(
        "-s",
        "--path-separator",
        default=os.getenv("DEPTRACK_PATH_SEPARATOR", "/"),
        help="Separator to use in project path (default: '/')",
    )
    project_selection_group.add_argument(
        "-t",
        "--tags",
        type=str,
        default=os.getenv("DEPTRACK_TAGS", ""),
        help="Comma separated list of tags to attach to the project",
    )
    project_selection_group.add_argument(
        "--parent-collection-logic",
        type=str,
        default=os.getenv(
            "DEPTRACK_PARENT_COLLECTION_LOGIC",
            CollectionLogic.ALL.name,
        ),
        choices=list(map(lambda x: x.name, list(CollectionLogic))),
        help="Set up how the parent aggregates its direct children (ALL: all, TAG: with tag matching --parent-collection-logic-tag, LATEST: flagged as latest, NONE: disable), default is ALL (DT version >= 4.13.0)",
    )
    project_selection_group.add_argument(
        "--parent-collection-logic-tag",
        type=str,
        default=os.getenv("DEPTRACK_PARENT_COLLECTION_LOGIC_TAG", ""),
        help="Tag for aggregation if --parent-collection-logic is set to TAG",
    )

    sbom_management_group = parser.add_argument_group("SBOM management")
    sbom_management_group.add_argument(
        "-m",
        "--merge",
        action="store_true",
        default=os.getenv("DEPTRACK_MERGE") in IS_STR_TRUE,
        help="Merge all SBOM files into one",
    )
    sbom_management_group.add_argument(
        "-o",
        "--merge-output",
        default=os.getenv("DEPTRACK_MERGE_OUTPUT"),
        help="Output merged SBOM file (only used with merge enabled) - for debugging purpose",
    )
    # <0: auto (from DT version) / 0: no trim / >0 max length
    sbom_management_group.add_argument(
        "-l",
        "--purl-max-len",
        type=int,
        default=int(os.getenv("DEPTRACK_PURL_MAX_LEN", "-1")),
        help="PURLs max length (-1: auto, 0: no trim, >0: trim to size - default: -1)",
    )

    vex_group = parser.add_argument_group("VEX")
    vex_group.add_argument(
        "-U",
        "--upload-vex",
        action="store_true",
        default=os.getenv("DEPTRACK_UPLOAD_VEX") in IS_STR_TRUE,
        help="Upload VEX file after SBOM analysis (requires VULNERABILITY_ANALYSIS permission). The VEX file(s) are resolved based on the sbom pattern(s). The first part of the SBOM file name is used to match it with a VEX file (e.g. if there is an SBOM file 'example.cyclonedx.json', the corresponding VEX file name must be 'example.vex.json')",
    )
    vex_group.add_argument(
        "-V",
        "--merged-vex-file",
        type=str,
        default=os.getenv("DEPTRACK_MERGED_VEX_FILE"),
        help="The VEX file to upload if multiple SBOMS are merged (--merge). Can only be used with --upload-vex and --merge.",
    )

    misc_group = parser.add_argument_group("Miscellaneous")
    misc_group.add_argument(
        "-S",
        "--show-findings",
        action="store_true",
        default=os.getenv("DEPTRACK_SHOW_FINDINGS") in IS_STR_TRUE,
        help="Wait for analysis and display found vulnerabilities",
    )
    misc_group.add_argument(
        "-R",
        "--risk-score-threshold",
        type=int,
        default=int(os.getenv("DEPTRACK_RISK_SCORE_THRESHOLD", "-1")),
        help="Risk score threshold to fail the scan (<0: disabled - default: -1)",
    )

    parser.add_argument(
        "sbom_patterns",
        nargs="*",
        default=os.getenv(
            "DEPTRACK_SBOM_PATTERNS", "**/*.cyclonedx.json **/*.cyclonedx.xml"
        ).split(" "),
        help="SBOM file patterns to publish (supports glob patterns). Default: '**/*.cyclonedx.json **/*.cyclonedx.xml'",
    )

    # parse command and args
    args = parser.parse_args()

    # check required args
    if not args.base_api_url:
        fail(
            "Dependency Track server base API url is required (use --base-api-url CLI option or DEPTRACK_BASE_API_URL variable)"
        )
    if not args.api_key:
        fail(
            "Dependency Track API key is required (use --api-key CLI option or DEPTRACK_API_KEY variable)"
        )
    if not args.project_path:
        fail(
            "Dependency Track target project path is required (use --project-path CLI option or DEPTRACK_PROJECT_PATH variable)"
        )
    if (
        not args.parent_collection_logic_tag
        and args.parent_collection_logic == CollectionLogic.TAG.name
    ):
        fail(
            f"You need to specify a tag with --parent-collection-logic-tag (or DEPTRACK_PARENT_COLLECTION_LOGIC_TAG env var) if parent collection logic has been set to {CollectionLogic.TAG.name}"
        )
    if args.merge and args.upload_vex and not args.merged_vex_file:
        fail(
            "You need to specify a VEX file with --merged-vex-file (or DEPTRACK_MERGED_VEX_FILE env var) if you want to upload a VEX file and are merging SBOM files (--merge)"
        )
    if not args.merge and args.upload_vex and args.merged_vex_file:
        fail(
            "You cannot specify a VEX file with --merged-vex-file (or DEPTRACK_MERGED_VEX_FILE env var) if you are NOT merging SBOM files (--merge is not set)"
        )

    # print execution parameters
    print("Scanning SBOM files...")
    print(
        f"- base API url     (--base-api-url): {AnsiColors.CYAN}{args.base_api_url}{AnsiColors.RESET}"
    )
    print(
        f"- project path     (--project-path): {AnsiColors.CYAN}{args.project_path}{AnsiColors.RESET}"
    )
    print(
        f"- project tags             (--tags): {AnsiColors.CYAN}{args.tags}{AnsiColors.RESET}"
    )
    print(
        f"- parent collection logic (--parent-collection-logic): {AnsiColors.CYAN}{args.parent_collection_logic}{AnsiColors.RESET}"
        + (
            f" matching {AnsiColors.CYAN}{args.parent_collection_logic_tag}{AnsiColors.RESET} (--parent-collection-logic-tag)"
            if args.parent_collection_logic == CollectionLogic.TAG.name
            else ""
        )
    )
    print(
        f"- path separator (--path-separator): {AnsiColors.CYAN}{args.path_separator}{AnsiColors.RESET}"
    )
    print(
        f"- PURLs max length (--purl-max-len): {AnsiColors.CYAN}{'auto (-1)' if args.purl_max_len < 0 else 'no trim (0)' if args.purl_max_len == 0 else args.purl_max_len}{AnsiColors.RESET}"
    )
    print(
        f"- merge SBOM files       (--merge) : {AnsiColors.CYAN}{args.merge}{AnsiColors.RESET}"
    )
    print(
        f"- merge output     (--merge-output): {AnsiColors.CYAN}{args.merge_output}{AnsiColors.RESET}"
    )
    print(
        f"- show findings   (--show-findings): {AnsiColors.CYAN}{args.show_findings}{AnsiColors.RESET}"
    )
    print(
        f"- risk score (--risk-score-threshold): {AnsiColors.CYAN}{args.risk_score_threshold}{AnsiColors.RESET}"
    )
    print(
        f"- insecure             (--insecure): {AnsiColors.CYAN}{args.insecure}{AnsiColors.RESET}"
    )
    print(
        f"- Upload VEX         (--upload-vex): {AnsiColors.CYAN}{args.upload_vex}{AnsiColors.RESET}"
    )
    print(
        f"- VEX file path for merged SBOM (--merged-vex-file): {AnsiColors.CYAN}{args.merged_vex_file}{AnsiColors.RESET}"
    )
    print(
        f"- SBOM file pattern                : {AnsiColors.CYAN}{', '.join(args.sbom_patterns)}{AnsiColors.RESET}"
    )
    print()

    # execute the scan
    scanner = Scanner(
        **vars(args),
        verify_ssl=not args.insecure,
    )
    scanner.scan(args.sbom_patterns)

    print("Done!")
    print(
        "----------------------------------------------------------------------------------------------"
    )
    print(f"Summary: {scanner.sbom_count} SBOM published")
    if scanner.sbom_count and scanner.sbom_scan_failed:
        fail(
            f"{scanner.sbom_scan_failed} SBOM scan failed. Check the logs for details."
        )
