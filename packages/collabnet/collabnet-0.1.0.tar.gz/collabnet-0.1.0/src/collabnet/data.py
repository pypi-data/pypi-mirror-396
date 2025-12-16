# Transform source data to required format.
# Source data can come from OpenAlex by using the utilites module.

import json
from pathlib import Path

import pandas as pd
import pyalex
from tqdm import tqdm


class TransformOA:
    """Read and transform Open Alex data.

    File list should be a list of file paths.
    Source files have to be in JSON format.

     Using TransformOA.run() has the following workflow:
       1) Open the UTF-8 encoded JSON file.
       2) Load a list of OpenAlex Work records.
       3) Normalize each record via `_process_entry`.
       4) Create a pandas DataFrame and write it as JSON to `self.out_path`
          using the same base filename.

     Side effects:
       - Writes a JSON file to `<self.out_path>/<file_path.name>`.

     Note:
       - UnicodeDecodeError from the JSON files are  caught and logged.
       - Other I/O and JSON parsing errors will propagate to the caller.

    :param src_files: List of source file paths to JSON files containing OpenAlex records.
    :type src_files: list[str] | list[pathlib.Path]
    :param out_path: Directory where transformed outputs will be written. Defaults to the current directory.
    :type out_path: str | pathlib.Path, optional
    """

    def __init__(self, src_files: list, out_path: str = "."):
        """Init class."""
        self.src_files = src_files
        self.out_path = out_path

    def _getAuthorAffilID(self, authors) -> tuple:
        """Extract author and affiliation identifiers and associated country codes.

        Expects the OpenAlex "authorships" structure:
            - Each item should contain an "author" dict with an "id".
            - Each item should contain an "institutions" list; each institution may have "id" and "country_code".

        Returns a tuple:
            - List of (author_id, [institution_ids]) pairs.
            - List of country codes (one per institution encountered, duplicates possible).

        Note: Missing keys are returned as empty dicts ({}).

        :param authors: List of authorship entries from an OpenAlex Work.
        :type authors: list[dict]
        :returns: (author_affils, countries)
                    where author_affils is list[tuple[str | dict, list[str | dict]]]
                    and countries is list[str | dict]
        :rtype: tuple[list[tuple[str | dict, list[str | dict]]], list[str | dict]]
        :raises TypeError: If `authors` is not iterable.
        """
        result = []
        countries = []
        for author in authors:
            idx = author.get("author", {}).get("id", {})
            instList = []
            institutions = author.get("institutions")
            for ins in institutions:
                instList.append(ins.get("id", {}))
                countries.append(ins.get("country_code", {}))
            result.append((idx, instList))
        return result, countries

    def _getTopicID(self, topics) -> list:
        """Collect topic identifiers from an OpenAlex Work.

        Expects a list of topic dicts, each with an "id" key.

        Note: Missing keys are returned as empty dicts ({}).

        :param topics: Topics section from an OpenAlex Work.
        :type topics: list[dict]
        :returns: List of topic IDs.
        :rtype: list[str | dict]
        :raises TypeError: If `topics` is not iterable.
        """
        result = []
        for topic in topics:
            result.append(topic.get("id", {}))
        return result

    def _getJournalID(self, publication_location) -> str | None:
        """Return the source (journal) identifier from a Work's primary location.

        Expects the "primary_location" structure:
            - A dict containing a "source" dict with an "id" key.

        :param publication_location: The Work's primary_location object.
        :type publication_location: dict
        :returns: Source ID if available; otherwise None.
        :rtype: str | None
        """
        source = publication_location.get("source", {})
        if source:
            return source.get("id", {})
        return None

    def _process_entry(self, work: dict) -> dict:
        """Normalize a single OpenAlex Work record.

            Extracts a subset of fields from the raw work, reconstructs the abstract
            from the abstract_inverted_index, replaces it with a plain-text abstract,
            and enriches the record with processed authorships, countries, topics, and
            primary_location identifiers.

            Required input keys in `work` for transformations:
              - abstract_inverted_index
              - authorships
              - topics
              - primary_location

            Output keys in the returned dict:
              - abstract            (reconstructed from abstract_inverted_index)
              - authorships         (processed via _getAuthorAffilID)
              - countries           (derived from authors' affiliations)
              - topics              (processed via _getTopicID)
              - primary_location    (processed via _getJournalID)

            The keys id, doi, title, type, publication_year and referenced_works are copied.

            :param work: Raw OpenAlex Work object as returned by the API.
            :type work: dict
            :returns: Normalized work record with selected fields and derived values.
            :rtype: dict
            :raises TypeError: If `work` is not a mapping-like object.
            :raises KeyError: If any required field is missing from `work`.
            """
        data_keys = [
            "doi",
            "title",
            "type",
            "publication_year",
            "abstract_inverted_index",
            "referenced_works",
        ]
        result = dict()
        result = {"id": work["id"]}
        for key in data_keys:
            result.update({key: work[key]})
        tempWork = pyalex.Work(result)
        abstract = tempWork["abstract"]
        result.update({"abstract": abstract})
        result.pop("abstract_inverted_index", None)
        authors, countries = self._getAuthorAffilID(work["authorships"])
        result.update({"authorships": authors})
        result.update({"countries": countries})
        result.update({"topics": self._getTopicID(work["topics"])})
        result.update(
            {"primary_location": self._getJournalID(work["primary_location"])}
        )
        return result

    def _process_file(self, file_path: Path) -> None:
        """Transform one source JSON file into the normalized output format.

        :param file_path: Path to a UTF-8 encoded JSON file containing a list of
                            OpenAlex Work objects.
        :type file_path: pathlib.Path
        :returns: None
        :rtype: None
        :raises FileNotFoundError: If the input file does not exist.
        :raises json.JSONDecodeError: If the file content is not valid JSON.
        :raises OSError: For general I/O errors while reading or writing.
        """
        with open(Path(file_path), encoding="utf-8") as infile:
            try:
                data = json.load(infile)
                result = [self._process_entry(work) for work in data]
                dftemp = pd.DataFrame(result)
                dftemp.to_json(f"{self.out_path}{file_path.name}")
            except UnicodeDecodeError as r:
                print("error in file", r)

    def run(self) -> None:
        """Process all source files defined in `self.src_files`.

        Iterates over `self.src_files` with a progress bar and invokes
        `_process_file` for each entry.

        :returns: None
        :rtype: None
        """
        for file_path in tqdm(self.src_files):
            self._process_file(file_path)


def join_to_df(
    src_folder: Path, out_folder: Path = Path("."), selection: str = "*.json"
) -> pd.DataFrame:
    """Create combined dataframe from JSON files.
    Entries are de-duplicated based on their work ID.

    If only specific JSON files should be joined,
    specify a regex pattern like 'works_s\*.json'.
    Supports glob to search files in subfolders, e.g.
    '\**/\*.json' for all JSON files in all subfolders.

    :param src_folder: Root directory to search for input JSON files.
    :type src_folder: pathlib.Path
    :param out_folder: Directory where any outputs or artifacts may be written.
                        Defaults to the current directory.
    :type out_folder: pathlib.Path, optional
    :param selection: Glob pattern used to select input JSON files relative to
                        src_folder. Defaults to '\*.json'.
    :type selection: str, optional
    :returns: Combined dataframe of unique works from the selected JSON files.
    :rtype: pandas.DataFrame
    """
    file_paths = list(src_folder.glob(selection))
    df_list = []
    for filepath in file_paths:
        data = pd.read_json(filepath)
        df_list.append(data)
    data = pd.concat(df_list, ignore_index=True)
    dedup_data = data.drop_duplicates(subset="id")
    dedup_data.to_json(out_folder / "joined_data.json", lines=True, orient="records")
    print(f"Deduplicated {data.shape[0] - dedup_data.shape[0]} entries.")
    return dedup_data
