"""
CWL-based microbial genome annotation pipeline.

This module provides a command-line interface and workflow execution logic
for annotating microbial genomes using Common Workflow Language (CWL) pipelines.
"""
import argparse
import glob
import gzip
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed, ProcessPoolExecutor
from pathlib import Path
from typing import Union

from cwltool.main import main

from migenpro.logger_utils import get_logger

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.DEBUG)


class GenomeAnnotationWorkflow:
    """Manages execution of genome annotation workflows using CWL.

    Attributes:
        cwl_file (Path | link): Resolved path or link to CWL workflow.
        output_dir (Path): Directory for workflow outputs
        threads (int): Number of parallel threads to use
    """
    def __init__(
            self,
            output_dir: str | Path,
            threads: int = 1,
            cwl_file: str = "https://workflowhub.eu/workflows/1170/git/1/raw/workflow_microbial_annotation_packed.cwl",
            ncbi_dataset_bin: str="dataset",
            debug=False,
            flags= "genome_fasta:\n    class: File\n    location: {}") -> None:
        """Initialize the workflow runner.

        Args:
            output_dir: Directory for workflow outputs
            threads: Number of parallel execution threads

        Raises:
            FileNotFoundError: If local CWL file doesn't exist
            ValueError: For invalid thread counts
        """
        if not debug:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
        self.output_dir = output_dir.resolve() if isinstance(output_dir, Path) else Path(output_dir).resolve()
        self.threads = threads
        self.cwl_file = cwl_file
        self._validate_environment()
        self.flags = flags
        self.ncbi_dataset_bin = ncbi_dataset_bin
        self.ncbi_dataset_bin_url = {"linux-amd64": "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/linux-amd64/datasets",
                                     "macos":       "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/mac/datasets",
                                     "windows":     "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/v2/win64/datasets.exe"}

    def _validate_environment(self) -> None:
        """Validate system environment and dependencies."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_input_template(self, fasta_path: str, yaml_file_path: Path | str):
        """Generate YAML input template for a FASTA file.
        Args:
            yaml_file_path:  yaml file path
            fasta_path: Path to input FASTA file
        """
        template = f"""cwl:tool: {self.cwl_file}\nthreads: {self.threads}\n{self.flags.format(fasta_path)}"""

        with open(yaml_file_path, "w", encoding='utf-8') as f:
            f.write(template)

    @staticmethod
    def execute_workflow(yaml_input: Path, output_dir: str):
        """Execute CWL workflow with given input parameters.

        Args:
            output_dir: Output directory for workflow output.
            yaml_input: Path to YAML input file

        Raises:
            cwltool.errors.WorkflowException: For workflow execution errors
        """

        try:
            abs_output_dir = Path(output_dir).resolve()
            arguments = [
                "--outdir",
                str(output_dir),
                str(yaml_input)
            ]
            exit_code = main(
                argsl=arguments,
                stdout=sys.stdout,
                stderr=sys.stderr,
                logger_handler=logger.handlers[0]
            )

            if exit_code != 0:
                logger.error(f"Workflow execution failed with exit code {exit_code}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

    def _is_dataset_installed(self, if_not_installed: bool = True) -> bool:

        # Determine the operating system
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Determine the appropriate binary name and URL
        if system == "windows":
            self.ncbi_dataset_bin = "datasets.exe"
            url = self.ncbi_dataset_bin_url["windows"]
        elif system == "darwin":  # macOS
            self.ncbi_dataset_bin = "datasets"
            url = self.ncbi_dataset_bin_url["macos"]
        elif system == "linux" and machine == "x86_64":
            self.ncbi_dataset_bin = "datasets"
            url = self.ncbi_dataset_bin_url["linux-amd64"]
        else:
            raise OSError("Unsupported operating system or architecture.")

        if os.path.exists(self.ncbi_dataset_bin):
            return True
        elif if_not_installed:
            logger.info(f"Downloading dataset cli to {self.ncbi_dataset_bin}...")
            urllib.request.urlretrieve(url, self.ncbi_dataset_bin)
            logger.info("Download completed.")
            return True
        else:
            return False

    def process_batch(self, fasta_paths: str | list[str] | set[str], threads: int = 50) -> list[str]:
        """Process a batch of genomes from various input types.
        Args:
            fasta_paths:
                - A single FASTA path or URL
                - A list of FASTA paths or URLs
                - A path to a file containing FASTA paths or URLs
            threads: Number of parallel threads to use (defaults to self.threads if None)
        Raises:
            ValueError: For empty input or invalid formats
        """
        if threads is None:
            threads = self.threads

        def is_url(s: str) -> bool:
            """Check if str is url"""
            return bool(re.match(r'^https?://', s.strip()))

        if isinstance(fasta_paths, (str, Path)):
            fasta_paths = str(fasta_paths).strip()
            path_obj = Path(fasta_paths)
            logger.debug(path_obj)
            logger.debug(f"fasta_paths: {fasta_paths}")

            if not is_url(fasta_paths) and path_obj.is_file() and path_obj.suffix not in [".fasta", ".fa", ".fna",
                                                                                          "fasta.gz", "fna.gz"]:
                # It's a list file containing paths or URLs.
                with open(path_obj, "r") as f:
                    fasta_paths = [line.strip() for line in f if line.strip()]
            else:
                # It's a single FASTA file or URL is fine too.
                fasta_paths = [fasta_paths]
        elif isinstance(fasta_paths, (list, set)):
            fasta_paths = [str(path).strip() for path in fasta_paths]
        else:
            raise ValueError("Invalid input type for fasta_paths")

        if not fasta_paths:
            raise ValueError("No valid FASTA paths or URLs provided")

        # Filter out already annotated genomes
        genomes_to_process = []
        for fasta in fasta_paths:
            logger.debug(f"fasta: {fasta}")
            genome_identifier = re.findall(r"([A-Z]{3}_\d{9})", fasta)[0]

            specific_output_dir = Path(self.output_dir) / "genomes" / genome_identifier[:7] / genome_identifier[
                :10] / f"{genome_identifier}_annotation"
            logger.debug(f"specific_output_dir: {specific_output_dir}")

            # Check if genome is already annotated
            if glob.glob(os.path.join(specific_output_dir, "*.SAPP.hdt.gz")):
                logger.debug(f"Skipping {genome_identifier} - already annotated")
            else:
                genomes_to_process.append((fasta, genome_identifier, specific_output_dir))

        if not genomes_to_process:
            logger.info("All genomes are already annotated, skipping annotation step")
            return glob.glob(os.path.join(self.output_dir, "**/*hdt.gz"))

        logger.info(f"Processing {len(genomes_to_process)} genomes with {threads} threads")

        def process_single_genome(genome_data):
            """Process a single genome annotation"""
            fasta, genome_identifier, specific_output_dir = genome_data

            os.makedirs(specific_output_dir, exist_ok=True)
            yaml_file_path = Path(specific_output_dir) / f"{genome_identifier}.yaml"
            logger.debug(f"yaml_file_path: {yaml_file_path}")

            self.generate_input_template(fasta, yaml_file_path)
            result = self.execute_workflow(yaml_file_path, output_dir=str(specific_output_dir))
            logger.debug(f"Annotation results for {genome_identifier}: {result}")
            return result

        # Process genomes in parallel
        if threads > 1:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=threads) as executor:
                # Submit all annotation jobs
                future_to_genome = {
                    executor.submit(process_single_genome, genome_data): genome_data[1]
                    for genome_data in genomes_to_process
                }

                # Process completed jobs
                for future in as_completed(future_to_genome):
                    genome_id = future_to_genome[future]
                    try:
                        result = future.result()
                        logger.info(f"Completed annotation for {genome_id}")
                    except Exception as exc:
                        logger.error(f"Genome {genome_id} annotation failed: {exc}")
        else:
            # Process sequentially if threads == 1
            for genome_data in genomes_to_process:
                try:
                    result = process_single_genome(genome_data)
                    logger.info(f"Completed annotation for {genome_data[1]}")
                except Exception as exc:
                    logger.error(f"Genome {genome_data[1]} annotation failed: {exc}")

        return glob.glob(os.path.join(self.output_dir, "**/*hdt.gz"))

    def download_genome_from_genome_identifier(self, genome_identifier: str) -> str:
        try:
            # Download only the genome FASTA file
            genome_identifier = re.findall( r"\b([A-Z]{3}_\d{9})\b", genome_identifier)[0]
            specific_output_dir = Path(self.output_dir) / "genomes" / genome_identifier[:7] / genome_identifier[
                                                                                              :10] / f"{genome_identifier}_annotation"
            logger.debug(f"specific_output_dir: {specific_output_dir}")
            downloaded_file = os.path.join(specific_output_dir, f"{genome_identifier}.zip")

            if self._is_dataset_installed():
                command = (f"{self.ncbi_dataset_bin} download genome accession {genome_identifier} --include genome --filename {downloaded_file} --no-progressbar && "
                           f"unzip -q {downloaded_file} -d {specific_output_dir} ")
            else:
                raise FileNotFoundError("No dataset-cli available for downloading genome accessions see: https://www.ncbi.nlm.nih.gov/datasets/docs/v2/command-line-tools/download-and-install/")

            os.makedirs(specific_output_dir, exist_ok=True)
            try:
                result = subprocess.run(
                    command,
                    check=True,
                    shell=True,
                    capture_output=True,
                    text=True
                )

                fasta_file = glob.glob(os.path.join(specific_output_dir, "**", "*.fna"), recursive=True)[0]
                logger.debug(fasta_file)
                with open(fasta_file, 'rb') as f_in:
                    with gzip.open(f"{fasta_file}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(fasta_file)
                return fasta_file + ".gz"

            except subprocess.CalledProcessError as e:
                logger.error(f"Command failed: {e.stderr}")
                return ""
            except Exception as e: # Todo specify exception later on.
                logger.error(f"Failed to download genome accession {genome_identifier} to directory {downloaded_file}")
                logger.error(command)
                logger.error(e)
                return ""

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise e

    def download_genomes_from_genome_identifier(self, genome_identifiers: Union[set[str], list[str]], threads: int = 1) -> \
    list[str]:
        matching_files = glob.glob(os.path.join(self.output_dir, "genomes", "**", "*.fna.gz"), recursive=True)
        existing_genome_ids = set(re.findall( r"\b([A-Z]{3}_\d{9}\.[0-9])\b", matching_file)[0] for matching_file in  matching_files)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Start the download operations and mark each future with its genome identifier
            future_to_id = {
                executor.submit(self.download_genome_from_genome_identifier, genome_id):
                    genome_id for genome_id in genome_identifiers if genome_id not in existing_genome_ids
            }
            for future in as_completed(future_to_id):
                result = future.result()

        # Go over each genome identifier and look for download .fna.gz files.
        return glob.glob(os.path.join(self.output_dir, "genomes", "**", "*.fna.gz"), recursive=True)


def command_line_interface_annotation(previously_unparsed_args: argparse.Namespace, output_dir) -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments

    Raises:
        argparse.ArgumentError: If invalid arguments are provided
    """
    parser = argparse.ArgumentParser(
        description="CWL Workflow Runner for Microbial Genome Annotation",
        epilog="Example: python annotate.py -i genomes.txt -c workflow.cwl -o results"
    )

    parser.add_argument(
        "-t", "--threads",
        default=1,
        help="Number of parallel threads to use (default: %(default)s)",
        type=int,
    )

    parser.add_argument(
         "--cwl_file",
        default="https://workflowhub.eu/workflows/1170/git/1/raw/workflow_microbial_annotation_packed.cwl",
        help="CWL file, can be url to file or absolute path. ",
        type=str
    )
    parser.add_argument(
        "--phenotype_matrix",
        default=Path(output_dir) / "phenotype_matrix.tsv",
        help="Path to the phenotype matrix file. Or a newline separated list of genome identifiers.",
        type=str
    )
    parser.add_argument(
        "--dataset_bin",
        default="dataset_bin",
        help="NCBI dataset cli package for downloading data from NCBI.",
        type=str
    )

    args, _ = parser.parse_known_args()
    return args
