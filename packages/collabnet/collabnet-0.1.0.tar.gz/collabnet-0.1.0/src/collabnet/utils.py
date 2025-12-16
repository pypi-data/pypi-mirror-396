# Query OA for works in relation to a journal or topic

import json
from pathlib import Path

import pyalex
from tqdm import tqdm
from validator_collection import validators

pyalex.config.max_retries = 1
pyalex.config.retry_backoff_factor = 0.1
pyalex.config.retry_http_codes = [429, 500, 503]


class QueryOA:
    """Query Open Alex to receive publication records.

    :param config_email: Contact email used for OpenAlex polite API requests.
    :type config_email: str
    :param query_list: List of query terms or identifiers to query against OpenAlex.
    :type query_list: list
    :param year_range: Inclusive (start_year, end_year) for filtering publication years.
    :type year_range: tuple[int, int]
    :param out_path: Directory where results/artifacts should be written. Defaults to the current directory.
    :type out_path: pathlib.Path, optional
    :param query_type: Type of query to perform ("journal", "topic", or "institution"). Defaults to "topic".
    :type query_type: str, optional
    """

    def __init__(
        self,
        config_email: str,
        query_list: list,
        year_range: tuple,
        out_path: Path = Path("."),
        query_type: str = "topic",
        n_max: int | None = None,
    ):
        assert query_type in ["topic", "journal", "institution"], (
            "Use supported query type: topic, journal or institution"
        )
        if query_type == "topic":
            assert all([x.startswith("t") for x in query_list]), (
                "Provide list of correct topic IDs starting with t."
            )
        elif query_type == "journal":
            assert all([x.startswith("s") for x in query_list]), (
                "Provide list of correct journal IDs starting with s."
            )
        else:
            pass
        assert validators.email(config_email), "Provide a valid email address."
        pyalex.config.email = config_email
        self.query_list = query_list
        self.query_type = query_type
        self.year_range = year_range
        self.out_path = out_path
        self.n_max = n_max

    def run(self) -> list:
        file_list = self._run_query(
            self.query_list, self.query_type, self.year_range, self.out_path
        )
        return file_list

    def _run_query(self, query_list, query_type, year_range, out_path) -> list:
        """Execute an OpenAlex query and collect publication records.

        :param query_list: List of query terms or identifiers to query against OpenAlex.
        :type query_list: list
        :param query_type: Type of query to perform (e.g., "topic", "author", "source").
        :type query_type: str
        :param year_range: Inclusive (start_year, end_year) for filtering publication years.
        :type year_range: tuple[int, int]
        :param out_path: Directory where results or intermediate artifacts may be written.
        :type out_path: pathlib.Path
        :returns: Retrieved publication records.
        :rtype: list[dict]
        """
        generated_files = []
        for entry in tqdm(query_list):
            all_current_works = []
            if query_type == "topic":
                temp_works = self._topic_query(entry, year_range)
            elif query_type == "journal":
                temp_works = self._journal_query(entry, year_range)
            elif query_type == "institution":
                temp_works = self._affiliation_query(entry, year_range)
            else:
                raise TypeError("Provide query_type.")
            for res_temp_works in temp_works:
                all_current_works.append(res_temp_works)
            with open(
                Path(out_path / f"works_{entry}.json"), "w", encoding="utf8"
            ) as json_file:
                json.dump(
                    [x for y in all_current_works for x in y],
                    json_file,
                    ensure_ascii=False,
                )
                generated_files.append(Path(out_path / f"works_{entry}.json"))
        return generated_files

    def _topic_query(self, entry: str, year_range: tuple):
        """Run a topic-based query against OpenAlex for a single entry.

        :param entry: Topic identifier to query (topic ids start with the letter t).
        :type entry: str
        :param year_range: Inclusive (start_year, end_year) range for filtering publication years.
        :type year_range: tuple[int, int]
        :returns: Publication records matching the topic and year filter.
        :rtype: list[dict]
        """
        temp_works = (
            pyalex.Works()
            .filter(
                topics={"id": entry},
                from_publication_date=f"{year_range[0]}-01-01",
                to_publication_date=f"{year_range[1]}-12-31",
            )
            .paginate(per_page=200, n_max=self.n_max)
        )
        return temp_works

    def _journal_query(self, entry: str, year_range: tuple):
        """Run a journal-based query against OpenAlex for a single entry.

        :param entry: Journal identifier to query (journal ids start with the letter s).
        :type entry: str
        :param year_range: Inclusive (start_year, end_year) range for filtering publication years.
        :type year_range: tuple[int, int]
        :returns: Publication records matching the topic and year filter.
        :rtype: list[dict]
        """
        temp_works = (
            pyalex.Works()
            .filter(
                primary_location={"source": {"id": entry}},
                from_publication_date=f"{year_range[0]}-01-01",
                to_publication_date=f"{year_range[1]}-12-31",
            )
            .paginate(per_page=200, n_max=self.n_max)
        )
        return temp_works

    def _affiliation_query(self, entry: str, year_range: tuple):
        """Run a institution-based query against OpenAlex for a single entry.

        :param entry: ROR ID to query (See ror.org for search options).
        :type entry: str
        :param year_range: Inclusive (start_year, end_year) range for filtering publication years.
        :type year_range: tuple[int, int]
        :returns: Publication records matching the topic and year filter.
        :rtype: list[dict]
        """
        temp_works = (
            pyalex.Works()
            .filter(
                authorships={"institutions": {"ror": entry}},
                from_publication_date=f"{year_range[0]}-01-01",
                to_publication_date=f"{year_range[1]}-12-31",
            )
            .paginate(per_page=200, n_max=self.n_max)
        )
        return temp_works
