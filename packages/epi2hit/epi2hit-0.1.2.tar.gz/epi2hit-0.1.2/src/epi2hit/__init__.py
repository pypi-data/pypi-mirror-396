"""
epi2hit: utilities for epi-TSG / methylation analysis.
"""

from .core import (
    read_dataset,
    find_open_chromatin_probes,
    probes2genes,
    prelim_filters,
    pomerantz_state,
    process_probes,
    resolve_duplicates,
    annotate_probes_with_loops,
    prepare_TCGA_dict,
    lin_reg,
    slice_probes_with_loops_by_linreg,
    methylation,
    filter_probes_by_methylation,
)

__all__ = [
    "read_dataset",
    "find_open_chromatin_probes",
    "probes2genes",
    "prelim_filters",
    "pomerantz_state",
    "process_probes",
    "resolve_duplicates",
    "annotate_probes_with_loops",
    "prepare_TCGA_dict",
    "lin_reg",
    "slice_probes_with_loops_by_linreg",
    "methylation",
    "filter_probes_by_methylation",
]

