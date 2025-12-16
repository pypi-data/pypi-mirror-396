"""
Constants for ABRomics SDK.
"""

FILE_TYPES = {
    'FASTQ': 'FASTQ',
    'FASTQ_GZ': 'FASTQ_GZ', 
    'FASTQSANGER_GZ': 'FASTQSANGER_GZ',
    'FASTA': 'FASTA'
}

SEQUENCING_TYPES = {
    'SINGLE': 'SINGLE',
    'PAIRED_FORWARD': 'PAIRED_FORWARD',
    'PAIRED_REVERSE': 'PAIRED_REVERSE',
    'MATE_PAIR': 'MATE_PAIR'
}

COMMON_METADATA_FIELDS = [
    'species',
    'collection_date',
    'sequencing_technology',
    'sequencing_partner',
    'country',
    'host',
    'sample_type'
]


