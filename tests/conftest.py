"""Pytest configuration and fixtures for mocking API calls."""
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_clinvar_response():
    """Mock response for ClinVar API fetch_clinvar_variant."""
    return {
        "found": True,
        "hgvs": "NC_000017.11:g.45983420G>T",
        "clinvar_id": "578075",
        "variant": {},
        "summary": {
            "eSummaryResult": {
                "DocumentSummarySet": {
                    "DocumentSummary": {
                        "accession": "VCV000578075",
                        "title": "NM_001377265.1(MAPT):c.841G>A (p.Ala281Ser)",
                        "germline_classification": {
                            "description": "Likely benign",
                            "review_status": "criteria provided, single submitter",
                            "trait_set": {
                                "trait": {
                                    "trait_name": "Frontotemporal dementia",
                                    "trait_xrefs": {
                                        "trait_xref": {
                                            "db_source": "OMIM",
                                            "db_id": "600274"
                                        }
                                    }
                                }
                            }
                        },
                        "variation_set": {
                            "variation": {
                                "canonical_spdi": "NC_000017.11:45983419:G:T",
                                "variation_loc": {
                                    "assembly_set": {
                                        "status": "current",
                                        "chr": "17",
                                        "start": "45983420"
                                    }
                                }
                            }
                        },
                        "genes": {
                            "gene": {
                                "symbol": "MAPT"
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_hgnc_response():
    """Mock response for HGNC API fetch_hgnc_id."""
    return {
        "response": {
            "numFound": 1,
            "docs": [
                {
                    "hgnc_id": "HGNC:6893",
                    "symbol": "MAPT"
                }
            ]
        }
    }


@pytest.fixture
def mock_hgnc_not_found():
    """Mock response for HGNC API when gene not found."""
    return {
        "response": {
            "numFound": 0,
            "docs": []
        }
    }
