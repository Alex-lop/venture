"""The plan and policy schema, ported from Graphene's mission models.

Every model is frozen and refuses unknown fields, so a document that parses is
a document whose every field this version understands.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
    model_validator,
)

from .globs import MAX_PATH_SEGMENTS, MAX_POLICY_WILDCARDS, wildcard_components

MAX_ARTIFACT_BYTES = 1_048_576

#: Most paths one plan may name in total, counting every task's `read_paths`,
#: `write_paths` and output paths. Every one of them is matched against every
#: policy glob and exclusion, so this is what keeps a document that fits inside
#: `MAX_DOCUMENT_BYTES` bounded in work as well as in bytes.
MAX_PLAN_PATHS = 2_048

#: Most globs one policy may list under `allowed_read_globs`, under
#: `allowed_write_globs` and under `exclusions`. Every path a plan names is
#: matched against every entry of all three, so this is the second factor -- of
#: three, with `MAX_PLAN_PATHS` and `globs.MAX_PATH_SEGMENTS` -- in how much
#: work a document inside `MAX_DOCUMENT_BYTES` can ask for.
MAX_POLICY_GLOBS = 64


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize to the one byte string this package hashes."""

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode()


def canonical_json_sha256(value: Any) -> str:
    """SHA-256 of the canonical JSON encoding of `value`."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


#: Control characters, line and paragraph separators, and the bidirectional
#: formatting characters. Text from a document reaches a report, a check
#: annotation or a review UI verbatim, and a newline in a path would let a plan
#: forge a line of this tool's own output while an override would let it render
#: as a different path than the one the policy is applied to. `cli` escapes the
#: same set on the way out for text that never went through a model -- a file
#: name off the command line -- so the two cannot drift apart.
#:
#: The zero-width non-joiner (U+200C) and joiner (U+200D) are *not* in the set:
#: they neither move the cursor nor hide text, they are mandatory orthography in
#: Persian, Urdu and Devanagari, and U+200D is how a multi-part emoji is spelled.
#: They are legal in text and refused in a *path*: `_hidden_code_point` below
#: refuses them with the rest of the C, Z and M categories, because a path is
#: not orthography and two leases that render alike are two files.
#: Every other character that renders as nothing *is* in the set, because two
#: leases a reviewer sees as one string are two files: the zero-width space
#: (U+200B), the soft hyphen (U+00AD), the Mongolian vowel separator (U+180E),
#: the word joiner and the invisible operators (U+2060-U+2064), the byte-order
#: mark used as a zero-width no-break space (U+FEFF), and the Hangul fillers
#: (U+115F, U+1160, U+3164, U+FFA0).
UNPRINTABLE = re.compile(
    r"[\x00-\x1f\x7f\u00ad\u115f\u1160\u180e\u2028\u2029\u200b\u200e\u200f"
    r"\u202a-\u202e\u2060-\u2064\u2066-\u2069\u3164\ufeff\uffa0]"
)

#: Unicode's `Default_Ignorable_Code_Point` property, transcribed by hand from
#: DerivedCoreProperties.txt -- https://www.unicode.org/Public/15.1.0/ucd/
#: DerivedCoreProperties.txt, the `# Default_Ignorable_Code_Point` block. The
#: ranges are the file's, with its adjacent lines merged (`180B..180D` +
#: `180E` + `180F`, `2060..2064` + `2065` + `2066..206F`, and the whole tag and
#: variation-selector plane `E0000..E0FFF`); they are identical in Unicode 14.0,
#: which CPython 3.11 ships, and in 16.0.
#:
#: A conforming renderer draws every one of them as nothing when it has no glyph
#: for it, which is the property that makes two paths a reviewer reads as one
#: string two different files. `str.isprintable` is not that property: 263 of
#: these are category Mn -- the combining grapheme joiner, the Khmer inherent
#: vowels, the Mongolian free variation selectors and the 256 variation
#: selectors -- and Python calls every one of those printable. The rest are
#: Cf or Cn, which it does not, plus the four Hangul fillers (U+115F, U+1160,
#: U+3164, U+FFA0), which are category Lo and which it DOES call printable --
#: the reason this lists the property rather than the categories.
DEFAULT_IGNORABLE = re.compile(
    r"[\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180b-\u180f"
    r"\u200b-\u200f\u202a-\u202e\u2060-\u206f\u3164\ufe00-\ufe0f\ufeff"
    r"\uffa0\ufff0-\ufff8\U0001bca0-\U0001bca3\U0001d173-\U0001d17a"
    r"\U000e0000-\U000e0fff]"
)

#: In no C or Z category and not `Default_Ignorable`, but it is the empty cell
#: of the Braille block and every font draws it blank, so it hides text exactly
#: the way the set above does. Refused in a path by name.
BLANK_BY_GLYPH = "\u2800"


def is_invisible(character: str) -> bool:
    """Whether `character` renders as nothing, or as something other than itself.

    One predicate with two callers -- `_hidden_code_point` refuses it in a path,
    `cli._printable` escapes it on the way out -- so what a document may contain
    and what this tool prints back cannot drift apart.
    """

    return (
        not character.isprintable()
        or UNPRINTABLE.match(character) is not None
        or DEFAULT_IGNORABLE.match(character) is not None
        or character == BLANK_BY_GLYPH
    )


def _hidden_code_point(value: str) -> str | None:
    """The first code point `value` may not contain as a path, or None.

    The rule, applied per code point: its Unicode general category may not begin
    with C (control, format, surrogate, private use, unassigned), Z (separator)
    or M (combining mark); it may not be in `DEFAULT_IGNORABLE`; and
    `BLANK_BY_GLYPH` is refused by name.

    U+0020 is the one exception, and a deliberate one: a space inside a file
    name is ordinary on every desktop filesystem, and a *trailing* space is
    refused below, where Windows would strip it. What the M clause costs is that
    a path may not carry a combining mark: `app/cafe.py` with a combining acute
    is refused where the composed spelling loads, and so is a path in a script
    whose vowel signs are separate code points. That is the trade this gate
    makes -- a path here is a lease key a human approves, not orthography -- and
    `docs/schema.md` states it.

    This replaced `str.isprintable`, which is only the C and Z half of the rule.
    What it admitted includes 264 code points that are hidden outright -- the 263
    combining marks in `DEFAULT_IGNORABLE` and `BLANK_BY_GLYPH` -- and every
    other mark besides: `app/sec<U+034F>rets/key.pem` renders character for
    character like `app/secrets/key.pem`, so it walked past an exclusion on that
    subtree and leased a second file a reviewer reads as the first.
    """

    if value.isascii():
        # Every ASCII code point outside the C categories is a letter, a digit,
        # punctuation or the space, and `_no_control_characters` refused the C
        # ones before this was called -- so the ordinary path costs one scan of
        # the string and no table lookup at all.
        return None
    for character in value:
        if character == " ":
            continue
        if is_invisible(character) or unicodedata.category(character)[0] == "M":
            return character
    return None


def _no_control_characters(value: str) -> str:
    """Refuse text that could forge, or disguise, a line in output that quotes it back."""

    if UNPRINTABLE.search(value):
        raise ValueError("text may not contain control or bidirectional formatting characters")
    return value


def _relative_posix_path(value: str) -> str:
    path = PurePosixPath(value)
    _no_control_characters(value)
    if (hidden := _hidden_code_point(value)) is not None:
        # Every character that renders as nothing, or as part of its neighbour,
        # is refused here and stays legal in `BoundedText`: U+200D is how a
        # multi-part emoji is spelled and the joiners are mandatory orthography
        # in Persian, Urdu and Devanagari. In a path they are not orthography.
        # The code point is named so the refusal can be acted on -- it is the one
        # thing a reviewer cannot read off the document.
        raise ValueError(
            f"path may not contain U+{ord(hidden):04X}, an invisible, combining or non-printable character"
        )
    if value in {"", "."} or "\\" in value or path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise ValueError("path must be canonical, relative, and stay inside the repo")
    if any(part != part.rstrip(". ") for part in path.parts):
        # Windows strips a trailing dot or space off a path component, so
        # `app/token.env.` and `app/token.env` are one file there while every
        # comparison in `validation` would call them two. `_path_key` folds the
        # case difference macOS and Windows also have; this one is refused at the
        # parse boundary instead, because folding it would make a path a policy
        # granted stop matching itself on Linux, where the spellings are two
        # genuinely different files.
        raise ValueError("path may not have a component ending in a dot or a space")
    if len(path.parts) > MAX_PATH_SEGMENTS:
        raise ValueError(f"path may not have more than {MAX_PATH_SEGMENTS} segments")
    return value


RepoPath = Annotated[
    str,
    Field(min_length=1, max_length=256),
    AfterValidator(_relative_posix_path),
]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
GitSha = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")]
IdempotencyKey = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{16,128}$")]
BoundedText = Annotated[str, Field(min_length=1, max_length=1024), AfterValidator(_no_control_characters)]


def _utc_datetime(value: datetime) -> datetime:
    if value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value.astimezone(UTC)


UtcDateTime = Annotated[datetime, AfterValidator(_utc_datetime)]

# Plan text is quoted back into logs, tickets and review UIs, so a credential
# pasted into a task title is refused at parse time rather than copied around.
# Every shape below is a *secret shape*, not a word: an English sentence that
# happens to say "password" is a task title this tool's own buyers write, and
# refusing it would make the gate unusable. `docs/schema.md` lists the shapes.
#: How long a bearer token has to be before the word "bearer" in front of it
#: means a credential rather than a sentence.
MIN_BEARER_CHARACTERS = 16
#: How long an unbroken run has to be, and how many digits it needs, before
#: mixed case makes it a generated key rather than a long identifier.
MIN_TOKEN_CHARACTERS = 32
MIN_TOKEN_DIGITS = 3

_PEM_BLOCK = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
_PROVIDER_KEY = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{20,}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{12,})"
)

#: A name that means "a secret follows", and whatever it was assigned. The value
#: is captured so `_is_secret_value` can decide whether it is a secret or the
#: *name* of one: `secret = AWS_SECRET_ACCESS_KEY_V2` and
#: `token = settings.OAUTH2_TOKEN` are the sentences a rotation ticket is made
#: of, and refusing them refused the document at exit 2.
_ASSIGNED_SECRET = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|password|passwd|secret|token)\s*[:=]\s*"
    r"(?P<value>\S+)(?!\S)"
)


def _is_secret_value(value: str) -> bool:
    """Whether an assigned value is a secret rather than the name of one.

    A secret is a provider-prefixed key, a PEM block, or a run of at least
    `MIN_TOKEN_CHARACTERS` characters that mixes case and carries
    `MIN_TOKEN_DIGITS` digits. Unlike `_high_entropy`, the run is *not* broken on
    `/`, `_` or `-` first, because a value written after `secret=` is one field:
    that is what this shape adds over the entropy rule. Everything shorter is a
    name -- an environment variable, a dotted attribute, a placeholder -- and a
    name is not a credential however loudly it is spelled.
    """

    return bool(
        _PROVIDER_KEY.search(value)
        or _PEM_BLOCK.search(value)
        or (
            len(value) >= MIN_TOKEN_CHARACTERS
            and sum(character.isdigit() for character in value) >= MIN_TOKEN_DIGITS
            and any(character.islower() for character in value)
            and any(character.isupper() for character in value)
        )
    )


_CREDENTIAL_SHAPES = (
    ("a PEM private key block", _PEM_BLOCK),
    ("a bearer token", re.compile(rf"(?i)\bbearer\s+[a-z0-9._~+/=-]{{{MIN_BEARER_CHARACTERS},}}")),
    ("a provider key prefix", _PROVIDER_KEY),
    ("a password inside a URL", re.compile(r"://[^/\s:@]+:[^/\s@]+@")),
    (
        "a path into a credential store",
        re.compile(r"(?:^|[/\\])(?:\.ssh|\.aws|\.gnupg)(?:[/\\]|$)|(?:^|[/\\])\.netrc(?:$|\s)|/var/run/secrets/"),
    ),
)

#: An unbroken run long enough, and mixed enough, to be a generated key rather
#: than a word. A commit SHA is one case (lower-case hex only) and a long
#: snake_case or CamelCase identifier is another; both stay legal, because a run
#: shorter than `MIN_TOKEN_CHARACTERS` is never measured at all.
_TOKEN_RUN = re.compile(rf"(?<![A-Za-z0-9+/=_-])[A-Za-z0-9+/=_-]{{{MIN_TOKEN_CHARACTERS},}}(?![A-Za-z0-9+/=_-])")

#: `/`, `_` and `-` break a run before it is measured. A generated key is one
#: unbroken blob; a branch name, a source path, an ADR filename, a release tag
#: and a snake_case migration name are short words joined by those three
#: characters, and measuring the joined string refused
#: `feature/AB-1234-refactor-user-profile-service` and
#: `run_MigrationV2_2024_backfill_Step3_final` as credentials. The prefixed
#: shapes above still catch `sk-`, `ghp_`, `AKIA`, a bearer token and
#: `secret=value`, so what this gives up is unprefixed base64 that happens to
#: contain a slash, an underscore or a dash.
_RUN_SEPARATOR = re.compile(r"[/_-]")


def _high_entropy(value: str) -> bool:
    for run in _TOKEN_RUN.findall(value):
        for part in _RUN_SEPARATOR.split(run):
            if (
                len(part) >= MIN_TOKEN_CHARACTERS
                and sum(character.isdigit() for character in part) >= MIN_TOKEN_DIGITS
                and any(character.islower() for character in part)
                and any(character.isupper() for character in part)
            ):
                return True
    return False


def _credential_shape(value: str | None) -> str | None:
    """What kind of credential `value` looks like, or None when it is ordinary text."""

    if value is None:
        return None
    for reason, expression in _CREDENTIAL_SHAPES:
        if expression.search(value):
            return reason
    for match in _ASSIGNED_SECRET.finditer(value):
        if _is_secret_value(match.group("value")):
            return "a secret name assigned a token-shaped value"
    return "a long high-entropy token" if _high_entropy(value) else None


def _refuse_credentials(**fields: str | None) -> None:
    """Refuse the first field whose text looks like a credential, naming it and why.

    The value is never echoed back: the point is to keep it out of the logs
    that quote this error.
    """

    for name, value in fields.items():
        reason = _credential_shape(value)
        if reason is not None:
            raise ValueError(f"{name} looks like it contains a credential: {reason}")


# argv[0] spellings that mean "run this through an interpreter". See
# `CommandTemplate.argv_is_direct`: a typo guard, never a containment boundary.
_SHELL_COMMANDS = frozenset(
    {
        "bash",
        "cmd",
        "csh",
        "dash",
        "env",
        "eval",
        "fish",
        "ksh",
        "powershell",
        "pwsh",
        "sh",
        "tcsh",
        "xargs",
        "zsh",
    }
)


class TaskKind(StrEnum):
    WORK = "work"
    ASSEMBLY = "assembly"
    VERIFICATION = "verification"


class TaskState(StrEnum):
    QUEUED = "queued"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    RETRYING = "retrying"
    NEEDS_INPUT = "needs_input"
    VERIFYING = "verifying"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NetworkMode(StrEnum):
    DENY = "deny"
    ALLOWLIST = "allowlist"


class AuthorizationMode(StrEnum):
    POLICY_PRE_AUTHORIZED = "policy_pre_authorized"
    REVIEW_REQUIRED = "review_required"


class FinalizationMode(StrEnum):
    AUTO_FINALIZE_ISOLATED = "auto_finalize_isolated"
    REVIEW_REQUIRED = "review_required"


class CriterionVerificationKind(StrEnum):
    DETERMINISTIC_CHECK = "deterministic_check"
    HUMAN_GATE = "human_gate"
    MODEL_ASSERTION = "model_assertion"


class NetworkPolicy(FrozenModel):
    mode: NetworkMode = NetworkMode.DENY
    allowed_hosts: tuple[str, ...] = Field(default=(), max_length=32)

    @model_validator(mode="after")
    def mode_matches_hosts(self) -> NetworkPolicy:
        if self.allowed_hosts != tuple(sorted(set(self.allowed_hosts))):
            raise ValueError("network hosts must be sorted and unique")
        if (self.mode == NetworkMode.DENY) != (not self.allowed_hosts):
            raise ValueError("deny network policy cannot contain allowed hosts")
        return self


class CommandTemplate(FrozenModel):
    template_id: Identifier
    argv: tuple[BoundedText, ...] = Field(min_length=1, max_length=32)
    timeout_seconds: int = Field(gt=0, le=3_600)
    cwd: RepoPath | None = None

    @model_validator(mode="after")
    def argv_is_direct(self) -> CommandTemplate:
        """Refuse the obvious shell spellings of argv[0].

        This is a typo guard, not a containment boundary: `python -c` is a
        shell too, and no list of names can close that. It catches the
        template that was meant to be a direct command and was written as a
        shell line, on any spelling of the interpreter's path.
        """

        stem = re.split(r"[\\/]", self.argv[0])[-1].rsplit(".", 1)[0].casefold()
        if stem in _SHELL_COMMANDS:
            raise ValueError("shell command templates are not allowed")
        return self


class ResourceBudget(FrozenModel):
    max_worker_seconds: int = Field(gt=0, le=86_400)
    max_attempts: int = Field(gt=0, le=10_000)
    max_artifact_bytes: int = Field(gt=0, le=MAX_ARTIFACT_BYTES * 100)


class ProjectPolicy(FrozenModel):
    schema_version: Literal[1, 2] = 1
    policy_id: Identifier
    revision: int = Field(ge=1)
    repo_id: Identifier
    base_ref: BoundedText
    base_sha: GitSha
    allowed_read_globs: tuple[RepoPath, ...] = Field(min_length=1, max_length=MAX_POLICY_GLOBS)
    allowed_write_globs: tuple[RepoPath, ...] = Field(min_length=1, max_length=MAX_POLICY_GLOBS)
    exclusions: tuple[RepoPath, ...] = Field(default=(), max_length=MAX_POLICY_GLOBS)
    case_sensitive_paths: bool = False
    command_templates: tuple[CommandTemplate, ...] = Field(min_length=1, max_length=64)
    network: NetworkPolicy = NetworkPolicy()
    agent_roles: tuple[Identifier, ...] = Field(min_length=1, max_length=32)
    max_concurrency: int = Field(gt=0, le=64)
    retry_limit: int = Field(ge=0, le=10)
    resource_budget: ResourceBudget
    risk_gates: tuple[Identifier, ...] = Field(default=(), max_length=32)
    authorization_mode: AuthorizationMode = AuthorizationMode.REVIEW_REQUIRED
    finalization_mode: FinalizationMode = FinalizationMode.REVIEW_REQUIRED

    @model_validator(mode="after")
    def collections_are_canonical(self) -> ProjectPolicy:
        collections = (
            self.allowed_read_globs,
            self.allowed_write_globs,
            self.exclusions,
            self.agent_roles,
            self.risk_gates,
        )
        if any(items != tuple(sorted(set(items))) for items in collections):
            raise ValueError("policy collections must be sorted and unique")
        # Every path a plan names is matched against every glob and exclusion
        # here, and only a component that is neither a literal name nor `*` nor
        # `**` costs a scan of the path's segments for each of those pairs.
        # Bounding how many *distinct* ones a policy may spend is what keeps
        # the matching work finite for a document inside the byte cap.
        spent = wildcard_components(self.allowed_read_globs + self.allowed_write_globs + self.exclusions)
        if len(spent) > MAX_POLICY_WILDCARDS:
            raise ValueError(f"a policy may use at most {MAX_POLICY_WILDCARDS} distinct wildcard path components")
        ids = tuple(item.template_id for item in self.command_templates)
        if ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("command templates must have sorted unique IDs")
        if self.schema_version == 1 and (
            self.authorization_mode != AuthorizationMode.REVIEW_REQUIRED
            or self.finalization_mode != FinalizationMode.REVIEW_REQUIRED
        ):
            raise ValueError("schema-1 policy supports review-required mode only")
        if self.schema_version == 2 and not {"authorization_mode", "finalization_mode"} <= self.model_fields_set:
            raise ValueError("schema-2 policy must declare its execution modes")
        if self.finalization_mode == FinalizationMode.AUTO_FINALIZE_ISOLATED and (
            self.authorization_mode != AuthorizationMode.POLICY_PRE_AUTHORIZED or "final-result" in self.risk_gates
        ):
            raise ValueError("automatic finalization requires pre-authorization and no final-result gate")
        return self

    @model_serializer(mode="wrap")
    def preserve_schema_one_bytes(self, handler: Any) -> dict[str, Any]:
        value = handler(self)
        if self.schema_version == 1:
            value.pop("authorization_mode", None)
            value.pop("finalization_mode", None)
        return value


class PlanPolicyDecisionV1(FrozenModel):
    schema_version: Literal[1] = 1
    goal_request_id: IdempotencyKey
    requested_mode: AuthorizationMode
    effective_mode: AuthorizationMode
    finalization_mode: FinalizationMode
    policy_id: Identifier
    policy_revision: int = Field(ge=1)
    policy_sha256: Sha256
    base_sha: GitSha
    plan_revision: int = Field(ge=1)
    plan_sha256: Sha256
    reason_codes: tuple[Identifier, ...] = Field(min_length=1, max_length=32)
    decision_sha256: Sha256

    @model_validator(mode="after")
    def exact_policy_decision(self) -> PlanPolicyDecisionV1:
        if self.reason_codes != tuple(sorted(set(self.reason_codes))):
            raise ValueError("policy decision reasons must be sorted and unique")
        if (
            self.finalization_mode == FinalizationMode.AUTO_FINALIZE_ISOLATED
            and self.effective_mode != AuthorizationMode.POLICY_PRE_AUTHORIZED
        ):
            raise ValueError("automatic finalization requires effective pre-authorization")
        expected = canonical_json_sha256(self.model_dump(mode="json", exclude={"decision_sha256"}))
        if self.decision_sha256 != expected:
            raise ValueError("policy decision digest does not match")
        return self

    @classmethod
    def create(cls, **values: object) -> PlanPolicyDecisionV1:
        core = {"schema_version": 1, **values}
        core.pop("decision_sha256", None)
        return cls.model_validate({**core, "decision_sha256": canonical_json_sha256(core)})


class ArtifactContract(FrozenModel):
    name: Identifier
    kind: Identifier
    paths: tuple[RepoPath, ...] = Field(default=(), max_length=64)

    @model_validator(mode="after")
    def paths_are_canonical(self) -> ArtifactContract:
        if self.paths != tuple(sorted(set(self.paths))):
            raise ValueError("artifact paths must be sorted and unique")
        return self


class ArtifactRequirement(FrozenModel):
    producer_task_id: Identifier
    name: Identifier
    kind: Identifier


class Criterion(FrozenModel):
    criterion_id: Identifier
    description: BoundedText
    producer_task_ids: tuple[Identifier, ...] = Field(default=(), max_length=64)
    verification_kind: CriterionVerificationKind
    verifier_task_id: Identifier | None = None
    verifier_id: Identifier | None = None

    @model_validator(mode="after")
    def producers_are_canonical(self) -> Criterion:
        if self.producer_task_ids != tuple(sorted(set(self.producer_task_ids))):
            raise ValueError("criterion producers must be sorted and unique")
        _refuse_credentials(description=self.description)
        return self


class Task(FrozenModel):
    schema_version: Literal[1] = 1
    task_id: Identifier
    title: BoundedText
    contract: BoundedText
    kind: TaskKind = TaskKind.WORK
    dependencies: tuple[Identifier, ...] = Field(default=(), max_length=64)
    assigned_role: Identifier
    read_paths: tuple[RepoPath, ...] = Field(min_length=1, max_length=256)
    write_paths: tuple[RepoPath, ...] = Field(default=(), max_length=128)
    allowed_commands: tuple[Identifier, ...] = Field(min_length=1, max_length=32)
    inputs: tuple[ArtifactRequirement, ...] = Field(default=(), max_length=64)
    expected_outputs: tuple[ArtifactContract, ...] = Field(min_length=1, max_length=64)
    acceptance_checks: tuple[Identifier, ...] = Field(min_length=1, max_length=32)
    priority: int = Field(ge=-1_000, le=1_000)
    state: TaskState = TaskState.QUEUED
    attempt_limit: int = Field(gt=0, le=20)
    attempt_count: int = Field(default=0, ge=0, le=20)
    retry_at: UtcDateTime | None = None
    blocker: BoundedText | None = None

    @model_validator(mode="after")
    def collections_and_state_are_consistent(self) -> Task:
        _refuse_credentials(title=self.title, contract=self.contract, blocker=self.blocker)
        collections = (
            self.dependencies,
            self.read_paths,
            self.write_paths,
            self.allowed_commands,
            self.acceptance_checks,
        )
        if any(items != tuple(sorted(set(items))) for items in collections):
            raise ValueError("task collections must be sorted and unique")
        if self.task_id in self.dependencies:
            raise ValueError("task cannot depend on itself")
        output_keys = tuple((item.name, item.kind) for item in self.expected_outputs)
        input_keys = tuple((item.producer_task_id, item.name, item.kind) for item in self.inputs)
        if len(output_keys) != len(set(output_keys)) or len(input_keys) != len(set(input_keys)):
            raise ValueError("artifact contracts must be unique")
        if output_keys != tuple(sorted(output_keys)) or input_keys != tuple(sorted(input_keys)):
            raise ValueError("artifact contracts must be sorted")
        exact_paths = (
            *self.write_paths,
            *(path for item in self.expected_outputs for path in item.paths),
        )
        if any(any(character in path for character in "*?[") for path in exact_paths):
            raise ValueError("task write and output paths must be exact")
        if self.attempt_count > self.attempt_limit:
            raise ValueError("task attempts exceed the limit")
        if (self.state == TaskState.RETRYING) != (self.retry_at is not None):
            raise ValueError("only retrying tasks carry retry_at")
        if (self.state in {TaskState.BLOCKED, TaskState.NEEDS_INPUT}) != (self.blocker is not None):
            raise ValueError("blocked and needs-input tasks require a blocker")
        return self


class Plan(FrozenModel):
    schema_version: Literal[1] = 1
    mission_id: Identifier
    revision: int = Field(ge=1)
    previous_revision: int | None = Field(default=None, ge=1)
    criteria: tuple[Criterion, ...] = Field(default=(), max_length=32)
    tasks: tuple[Task, ...] = Field(min_length=3, max_length=256)
    max_concurrency: int = Field(gt=0, le=64)

    @model_validator(mode="after")
    def revision_and_ids_are_canonical(self) -> Plan:
        criterion_ids = tuple(item.criterion_id for item in self.criteria)
        if criterion_ids != tuple(sorted(criterion_ids)) or len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("plan criteria must have sorted unique IDs")
        ids = tuple(item.task_id for item in self.tasks)
        if ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("plan tasks must have sorted unique IDs")
        if self.revision == 1 and self.previous_revision is not None:
            raise ValueError("initial plan cannot have a previous revision")
        if self.revision > 1 and self.previous_revision != self.revision - 1:
            raise ValueError("plan revisions must link contiguously")
        named = sum(
            len(task.read_paths) + len(task.write_paths) + sum(len(item.paths) for item in task.expected_outputs)
            for task in self.tasks
        )
        if named > MAX_PLAN_PATHS:
            raise ValueError(f"a plan may name at most {MAX_PLAN_PATHS} paths in total")
        return self
