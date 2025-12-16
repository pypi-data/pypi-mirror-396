###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from copy import deepcopy
from textwrap import dedent

import pytest
import yaml

from LbAPCommon.models import parse_yaml, validate_yaml

OPTIONAL_KEYS = [
    "root_in_tes",
    "simulation",
    "luminosity",
    "data_type",
    "input_type",
    "dddb_tag",
    "conddb_tag",
    "comment",
]


def test_good_no_defaults():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: cernuser
        priority: 1a
        completion_percentage: 99.5
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py", "$VAR/a.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 99.5


@pytest.mark.parametrize(
    "input_runs,expected_runs,expected_start_run,expected_end_run",
    [
        (["1234:1238"], None, 1234, 1238),
        (["1234:1238", "1240"], ["1234:1238", "1240"], None, None),
    ],
)
def test_good_runs(input_runs, expected_runs, expected_start_run, expected_end_run):
    runs = "".join([f"\n             - {run}" for run in input_runs])
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            runs: {runs}
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    if expected_runs is None:
        assert "runs" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["runs"] == expected_runs
    if expected_start_run is None:
        assert "start_run" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["start_run"] == expected_start_run
    if expected_end_run is None:
        assert "end_run" not in jobs_data["job_1"]["input"]
    else:
        assert jobs_data["job_1"]["input"]["end_run"] == expected_end_run


@pytest.mark.parametrize("key", ["start_run", "end_run"])
def test_good_run_limit(key):
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            {key}: 42
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["input"][key] == 42
    other_key = {"start_run": "end_run", "end_run": "start_run"}[key]
    assert other_key not in jobs_data["job_1"]["input"]


@pytest.mark.parametrize("key", ["start_run", "end_run"])
def test_bad_runs_and_limit(key):
    rendered_yaml = dedent(
        f"""\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            runs:
                - 1234:1238
            {key}: 1237
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    with pytest.raises(
        ValueError,
        match="Either use `start_run` and `end_run`, or use `runs` - can't use both.",
    ):
        parse_yaml(rendered_yaml)


def test_bad_end_run():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
            start_run: 42
            end_run: 41
        output: FILETYPE.ROOT
        options:
            - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
    """
    )
    with pytest.raises(ValueError, match="must be less than end run"):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("FILETYPE.ROOT", ["FILETYPE.ROOT"]),
        ("filetype.root", ["FILETYPE.ROOT"]),
        ("filetype.ROOT", ["FILETYPE.ROOT"]),
        ("\n        - filetype.ROOT", ["FILETYPE.ROOT"]),
        (
            "\n        - filetype.ROOT\n        - filetype.dst",
            ["FILETYPE.ROOT", "FILETYPE.DST"],
        ),
    ],
)
def test_good_output_filetype_scalar(value, expected):
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: {value}
        options:
            - $VAR/a.py
        wg: Charm
        inform: cernuser
    """.format(
            value=value
        )
    )
    jobs_data = parse_yaml(rendered_yaml)
    validate_yaml(jobs_data, "a", "b")
    assert len(jobs_data) == 1

    assert jobs_data["job_1"]["output"] == expected

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["options"] == {"files": ["$VAR/a.py"]}
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]


def test_good_with_defaults():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        inform:
            - cernuser
        priority: 1a
        completion_percentage: 95.6
        comment: This production will produce tuples of a, b, c decays for the x analysis in the y working group

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser
        priority: 2a
        completion_percentage: 87.35
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 2

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 95.6
    assert (
        jobs_data["job_1"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]
    assert jobs_data["job_2"]["priority"] == "2a"
    assert jobs_data["job_2"]["completion_percentage"] == 87.35
    assert (
        jobs_data["job_2"]["comment"]
        == "This production will produce tuples of a, b, c decays for the x analysis in the y working group"
    )


def test_good_all_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: yes
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: no
        options:
            - options.py
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is True
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is True
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is False
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]


def test_good_some_turbo():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    for key in OPTIONAL_KEYS:
        for job in ["job_1", "job_2", "job_3"]:
            assert key not in jobs_data[job]


def test_good_automatically_configure_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    for key in OPTIONAL_KEYS:
        assert key not in jobs_data["job_1"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Charm"
    assert jobs_data["job_3"]["simulation"] is True
    assert jobs_data["job_3"]["luminosity"] is False
    assert jobs_data["job_3"]["data_type"] == "2018"
    assert jobs_data["job_3"]["input_type"] == "DST"
    assert jobs_data["job_3"]["dddb_tag"] == "xyz-234"
    assert jobs_data["job_3"]["conddb_tag"] == "abc-def-20u"


def test_good_automatically_configure_defaults_overrides():
    rendered_yaml = dedent(
        """\
    defaults:
        wg: Charm
        automatically_configure: yes
        turbo: no
        inform:
            - cernuser
        root_in_tes: "/Event/Charm"
        simulation: yes
        luminosity: no
        data_type: "2018"
        input_type: "DST"
        dddb_tag: "xyz-234"
        conddb_tag: "abc-def-20u"

    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - options.py

    job_2:
        application: DaVinci/v44r0
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        options:
            - other_options.py
        wg: B2OC
        automatically_configure: false
        inform:
            - cernuser

    job_3:
        application: DaVinci/v45r3
        input:
            bk_query: "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        output: FILETYPE.ROOT
        turbo: yes
        options:
            - options.py
        root_in_tes: "/Event/Other"
        simulation: no
        luminosity: yes
        data_type: "2017"
        input_type: "MDST"
        dddb_tag: "tuv-345"
        conddb_tag: "ghj-20z"
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 3

    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is True
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]

    assert jobs_data["job_2"]["application"] == "DaVinci/v44r0"
    assert jobs_data["job_2"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagUp/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_2"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_2"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/other_options.py"]
    }
    assert jobs_data["job_2"]["wg"] == "B2OC"
    assert jobs_data["job_2"]["automatically_configure"] is False
    assert jobs_data["job_2"]["turbo"] is False
    assert jobs_data["job_2"]["inform"] == ["cernuser"]

    for job in ["job_1", "job_2"]:
        assert jobs_data[job]["root_in_tes"] == "/Event/Charm"
        assert jobs_data[job]["simulation"] is True
        assert jobs_data[job]["luminosity"] is False
        assert jobs_data[job]["data_type"] == "2018"
        assert jobs_data[job]["input_type"] == "DST"
        assert jobs_data[job]["dddb_tag"] == "xyz-234"
        assert jobs_data[job]["conddb_tag"] == "abc-def-20u"

    assert jobs_data["job_3"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_3"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_3"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_3"]["options"] == {
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]
    }
    assert jobs_data["job_3"]["wg"] == "Charm"
    assert jobs_data["job_3"]["automatically_configure"] is True
    assert jobs_data["job_3"]["turbo"] is True
    assert jobs_data["job_3"]["inform"] == ["cernuser"]

    assert jobs_data["job_3"]["root_in_tes"] == "/Event/Other"
    assert jobs_data["job_3"]["simulation"] is False
    assert jobs_data["job_3"]["luminosity"] is True
    assert jobs_data["job_3"]["data_type"] == "2017"
    assert jobs_data["job_3"]["input_type"] == "MDST"
    assert jobs_data["job_3"]["dddb_tag"] == "tuv-345"
    assert jobs_data["job_3"]["conddb_tag"] == "ghj-20z"


def test_good_gaudipython():
    rendered_yaml = dedent(
        """\
    job_1:
        application: DaVinci/v45r3
        input:
            bk_query: /MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            command:
                - python
            files:
                - options.py
        wg: Charm
        inform: cernuser
        priority: 1a
        completion_percentage: 99.5
    """
    )
    jobs_data = parse_yaml(rendered_yaml)
    assert len(jobs_data) == 1
    assert jobs_data["job_1"]["application"] == "DaVinci/v45r3"
    assert jobs_data["job_1"]["input"] == {
        "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST",
        "input_plugin": "default",
        "keep_running": True,
        "n_test_lfns": 1,
    }
    assert jobs_data["job_1"]["output"] == ["FILETYPE.ROOT"]
    assert jobs_data["job_1"]["options"] == {
        "command": ["python"],
        "files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"],
    }
    assert jobs_data["job_1"]["wg"] == "Charm"
    assert jobs_data["job_1"]["automatically_configure"] is False
    assert jobs_data["job_1"]["turbo"] is False
    assert jobs_data["job_1"]["inform"] == ["cernuser"]
    assert jobs_data["job_1"]["priority"] == "1a"
    assert jobs_data["job_1"]["completion_percentage"] == 99.5


@pytest.mark.parametrize(
    "missing_key", ["application", "input", "output", "wg", "inform"]
)
def test_bad_missing_key(missing_key):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    del data["job_1"][missing_key]
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(
        ValueError,
        match=rf"Configuration validation failed(.|\n)*❌ job_1 -> {missing_key}(.|\n)*Field required(.|\n)*type=missing",
    ):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "key,value",
    [
        ("application", "DaVinci"),
        ("input", "hello"),
        ("output", ""),
        ("wg", ""),
        ("inform", ""),
        ("automatically_configure", "null"),
        ("turbo", "absolutely"),
        ("root_in_tes", "DST"),
        ("simulation", "absolutely"),
        ("luminosity", "nope"),
        ("data_type", "MSDT"),
        ("input_type", "2016"),
        ("dddb_tag", ""),
        ("conddb_tag", ""),
        ("priority", "3a"),
    ],
)
def test_bad_invalid_value(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(
        ValueError,
        match=rf"Configuration validation failed(.|\n)*❌ job_1 -> {key}",
    ):
        parse_yaml(rendered_yaml)


@pytest.mark.parametrize(
    "key,value",
    [
        ("completion_percentage", "ninety-nine"),
        ("completion_percentage", 100.1),
        ("completion_percentage", -24.33),
        ("completion_percentage", 9.9),
    ],
)
def test_bad_invalid_completion_percentage(key, value):
    data = {
        "job_1": {
            "application": "DaVinci/v45r3",
            "input": {
                "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
            },
            "output": "FILETYPE.ROOT",
            "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
            "wg": "Charm",
            "inform": "cernuser",
        }
    }
    data["job_1"][key] = value
    rendered_yaml = yaml.safe_dump(data)
    with pytest.raises(ValueError):
        validate_yaml(*parse_yaml(rendered_yaml), "a", "b")


def test_completion_percentage_not_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
        "wg": "Charm",
        "inform": "cernuser",
    }
    data = {
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data = parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 100
    assert jobs_data["job_3"]["completion_percentage"] == 20


def test_completion_percentage_in_defaults():
    job_template = {
        "application": "DaVinci/v45r3",
        "input": {
            "bk_query": "/MC/2018/Beam6500GeV-2018-MagDown/Sim09g/Trig0x617d18a4/Reco18/24142001/ALLSTREAMS.DST"
        },
        "output": "FILETYPE.ROOT",
        "options": {"files": ["$ANALYSIS_PRODUCTIONS_BASE/options.py"]},
        "wg": "Charm",
        "inform": "cernuser",
    }
    data = {
        "defaults": {
            "completion_percentage": 50,
        },
        "job_1": deepcopy({**job_template, "completion_percentage": 100}),
        "job_2": deepcopy({**job_template}),
        "job_3": deepcopy({**job_template, "completion_percentage": 20}),
    }
    rendered_yaml = yaml.safe_dump(data)
    jobs_data = parse_yaml(rendered_yaml)
    assert jobs_data["job_1"]["completion_percentage"] == 100
    assert jobs_data["job_2"]["completion_percentage"] == 50
    assert jobs_data["job_3"]["completion_percentage"] == 20


# def test_filetype_validation():
#     from parsing import _normalise_filetype

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072_2016_MAGUP.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" in str(excinfo.value)
#     assert "magnet polarity" in str(excinfo.value)
#     assert "data taking year" in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_26265072.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" in str(excinfo.value)
#     assert "magnet polarity" not in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "XICPS_MC_MagDown.ROOT")
#     assert "is excessively long" not in str(excinfo.value)
#     assert "event type" not in str(excinfo.value)
#     assert "magnet polarity" in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     with pytest.raises(ValueError) as excinfo:
#         _normalise_filetype("PROD", "JOB", "A" * 100)
#     assert "is excessively long" in str(excinfo.value)
#     assert "event type" not in str(excinfo.value)
#     assert "magnet polarity" not in str(excinfo.value)
#     assert "data taking year" not in str(excinfo.value)

#     assert _normalise_filetype("PROD", "JOB", "XICPS_MC.ROOT") == "XICPS_MC.ROOT"
#     assert _normalise_filetype("PROD", "JOB", "xicps_mc.root") == "XICPS_MC.ROOT"


def test_split_trees_recipe():
    """Test that the split-trees recipe works correctly with APConfiguration model validation."""
    rendered_yaml = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    analysis_job:
        options:
            entrypoint: test_analysis.script:main_function
        input:
            bk_query: "/LHCb/Collision25/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing25c3/94000000/B2OC.DST"
            sample_fraction: 0.05
            keep_running: true
            n_test_lfns: 1

    analysis_job_split:
        input:
            job_name: "analysis_job"
        recipe:
            name: "split-trees"
            split:
                - key: "Bu2D0pip_.*?/DecayTree"
                  into: "BU2D0PI.ROOT"
                - key: "Bu2D0Kp_.*?/DecayTree"
                  into: "BU2D0K.ROOT"
                - key: ".*_D02KSLL.*?/DecayTree"
                  into: "KSLL.ROOT"
                - key: ".*_D02KSDD.*?/DecayTree"
                  into: "KSDD.ROOT"
                - key: ".*pipim/DecayTree"
                  into: "PIPI.ROOT"
                - key: ".*piKm/DecayTree"
                  into: "PIKM.ROOT"
                - key: ".*Kpim/DecayTree"
                  into: "KPIM.ROOT"
                - key: ".*KKm/DecayTree"
                  into: "KK.ROOT"
    """
    )

    # This should not raise any validation errors
    jobs_data = parse_yaml(rendered_yaml)

    # Check that we have the expected jobs
    assert len(jobs_data) == 2
    assert "analysis_job" in jobs_data
    assert "analysis_job_split" in jobs_data

    # Check the original analysis job
    analysis_job = jobs_data["analysis_job"]
    assert analysis_job["application"] == "DaVinci/v66r5"
    assert analysis_job["output"] == ["DATA.ROOT"]
    assert analysis_job["wg"] == "DPA"
    assert analysis_job["inform"] == ["testuser"]
    assert analysis_job["options"]["entrypoint"] == "test_analysis.script:main_function"

    # Check the splitting job (recipe has been processed, so check the transformed job)
    split_job = jobs_data["analysis_job_split"]
    assert split_job["input"]["job_name"] == "analysis_job"

    # After recipe processing, the job should be transformed
    assert split_job["application"] == "lb-conda/default/2025-11-06"
    assert split_job["options"]["entrypoint"] == "LbExec:skim_and_merge"

    # Check that extra_args contains the split commands
    extra_args = split_job["options"]["extra_args"]
    assert "--" in extra_args
    assert any("--write=bu2d0pi=Bu2D0pip_.*?/DecayTree" in arg for arg in extra_args)
    assert any("--write=bu2d0k=Bu2D0Kp_.*?/DecayTree" in arg for arg in extra_args)

    # Check output files have been set correctly
    expected_outputs = [
        "BU2D0PI.ROOT",
        "BU2D0K.ROOT",
        "KSLL.ROOT",
        "KSDD.ROOT",
        "PIPI.ROOT",
        "PIKM.ROOT",
        "KPIM.ROOT",
        "KK.ROOT",
    ]
    assert split_job["output"] == expected_outputs

    # Check that there's no recipe field left (it should be consumed)
    assert "recipe" not in split_job


def test_split_trees_recipe_validation_errors():
    """Test that split-trees recipe validation catches common errors."""

    # Test invalid 'into' field (should be uppercase with .ROOT extension)
    rendered_yaml_invalid_into = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    analysis_job:
        options:
            entrypoint: test_analysis.script:main_function
        input:
            bk_query: "/LHCb/Collision25/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing25c3/94000000/B2OC.DST"

    analysis_job_split:
        input:
            job_name: "analysis_job"
        recipe:
            name: "split-trees"
            split:
                - key: "Bu2D0pip_.*?/DecayTree"
                  into: "bu2d0pi.root"  # Invalid: should be uppercase with .ROOT
    """
    )

    with pytest.raises(ValueError, match="String should match pattern"):
        parse_yaml(rendered_yaml_invalid_into)

    # Test missing required fields
    rendered_yaml_missing_key = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    analysis_job:
        options:
            entrypoint: test_analysis.script:main_function
        input:
            bk_query: "/LHCb/Collision25/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing25c3/94000000/B2OC.DST"

    analysis_job_split:
        input:
            job_name: "analysis_job"
        recipe:
            name: "split-trees"
            split:
                - into: "BU2D0PI.ROOT"  # Missing 'key' field
    """
    )

    with pytest.raises(ValueError, match="Field required"):
        parse_yaml(rendered_yaml_missing_key)


def test_split_trees_recipe_configured_method():
    """Test that the split-trees recipe configured method works correctly."""
    from LbAPCommon.models.recipes import SplittingRecipe

    # Create a splitting recipe instance
    recipe_data = {
        "name": "split-trees",
        "split": [
            {"key": "Bu2D0pip_.*?/DecayTree", "into": "BU2D0PI.ROOT"},
            {"key": "Bu2D0Kp_.*?/DecayTree", "into": "BU2D0K.ROOT"},
        ],
    }

    recipe = SplittingRecipe.model_validate(recipe_data)

    # Test job configuration
    job_config = {
        "application": "DaVinci/v66r5",
        "wg": "DPA",
        "inform": ["testuser"],
        "input": {"job_name": "analysis_job"},
    }

    configured_jobs = recipe.configured(job_config)

    # Should return a list with one configured job
    assert len(configured_jobs) == 1
    configured_job = configured_jobs[0]

    # Check that the recipe modified the job configuration correctly
    assert configured_job["application"] == "lb-conda/default/2025-11-06"
    assert configured_job["options"]["entrypoint"] == "LbExec:skim_and_merge"

    # Check extra_args contains the split commands
    extra_args = configured_job["options"]["extra_args"]
    assert "--" in extra_args
    assert "--write=bu2d0pi=Bu2D0pip_.*?/DecayTree" in extra_args
    assert "--write=bu2d0k=Bu2D0Kp_.*?/DecayTree" in extra_args

    # Check output files
    assert configured_job["output"] == ["BU2D0PI.ROOT", "BU2D0K.ROOT"]

    # Check that original job config is preserved
    assert configured_job["wg"] == "DPA"
    assert configured_job["inform"] == ["testuser"]
    assert configured_job["input"] == {"job_name": "analysis_job"}


def test_filter_trees_recipe():
    """Test that the filter-trees recipe works correctly with APConfiguration model validation."""
    rendered_yaml = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    analysis_job:
        options:
            entrypoint: test_analysis.script:main_function
        input:
            bk_query: "/LHCb/Collision25/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing25c3/94000000/B2OC.DST"
            sample_fraction: 0.05
            keep_running: true
            n_test_lfns: 1

    filter_job:
        input:
            job_name: "analysis_job"
        recipe:
            name: "filter-trees"
            entrypoint: "MyAnalysis.filter_script:run_preselection"
    """
    )

    # This should not raise any validation errors
    jobs_data = parse_yaml(rendered_yaml)

    # Check that we have the expected jobs
    assert len(jobs_data) == 2
    assert "analysis_job" in jobs_data
    assert "filter_job" in jobs_data

    # Check the original analysis job
    analysis_job = jobs_data["analysis_job"]
    assert analysis_job["application"] == "DaVinci/v66r5"
    assert analysis_job["output"] == ["DATA.ROOT"]
    assert analysis_job["wg"] == "DPA"
    assert analysis_job["inform"] == ["testuser"]
    assert analysis_job["options"]["entrypoint"] == "test_analysis.script:main_function"

    # Check the filtering job (recipe has been processed, so check the transformed job)
    filter_job = jobs_data["filter_job"]
    assert filter_job["input"]["job_name"] == "analysis_job"

    # After recipe processing, the job should be transformed
    assert filter_job["application"] == "lb-conda/default/2025-11-06"
    assert (
        filter_job["options"]["entrypoint"]
        == "MyAnalysis.filter_script:run_preselection"
    )

    # Check extra_options
    extra_options = filter_job["options"]["extra_options"]
    assert "compression" in extra_options
    assert extra_options["compression"]["optimise_baskets"] is False

    # Check that there's no recipe field left (it should be consumed)
    assert "recipe" not in filter_job


def test_filter_trees_recipe_validation_errors():
    """Test that filter-trees recipe validation catches common errors."""

    # Test missing entrypoint field
    rendered_yaml_missing_entrypoint = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    analysis_job:
        options:
            entrypoint: test_analysis.script:main_function
        input:
            bk_query: "/LHCb/Collision25/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing25c3/94000000/B2OC.DST"

    filter_job:
        input:
            job_name: "analysis_job"
        recipe:
            name: "filter-trees"
            # Missing entrypoint field
    """
    )

    with pytest.raises(ValueError, match="Field required"):
        parse_yaml(rendered_yaml_missing_entrypoint)


def test_filter_trees_recipe_configured_method():
    """Test that the filter-trees recipe configured method works correctly."""
    from LbAPCommon.models.recipes import FilteringRecipe

    # Create a filtering recipe instance
    recipe_data = {
        "name": "filter-trees",
        "entrypoint": "MyAnalysis.filter_script:run_preselection",
    }

    recipe = FilteringRecipe.model_validate(recipe_data)

    # Test job configuration
    job_config = {
        "application": "DaVinci/v66r5",
        "wg": "DPA",
        "inform": ["testuser"],
        "input": {"job_name": "analysis_job"},
        "output": ["DATA.ROOT"],
    }

    configured_jobs = recipe.configured(job_config)

    # Should return a list with one configured job
    assert len(configured_jobs) == 1
    configured_job = configured_jobs[0]

    # Check that the recipe modified the job configuration correctly
    assert configured_job["application"] == "lb-conda/default/2025-11-06"
    assert (
        configured_job["options"]["entrypoint"]
        == "MyAnalysis.filter_script:run_preselection"
    )

    # Check extra_options
    extra_options = configured_job["options"]["extra_options"]
    assert "compression" in extra_options
    assert extra_options["compression"]["optimise_baskets"] is False

    # Check that original job config is preserved
    assert configured_job["wg"] == "DPA"
    assert configured_job["inform"] == ["testuser"]
    assert configured_job["input"] == {"job_name": "analysis_job"}
    assert configured_job["output"] == ["DATA.ROOT"]


def test_expand_bk_path_recipe():
    """Test that the expand recipe works correctly with APConfiguration model validation."""
    rendered_yaml = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA
        options:
            entrypoint: test_analysis.script:main_function

    base_job:
        input:
            bk_query: "placeholder"  # Will be replaced by recipe
            sample_fraction: 0.05
            keep_running: true
            n_test_lfns: 1
        recipe:
            name: "expand"
            path: "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
            substitute:
                polarity: ["MagUp", "MagDown"]
                sprucing: ["24c3", "24c2"]
                stream: "94000000"
    """
    )

    # This should not raise any validation errors
    jobs_data = parse_yaml(rendered_yaml)

    # Check that we have the expected expanded jobs (2 polarities × 2 sprucing versions = 4 jobs)
    assert len(jobs_data) == 4

    # Check that the expanded job names are correct
    expected_job_names = [
        "base_job_MagUp_24c3_94000000",
        "base_job_MagUp_24c2_94000000",
        "base_job_MagDown_24c3_94000000",
        "base_job_MagDown_24c2_94000000",
    ]

    for job_name in expected_job_names:
        assert job_name in jobs_data

    # Check configuration is preserved in all expanded jobs
    for _, job_data in jobs_data.items():
        assert job_data["application"] == "DaVinci/v66r5"
        assert job_data["output"] == ["DATA.ROOT"]
        assert job_data["wg"] == "DPA"
        assert job_data["inform"] == ["testuser"]
        assert job_data["options"]["entrypoint"] == "test_analysis.script:main_function"

        # Check that the BK query has been properly formatted
        bk_query = job_data["input"]["bk_query"]
        assert "/LHCb/Collision24/Beam6800GeV-VeloClosed-" in bk_query
        assert "/Real Data/Sprucing" in bk_query
        assert "/94000000/CHARM.DST" in bk_query

        # Check that there's no recipe field left (it should be consumed)
        assert "recipe" not in job_data

    # Check specific BK queries for a few jobs
    assert (
        jobs_data["base_job_MagUp_24c3_94000000"]["input"]["bk_query"]
        == "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c3/94000000/CHARM.DST"
    )
    assert (
        jobs_data["base_job_MagDown_24c2_94000000"]["input"]["bk_query"]
        == "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c2/94000000/CHARM.DST"
    )


def test_expand_bk_path_recipe_validation_errors():
    """Test that expand recipe validation catches common errors."""

    # Test missing path field
    rendered_yaml_missing_path = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    base_job:
        input:
            bk_query: "placeholder"
        options:
            entrypoint: test_analysis.script:main_function
        recipe:
            name: "expand"
            # Missing path field
            substitute:
                polarity: ["MagUp", "MagDown"]
    """
    )

    with pytest.raises(ValueError, match="Field required"):
        parse_yaml(rendered_yaml_missing_path)

    # Test missing substitute field
    rendered_yaml_missing_substitute = dedent(
        """\
    defaults:
        application: DaVinci/v66r5
        output: DATA.ROOT
        inform:
            - testuser
        wg: DPA

    base_job:
        input:
            bk_query: "placeholder"
        options:
            entrypoint: test_analysis.script:main_function
        recipe:
            name: "expand"
            path: "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
            # Missing substitute field
    """
    )

    with pytest.raises(ValueError, match="Field required"):
        parse_yaml(rendered_yaml_missing_substitute)


def test_expand_bk_path_recipe_configured_method():
    """Test that the expand recipe configured method works correctly."""
    from LbAPCommon.models.recipes import ExpandBKPath

    # Create an expand recipe instance
    recipe_data = {
        "name": "expand",
        "path": "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST",
        "substitute": {
            "polarity": ["MagUp", "MagDown"],
            "sprucing": ["24c3", "24c2"],
            "stream": "94000000",
        },
    }

    recipe = ExpandBKPath.model_validate(recipe_data)

    # Test job configuration
    job_config = {
        "application": "DaVinci/v66r5",
        "wg": "DPA",
        "inform": ["testuser"],
        "input": {
            "bk_query": "placeholder",
            "sample_fraction": 0.05,
        },
        "output": ["DATA.ROOT"],
        "options": {"entrypoint": "test_analysis.script:main_function"},
    }

    configured_jobs = recipe.configured(job_config)

    # Should return 4 jobs (2 polarities × 2 sprucing versions)
    assert len(configured_jobs) == 4

    # Check that each job has the correct BK path and append_name
    expected_combinations = [
        ("MagUp", "24c3"),
        ("MagUp", "24c2"),
        ("MagDown", "24c3"),
        ("MagDown", "24c2"),
    ]

    for i, (polarity, sprucing) in enumerate(expected_combinations):
        job = configured_jobs[i]

        # Check append_name
        expected_append = f"_{polarity}_{sprucing}_94000000"
        assert job["append_name"] == expected_append

        # Check BK path substitution
        expected_path = f"/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/94000000/CHARM.DST"
        assert job["input"]["bk_query"] == expected_path

        # Check that original job config is preserved
        assert job["application"] == "DaVinci/v66r5"
        assert job["wg"] == "DPA"
        assert job["inform"] == ["testuser"]
        assert job["output"] == ["DATA.ROOT"]
        assert job["options"]["entrypoint"] == "test_analysis.script:main_function"

        # Check that other input fields are preserved
        assert job["input"]["sample_fraction"] == 0.05


def test_expand_bk_path_recipe_single_value_substitute():
    """Test expand recipe with single string values in substitute."""
    from LbAPCommon.models.recipes import ExpandBKPath

    recipe_data = {
        "name": "expand",
        "path": "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST",
        "substitute": {
            "polarity": ["MagUp", "MagDown"],  # List
            "sprucing": "24c3",  # Single string
            "stream": "94000000",  # Single string
        },
    }

    recipe = ExpandBKPath.model_validate(recipe_data)

    job_config = {
        "application": "DaVinci/v66r5",
        "wg": "DPA",
        "inform": ["testuser"],
        "input": {"bk_query": "placeholder"},
        "output": ["DATA.ROOT"],
        "options": {"entrypoint": "test_analysis.script:main_function"},
    }

    configured_jobs = recipe.configured(job_config)

    # Should return 2 jobs (2 polarities, 1 sprucing, 1 stream)
    assert len(configured_jobs) == 2

    # Check the generated paths
    expected_paths = [
        "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c3/94000000/CHARM.DST",
        "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c3/94000000/CHARM.DST",
    ]

    for i, expected_path in enumerate(expected_paths):
        assert configured_jobs[i]["input"]["bk_query"] == expected_path
