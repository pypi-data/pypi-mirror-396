###############################################################################
# (c) Copyright 2021-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import datetime
import re
from collections import OrderedDict
from enum import StrEnum
from os.path import isfile, join, relpath
from typing import Annotated, Any, Dict, Self

import jinja2
import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Discriminator,
    Field,
    RootModel,
    Tag,
    TypeAdapter,
    ValidationInfo,
    field_validator,
    model_validator,
)

from LbAPCommon import config as config
from LbAPCommon.linting.bk_paths import InvalidBKQueryError, validate_bk_query
from LbAPCommon.models.validators import force_to_list, output_filetype_validator

from .recipes import AllRecipes

RE_APPLICATION = r"^(([A-Za-z]+/)+v\d+r\d+(p\d+)?(\@[a-z0-9_\-\+]+)?)|(lb\-conda/[A-Za-z0-9_]+/(\d\d\d\d\-\d\d-\d\d))"
RE_JOB_NAME = r"^[a-zA-Z0-9][a-zA-Z0-9_\-]+$"
RE_OUTPUT_FILE_TYPE = (
    r"^([A-Za-z][A-Za-z0-9_]+\.)+((ROOT|root|HIST|hist)|.?(DST|dst|mdf|MDF))$"
)
RE_OPTIONS_FN = r"^\$?[a-zA-Z0-9/\.\-\+\=_]+$"
RE_INFORM = r"^[a-z]+$"

RE_ROOT_IN_TES = r"^\/.+$"
RE_DDDB_TAG = r"^.{1,50}$"
RE_CONDDB_TAG = r"^.{1,50}$"

RE_COMMENT = r"(.{1,5000})"

RE_RUN_SPEC = r"(\d+:\d+)|(\d+)"

# TODO: make annotated string field types for each of the above
APJobName = Annotated[str, Field(pattern=RE_JOB_NAME)]

OutputFileType = Annotated[
    str,
    Field(pattern=RE_OUTPUT_FILE_TYPE, max_length=50),
    AfterValidator(output_filetype_validator),
]
OptionsFile = Annotated[str, Field(pattern=RE_OPTIONS_FN)]

CondDBTag = Annotated[str, Field(pattern=RE_CONDDB_TAG)]
DDDBTag = Annotated[str, Field(pattern=RE_DDDB_TAG)]


def validate_inform_username(value: str) -> str:
    """Validate that the inform field contains only lowercase alphabetical characters."""
    import re

    if not re.match(RE_INFORM, value):
        raise ValueError(
            f"Invalid CERN username '{value}'. "
            f"The 'inform' field requires CERN usernames (not email addresses) "
            f"containing only lowercase letters (a-z). "
            f"Valid examples: 'johndoe', 'alice', 'bob'. "
            f"See documentation for more details on the 'inform' field."
        )
    return value


Inform = Annotated[
    str,
    Field(
        min_length=1,
        title="CERN username",
        description=(
            "A CERN username referring to a user that should"
            " be informed about the production status and assigned as an owner."
            " Must contain only lowercase alphabetical characters."
        ),
        examples=["johndoe", "alice", "bob"],
    ),
    AfterValidator(validate_inform_username),
]
RunSpec = Annotated[str, Field(pattern=RE_RUN_SPEC, coerce_numbers_to_str=True)]


class Input(BaseModel):
    sample_fraction: Annotated[float, Field(gt=0, lt=1)] | None = Field(
        title="Sample fraction",
        description="The sampling fraction to use when sampling input LFNs (0.0 to 1.0). For example, 0.1 will sample 10% of input files.",
        default=None,
        examples=[0.1, 0.5],
    )
    sample_seed: str | None = Field(
        title="Sample seed",
        description="The seed to use when sampling input LFNs for reproducible sampling.",
        default=None,
        examples=["HelloWorld", "analysis_2024"],
    )


class DQFlag(StrEnum):
    OK = "OK"
    BAD = "BAD"
    UNCHECKED = "UNCHECKED"
    EXPRESS_OK = "EXPRESS_OK"
    CONDITIONAL = "CONDITIONAL"


class InputPlugin(StrEnum):
    default = "default"
    byrun = "by-run"


class WorkingGroup(StrEnum):
    """
    Working Groups in the LHCb collaboration.

    These represent the different physics and detector working groups
    responsible for various aspects of LHCb analysis and operations.

    For the complete list and descriptions, see:
    https://lhcb-ap.docs.cern.ch/user_guide/creating.html#working-groups
    """

    B2CC = "B2CC"  # B hadrons to charmonium and charm
    B2OC = "B2OC"  # B hadrons to open charm
    BandQ = "BandQ"  # B physics and QCD
    BnoC = "BnoC"  # B hadrons without charm
    Calib = "Calib"  # Calibration and alignment
    Calo = "Calo"  # Calorimeter systems
    Charm = "Charm"  # Charm physics
    DPA = "DPA"  # Data Processing and Analysis
    FlavourTagging = "FlavourTagging"  # Flavour tagging algorithms
    HLT = "HLT"  # High Level Trigger
    IFT = "IFT"
    Luminosity = "Luminosity"  # Luminosity measurements
    OpenData = "OpenData"  # Open data initiative
    PID = "PID"  # Particle identification
    QCD = "QCD"  # Quantum chromodynamics
    QEE = "QEE"  # QCD, electroweak and exotics
    RD = "RD"  # Rare decays
    RTA = "RTA"  # Real-time analysis
    RICH = "RICH"  # Ring-imaging Cherenkov detectors
    Run12Performance = "Run12Performance"  # Run 1 and 2 performance studies
    Simulation = "Simulation"  # Monte Carlo simulation
    SL = "SL"  # Semileptonic decays
    Statistics = "Statistics"  # Statistical methods
    Stripping = "Stripping"  # Data stripping and selection
    Tracking = "Tracking"  # Track reconstruction


class DataType(StrEnum):
    Upgrade = "Upgrade"
    YEAR_2011 = "2011"
    YEAR_2012 = "2012"
    YEAR_2015 = "2015"
    YEAR_2016 = "2016"
    YEAR_2017 = "2017"
    YEAR_2018 = "2018"

    YEAR_2022 = "2022"
    YEAR_2023 = "2023"
    YEAR_2024 = "2024"


class InputType(StrEnum):
    DST = "DST"
    MDST = "MDST"
    RAW = "RAW"


class Priority(StrEnum):
    PRIO_1A = "1a"
    PRIO_1B = "1b"
    PRIO_2A = "2a"
    PRIO_2B = "2b"


def input_discriminator(v: Any):
    tags = ["bk_query", "transform_ids", "sample", "job_name", "tags"]
    for tag in tags:
        if tag in v:
            return tag
    return None


class APJob(BaseModel):
    """
    Analysis Production Job Configuration

    Defines a complete job specification for LHCb Analysis Productions,
    including input data, processing options, and output configuration.

    See https://lhcb-ap.docs.cern.ch/ for comprehensive documentation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Clean up string inputs
        validate_assignment=True,  # Validate on field assignment
        use_enum_values=True,
        title="LbAP Job Configuration",
        json_schema_extra={
            "examples": [
                {
                    "wg": "Charm",
                    "inform": ["alice"],
                    "application": "DaVinci/v64r14",
                    "input": {"bk_query": "/LHCb/Collision24/.../CHARM.DST"},
                    "output": ["TUPLE.ROOT"],
                    "options": {"entrypoint": "my_analysis:main"},
                }
            ]
        },
    )

    wg: WorkingGroup = Field(
        title="Working Group",
        description="The working group which this request belongs to.",
    )
    inform: Annotated[list[Inform], BeforeValidator(force_to_list)] = Field(
        title="Inform",
        description="Who to inform about the request status.",
        examples=["your_cern_username"],
    )
    application: str = Field(
        title="Application",
        description="Which application environment the options should be run within.",
        examples=["DaVinci/v64r14", "lb-conda/default/2024-12-12"],
        pattern=RE_APPLICATION,
    )

    class BKQueryInput(Input, use_enum_values=True):
        bk_query: str = Field(
            title="Bookkeeping query path",
            description="The bookkeeping query path to use as the input.",
            examples=[
                "/LHCb/Collision16/Beam6500GeV-VeloClosed-MagDown/Real Data/Turbo03a/94000000/CHARMMULTIBODY.MDST"
            ],
        )

        smog2_state: list[str] | None = Field(
            title="SMOG2 gas state",
            description="Gas injected in SMOG2.",
            examples=[["Argon"], ["ArgonUnstable"], ["Hydrogen", "HydrogenUnstable"]],
            default=None,
        )
        dq_flags: list[DQFlag] | None = Field(
            title="Data Quality flags",
            description="What data quality to query from the Bookkeeping. Multiple flags can be specified.",
            examples=[["OK"], ["OK", "BAD"], ["UNCHECKED"]],
            default=None,
        )
        extended_dq_ok: list[str] | None = Field(
            title="Extended Data Quality OK flags",
            description="Additional DQ flags required for subsystems. Runs without specified subsystem DQ OK flags are excluded.",
            examples=[["RICH"], ["MUON", "CALO"]],
            default=None,
        )
        runs: list[RunSpec] | None = Field(
            title="Inclusive run-ranges",
            default=None,
            examples=[["1234"], ["1234:2000"]],
        )
        start_run: int | None = Field(
            title="StartRun",
            description="Filter the BK query output such that runs before this run number are excluded.",
            examples=[1234],
            default=None,
        )
        end_run: int | None = Field(
            title="EndRun",
            description="Filter the BK query output such that runs after this run number are excluded.",
            examples=[1234],
            default=None,
        )
        input_plugin: InputPlugin = Field(
            title="Input plugin",
            description="The input plugin setting to use for processing input data.",
            default=InputPlugin.default,
            validate_default=True,
        )
        keep_running: bool = Field(
            title="Keep running",
            description="Whether to keep running on new data as it comes in.",
            default=True,
        )
        n_test_lfns: int = Field(
            title="Number of test LFNs",
            description="The number of files to use as input to test jobs. Only use for samples with very few output candidates.",
            default=1,
            ge=1,
        )

        @model_validator(mode="after")
        def use_runs_or_startend_run(self) -> Self:
            if self.runs and (self.start_run or self.end_run):
                raise ValueError(
                    "Either use `start_run` and `end_run`, or use `runs` - can't use both."
                )

            if not self.runs and (self.start_run and self.end_run):
                if self.start_run >= self.end_run:
                    raise ValueError(
                        f"Start run {self.start_run} must be less than end run {self.end_run}."
                    )
            if self.runs and not (self.start_run or self.end_run):
                if len(self.runs) == 1 and ":" in self.runs[0]:
                    self.start_run, self.end_run = map(int, self.runs[0].split(":"))
                    self.runs = None

                    if self.start_run >= self.end_run:
                        raise ValueError(
                            f"Start run {self.start_run} must be less than end run {self.end_run}."
                        )

            return self

        @field_validator("bk_query", mode="after")
        def check_bk_path(bk_query):
            if not bk_query.startswith("/"):
                raise InvalidBKQueryError(
                    "Bookkeeping paths must start with a forward-slash '/'."
                )
            validate_bk_query(bk_query)
            return bk_query

    class JobInput(Input):
        job_name: str = Field(
            title="Job input name",
            description="The name of the job to consume output from.",
            pattern=RE_JOB_NAME,
        )
        filetype: str | None = Field(
            title="File type",
            description="Which filetype to consume from the output of the referenced analysis productions job.",
            pattern=RE_OUTPUT_FILE_TYPE,
            default=None,
            examples=["XICP.ROOT", "DATA.ROOT", "MC.ROOT", "HLT2.DST"],
        )

    class APSampleInput(Input):
        wg: WorkingGroup = Field(
            title="Working group",
            description="The working group that owns the sample data.",
        )
        analysis: str = Field(
            title="Analysis name",
            description="The name of the analysis to query samples for.",
            examples=["B2DKstar", "Charm_physics"],
        )
        tags: dict[str, str] = Field(
            title="Sample tags",
            description="Additional tags to filter sample data.",
            default_factory=lambda: {},
            examples=[{"polarity": "MagUp"}, {"year": "2018", "stream": "AllStreams"}],
        )
        at_time: datetime.datetime = Field(
            title="Query time (UTC)",
            description="The timestamp at which to query the sample database.",
            default_factory=lambda: datetime.datetime.now(datetime.UTC),
        )
        n_test_lfns: int = Field(
            title="Number of test LFNs",
            description="The number of files to use as input to test jobs.",
            default=1,
            ge=1,
        )
        keep_running: bool = Field(
            title="Keep running",
            description="Whether to keep running on new data as it comes in.",
            default=True,
        )

    class TransformIDInput(Input):
        transform_ids: list[int] = Field(
            title="Transformation IDs",
            description="A list of transformation IDs from which to query input from.",
        )
        filetype: str | None = Field(
            title="File type",
            description="Which filetype to consume from the output of the referenced analysis productions job.",
            pattern=RE_OUTPUT_FILE_TYPE,
            default=None,
            examples=["XICP.ROOT"],
        )
        n_test_lfns: int = Field(
            title="Number of test LFNs",
            description="The number of files to use as input to test jobs.",
            default=1,
            ge=1,
        )
        keep_running: bool = Field(
            title="Keep running",
            description="Whether to keep running on new data as it comes in.",
            default=True,
        )

    input: (
        Annotated[BKQueryInput, Tag("bk_query")]
        | Annotated[TransformIDInput, Tag("transform_ids")]
        | Annotated[JobInput, Tag("job_name")]
        | Annotated[APSampleInput, Tag("tags")]
    ) = Field(
        title="Input specification",
        description="Where to specify the input to the job.",
        discriminator=Discriminator(input_discriminator),
    )

    output: Annotated[list[OutputFileType], BeforeValidator(force_to_list)] = Field(
        title="Output files",
        description=(
            "List of output file types that will be produced by this job. "
            r"File types must follow the pattern [A-Za-z][A-Za-z0-9_]+\.((ROOT|root|HIST|hist)|.?(DST|dst|mdf|MDF))."
        ),
        examples=[["DATA.ROOT"], ["CHARM.DST", "SUMMARY.ROOT"]],
    )

    recipe: AllRecipes | None = Field(
        title="Recipe",
        description="A predefined job recipe.",
        discriminator="name",
        default_factory=lambda: None,
    )

    automatically_configure: bool = Field(
        title="Automatically configure",
        description="Whether to automatically configure input-specific job options such as Data Type, RootInTES, et cetera.",
        default=False,
    )
    turbo: bool = Field(
        title="Turbo stream processing",
        description="Set this to true if processing turbo (run 2) data.",
        default=False,
    )

    class LegacyOptions(BaseModel):
        files: list[OptionsFile] = Field(
            title="Options files",
            description="List of Python options files for Run 1/2 applications (gaudirun.py style).",
            examples=[["options.py"], ["data_options.py", "reco_options.py"]],
        )
        command: list[str] | None = Field(
            title="Command",
            description="Command to call with the provided options file.",
            default=None,
            examples=[["gaudirun.py", "-T"]],
        )

    class LbExecOptions(BaseModel):
        entrypoint: str = Field(
            title="Entrypoint",
            description="The entry point for Run 3+ applications in the format 'module:function'.",
            pattern=r".+:.+",
            examples=["my_production.script:my_job", "LbExec:skim_and_merge"],
        )
        extra_options: Dict[str, Any] | None = Field(
            title="Extra options",
            description="Additional YAML configuration options passed to the application.",
            default_factory=lambda: None,
            examples=[
                {"compression": {"optimise_baskets": False}},
                {
                    "input_type": "ROOT",
                    "input_raw_format": 0.5,
                    "data_type": "Upgrade",
                    "simulation": False,
                },
            ],
        )
        extra_args: list[str] | None = Field(
            title="Extra arguments",
            description="Additional command line arguments passed to the application.",
            default_factory=lambda: None,
            examples=[["--debug"], ["--", "--write=output.root"]],
        )

        @field_validator("extra_args", mode="before")
        def extra_args_as_str(cls, extra_args):
            if isinstance(extra_args, list):
                return map(str, extra_args)

            return extra_args

    options: LbExecOptions | LegacyOptions = Field(
        title="Job options",
        description="Configuration for the job execution. Use LbExecOptions for Run 3+ applications or LegacyOptions for Run 1/2 applications.",
        union_mode="smart",
    )

    # auto-configure

    root_in_tes: str | None = Field(
        title="Root in TES",
        description="Set the value of RootInTES for MDST input processing.",
        pattern=RE_ROOT_IN_TES,
        default_factory=lambda: None,
        examples=["/Event/Turbo", "/Event/AllStreams"],
    )
    simulation: bool | None = Field(
        title="Simulation flag",
        description="Whether this job processes simulation (MC) data.",
        default=None,
    )
    luminosity: bool | None = Field(
        title="Luminosity flag",
        description="Whether luminosity information should be included.",
        default=None,
    )
    data_type: DataType | None = Field(
        title="Data type",
        description="The data taking period/year for this job.",
        default=None,
        examples=["2018", "2024", "Upgrade"],
    )
    input_type: InputType | None = Field(
        title="Input type",
        description="The type of input files being processed.",
        default=None,
        examples=["DST", "MDST", "RAW"],
    )
    dddb_tag: DDDBTag | None = Field(
        title="DDDB tag",
        description="The detector description database tag to use.",
        default=None,
        examples=["dddb-20170721-3"],
    )
    conddb_tag: CondDBTag | None = Field(
        title="CondDB tag",
        description="The conditions database tag to use.",
        default=None,
        examples=["cond-20170724"],
    )

    # checks (TODO!! or add deprecation warning)
    checks: list[str] | None = Field(
        title="Checks",
        description="Defunct. Don't use.",
        default=None,
        deprecated=True,
    )
    extra_checks: list[str] | None = Field(
        title="Extra checks",
        description="Defunct. Don't use.",
        default=None,
        deprecated=True,
    )

    # Production submission metadata
    comment: str | None = Field(
        title="DIRAC request comment",
        description="Optional comment for the DIRAC production request. Typically not used.",
        default=None,
        pattern=RE_COMMENT,
    )
    tags: dict[str, str] | None = Field(
        title="Job tags",
        description="Additional metadata tags for the job.",
        default=None,
        examples=[{"priority": "high"}, {"campaign": "2024_analysis"}],
    )
    priority: Priority | None = Field(
        title="Request priority",
        description="DIRAC request priority. Typically not used.",
        default=Priority.PRIO_1B,
        validate_default=True,
    )
    completion_percentage: float | None = Field(
        title="Completion percentage",
        description="Target completion percentage for the job (10-100%).",
        default=100.0,
        ge=10.0,
        le=100.0,
    )

    @field_validator("options", mode="before")
    def normalise_to_lists(cls, options, info: ValidationInfo):
        repo_root = info.context.get("repo_root", "") or None
        prod_name = info.context.get("prod_name", "") or ""

        options = force_to_list(options)

        # Normalise the options filenames if we're using a non-PyConf application
        if isinstance(options, list):
            options = {"files": options}

        if "files" in options:
            normalised_options = []
            for fn in options["files"]:
                if fn.startswith("$"):
                    normalised_options.append(fn)
                    continue

                fn_normed = (
                    fn
                    if repo_root is None
                    else relpath(join(repo_root, fn), start=repo_root)
                )
                if fn_normed.startswith("../"):
                    raise ValueError(f"{fn} not found inside {repo_root}")
                if repo_root is not None and not isfile(
                    join(repo_root, prod_name, fn_normed)
                ):
                    raise FileNotFoundError(
                        f"Missing options file: " f"{join(prod_name, fn_normed)!r}",
                    )
                normalised_options.append(
                    join("$ANALYSIS_PRODUCTIONS_BASE", prod_name, fn_normed)
                )
            options["files"] = normalised_options
        return options


class APConfiguration(RootModel):

    root: dict[APJobName, APJob]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    @model_validator(mode="before")
    def convert_data(cls, data: dict) -> Self:
        # pop checks (FIXME)
        _: dict[str, Any] = data.pop("checks", {})
        # propagate defaults to each job
        defaults: dict[str, Any] = data.pop("defaults", {})
        for job_name in data.keys():
            data[job_name] = {**defaults, **data[job_name]}

        # evaluate recipe expansions
        job_keys = list(data.keys())  # Create a copy to avoid iteration issues

        for job_name in job_keys:
            if "recipe" in data[job_name] and data[job_name]["recipe"] is not None:
                # validate the recipe and then update the model with
                # the recipe expansion
                recipe_data = data[job_name]["recipe"]
                recipe_adapter = TypeAdapter(AllRecipes)
                validated_recipe = recipe_adapter.validate_python(recipe_data)

                # Check for the appropriate configuration method
                updated = validated_recipe.configured(data[job_name])

                if len(updated) == 1:
                    data[job_name] = updated[0]
                    # Remove the recipe field since it's been processed
                    if "recipe" in data[job_name]:
                        del data[job_name]["recipe"]
                else:
                    del data[job_name]
                    for i, update in enumerate(updated):
                        new_key = f"{job_name}{update.get("append_name", i)}"
                        if "append_name" in update:
                            del update["append_name"]
                        # Remove the recipe field since it's been processed
                        if "recipe" in update:
                            del update["recipe"]
                        data[new_key] = update
        return data

    @model_validator(mode="after")
    def check_name_magnet_polarity(self, info: ValidationInfo):
        data = self.root
        for job_name in data.keys():
            if not isinstance(data[job_name].input, APJob.BKQueryInput):
                continue
            bk_query = data[job_name].input.bk_query

            match = re.search(r"-mag(up|down)[-/]", bk_query)
            if not match:
                return self
            good_pol = match.groups()[0]
            bad_pol = {"down": "up", "up": "down"}[good_pol]
            if f"mag{bad_pol}" in job_name:
                raise ValueError(
                    f"Found 'mag{bad_pol}' in job name {job_name!r} with"
                    f"'mag{good_pol}' input ({bk_query!r}). "
                    "Has the wrong magnet polarity been used?"
                )
            match = re.search(r"([^a-z0-9]|\b)m(u|d)([^a-z0-9]|\b)", job_name)
            if match and match.groups()[1] == bad_pol[0]:
                raise ValueError(
                    f"Found 'm{bad_pol[0]}' in job name {job_name!r} with"
                    f" 'mag{good_pol}' input ({bk_query!r}). "
                    "Has the wrong magnet polarity been used?"
                )

        return self

    @model_validator(mode="after")
    def check_job_names_and_completion(self):
        jobs_data = self.root
        # Ensure job name inputs are unambiguous
        for job_name, job_data in jobs_data.items():
            if isinstance(job_data.input, APJob.JobInput):
                if job_data.input.job_name not in jobs_data:
                    raise ValueError(
                        f"Unrecognised job name in input: {job_data.input.job_name}"
                    )
                input_job_data = jobs_data[job_data.input.job_name]
                input_filetype = (job_data.input.filetype or "").upper()
                if len(input_job_data.output) == 1:
                    if input_filetype not in [""] + input_job_data.output:
                        raise ValueError(
                            f"Unrecognised {input_filetype=} for {job_name=} input, "
                            f"expected one of: {input_job_data['output']}"
                        )
                elif input_filetype == "":
                    raise ValueError(
                        f"{job_name} gets its input from a job with multiple outputs. "
                        "The 'filetype' key must be specified in the 'input' section."
                    )
                elif input_filetype.upper() not in input_job_data.output:
                    raise ValueError(
                        f"Unrecognised {input_filetype=} for {job_name=} input, "
                        f"expected one of: {input_job_data['output']}"
                    )
        return self


def _ordered_dict_to_dict(a):
    if isinstance(a, (OrderedDict, dict)):
        return {k: _ordered_dict_to_dict(v) for k, v in a.items()}
    elif isinstance(a, (list, tuple)):
        return [_ordered_dict_to_dict(v) for v in a]
    else:
        return a


def render_yaml(raw_yaml):
    """Render a "raw" YAML jinja template.

    Accepts LbAP yaml configuration jinja template and renders it into a full YAML configuration.

    Args:
        raw_yaml (str): YAML jinja-template string

    Raises:
        ValueError: raised if jinja2 couldn't render the raw_yaml string.

    Returns:
        str: a jinja-rendered YAML string.
    """
    try:
        rendered_yaml = jinja2.Template(
            raw_yaml, undefined=jinja2.StrictUndefined
        ).render()
    except jinja2.TemplateError as e:
        raise ValueError(
            "Failed to render with jinja2 on line %s: %s"
            % (getattr(e, "lineno", "unknown"), e)
        ) from e
    return rendered_yaml


def validate_yaml(jobs_data, repo_root, prod_name):
    """Validate YAML configuration for anything that would definitely break a job or the production.

    Args:
        jobs_data (dict): Parsed job configuration.
        repo_root (str): Repository location.
        prod_name (str): Production name.

    Raises:
        ValueError: Raised if there are showstopper issues in the parsed job configuration.
    """

    # same as parse_yaml.
    pass


def _validate_proc_pass_map(job_names, proc_pass_map):
    """Build processing paths and validate them from a processing pass map.

    Given a list of step job names (in correct order), and the processing pass map,
    build the processing path for each step and verify the length is below 100.

    Args:
        job_names (list[str]): a list containing step job names.
        proc_pass_map (dict): A dictionary mapping job names to processing pass

    Raises:
        ValueError: raised if the processing path length is over 100 characters
    """
    for i, job_name in enumerate(job_names):
        proc_passes = map(proc_pass_map.get, job_names[:i] + [job_name])
        pro_path = "/".join(proc_passes)
        if len(pro_path) >= 100:
            proc_pass = proc_pass_map[job_name]
            step_jobs_list = "  - " + "\n  - ".join(job_names)
            raise ValueError(
                f"The expected processing path length for the job {job_name!r} is too long.\n"
                "DIRAC requires this to be less than 100 characters.\n\n"
                f"'Step' jobs:\n{step_jobs_list!r}\n"
                f"Job name: {job_name!r}\n"
                f"Processing pass for this step: {proc_pass!r}\n"
                f"Processing path for this step ({len(pro_path)} chars): {pro_path}\n\n"
                "To recover from this issue, consider:"
                "  - Removing redundant information from your job name.\n"
                "  - Shortening your job names.\n"
                "  - If the offending job depends on output from other jobs, ensure that they have a common prefix.\n"
            )


def create_proc_pass_map(job_names, version, default_proc_pass="default"):
    """Create a job name to processing pass map.

    Given a list of step job names and the production version, produce a
    job_name --> processing pass mapping.

    Args:
        job_names (list): step job names
        version (str): LbAPproduction version
        default_proc_pass (str, optional): the default processing pass. Defaults to "default".

    Returns:
        dict: a step job name to processing pass map
    """
    proc_pass_prefix = f"AnaProd-{version}-"
    proc_pass_map = {}

    # dummy_version = "v0r0p00000000"

    def clean_proc_pass(i, original_job_name):
        # attempt to remove redundant information from the job name
        job_name = re.sub(
            r"([0-9]{8})|(MagUp|MagDown|MU|MD)|((^|[^0*9])201[125678]($|[^0*9]))",
            "",
            original_job_name,
        )
        # Remove repeated separator chatacters
        job_name = re.sub(r"([-_])[-_]+", r"\1", job_name).strip("_-")
        if i == 0:
            return f"{proc_pass_prefix}{job_name}"

        proc_pass = job_name
        for previous_job_name in job_names[:i]:
            size = 0
            previous_proc_pass = proc_pass_map[previous_job_name]
            # Remove the prefix if this is the first job
            if previous_proc_pass.startswith(proc_pass_prefix):
                previous_proc_pass = previous_proc_pass[len(proc_pass_prefix) :]
            # Look for a common prefix and remove it
            for last, this in zip(previous_proc_pass, proc_pass):
                if last != this:
                    break
                size += 1
            proc_pass = proc_pass[size:].strip("_-+")
            # If the processing pass has been entirely stripped use a default
            if not proc_pass:
                proc_pass = default_proc_pass

        return proc_pass

    for i, job_name in enumerate(job_names):
        proc_pass_map[job_name] = clean_proc_pass(i, job_name)

    _validate_proc_pass_map(job_names, proc_pass_map)

    return proc_pass_map


def is_simulation_job(prod_data: dict, job_name: str):
    """Determine if a job is using MC input or not.

    Args:
        prod_data (dict): Entire production information from yaml parsing
        job_name (str): Name of the job to determine if it's using MC input or not

    Raises:
        NotImplementedError: No bookkeeping location or job name provided.

    Returns:
        bool: True if the job is using MC input, False if it is not
    """
    job_dict = prod_data[job_name]
    if "simulation" not in job_dict:
        if "bk_query" in job_dict["input"]:
            if "/mc/" in job_dict["input"]["bk_query"].lower():
                return True
            else:
                return False
        elif "job_name" in job_dict["input"]:
            dependent_job = prod_data[job_name]["input"]["job_name"]
            return is_simulation_job(prod_data, dependent_job)
        else:
            raise NotImplementedError(
                "Input requires either a bookkeeping location or a previous job name"
            )


def format_validation_error(error, model_class=None):
    """
    Format a Pydantic validation error with enhanced field information.

    Args:
        error: The ValidationError from Pydantic
        model_class: The model class for additional context

    Returns:
        str: A formatted error message with field documentation
    """
    from pydantic import ValidationError

    if not isinstance(error, ValidationError):
        return str(error)

    formatted_errors = []
    for error_dict in error.errors():
        field_path = " -> ".join(str(loc) for loc in error_dict["loc"])
        error_msg = error_dict["msg"]
        error_type = error_dict["type"]

        # Try to get field information from the model
        field_info = ""
        if model_class and hasattr(model_class, "model_fields"):
            try:
                field_name = error_dict["loc"][0] if error_dict["loc"] else None
                if field_name and field_name in model_class.model_fields:
                    field = model_class.model_fields[field_name]
                    if hasattr(field, "title") and field.title:
                        field_info += f"\n  Field: {field.title}"
                    if hasattr(field, "description") and field.description:
                        field_info += f"\n  Description: {field.description}"
                    if hasattr(field, "examples") and field.examples:
                        examples = ", ".join(str(ex) for ex in field.examples[:3])
                        field_info += f"\n  Examples: {examples}"
            except (IndexError, KeyError, AttributeError):
                pass

        formatted_error = (
            f"❌ {field_path}: {error_msg} (type={error_type}){field_info}"
        )
        formatted_errors.append(formatted_error)

    return (
        f"Configuration validation failed with {len(formatted_errors)} error(s):\n\n"
        + "\n\n".join(formatted_errors)
        + "\n\n📖 For complete documentation, see: https://lhcb-ap.docs.cern.ch/"
    )


def parse_yaml(rendered_yaml, prod_name=None, repo_root=None):
    """Parse rendered YAML text.

    Args:
        rendered_yaml (str): The rendered YAML jinja template.
        prod_name (str, optional): Production name for context.
        repo_root (str, optional): Repository root path for context.

    Raises:
        ValueError: raised if errors occurred during parsing, with enhanced error messages.

    Returns:
        dict: a validated configuration data dictionary.
    """
    from pydantic import ValidationError

    try:
        py_object = yaml.load(rendered_yaml, Loader=yaml.BaseLoader)
        data = APConfiguration.model_validate(
            py_object,
            context={
                "prod_name": prod_name,
                "repo_root": repo_root,
            },
        )
        return data.model_dump(exclude_none=True)
    except ValidationError as e:
        # Provide enhanced error message with field documentation
        enhanced_error = format_validation_error(e, APConfiguration)
        raise ValueError(enhanced_error) from e
    except yaml.YAMLError as e:
        # Provide enhanced YAML error information
        error_msg = f"❌ YAML parsing failed: {str(e)}\n"

        # Add context-specific hints based on the error type and message
        hints = []

        # General YAML best practices
        hints.extend(
            [
                "💡 Common YAML rules:",
                "  - Use spaces (not tabs) for indentation",
                "  - Maintain consistent indentation levels",
                "  - Use quotes for strings with special characters",
                "  - End files with a newline",
                "  - Check for trailing spaces",
            ]
        )

        if hints:
            error_msg += "\n" + "\n".join(hints) + "\n"

        error_msg += (
            "\n📖 For YAML syntax help, see:\n"
            "   • LbAP Documentation: https://lhcb-ap.docs.cern.ch/user_guide/yaml_sub_keys.html\n"
            "   • YAML Specification: https://yaml.org/spec/\n"
        )

        raise ValueError(error_msg) from e


def validate_yaml_with_enhanced_errors(yaml_content, prod_name=None, repo_root=None):
    """
    Validate YAML configuration with enhanced error reporting.

    This is a wrapper around parse_yaml that provides additional context
    and formatting for validation errors.

    Args:
        yaml_content (str): Raw YAML content to validate
        prod_name (str, optional): Production name for context
        repo_root (str, optional): Repository root for context

    Returns:
        dict: Validated configuration

    Raises:
        ValueError: Enhanced validation error with field documentation
    """
    try:
        rendered = render_yaml(yaml_content)
        return parse_yaml(rendered, prod_name, repo_root)
    except ValueError as e:
        # Add additional context for common errors
        error_msg = str(e)

        # Add helpful hints for common mistakes
        hints = []
        if "working group" in error_msg.lower() or "'wg'" in error_msg:
            available_wgs = [wg.value for wg in WorkingGroup]
            hints.append(
                f"💡 Available working groups: {', '.join(available_wgs[:10])}{'...' if len(available_wgs) > 10 else ''}"
            )

        if "inform" in error_msg.lower():
            hints.append(
                "💡 The 'inform' field requires CERN usernames (lowercase letters only), not email addresses"
            )

        if "bk_query" in error_msg.lower():
            hints.append(
                "💡 Bookkeeping paths should start with '/' and follow the standard BK path format"
            )

        if hints:
            error_msg += "\n\n" + "\n".join(hints)

        raise ValueError(error_msg) from e
