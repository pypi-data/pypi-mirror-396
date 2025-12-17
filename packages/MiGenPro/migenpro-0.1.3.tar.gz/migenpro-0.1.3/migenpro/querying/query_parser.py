"""Parse query outputs into phenotype and feature matrices with filters.

Lint-focused cleanups: encoding specifiers, logging formatting, and small
style fixes without changing behaviour.
"""
import logging
from collections import defaultdict
from os import path

import numpy as np
from ete4 import NCBITaxa

from migenpro.logger_utils import get_logger


class QueryParser:
    """
    A class to handle query output data and convert it into different formats.

    Attributes:
        data (numpy.ndarray): The data loaded from the file.
        headers (list): The headers of the data.
        feature_matrix (numpy.ndarray): The feature matrix generated from the data.
    """

    def __init__(self, file_path: str, phenotype_trim_below_percentage = 0.1, debug=False):
        """
        Initializes the QueryParser object with data from the specified file.

        Args:
            file_path (str): The path to the file containing the data.
        """
        if debug:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                log_level=logging.DEBUG)
        else:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                     log_level=logging.INFO)

        abs_path = path.abspath(file_path)
        self.logger.debug("relative path: %s -> absolute path: %s", file_path, abs_path)
        self.data = np.loadtxt(abs_path, delimiter="\t", dtype=str, skiprows=1)
        with open(abs_path, 'r', encoding='utf-8') as file:
            self.headers = file.readline().strip().split('\t')
        self.feature_matrix = None
        self.phenotype_matrix = None
        self.phenotype_trim_below_percentage = phenotype_trim_below_percentage # If a phenotype makes up less than x% of the total do not incorporate it in the analysis. 

    def filter_by_relative_frequency(self, threshold: float):
        column_idx = 1
        if column_idx >= self.data.shape[1]:
            raise IndexError(f"Column index {column_idx} is out of bounds for the array with shape {self.data.shape}")

        unique, counts = np.unique(self.data[:, column_idx], return_counts=True)

        relative_frequencies = counts / self.data.shape[0]
        valid_values = unique[relative_frequencies >= threshold]
        deleted_values =  "-".join(unique[relative_frequencies < threshold])
        min_thres = int(len(self.data) * threshold)
        if len(deleted_values) > 0:
            self.logger.debug(
                "Phenotype(s) that were removed because these had less than %d instances: %s",
                min_thres,
                deleted_values,
            )
        else:
            self.logger.debug(
                "No phenotypes were found that had less than %d instances",
                min_thres,
            )

        self.data = self.data[np.isin(self.data[:, column_idx], valid_values)]

    @staticmethod
    def _get_species_taxid(taxid: int | str, ncbi: NCBITaxa):
        """
        Get the species-level taxid for a given taxid using ete4.

        Args:
            taxid: The input taxid (as a string or number).
            ncbi: An initialized NCBITaxa object.

        Returns:
            The species-level taxid if found, None if other or not found. .
        """
        try:
            taxid = int(taxid)
            lineage = ncbi.get_lineage(taxid)
            ranks = ncbi.get_rank(lineage)
            for tid, rank in ranks.items():
                if rank == 'species':
                    return tid
            return None
        except (ValueError, KeyError):
            return None

    def filter_by_species_frequency(self, threshold: int, species_column_index: int = None):
        """
        Filters the NumPy array to retain the first 'threshold' occurrences of each species.
        Uses ete4 to interpret taxids at the species level.

        Args:
            threshold (int): The maximum number of occurrences to retain for each species.
            species_column_index (int): The index of the column containing species taxids. If None, the last column is used.
        """
        if species_column_index is None:
            species_column_index = self.data.shape[1] - 1

        species_column = self.data[:, species_column_index]
        ncbi = NCBITaxa()

        unique_taxids = set()
        for taxid in species_column:
            try:
                if isinstance(taxid, (np.integer, np.floating)):
                    taxid = int(taxid)
                unique_taxids.add(str(taxid))
            except Exception:
                continue

        taxid_to_species = {}
        for taxid in unique_taxids:
            species_taxid = self._get_species_taxid(int(taxid), ncbi)
            if species_taxid is not None:
                taxid_to_species[taxid] = species_taxid

        species_counts = defaultdict(int)
        rows_to_keep = []

        for index, value in enumerate(species_column):
            taxid = str(value)
            if taxid in taxid_to_species:
                species_taxid = taxid_to_species[taxid]
                if species_counts[species_taxid] < threshold:
                    rows_to_keep.append(index)
                    species_counts[species_taxid] += 1

        filtered_data = self.data[rows_to_keep]
        self.data = filtered_data

    def filter_by_absolute_frequency(self, threshold: int):
        n_rows, _  = self.data.shape
        relative_threshold = float(threshold/n_rows)
        self.filter_by_relative_frequency(relative_threshold)

    def convert_to_phenotype_matrix(self):
        """
        Converts the data to a phenotype matrix by replacing dots with underscores
        and stripping quotes in the '?accession' column.
        """
        # Replace dots with underscores and strip quotes in the '?accession' column
        self.phenotype_matrix = self.data.copy()
        if self.phenotype_matrix.size == 0:
           raise ValueError("No data found in the phenotype matrix.")
        self.phenotype_matrix[:, self.headers.index('?accession')] = np.char.replace(self.phenotype_matrix[:, self.headers.index('?accession')], '.', '_')
        self.phenotype_matrix[:, self.headers.index('?accession')] = np.char.strip(self.phenotype_matrix[:, self.headers.index('?accession')], '"')

    def convert_to_feature_matrix(self):
        """
        Converts the data to a feature matrix where rows represent genomes and
        columns represent accessions.
        """
        # Extract unique accessions and create columns
        accessions = np.unique(self.data[:, self.headers.index('?accession')])
        columns = np.insert(accessions, 0, "Genomes")

        # Create a dictionary to map genome IDs to rows
        genome_dict = {genome: idx for idx, genome in enumerate(np.unique(self.data[:, self.headers.index('?genomeID')]))}

        # Initialize the feature matrix with zeros
        self.feature_matrix = np.zeros((len(genome_dict), len(columns)), dtype=object)
        self.feature_matrix[:, 0] = list(genome_dict.keys())

        # Fill the feature matrix with counts
        for row in self.data:
            genome_id = row[self.headers.index('?genomeID')]
            accession = row[self.headers.index('?accession')]
            count = row[self.headers.index('?count')]
            self.feature_matrix[genome_dict[genome_id], columns.tolist().index(accession)] = count
        self.feature_matrix[0] = columns

    def write_feature_matrix_to_file(self, output_file: str):
        """
        Writes the feature matrix to a file.

        Args:
            output_file (str): The path to the output file.
        """
        np.savetxt(output_file, self.feature_matrix, delimiter="\t", fmt='%s')

    def write_phenotype_matrix_to_file(self, output_file: str):
        """
        Writes the original data to a file.

        Args:
            output_file (str): The path to the output file.
        """
        header = "genome\tphenotype"
        np.savetxt(output_file, self.phenotype_matrix, delimiter="\t", fmt='%s', header=header)


if __name__ == "__main__":
    phenotype_output = QueryParser(file_path="/home/mike/git/genopro/data/phenotype_output/motility_output/phenotype.tsv")
    # phenotype_output.filter_by_relative_frequency(0.005)
    phenotype_output.filter_by_absolute_frequency(500)
    phenotype_output.convert_to_phenotype_matrix()
    phenotype_output.write_phenotype_matrix_to_file("//home/mike/git/genopro/data/phenotype_output/motility_output/phenotype_matrix.tsv")
