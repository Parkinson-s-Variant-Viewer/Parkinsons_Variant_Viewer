# import pytest
# from parkinsons_variant_viewer.clinvar_api import (
#     fetch_clinvar_variant, 
#     get_variant_info, 
#     map_review_status_to_stars,
#     ClinVarApiError
# )

# def test_clinvar_api_result():

#     """Test ClinVar API integration."""


#     clinvar_data = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
#     variant_info = get_variant_info(clinvar_data)
#     assert variant_info.chrom == "17"
#     assert variant_info.pos == "45983420"
#     assert variant_info.variant_id == "VCV000578075"
#     assert variant_info.ref == "G"
#     assert variant_info.alt == "T"
#     assert variant_info.hgvs == "NC_000017.11:g.45983420G>T"
#     assert variant_info.clinvar_id == "578075"
#     assert variant_info.clinical_significance == "Likely benign"
#     assert variant_info.star_rating == "1"
#     assert variant_info.review_status == "criteria provided, single submitter"
#     assert variant_info.conditions_assoc == "Frontotemporal dementia"
#     assert variant_info.transcript == "NM_001377265.1"
#     assert variant_info.ref_seq_id == "NC_000017.11"
#     assert variant_info.hgnc_id == "GeneID:4137"
#     assert variant_info.omim_id == "600274"
#     assert variant_info.gene_symbol == "MAPT"


# def test_map_review_status_to_stars():
#     """Test star rating mapping for different review statuses."""
#     # Expert panel (4 stars)
#     assert map_review_status_to_stars("reviewed by expert panel") == "4"
#     assert map_review_status_to_stars("criteria provided, reviewed by expert panel") == "4"
    
#     # Multiple submitters, no conflicts (3 stars)
#     assert map_review_status_to_stars("criteria provided, multiple submitters, no conflicts") == "3"
    
#     # Multiple submitters (2 stars)
#     assert map_review_status_to_stars("criteria provided, multiple submitters") == "2"
    
#     # Single submitter (1 star)
#     assert map_review_status_to_stars("criteria provided, single submitter") == "1"
    
#     # No assertion (0 stars)
#     assert map_review_status_to_stars("no assertion criteria provided") == "0"
#     assert map_review_status_to_stars("no criteria provided") == "0"
    
#     # Empty or None (0 stars)
#     assert map_review_status_to_stars("") == "0"
#     assert map_review_status_to_stars(None) == "0"


# def test_get_variant_info_not_found():
#     """Test get_variant_info when variant is not found."""
#     data = {
#         "found": False,
#         "hgvs": "NC_000000.00:g.0A>T",
#         "clinvar_id": "",
#         "variant": None,
#         "summary": None
#     }
#     variant_info = get_variant_info(data)
#     assert variant_info.hgvs == "NC_000000.00:g.0A>T"
#     assert variant_info.clinical_significance == "Not found"


# def test_variant_info_to_dict():
#     """Test VariantInfo to_dict conversion."""
#     data = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
#     variant_info = get_variant_info(data)
#     result_dict = variant_info.to_dict()
    
#     # Check that all expected keys are present
#     assert "CHROM" in result_dict
#     assert "POS" in result_dict
#     assert "ID" in result_dict
#     assert "REF" in result_dict
#     assert "ALT" in result_dict
#     assert "HGVS" in result_dict
#     assert "CLINVAR_ID" in result_dict
#     assert "CLINICAL_SIGNIFICANCE" in result_dict
#     assert "GENE_SYMBOL" in result_dict
    
#     # Check specific values
#     assert result_dict["CHROM"] == "17"
#     assert result_dict["GENE_SYMBOL"] == "MAPT"


# def test_fetch_clinvar_variant_returns_dict():
#     """Test that fetch_clinvar_variant returns a dictionary with expected keys."""
#     result = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
#     assert isinstance(result, dict)
#     assert "variant" in result
#     assert "summary" in result
#     assert "hgvs" in result
#     assert "found" in result
#     assert result["found"] is True


# def test_variant_info_has_all_attributes():
#     """Test that VariantInfo object has all expected attributes."""
#     data = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
#     variant_info = get_variant_info(data)
    
#     # Check all attributes exist
#     assert hasattr(variant_info, "hgvs")
#     assert hasattr(variant_info, "clinvar_id")
#     assert hasattr(variant_info, "chrom")
#     assert hasattr(variant_info, "pos")
#     assert hasattr(variant_info, "ref")
#     assert hasattr(variant_info, "alt")
#     assert hasattr(variant_info, "clinical_significance")
#     assert hasattr(variant_info, "star_rating")
#     assert hasattr(variant_info, "review_status")
#     assert hasattr(variant_info, "gene_symbol")
            
