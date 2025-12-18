import io
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

from parkinsons_variant_viewer.web.loaders.upload_handler import (
    handle_uploaded_file,
)


class FakeVariantInfo:
    """Fake object to mimic ClinVar variant info."""

    def __init__(self):
        self.hgvs = "chr1:g.123A>T"
        self.clinvar_id = "12345"
        self.clinical_significance = "Pathogenic"
        self.star_rating = 2
        self.review_status = "criteria provided, single submitter"
        self.conditions_assoc = "DiseaseX"
        self.transcript = "NM_000000"
        self.ref_seq_id = "RefSeq1"
        self.hgnc_id = 101
        self.omim_id = 100000
        self.gene_symbol = "GENE1"
        self.g_change = "g.123A>T"
        self.c_change = "c.123A>T"
        self.p_change = "p.Lys41Asn"


def test_handle_uploaded_file_unsupported_extension():
    """Unsupported file types should log an error and return None."""
    fake_file_path = "file.unsupported"

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger, patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db"
    ):
        result = handle_uploaded_file(fake_file_path)

    assert result is None
    mock_logger.error.assert_called()


def test_handle_uploaded_file_minimal_vcf():
    """Minimal valid VCF should be parsed and inserted into inputs table."""
    fake_vcf_content = "# comment line\nchr1\t123\t.\tA\tT\n"
    fake_file_path = "Patient99.vcf"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ):
        handle_uploaded_file(fake_file_path)

    assert mock_db.execute.call_count == 1
    mock_db.commit.assert_called()

    call_args = mock_db.execute.call_args[0][1]
    assert call_args[0] == 99  # patient_id
    assert call_args[1] == 1   # variant_number
    assert call_args[2] == "chr1"
    assert call_args[3] == 123
    assert call_args[5] == "A"
    assert call_args[6] == "T"


def test_handle_uploaded_file_vcf_with_hgvs_clinvar():
    """VCF parsing + HGVS + ClinVar should populate inputs and outputs."""
    fake_vcf_content = "# comment line\nchr1\t123\t.\tA\tT\n"
    fake_file_path = "Patient99.vcf"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger, patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.HGVSVariant"
    ) as mock_hgvs_class, patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.fetch_clinvar_variant"
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_variant_info"
    ) as mock_get_info, patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.time.sleep",
        return_value=None,
    ):
        mock_hgvs_instance = mock_hgvs_class.return_value
        mock_hgvs_instance.get_hgvs.return_value = "chr1:g.123A>T"
        mock_get_info.return_value = FakeVariantInfo()

        handle_uploaded_file(fake_file_path)

    assert mock_db.execute.call_count >= 2
    assert mock_db.commit.call_count >= 2
    mock_logger.error.assert_not_called()


def test_handle_uploaded_file_csv_missing_columns():
    """CSV missing required columns should log an error and stop."""
    fake_csv_content = "chrom,pos,ref,patient_id\nchr1,123,A,99\n"
    fake_file_path = "variants.csv"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_csv_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger:
        result = handle_uploaded_file(fake_file_path)

    assert result is None
    mock_logger.error.assert_called()
    mock_db.execute.assert_not_called()
    mock_db.commit.assert_not_called()


def test_handle_uploaded_file_duplicate_input_entry():
    """Duplicate DB inserts should be skipped with a warning."""
    fake_vcf_content = "# comment\nchr1\t123\t.\tA\tT\n"
    fake_file_path = "Patient99.vcf"

    mock_db = MagicMock()
    mock_db.execute.side_effect = [
        sqlite3.IntegrityError("duplicate"),
    ]

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger:
        handle_uploaded_file(fake_file_path)

    mock_logger.warning.assert_called()
    mock_db.commit.assert_called()


def test_handle_uploaded_file_hgvs_none_skips_output():
    """If HGVS lookup fails, output insert should be skipped."""
    fake_vcf_content = "# comment\nchr1\t123\t.\tA\tT\n"
    fake_file_path = "Patient99.vcf"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.HGVSVariant"
    ) as mock_hgvs_class, patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger:
        mock_hgvs_class.return_value.get_hgvs.return_value = None

        handle_uploaded_file(fake_file_path)

    mock_logger.warning.assert_called()
    assert mock_db.execute.call_count == 1  # inputs only


def test_handle_uploaded_file_invalid_vcf_line():
    """Invalid VCF format should log error and stop."""
    fake_vcf_content = "chr1\t123\tA\n"  # too few columns
    fake_file_path = "Patient99.vcf"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger:
        result = handle_uploaded_file(fake_file_path)

    assert result is None
    mock_logger.error.assert_called()
    mock_db.execute.assert_not_called()


def test_handle_uploaded_file_invalid_patient_id():
    """VCF filename without patient ID should error."""
    fake_vcf_content = "# comment\nchr1\t123\t.\tA\tT\n"
    fake_file_path = "sample.vcf"

    mock_db = MagicMock()

    with patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.open",
        return_value=io.StringIO(fake_vcf_content),
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.get_db",
        return_value=mock_db,
    ), patch(
        "parkinsons_variant_viewer.web.loaders.upload_handler.logger"
    ) as mock_logger:
        result = handle_uploaded_file(fake_file_path)

    assert result is None
    mock_logger.error.assert_called()
