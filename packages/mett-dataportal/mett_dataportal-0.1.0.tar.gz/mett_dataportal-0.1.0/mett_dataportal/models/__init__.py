"""Convenience re-exports of generated SDK models."""

from __future__ import annotations

from typing import TypedDict

from mett_dataportal_sdk.models.drug_metabolism_data_schema import DrugMetabolismDataSchema
from mett_dataportal_sdk.models.drug_mic_data_schema import DrugMICDataSchema
from mett_dataportal_sdk.models.gene_paginated_response_schema import GenePaginatedResponseSchema
from mett_dataportal_sdk.models.gene_response_schema import GeneResponseSchema
from mett_dataportal_sdk.models.genome_paginated_response_schema import GenomePaginatedResponseSchema
from mett_dataportal_sdk.models.genome_response_schema import GenomeResponseSchema
from mett_dataportal_sdk.models.paginated_response_schema import PaginatedResponseSchema
from mett_dataportal_sdk.models.paginated_strain_drug_metabolism_response_schema import (
    PaginatedStrainDrugMetabolismResponseSchema,
)
from mett_dataportal_sdk.models.paginated_strain_drug_mic_response_schema import PaginatedStrainDrugMICResponseSchema
from mett_dataportal_sdk.models.pagination_metadata_schema import PaginationMetadataSchema
from mett_dataportal_sdk.models.success_response_schema import SuccessResponseSchema


class SpeciesDict(TypedDict, total=False):
    """Lightweight species representation."""

    species_acronym: str
    species_scientific_name: str
    description: str
    taxonomy_id: int


Pagination = PaginationMetadataSchema
PaginatedResponse = PaginatedResponseSchema
GenomePage = GenomePaginatedResponseSchema
GenePage = GenePaginatedResponseSchema
StrainDrugMICPage = PaginatedStrainDrugMICResponseSchema
StrainDrugMetabolismPage = PaginatedStrainDrugMetabolismResponseSchema
SuccessResponse = SuccessResponseSchema

Genome = GenomeResponseSchema
Gene = GeneResponseSchema
DrugMIC = DrugMICDataSchema
DrugMetabolism = DrugMetabolismDataSchema
Species = SpeciesDict

__all__ = [
    "Pagination",
    "PaginatedResponse",
    "GenomePage",
    "GenePage",
    "StrainDrugMICPage",
    "StrainDrugMetabolismPage",
    "SuccessResponse",
    "Genome",
    "Gene",
    "DrugMIC",
    "DrugMetabolism",
    "Species",
]
