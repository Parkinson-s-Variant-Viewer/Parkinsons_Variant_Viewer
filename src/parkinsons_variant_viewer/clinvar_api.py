"""
ClinVar API interaction module for Parkinsons Variant Viewer.

Provides functions to query ClinVar using HGVS nomenclature and extract
variant information. Supports fetching ClinVar IDs via esearch, retrieving
detailed variant records via efetch and esummary, and mapping review
statuses to star ratings. Also includes a helper to fetch HGNC IDs from
gene symbols.
"""

import re
import requests
import xmltodict

from parkinsons_variant_viewer.utils.logger import logger

class ClinVarApiError(Exception):
    """Custom exception for ClinVar API errors."""
    pass
    
def fetch_hgnc_id(gene_symbol):
    """
    Fetch HGNC ID for a given gene symbol using the HGNC REST API.

    Parameters
    ----------
    gene_symbol : str
        Gene symbol to query (e.g., "LRRK2").

    Returns
    -------
    str or None
        HGNC ID in the format "HGNC:XXXX", or None if not found.
    """

    try:
        url = f"https://rest.genenames.org/fetch/symbol/{gene_symbol}"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get('response', {}).get('numFound', 0) > 0:
            docs = data['response']['docs']
            if docs:
                hgnc_id = docs[0].get('hgnc_id')
                if hgnc_id:
                    # HGNC ID comes as "HGNC:6893"
                    return hgnc_id
    except Exception as e:
        logger.warning(f"Failed to fetch HGNC ID for {gene_symbol}: {e}")
    
    return None

def fetch_clinvar_variant(hgvs):
    """
    Query ClinVar for a given HGVS variant and return XML-parsed data.

    The function searches ClinVar using the esearch endpoint, retrieves
    variant IDs, and fetches detailed variant data with efetch and esummary.

    Parameters
    ----------
    hgvs : str
        HGVS-formatted variant string (e.g., "NC_000017.11:g.45983420G>T").

    Returns
    -------
    dict
        Dictionary containing:
        - 'variant': Parsed efetch XML data
        - 'summary': Parsed esummary XML data
        - 'hgvs': Original HGVS string
        - 'found': True if variant found, else False
        - 'clinvar_id': ClinVar ID if found, else None

    Raises
    ------
    ClinVarApiError
        If a request to the ClinVar API fails.
    """

    # Search for variant
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {"db": "clinvar", "term": f'"{hgvs}"[variant name]', "retmode": "xml"}
    
    try:
        search_resp = requests.get(search_url, params=search_params)
        search_resp.raise_for_status()
        search_data = xmltodict.parse(search_resp.text)
        
        # Get variant IDs
        id_list = search_data.get("eSearchResult", {}).get("IdList", {})
        ids = id_list.get("Id", [])
        if isinstance(ids, str):
            ids = [ids]
        
        if not ids:
            logger.warning(f"No variants found for HGVS: {hgvs}")
            return {"variant": None, "summary": None, "hgvs": hgvs, "found": False}
        
        # Get detailed data
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        
        fetch_params = {"db": "clinvar", "id": ids[0], "rettype": "clinvarset", "retmode": "xml"}
        summary_params = {"db": "clinvar", "id": ids[0], "retmode": "xml"}
        
        fetch_resp = requests.get(fetch_url, params=fetch_params)
        summary_resp = requests.get(summary_url, params=summary_params)
        
        fetch_resp.raise_for_status()
        summary_resp.raise_for_status()
        
        return {
            "variant": xmltodict.parse(fetch_resp.text),
            "summary": xmltodict.parse(summary_resp.text),
            "hgvs": hgvs,
            "found": True,
            "clinvar_id": ids[0]
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching ClinVar data for {hgvs}: {e}")
        raise ClinVarApiError(f"Failed to fetch ClinVar data: {e}")

def get_variant_info(data):
    """
    Parse ClinVar API response into a structured VariantInfo object.

    Converts the raw XML-parsed ClinVar response into a VariantInfo object
    with attributes such as HGVS, ClinVar ID, clinical significance,
    star rating, transcript, reference/alternate alleles, and gene info.
    If the variant is not found, default values are returned.

    Parameters
    ----------
    data : dict
        Dictionary returned by `fetch_clinvar_variant`.

    Returns
    -------
    VariantInfo
        An object containing variant annotations and genomic details.
    """
    
    class VariantInfo:
        """
        Stores variant information extracted from ClinVar data.

        Attributes
        ----------
        hgvs : str
            HGVS nomenclature for the variant (e.g., "NC_000017.11:g.45983420G>T").
        clinvar_id : str
            ClinVar ID associated with the variant.
        variant_id : str
            Identifier for the variant; usually same as ClinVar ID.
        chrom : str
            Chromosome where the variant is located.
        pos : str or int
            Position of the variant on the chromosome (1-based).
        ref : str
            Reference allele.
        alt : str
            Alternate allele.
        clinical_significance : str
            ClinVar clinical significance classification.
        star_rating : str
            ClinVar review star rating (0-4 or N/A).
        review_status : str
            ClinVar review status description.
        conditions_assoc : str
            Associated conditions/phenotypes from ClinVar.
        transcript : str
            Transcript ID or name associated with the variant.
        ref_seq_id : str
            Reference sequence ID from ClinVar SPDI data.
        g_change : str
            Genomic HGVS change (g.) notation.
        c_change : str
            Coding DNA HGVS change (c.) notation.
        p_change : str
            Protein HGVS change (p.) notation.
        hgnc_id : str
            HGNC ID for the associated gene, if available.
        omim_id : str
            OMIM ID for associated conditions, if available.
        gene_symbol : str
            Gene symbol (e.g., "LRRK2").
        """

        def __init__(self, **kwargs):
            self.hgvs = kwargs.get('hgvs')
            self.clinvar_id = kwargs.get('clinvar_id')
            self.chrom = kwargs.get('chrom')
            self.pos = kwargs.get('pos')
            self.variant_id = kwargs.get('variant_id')
            self.ref = kwargs.get('ref')
            self.alt = kwargs.get('alt')
            self.clinical_significance = kwargs.get('clinical_significance')
            self.star_rating = kwargs.get('star_rating')
            self.review_status = kwargs.get('review_status')
            self.conditions_assoc = kwargs.get('conditions_assoc')
            self.transcript = kwargs.get('transcript')
            self.ref_seq_id = kwargs.get('ref_seq_id')
            self.g_change = kwargs.get('g_change')
            self.c_change = kwargs.get('c_change')
            self.p_change = kwargs.get('p_change')
            self.hgnc_id = kwargs.get('hgnc_id')
            self.omim_id = kwargs.get('omim_id')
            self.gene_symbol = kwargs.get('gene_symbol')
            
        def to_dict(self):
            """Convert variant information to dictionary for CSV export."""
            return {
                'CHROM': self.chrom,
                'POS': self.pos,
                'ID': self.variant_id,
                'G_CHANGE': self.g_change,
                'REF': self.ref,
                'ALT': self.alt,
                'HGVS': self.hgvs,
                'CLINVAR_ID': self.clinvar_id,
                'CLINICAL_SIGNIFICANCE': self.clinical_significance,
                'STAR_RATING': self.star_rating,
                'REVIEW_STATUS': self.review_status,
                'CONDITIONS_ASSOC': self.conditions_assoc,
                'TRANSCRIPT': self.transcript,
                'C_CHANGE': self.c_change,
                'P_CHANGE': self.p_change,
                'REF_SEQ_ID': self.ref_seq_id,
                'HGNC_ID': self.hgnc_id,
                'OMIM_ID': self.omim_id,
                'GENE_SYMBOL': self.gene_symbol
            }
    
    if not data.get("found", False):
        return VariantInfo(
            hgvs=data.get("hgvs", ""),
            clinvar_id=data.get("clinvar_id", ""),
            clinical_significance="Not found"
        )
    
    # Get data
    summary = data.get("summary", {}).get("eSummaryResult", {}).get("DocumentSummarySet", {}).get("DocumentSummary", {})
    
    # Default values
    result = {
        'hgvs': data.get("hgvs", ""),
        'clinvar_id': data.get("clinvar_id", ""),
        'variant_id': data.get("clinvar_id", ""),
        'clinical_significance': "Unknown",
        'star_rating': "N/A",
        'review_status': "Unknown",
        'conditions_assoc': "Unknown",
        # HGVS subtypes
        'g_change': None,
        'c_change': None,
        'p_change': None
    }
    
    try:
        # Basic info
        result['variant_id'] = summary.get("accession", result['clinvar_id'])
        
        # Extract transcript from title
        title = summary.get("title", "")
        if title:
            match = re.match(r'^([^(]+)', title)
            if match:
                result['transcript'] = match.group(1).strip()
            # try to extract protein change from title like '(p.Ala281Ser)'
            pmatch = re.search(r'\(p\.[^)]*\)', title)
            if pmatch:
                # keep the parentheses or strip them as desired
                result['p_change'] = pmatch.group(0).strip('()')
        
        # Clinical significance
        germline = summary.get("germline_classification", {})
        if germline:
            result['clinical_significance'] = germline.get("description", "Unknown")
            result['review_status'] = germline.get("review_status", "Unknown")
            result['star_rating'] = map_review_status_to_stars(result['review_status'])
            
            # Conditions and OMIM
            trait_set = germline.get("trait_set", {})
            if trait_set:
                traits = trait_set.get("trait", [])
                if not isinstance(traits, list):
                    traits = [traits]
                
                conditions = []
                for trait in traits:
                    name = trait.get("trait_name", "")
                    if name:
                        conditions.append(name)
                    
                    # OMIM ID
                    xrefs = trait.get("trait_xrefs", {}).get("trait_xref", [])
                    if not isinstance(xrefs, list):
                        xrefs = [xrefs]
                    
                    for xref in xrefs:
                        if xref.get("db_source") == "OMIM":
                            result['omim_id'] = xref.get("db_id")
                
                if conditions:
                    result['conditions_assoc'] = "; ".join(conditions)
        
        # Genomic coordinates
        var_set = summary.get("variation_set", {}).get("variation", {})
        if var_set:
            # REF/ALT from SPDI
            spdi = var_set.get("canonical_spdi", "")
            if spdi:
                parts = spdi.split(":")
                if len(parts) >= 4:
                    result['ref_seq_id'] = parts[0]
                    result['pos'] = str(int(parts[1]) + 1) if parts[1].isdigit() else parts[1]
                    result['ref'] = parts[2]
                    result['alt'] = parts[3]
                    # build genomic HGVS (g.) if possible
                    try:
                        if result.get('ref_seq_id') and result.get('pos') and result.get('ref') is not None and result.get('alt') is not None:
                            result['g_change'] = f"{result['ref_seq_id']}:g.{result['pos']}{result['ref']}>{result['alt']}"
                    except Exception:
                        pass
                # try to get c. change from variation block if present
                cchange = var_set.get('cdna_change') or var_set.get('variation_name') or ''
                if cchange:
                    # cdna_change is usually like 'c.841G>T'
                    if 'c.' in cchange:
                        # prefer exact cdna_change
                        result['c_change'] = cchange
                    else:
                        # try to find c. pattern inside the string
                        cm = re.search(r'c\.[0-9+_>ginsdelA-Za-z:-]+', str(cchange))
                        if cm:
                            result['c_change'] = cm.group(0)
            
            # Chromosome
            var_loc = var_set.get("variation_loc", {})
            if var_loc:
                assemblies = var_loc.get("assembly_set", [])
                if not isinstance(assemblies, list):
                    assemblies = [assemblies]
                
                for assembly in assemblies:
                    if assembly.get("status") == "current" or not result.get('chrom'):
                        result['chrom'] = assembly.get("chr", "")
                        if not result.get('pos'):
                            result['pos'] = assembly.get("start", "")
                        break
        
        # Gene info
        genes = summary.get("genes", {}).get("gene", [])
        if not isinstance(genes, list):
            genes = [genes]
        
        for gene in genes:
            if isinstance(gene, dict):
                result['gene_symbol'] = gene.get("symbol", "")
                
                # Fetch HGNC ID from HGNC API using gene symbol
                if result['gene_symbol']:
                    hgnc_id = fetch_hgnc_id(result['gene_symbol'])
                    if hgnc_id:
                        result['hgnc_id'] = hgnc_id
                break
        # if protein change not found from title, try the summary protein_change field
        if not result.get('p_change'):
            prot = summary.get('protein_change')
            if prot:
                # choose first protein change entry if comma-separated
                if isinstance(prot, str):
                    # sometimes it's like 'A206S, A281S' -> we keep as-is
                    result['p_change'] = prot
                else:
                    result['p_change'] = str(prot)
    
    except Exception as e:
        logger.warning(f"Error extracting variant details: {e}")
    
    return VariantInfo(**result)


def map_review_status_to_stars(status):
    """
    Map a ClinVar review status string to a star rating.

    Parameters
    ----------
    status : str
        Review status description from ClinVar.

    Returns
    -------
    str
        Star rating as a string: "0"-"4" or "N/A" if unknown.
    """

    if not status:
        return "0"
    
    status = status.lower()
    if "expert panel" in status:
        return "4"
    elif "multiple submitters" in status and "no conflict" in status:
        return "3"
    elif "multiple submitters" in status:
        return "2"
    elif "single submitter" in status:
        return "1"
    elif "no assertion" in status or "no criteria" in status:
        return "0"
    else:
        return "N/A"


if __name__ == "__main__":  # pragma: no cover
    # Example HGVS variant
    example_hgvs = "NC_000017.11:g.45983420G>T"

    # Fetch ClinVar data and extract info
    result = fetch_clinvar_variant(example_hgvs)
    info = get_variant_info(result)

    # Attributes to display
    attrs = [
        "chrom", "pos", "variant_id", "ref", "alt", "hgvs", "clinvar_id",
        "clinical_significance", "star_rating", "review_status",
        "conditions_assoc", "transcript", "ref_seq_id", "hgnc_id",
        "omim_id", "gene_symbol", "g_change", "c_change", "p_change"
    ]

    print("Variant Information:")
    for attr in attrs:
        print(f"{attr.upper()}: {getattr(info, attr, None)}")
    
