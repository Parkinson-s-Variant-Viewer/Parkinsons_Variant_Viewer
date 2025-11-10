import pytest
from parkinsons_variant_viewer.clinvar_api import fetch_clinvar_variant, get_variant_info

def test_clinvar_api_result():

    """Test ClinVar API integration."""


    clinvar_data = fetch_clinvar_variant("NC_000017.11:g.45983420G>T")
    variant_info = get_variant_info(clinvar_data)
    assert variant_info.chrom == "17"
    assert variant_info.pos == "45983420"
    assert variant_info.variant_id == "VCV000578075"
    assert variant_info.ref == "G"
    assert variant_info.alt == "T"
    assert variant_info.hgvs == "NC_000017.11:g.45983420G>T"
    assert variant_info.clinvar_id == "578075"
    assert variant_info.clinical_significance == "Likely benign"
    assert variant_info.star_rating == "1"
    assert variant_info.review_status == "criteria provided, single submitter"
    assert variant_info.conditions_assoc == "Frontotemporal dementia"
    assert variant_info.transcript == "NM_001377265.1"
    assert variant_info.ref_seq_id == "NC_000017.11"
    assert variant_info.hgnc_id == "GeneID:4137"
    assert variant_info.omim_id == "600274"
    assert variant_info.gene_symbol == "MAPT"
            
