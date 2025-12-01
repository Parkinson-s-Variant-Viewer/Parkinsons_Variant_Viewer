# tests/test_upload_handler.py
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from parkinsons_variant_viewer.web.loaders.upload_handler import handle_uploaded_file

# Mock variant info object returned by get_variant_info
class MockVariantInfo:
    hgvs = "NC_000017.11:g.430457A>T"
    clinvar_id = "12345"
    clinical_significance = "Pathogenic"
    star_rating = 2
    review_status = "criteria provided"
    conditions_assoc = "Parkinson's disease"
    transcript = "NM_000000.1"
    ref_seq_id = "NC_000017.11"
    hgnc_id = "HGNC:5"
    omim_id = "123456"
    gene_symbol = "LRRK2"
    g_change = "g.430457A>T"
    c_change = "c.123A>T"
    p_change = "p.Lys41Asn"

@pytest.fixture
def temp_csv_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("chrom,pos,ref,alt,patient_id,variant_number,id\n")
        f.write("17,430457,A,T,101,1,rs123\n")
        fname = f.name
    yield fname
    os.remove(fname)

@pytest.fixture
def temp_vcf_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".vcf", delete=False) as f:
        f.write("##fileformat=VCFv4.2\n")
        f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        f.write("17\t430457\trs123\tA\tT\t.\t.\t.\n")
        fname = f.name
    yield fname
    os.remove(fname)

@patch("parkinsons_variant_viewer.web.loaders.upload_handler.get_db")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.HGVSVariant")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.fetch_clinvar_variant")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.get_variant_info")
def test_handle_uploaded_file_csv(mock_get_variant_info, mock_fetch, mock_hgvs, mock_get_db, temp_csv_file):
    # Setup mocks
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_hgvs.return_value.get_hgvs.return_value = "NC_000017.11:g.430457A>T"
    mock_fetch.return_value = "raw_data"
    mock_get_variant_info.return_value = MockVariantInfo()

    # Call function
    handle_uploaded_file(temp_csv_file)

    # Assertions: check DB insert called at least once
    assert mock_db.execute.called
    assert mock_db.commit.called

@patch("parkinsons_variant_viewer.web.loaders.upload_handler.get_db")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.HGVSVariant")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.fetch_clinvar_variant")
@patch("parkinsons_variant_viewer.web.loaders.upload_handler.get_variant_info")
def test_handle_uploaded_file_vcf(mock_get_variant_info, mock_fetch, mock_hgvs, mock_get_db, temp_vcf_file):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    mock_hgvs.return_value.get_hgvs.return_value = "NC_000017.11:g.430457A>T"
    mock_fetch.return_value = "raw_data"
    mock_get_variant_info.return_value = MockVariantInfo()

    handle_uploaded_file(temp_vcf_file)

    assert mock_db.execute.called
    assert mock_db.commit.called

def test_handle_uploaded_file_wrong_extension():
    # Should not raise exception; logs error and returns
    assert handle_uploaded_file("file.txt") is None
