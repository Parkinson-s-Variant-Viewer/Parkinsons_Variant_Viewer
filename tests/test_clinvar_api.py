"""
Tests for ClinVar API module.

All tests use mocked API responses to avoid hitting rate limits and ensure
fast, reliable test execution in CI/CD pipelines.
"""

import pytest
from unittest.mock import patch, Mock

from parkinsons_variant_viewer.clinvar_api import (
    fetch_clinvar_variant, 
    get_variant_info, 
    map_review_status_to_stars,
    fetch_hgnc_id,
    ClinVarApiError
)


def test_clinvar_api_result(mock_clinvar_response):
    """
    Test complete parsing of ClinVar API response data.
    
    Verifies that all variant fields (chromosome, position, reference allele,
    alternate allele, clinical significance, gene symbol, etc.) are correctly
    extracted from the API response structure.
    """
    # Mock HGNC API call to avoid external dependency
    with patch('parkinsons_variant_viewer.clinvar_api.fetch_hgnc_id', return_value="HGNC:6893"):
        variant_info = get_variant_info(mock_clinvar_response)
    
    # Verify genomic coordinates
    assert variant_info.chrom == "17"
    assert variant_info.pos == "45983420"
    assert variant_info.ref == "G"
    assert variant_info.alt == "T"
    
    # Verify identifiers
    assert variant_info.variant_id == "VCV000578075"
    assert variant_info.gene_symbol == "MAPT"
    assert variant_info.hgnc_id == "HGNC:6893"
    
    # Verify clinical annotations
    assert variant_info.clinical_significance == "Likely benign"
    assert variant_info.star_rating == "1"


def test_map_review_status_to_stars():
    """
    Test ClinVar review status to star rating conversion.
    
    ClinVar uses star ratings (0-4) to indicate confidence:
    - 4 stars: Reviewed by expert panel
    - 3 stars: Multiple submitters, no conflicts
    - 2 stars: Multiple submitters (with conflicts)
    - 1 star: Single submitter
    - 0 stars: No assertion criteria
    """
    # 4-star ratings
    assert map_review_status_to_stars("reviewed by expert panel") == "4"
    
    # 3-star ratings
    assert map_review_status_to_stars("criteria provided, multiple submitters, no conflicts") == "3"
    
    # 2-star ratings
    assert map_review_status_to_stars("criteria provided, multiple submitters") == "2"
    
    # 1-star ratings
    assert map_review_status_to_stars("criteria provided, single submitter") == "1"
    
    # 0-star ratings
    assert map_review_status_to_stars("no assertion criteria provided") == "0"
    assert map_review_status_to_stars(None) == "0"
    
    # Unknown status
    assert map_review_status_to_stars("unknown") == "N/A"


def test_variant_not_found():
    """
    Test handling of variants not found in ClinVar database.
    
    When a variant isn't found, the function should still return a VariantInfo
    object with "Not found" as the clinical significance rather than crashing.
    """
    data = {"found": False, "hgvs": "NC_000000.00:g.0A>T", "clinvar_id": "", "variant": None, "summary": None}
    variant_info = get_variant_info(data)
    assert variant_info.clinical_significance == "Not found"


def test_variant_info_to_dict(mock_clinvar_response):
    """
    Test conversion of VariantInfo object to dictionary.
    
    The to_dict() method is used for CSV export and API responses.
    Verifies all expected keys are present and values are correct.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.fetch_hgnc_id', return_value="HGNC:6893"):
        variant_info = get_variant_info(mock_clinvar_response)
    
    result_dict = variant_info.to_dict()
    
    # Check required keys exist
    assert "CHROM" in result_dict
    assert "GENE_SYMBOL" in result_dict
    
    # Verify values
    assert result_dict["CHROM"] == "17"
    assert result_dict["GENE_SYMBOL"] == "MAPT"


def test_fetch_hgnc_id_valid(mock_hgnc_response):
    """
    Test successful HGNC ID lookup for a known gene symbol.
    
    HGNC (HUGO Gene Nomenclature Committee) IDs are standardized identifiers
    for human genes. This test verifies the function correctly fetches the
    HGNC ID for the MAPT gene.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_hgnc_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        assert fetch_hgnc_id("MAPT") == "HGNC:6893"


def test_fetch_hgnc_id_not_found(mock_hgnc_not_found):
    """
    Test HGNC ID lookup for non-existent gene symbol.
    
    When a gene symbol doesn't exist, the function should return None
    rather than raising an exception.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_hgnc_not_found
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        assert fetch_hgnc_id("INVALID_GENE") is None


def test_fetch_hgnc_id_error():
    """
    Test HGNC ID lookup handles network errors gracefully.
    
    Network failures should not crash the application. The function should
    catch exceptions and return None, allowing processing to continue.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get', side_effect=Exception("Network error")):
        assert fetch_hgnc_id("MAPT") is None


def test_fetch_clinvar_variant_not_found():
    """
    Test ClinVar API response when variant doesn't exist.
    
    Queries for variants that don't exist in ClinVar should return a structured
    response with found=False rather than raising an exception.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get') as mock_get:
        # Mock empty search results
        mock_response = Mock()
        mock_response.text = '<?xml version="1.0"?><eSearchResult><IdList><Id/></IdList></eSearchResult>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = fetch_clinvar_variant("NC_000000.00:g.0A>T")
        assert result["found"] is False


def test_fetch_clinvar_variant_request_error():
    """
    Test ClinVar API handles network failures properly.
    
    Network errors during API calls should raise ClinVarApiError with a
    descriptive message rather than letting the raw exception propagate.
    """
    import requests
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get', 
               side_effect=requests.exceptions.RequestException("Connection error")):
        with pytest.raises(ClinVarApiError):
            fetch_clinvar_variant("NC_000017.11:g.45983420G>T")


def test_fetch_clinvar_variant_success():
    """
    Test successful ClinVar variant fetch with complete workflow.
    
    The function makes three API calls:
    1. esearch - Search for variant by HGVS notation
    2. efetch - Fetch detailed variant data
    3. esummary - Fetch summary information
    
    This test mocks all three calls to verify the complete flow works.
    """
    with patch('parkinsons_variant_viewer.clinvar_api.requests.get') as mock_get:
        # Mock search response with variant ID
        search_mock = Mock()
        search_mock.text = '<?xml version="1.0"?><eSearchResult><IdList><Id>578075</Id></IdList></eSearchResult>'
        search_mock.raise_for_status.return_value = None
        
        # Mock detailed variant data
        fetch_mock = Mock()
        fetch_mock.text = '<ClinVarSet></ClinVarSet>'
        fetch_mock.raise_for_status.return_value = None
        
        # Mock summary data
        summary_mock = Mock()
        summary_mock.text = '<eSummaryResult></eSummaryResult>'
        summary_mock.raise_for_status.return_value = None
        
        # Return different mocks for each sequential call
        mock_get.side_effect = [search_mock, fetch_mock, summary_mock]
        
        result = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
        assert result["found"] is True
        assert result["clinvar_id"] == "578075"


def test_multiple_conditions():
    """
    Test parsing variants associated with multiple clinical conditions.
    
    Some variants are associated with multiple phenotypes/conditions.
    This test verifies that:
    1. Multiple conditions are correctly parsed from the trait array
    2. They are joined with semicolons in the conditions_assoc field
    3. Star rating is correctly calculated (3 stars for "no conflicts")
    """
    data = {
        "found": True,
        "hgvs": "NC_000017.11:g.45983420G>T",
        "clinvar_id": "578075",
        "variant": {},
        "summary": {
            "eSummaryResult": {
                "DocumentSummarySet": {
                    "DocumentSummary": {
                        "accession": "VCV000578075",
                        "germline_classification": {
                            "description": "Likely benign",
                            "review_status": "criteria provided, multiple submitters, no conflicts",
                            "trait_set": {
                                "trait": [
                                    {"trait_name": "Condition 1", "trait_xrefs": {"trait_xref": {"db_source": "OMIM", "db_id": "600274"}}},
                                    {"trait_name": "Condition 2", "trait_xrefs": {"trait_xref": {"db_source": "OMIM", "db_id": "600275"}}}
                                ]
                            }
                        },
                        "variation_set": {
                            "variation": {
                                "canonical_spdi": "NC_000017.11:45983419:G:T",
                                "variation_loc": {"assembly_set": {"status": "current", "chr": "17", "start": "45983420"}}
                            }
                        },
                        "genes": {"gene": {"symbol": "MAPT"}}
                    }
                }
            }
        }
    }
    
    with patch('parkinsons_variant_viewer.clinvar_api.fetch_hgnc_id', return_value="HGNC:6893"):
        variant_info = get_variant_info(data)
    
    # Verify both conditions are present
    assert "Condition 1" in variant_info.conditions_assoc
    assert "Condition 2" in variant_info.conditions_assoc
    
    # Verify star rating calculation
    assert variant_info.star_rating == "3"


def test_parsing_error_handling():
    """
    Test robust error handling for malformed API responses.
    
    ClinVar API responses can sometimes have unexpected formats or missing fields.
    The parser should handle these gracefully without crashing, returning a
    VariantInfo object with whatever data is available.
    
    This test uses intentionally malformed data (invalid SPDI format, wrong
    data types) to verify defensive programming.
    """
    data = {
        "found": True,
        "hgvs": "NC_000017.11:g.45983420G>T",
        "clinvar_id": "578075",
        "variant": {},
        "summary": {
            "eSummaryResult": {
                "DocumentSummarySet": {
                    "DocumentSummary": {
                        "accession": "VCV000578075",
                        "variation_set": {
                            "variation": {
                                # Invalid SPDI format (should have 4 colon-separated parts)
                                "canonical_spdi": "invalid:format",
                                # Wrong data type (string instead of dict)
                                "variation_loc": "not_a_dict"
                            }
                        }
                    }
                }
            }
        }
    }
    
    with patch('parkinsons_variant_viewer.clinvar_api.fetch_hgnc_id', return_value=None):
        variant_info = get_variant_info(data)
    
    # Should return object with available data, not crash
    assert variant_info.hgvs == "NC_000017.11:g.45983420G>T"

