# Create networks from publication records.
import json
from itertools import combinations
from pathlib import Path

import igraph as ig
import numpy as np
import pandas as pd
from tqdm import tqdm


def _json_default(o):
    # Make common non-JSON types serializable
    try:
        if isinstance(o, (np.integer, np.floating, np.bool_)):
            return o.item()
    except Exception:
        pass
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def _serialize_seq_attrs(seq):
    # seq is g.vs or g.es
    attrs = list(seq.attributes())
    for a in attrs:
        vals = seq[a]
        # If any value is not a GraphML primitive, serialize the entire column to JSON strings
        if any(not (v is None or isinstance(v, (bool, int, float, str))) for v in vals):
            seq[a] = [
                json.dumps(
                    v, default=_json_default, ensure_ascii=False, separators=(",", ":")
                )
                if v is not None
                else None
                for v in vals
            ]


def _serialize_graph_attrs(g: ig.Graph):
    for a in list(g.attributes()):
        v = g[a]
        if not (v is None or isinstance(v, (bool, int, float, str))):
            g[a] = json.dumps(
                v, default=_json_default, ensure_ascii=False, separators=(",", ":")
            )


def write_graphml_with_json(g: ig.Graph, path: Path):
    """Routine to JSON serialize entries in node or edge attributes."""
    _serialize_seq_attrs(g.vs)
    _serialize_seq_attrs(g.es)
    _serialize_graph_attrs(g)
    g.write_graphml(path.as_posix())


class CreateNetwork:
    """Create networks for co-author and co-country analysis

    Builds time-sliced networks from a dataframe of OpenAlex works (e.g., as
    produced by TransformOA). A time window can be defined as (year - window, year),
    e.g. (1960 - 5, 1960) -> (1955, 1960), to gather all entries for that range in
    one network.

    Expected dataframe columns:
        - publication_year: int
        - authorships: list of (author_id, [institution_ids]) for coauthor mode
        - countries: list[str] of ISO 3166-1 alpha-2 codes for cocountry mode


    :param dataframe: Source records to derive networks from.
    :type dataframe: pandas.DataFrame
    :param year_range: Inclusive (start_year, end_year) for filtering works.
    :type year_range: tuple[int, int]
    :param interval: Size of each time window in years. Defaults to 1.
    :type interval: int, optional
    :param out_path: Directory where network files/exports will be written.
    :type out_path: pathlib.Path, optional
    :param net_type: Network type to build: "coauthor" or "cocountry".
                        Defaults to "coauthor".
    :type net_type: str, optional
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        year_range: tuple,
        interval: int = 1,
        out_path: Path = Path("."),
        net_type: str = "coauthor",
    ):
        """Init class."""
        self.dataframe = dataframe
        self.year_range = year_range
        self.interval = interval
        self.out_path = out_path
        self.net_type = net_type

    def run(self) -> str:
        self._write_graphml()
        return "Done"

    def _create_edge(self, row: dict) -> list:
        """Create all co-author edges for a single publication record.

        Generates unordered author pairs (nC2) from the `authorships` field of the
        input row. Any author entries with missing/None IDs are ignored. Single-
        author publications yield no edges.

        Expected input structure:
            - row["authorships"]: list of (author_id, [institution_ids])

        where author_id may be str or None.

        Optional fields (copied into edge metadata if present):
            - row["id"], row["doi"], row["title"], row["type"],
            - row["publication_year"], row["countries"], row["topics"],
            - row["primary_location"], row["referenced_works"], etc.

        Returned edge format:
            - A list of tuples (author_u, author_v, metadata)

            where:
            - author_u: str — source author ID
            - author_v: str — target author ID
            - metadata: dict — publication-level attributes carried from `row`

        (contents depend on available keys)

        Notes:
            - Pairs are unique combinations (no self-pairs, order-independent).
            - Entries with missing author IDs are skipped.

        :param row: Publication record providing authorships and optional metadata.
        :type row: dict | pandas.Series
        :returns: List of co-author edges with metadata for the given publication.
        :rtype: list[tuple[str, str, dict]]
        :raises KeyError: If 'authorships' is missing from the input row.
        :raises TypeError: If 'authorships' is not iterable.
        """
        list_entry = []
        if self.net_type == "coauthor":
            key = "authorships"
        elif self.net_type == "cocountry":
            key = "countries"
        else:
            raise KeyError("Please select net_type equals coauthor or cocountry.")
        if len(row[key]) > 2:
            pairs = combinations(row[key], 2)
            for pair in pairs:
                if None not in pair:
                    # Handle different data structure of author and country entries
                    if self.net_type == "coauthor":
                        src = pair[0][0]
                        trg = pair[1][0]
                    else:
                        src = pair[0]
                        trg = pair[1]
                    list_entry.append(
                        (
                            src,
                            trg,
                            1,
                            row["id"],
                            row["title"],
                            int(row["publication_year"]),
                            row["topics"],
                        )
                    )
            return list_entry
        return []

    def _write_graphml(self):
        """Build rolling-window networks and export them to GraphML files.

        For each year in the inclusive range [year_range[0], year_range[1]], this
        method:

        1) Selects works with publication_year in [year - self.interval, year] (inclusive).
        2) Creates per-publication co-occurrence edges via `_create_edge(row)`.
        3) Flattens edges and aggregates by (source, target) to compute

        - weight: number of co-occurrences in the window,
        - paper: unique list of publication identifiers,
        - years: unique list of publication years,
        - topics: unique list aggregated across publications.

        4) Builds an igraph Graph and writes a GraphML file named f"{self.net_type}_{year}.graphml" to `self.out_path`.

        Expected dataframe columns and behavior:
            - publication_year: int; used for time-window filtering.
            - `_create_edge(row)` must return a list of tuples with the following order per edge: (source, target, weight, paper, title, years, topics)

            where:
                - source, target: author or country IDs (str-like),
                - weight: typically 1 per publication-level edge,
                - paper: publication/work identifier (e.g., OpenAlex ID),
                - title: publication title (not used in aggregation),
                - years: publication year (int),
                - topics: list of topic IDs.

            Single-actor rows should yield no edges.

        :returns: None
        :rtype: None
        :raises KeyError: If required dataframe columns are missing (e.g., publication_year)
                            or if `_create_edge` omits expected fields.
        :raises ValueError: If edge tuples do not match the expected shape/order.
        :raises ImportError: If igraph or required serialization utilities are missing.
        :raises OSError: For I/O errors while writing GraphML files.
        """
        for year in tqdm(range(self.year_range[0], self.year_range[1] + 1, 1)):
            entries = []
            for idx, row in self.dataframe.query(
                f"publication_year >= {year - self.interval} & publication_year <= {year}"
            ).iterrows():
                entries.append(self._create_edge(row))
            edges = [x for y in entries for x in y]
            dftemp = pd.DataFrame(
                edges,
                columns=[
                    "source",
                    "target",
                    "weight",
                    "paper",
                    "title",
                    "years",
                    "topics",
                ],
            )
            weighted_edges = []
            for idx, g0 in dftemp.groupby(["source", "target"]):
                weighted_edges.append(
                    (
                        idx[0],
                        idx[1],
                        g0.shape[0],
                        list(g0.paper.unique()),
                        list(g0.years.unique()),
                        list(set([x for y in list(g0.topics.values) for x in y])),
                    )
                )
            graph = ig.Graph.TupleList(
                weighted_edges, edge_attrs=["weight", "paper", "years", "topics"]
            )
            write_graphml_with_json(
                graph, self.out_path / f"{self.net_type}_{year}.graphml"
            )


class CalculateAICI:
    """Calculate adjusted internationalization collaboration index.

    Input dataframe generated by `collabnet.data.OpenAlex`.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """Init class."""
        self.dataframe = dataframe

    def _check_country_exist(self, row: dict) -> bool:
        if row["countries"]:
            return True
        return False

    def _check_no_country_exist(self, row: dict) -> bool:
        if not row["countries"]:
            return True
        return False

    def _check_is_international(self, row: dict) -> bool:
        if row["countries"] and len(set(row["countries"])) > 1:
            return True
        else:
            return False

    def _generate_df(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate AICI for the dataframe."""
        article_per_year = dataframe.groupby("publication_year").size().to_dict()
        affil_per_year = {}
        no_affil_per_year = {}
        is_international_per_year = {}
        for idx, g0 in dataframe.groupby("publication_year"):
            affil_per_year.update(
                {
                    idx: int(
                        g0.apply(lambda x: self._check_country_exist(x), axis=1).sum()
                    )
                }
            )
            no_affil_per_year.update(
                {
                    idx: int(
                        g0.apply(
                            lambda x: self._check_no_country_exist(x), axis=1
                        ).sum()
                    )
                }
            )
            is_international_per_year.update(
                {
                    idx: int(
                        g0.apply(
                            lambda x: self._check_is_international(x), axis=1
                        ).sum()
                    )
                }
            )
        aici_df = pd.DataFrame(
            [
                article_per_year,
                affil_per_year,
                no_affil_per_year,
                is_international_per_year,
            ]
        ).T.rename(
            columns={0: "papers", 1: "with_affil", 2: "no_affil", 3: "is_international"}
        )
        aici_df = aici_df.reset_index().rename(columns={"index": "year"})
        return aici_df

    def complete_df(self) -> pd.DataFrame:
        """Calculate values for full dataframe."""
        dftemp = self._generate_df(self.dataframe)
        dftemp.insert(0, "level", "global")
        return dftemp

    def country_df(self, country: str) -> pd.DataFrame:
        """Calculate values for one country."""
        country_mask = self.dataframe.countries.apply(
            lambda x: True if country in x else False
        )
        dataframe = self.dataframe[country_mask].reset_index(drop=True)
        dftemp = self._generate_df(dataframe)
        dftemp.insert(0, "level", country)
        return dftemp

    def country_compare(self, country_list: list) -> pd.DataFrame:
        """Create data to compare country AICI."""
        complete_df = self.complete_df()
        aici_complete = complete_df["is_international"]/complete_df["with_affil"]
        complete_df.insert(0, "aici", aici_complete)
        norm_series = complete_df[["year", "with_affil"]].set_index("year")["with_affil"]
        df_list = [complete_df]
        for country in country_list:
            country_df = self.country_df(country)
            aici_cnty = country_df.set_index("year")["is_international"]/norm_series
            country_df = country_df.merge(
                aici_cnty.to_frame("aici"), left_on="year", right_index=True
            )
            df_list.append(country_df)
        data = pd.concat(df_list, ignore_index=True)
        return data
