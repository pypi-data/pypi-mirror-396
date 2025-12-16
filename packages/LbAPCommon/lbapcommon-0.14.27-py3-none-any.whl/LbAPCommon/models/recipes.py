###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from itertools import product
from typing import Literal

from pydantic import BaseModel, Field


def expand_dict(data: dict):
    """Expand a dictionary where values can be strings or lists into multiple dictionaries."""
    # Convert all values to lists for uniform processing
    data = {k: [v] if not isinstance(v, list) else v for k, v in data.items()}

    # Get all keys that have multiple values (lists with more than one element)
    list_keys = [k for k, v in data.items() if len(v) > 1]

    if not list_keys:
        # No lists to expand, return single dictionary with first values
        return [{k: v[0] for k, v in data.items()}]

    # Generate all combinations of the list values
    result = []

    for combination in product(*[data[k] for k in list_keys]):
        # Create a new dictionary with the current combination
        expanded = {}
        for k, v in data.items():
            if k in list_keys:
                # Use the value from the current combination
                expanded[k] = combination[list_keys.index(k)]
            else:
                # Use the single value (first element of the list)
                expanded[k] = v[0]
        result.append(expanded)

    return result


class SplittingRecipe(BaseModel):
    name: Literal["split-trees"]

    class SplitHow(BaseModel):
        key: str = Field(
            title="Key pattern.",
            description="Any object inside the ROOT file matching this regular expression would be selected to be saved.",
            examples=["Tuple_SpruceSLB_(Bc).*?/DecayTree"],
        )
        into: str = Field(
            title="File to save matching keys into.",
            description=(
                "The output file type without an extension. Should be lowercase. "
                "For example: 'BC.ROOT' would save any key names matching the 'key' regular expression into 'BC.ROOT'."
            ),
            pattern=r"[A-Z][A-Z0-9]+\.ROOT",
            examples=["BC", "RIGHTSIGN"],
        )

    split: list[SplitHow]

    def configured(self, v):
        def transform_into(split_into):
            return split_into.lower().removesuffix(".root")

        return [
            {
                **v,
                "application": "lb-conda/default/2025-11-06",
                "options": {
                    "entrypoint": "LbExec:skim_and_merge",
                    "extra_options": {
                        "compression": {
                            "optimise_baskets": False,
                        },
                    },
                    "extra_args": [
                        "--",
                        *[
                            f"--write={transform_into(split.into)}={split.key}"
                            for split in self.split
                        ],
                    ],
                },
                "output": [split.into for split in self.split],
            }
        ]


class FilteringRecipe(BaseModel):
    name: Literal["filter-trees"]
    entrypoint: str = Field(
        title="Entrypoint",
        description="Which filtering entrypoint to run.",
        examples=["MyAnalysis.filter_script:run_preselection"],
    )

    def configured(self, v):
        return [
            {
                **v,
                "application": "lb-conda/default/2025-11-06",
                "options": {
                    "entrypoint": self.entrypoint,
                    "extra_options": {
                        "compression": {
                            "optimise_baskets": False,
                        },
                    },
                },
            }
        ]


class ExpandBKPath(BaseModel):
    """
    A recipe to expand the provided BK path elements into multiple jobs.

    Use format strings in the path to mark where you would like the substitutions to go.

        recipe:
          - name: "expand"
            path: "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
            substitute:
                polarity: ["MagUp", "MagDown"]
                sprucing: ["24c3", "24c2"]
                stream: "94000000"

    generates 4 jobs for each BK path:

    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c3/94000000/CHARM.DST"
    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagUp/Real Data/Sprucing24c2/94000000/CHARM.DST"

    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c3/94000000/CHARM.DST"
    "/LHCb/Collision24/Beam6800GeV-VeloClosed-MagDown/Real Data/Sprucing24c2/94000000/CHARM.DST"

    """

    name: Literal["expand"]

    path: str = Field(
        title="BK path",
        description="The BK path to expand.",
        examples=[
            "/LHCb/Collision24/Beam6800GeV-VeloClosed-{polarity}/Real Data/Sprucing{sprucing}/{stream}/CHARM.DST"
        ],
    )
    substitute: dict[str, list[str] | str]

    def configured(self, v):
        expanded_dicts = expand_dict(self.substitute)
        return [
            {
                **v,
                "append_name": f"_{'_'.join(expanded_dict.values())}",
                "input": {
                    **v.get("input", {}),
                    "bk_query": self.path.format(**expanded_dict),
                },
            }
            for expanded_dict in expanded_dicts
        ]


AllRecipes = SplittingRecipe | FilteringRecipe | ExpandBKPath
