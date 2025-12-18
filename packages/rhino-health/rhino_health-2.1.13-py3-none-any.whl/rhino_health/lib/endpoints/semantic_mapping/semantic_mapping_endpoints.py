from typing import List, Optional, Union
from warnings import warn

import arrow
import pydantic

from rhino_health.lib.endpoints.endpoint import Endpoint, NameFilterMode, VersionMode
from rhino_health.lib.endpoints.semantic_mapping.semantic_mapping_dataclass import (
    SemanticMapping,
    SemanticMappingApproveList,
    SemanticMappingCreateInput,
    Vocabulary,
    VocabularyInput,
    VocabularySearch,
    VocabularyTermDisplayNameAndIdentifier,
    VocabularyTermsPage,
)
from rhino_health.lib.utils import rhino_error_wrapper

BUFFER_TIME_IN_SEC = 300
"""
@autoapi False
"""


class SemanticMappingEndpoints(Endpoint):
    """
    @autoapi True

    Endpoints to interact with semantic mappings
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "semantic_mapping"

    @property
    def semantic_mapping_dataclass(self):
        """
        @autoapi False
        :return:
        """
        return SemanticMapping

    @rhino_error_wrapper
    def create_semantic_mapping(self, semantic_mapping_create_input: SemanticMappingCreateInput):
        data = semantic_mapping_create_input.dict(by_alias=True)
        result = self.session.post(
            "/semantic_mappings",
            data=data,
        )
        return result.to_dataclass(self.semantic_mapping_dataclass)

    @rhino_error_wrapper
    def get_semantic_mapping(self, semantic_mapping_or_uid: Union[str, SemanticMapping]):
        result = self.session.get(
            f"/semantic_mappings/{semantic_mapping_or_uid if isinstance(semantic_mapping_or_uid, str) else semantic_mapping_or_uid.uid}"
        )
        return result.to_dataclass(self.semantic_mapping_dataclass)

    @rhino_error_wrapper
    def get_semantic_mapping_by_name(
        self, name, version=VersionMode.LATEST, project_uid=None
    ) -> Optional[SemanticMapping]:
        """
        @autoapi True
        Returns the latest or a specific SemanticMapping dataclass

        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the SemanticMapping
        version: Optional[Union[int, VersionMode]]
            Version of the CodeObject, latest by default, for an earlier version pass in an integer
        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        semantic_mapping: Optional[SemanticMapping]
            SemanticMapping with the name or None if not found

        Examples
        --------
        >>> session.semantic_mapping.get_semantic_mapping_by_name("My SemanticMapping")
        SemanticMapping(name="My SemanticMapping")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_semantic_mapping_by_name(), did you mean to use search_for_semantic_mappings_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_semantic_mappings_by_name(
            name, version, project_uid, NameFilterMode.EXACT
        )
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    def search_for_semantic_mappings_by_name(
        self,
        name,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        @autoapi True
        Returns SemanticMapping dataclasses

        Parameters
        ----------
        name: str
            Full or partial name for the SemanticMapping
        version: Optional[Union[int, VersionMode]]
            Version of the SemanticMapping, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode. By default uses CONTAINS

        Returns
        -------
        semantic_mappings: List[SemanticMapping]
            SemanticMapping dataclasses that match the name

        Examples
        --------
        >>> session.semantic_mappings.search_for_semantic_mappings_by_name("My SemanticMapping")
        [SemanticMapping(name="My SemanticMapping)]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        results = self.session.get("/semantic_mappings", params=query_params)
        return results.to_dataclasses(self.semantic_mapping_dataclass)

    @rhino_error_wrapper
    def get_semantic_mapping_data(self, semantic_mapping_or_uid: Union[str, SemanticMapping]):
        """
        @autoapi False

        Internal use only
        """
        result = self.session.get(
            f"/semantic_mappings/{semantic_mapping_or_uid if isinstance(semantic_mapping_or_uid, str) else semantic_mapping_or_uid.uid}/data"
        )
        return result  # TODO: Convert to dataclass.

    @rhino_error_wrapper
    def approve_mappings(self, semantic_mapping_uid: str, mapping_data: SemanticMappingApproveList):
        """
        @autoapi False

        Internal use only
        """
        data = mapping_data.dict(by_alias=True)
        result = self.session.post(
            f"/semantic_mappings/{semantic_mapping_uid}/approve_mappings",
            data=data,
        )
        return result.no_dataclass_response()

    @rhino_error_wrapper
    def remove_semantic_mapping(self, semantic_mapping_or_uid: Union[str, SemanticMapping]):
        """
        Remove a SemanticMapping with SEMANTIC_MAPPING_OR_UID from the system
        """
        return self.session.delete(
            f"/semantic_mappings/{semantic_mapping_or_uid if isinstance(semantic_mapping_or_uid, str) else semantic_mapping_or_uid.uid}"
        ).no_dataclass_response()


class VocabularyEndpoints(Endpoint):
    """
    @autoapi False
    """

    @classmethod
    def _endpoint_name(cls):
        """@autoapi False Used to autoassign endpoints the session object"""
        return "vocabulary"

    @property
    def vocabulary_dataclass(self):
        """
        @autoapi False
        :return:
        """
        return Vocabulary

    def create_vocabulary(self, vocabulary_input: VocabularyInput):
        """
        @autoapi True
        Create a vocabulary on the Rhino Health Platform

        Parameters
        ----------
        vocabulary_input: VocabularyInput
            Input arguments for the vocabulary to create

        Returns
        -------
        vocabulary: Vocabulary
            A response object containing the created vocabulary
        """
        data = vocabulary_input.dict(by_alias=True)

        # Convert terms into expected CSV input format
        terms = data.pop("terms")
        if terms and isinstance(terms, list):
            type_adapter = pydantic.TypeAdapter(List[VocabularyTermDisplayNameAndIdentifier])
            terms = type_adapter.validate_python(terms)
            terms_input_csv = "".join(
                [f"{term.term_identifier},{term.term_display_name}\n" for term in terms]
            )
        elif terms and isinstance(terms, str):
            terms_input_csv = terms
        else:
            raise ValueError(f"Unexpected terms input: {terms}")
        data["terms"] = terms_input_csv

        result = self.session.post(
            "/vocabularies/",
            data=data,
        )
        return result.to_dataclass(self.vocabulary_dataclass)

    def get_vocabulary(
        self,
        vocabulary_or_uid: Union[str, Vocabulary],
    ) -> Vocabulary:
        result = self.session.get(
            f"/vocabularies/{vocabulary_or_uid if isinstance(vocabulary_or_uid, str) else vocabulary_or_uid.uid}",
        )
        return result.to_dataclass(self.vocabulary_dataclass)

    @rhino_error_wrapper
    def get_vocabularies_by_name(
        self,
        name,
        version=VersionMode.LATEST,
        project_uid=None,
    ) -> Optional[Vocabulary]:
        """
        @autoapi True
        Returns the latest or a specific Vocabulary dataclass

        .. warning:: VersionMode.ALL will return the same as VersionMode.LATEST

        Parameters
        ----------
        name: str
            Full name for the Vocabulary
        version: Optional[Union[int, VersionMode]]
            Version of the Vocabulary, latest by default, for an earlier version pass in an integer
        project_uid: Optional[str]
            Project UID to search under

        Returns
        -------
        vocabulary: Optional[Vocabulary]
            Vocabulary with the name or None if not found

        Examples
        --------
        >>> session.vocabulary.get_vocabulary_by_name("My Vocabulary")
        Vocabulary(name="My Vocabulary")
        """
        if version == VersionMode.ALL:
            warn(
                "VersionMode.ALL behaves the same as VersionMode.LATEST for get_vocabularies_by_name(), did you mean to use search_for_vocabularies_by_name()?",
                RuntimeWarning,
            )
        results = self.search_for_vocabularies_by_name(
            name, version, project_uid, NameFilterMode.EXACT
        )
        return max(results, key=lambda x: arrow.get(x.created_at)) if results else None

    def search_for_vocabularies_by_name(
        self,
        name,
        version: Optional[Union[int, VersionMode]] = VersionMode.LATEST,
        project_uid: Optional[str] = None,
        name_filter_mode: Optional[NameFilterMode] = NameFilterMode.CONTAINS,
    ):
        """
        @autoapi True
        Returns Vocabulary dataclasses

        Parameters
        ----------
        name: str
            Full or partial name for the Vocabulary
        version: Optional[Union[int, VersionMode]]
            Version of the Vocabulary, latest by default
        project_uid: Optional[str]
            Project UID to search under
        name_filter_mode: Optional[NameFilterMode]
            Only return results with the specified filter mode. By default uses CONTAINS

        Returns
        -------
        vocabularies: List[Vocabulary]
            Vocabulary dataclasses that match the name

        Examples
        --------
        >>> session.vocabulary.search_for_vocabularies_by_name("My Vocabulary")
        [Vocabulary(name="My Vocabulary)]

        See Also
        --------
        rhino_health.lib.endpoints.endpoint.FilterMode : Different modes to filter by
        rhino_health.lib.endpoints.endpoint.VersionMode : Which version to return
        """
        query_params = self._get_filter_query_params(
            {"name": name, "object_version": version, "project_uid": project_uid},
            name_filter_mode=name_filter_mode,
        )
        results = self.session.get("/vocabularies", params=query_params)
        return results.to_dataclasses(self.vocabulary_dataclass)

    @rhino_error_wrapper
    def vocabulary_search(self, vocabulary_uid: str, vocabulary_search_params: VocabularySearch):
        """
        Perform a search against a specific vocabulary (for the FE autocomplete)

        @autoapi False
        Internal Use Only
        """
        return self.session.post(
            f"/vocabularies/{vocabulary_uid}/search/",
            vocabulary_search_params.dict(by_alias=True),
        )

    @rhino_error_wrapper
    def remove_vocabulary(self, vocabulary_or_uid: Union[str, Vocabulary]):
        """
        @autoapi True
        Remove a Vocabulary with VOCABULARY_OR_UID from the system
        """
        vocabulary_uid = (
            vocabulary_or_uid if isinstance(vocabulary_or_uid, str) else vocabulary_or_uid.uid
        )
        return self.session.delete(f"/vocabularies/{vocabulary_uid}/").no_dataclass_response()

    @rhino_error_wrapper
    def get_vocabulary_terms(
        self, vocabulary_or_uid: Union[str, Vocabulary], page_size: int = 10_000
    ) -> List[VocabularyTermDisplayNameAndIdentifier]:
        """
        @autoapi True
        Get the terms for a vocabulary.

        Parameters
        ----------
        vocabulary_or_uid: Union[str, Vocabulary]
            The vocabulary object or the UID
        page_size: int
            The number of terms to return per page by the API. Defaults to 10,000, the maximum supported size.

        Returns
        -------
        terms: List[VocabularyTermDisplayNameAndIdentifier]
            The terms for the vocabulary
        """
        vocabulary_uid = (
            vocabulary_or_uid if isinstance(vocabulary_or_uid, str) else vocabulary_or_uid.uid
        )
        terms_page_response = self.session.get(
            f"/vocabularies/{vocabulary_uid}/terms/", params={"page_size": page_size}
        )
        terms_page = terms_page_response.to_dataclass(VocabularyTermsPage)
        terms_count = terms_page.count
        terms = terms_page.results
        if len(terms) < terms_count:
            page_size = len(terms)
            for page_num in range(2, (terms_count - 1) // page_size + 2):
                terms_page_response = self.session.get(
                    f"/vocabularies/{vocabulary_uid}/terms/",
                    params={"page": page_num, "page_size": page_size},
                )
                terms_page = terms_page_response.to_dataclass(VocabularyTermsPage)
                terms.extend(terms_page.results)
        return terms
