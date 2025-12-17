import itertools
import json
import argparse
import json
import logging
import os
import re
from sys import exit

import pandas as pd

from migenpro.logger_utils import get_logger
from migenpro.ml.parameter_optimisation import ParameterOptimisation

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.INFO)

def argument_parser(args: list[str]=None) -> tuple:
    """
    Argument parser for the migenpro package.
    This function sets up the command line arguments for the main function.
    """

    parser = argparse.ArgumentParser(description="migenpro package main function", add_help=False)
    parser.add_argument("--output", type=str, help="Output directory, default is ./output/", required=False, default="./output/")
    parser.add_argument("--annotation", help="Enables genome annotation mode", required=False, default=False, action="store_true")
    parser.add_argument("--df", help="Enables data formatting mode", required=False, default=False, action="store_true")
    parser.add_argument("--gq", help="Enables genome querying mode", required=False, default=False, action="store_true")
    parser.add_argument("--ml", help="Enables machine learning mode", required=False, default=False, action="store_true")
    parser.add_argument("--fi", help="Enables feature importance assessment mode", required=False, default=False, action="store_true")
    parser.add_argument("--summarise", help="Enables summarising machine learning mode", required=False, default=False, action="store_true")
    parser.add_argument("--debug", help=argparse.SUPPRESS, required=False, default=False, action="store_true")

    args, unparsed_args = parser.parse_known_args(args=args)

    if not any([args.annotation, args.df, args.gq, args.ml, args.fi, args.summarise]):
        # Check if help was requested
        if '--help' in unparsed_args or '-h' in unparsed_args:
            full_parser = argparse.ArgumentParser(
                parents=[parser]
            )
            full_parser.parse_args()
            exit(1)
        parser.error("No main arguments provided. Please specify one of: --annotation, --df, --gq, --ml, or --fi, --summarise.")
    if args.debug:
        logger.debug("Debug mode is enabled. This will produce a lot of output.")
        logger.setLevel(logging.DEBUG)
    if not args.debug:
        logger.setLevel(logging.INFO)

    return args, unparsed_args

def annotation(previously_unparsed_args: argparse.Namespace, output_dir: str,debug=False):
    """
    Takes the phenotype matrix and annotates all the genome IDs that are present in the first column of the phenotype matrix.
    Args:
        output_dir:
        debug:
        args (argparse.Namespace): Command line arguments which include configuration for genome annotation.
    """
    from migenpro.querying.genome_annotation import GenomeAnnotationWorkflow, command_line_interface_annotation

    ga_workflow_args = command_line_interface_annotation(previously_unparsed_args, output_dir)

    workflow = GenomeAnnotationWorkflow(output_dir, ga_workflow_args.threads, ga_workflow_args.cwl_file, debug=debug)

    phenotype_df = pd.read_csv(ga_workflow_args.phenotype_matrix, index_col=0, sep="\t")
    genome_identifiers = set(phenotype_df.index.to_list())
    if os.path.exists(ga_workflow_args.dataset_bin):
        logger.debug("Downloading genomes using ncbi-datasets-cli. ")
        fasta_genome_paths = workflow.download_genomes_from_genome_identifier(genome_identifiers)
    # Ena browser tools.
    else:
        if len(genome_identifiers) > 100:
            logger.warning("Downloading more than 100 genomes from NCBI may take a long time. Please consider using ncbi-datasets-cli by providing the --dataset_bin argument.")
        logger.debug("Downloading genomes using URLs. ")
        regex = r'([A-Z]{3}_\d{9})(_|\.)'
        genome_identifiers = [re.search(regex, genome_identifier).group(1) for genome_identifier in genome_identifiers if re.search(regex, genome_identifier)]

        fasta_genome_paths = [f"http://www.ebi.ac.uk/ena/browser/api/fasta/{genome_identifier}?download=true&gzip=true" for genome_identifier in genome_identifiers]
    genome_hdt_files = workflow.process_batch(fasta_genome_paths)

def load_feature_matrix_and_phenotype_matrix(feature_matrix_path: str, phenotype_matrix_path,output_dir: str) -> tuple:
    """
    Load feature and phenotype matrices, then return subsets of these matrices that share common genomes.

    Args:
        feature_matrix_path (str): Path to the feature matrix file. If None, defaults to a specific path within output_dir.
        phenotype_matrix_path (str): Path to the phenotype matrix file. If None, defaults to a specific path within output_dir.
        output_dir (str): Directory where default matrix files are located if paths are not provided.

    Returns:
        tuple: A tuple containing two elements -
            - feature_matrix_subset: A subset of the feature matrix filtered by common genomes.
            - phenotype_matrix_subset: A subset of the phenotype matrix filtered by common genomes.
    """
    from migenpro.ml.machine_learning_main import FeatureMatrix, PhenotypeMatrix

    if feature_matrix_path:
        feature_matrix = FeatureMatrix(feature_matrix_path)
        logger.debug(f"read {feature_matrix_path}")
    else:
        feature_matrix = FeatureMatrix(os.path.join(output_dir, "feature_matrix.tsv"))
        logger.debug(f"read {os.path.join(output_dir, 'feature_matrix.tsv')}")

    if phenotype_matrix_path:
        phenotype_matrix = PhenotypeMatrix(phenotype_matrix_path)
        logger.debug(f"read {phenotype_matrix_path}")

    else:
        phenotype_matrix = PhenotypeMatrix(os.path.join(output_dir, "phenotype_matrix.tsv"))
        logger.debug(f"read {os.path.join(output_dir, 'phenotype_matrix.tsv')}")

    phenotype_matrix.load_matrix()
    feature_matrix.load_matrix()
    logger.debug("Indices of phenotype_matrix: " + str(phenotype_matrix.get_matrix().index[:10
                if len(phenotype_matrix.get_matrix().index) >= 10 else len(phenotype_matrix.get_matrix().index)]))
    logger.debug("Indices of feature_matrix: " + str(feature_matrix.get_matrix().index[:10
                if len(feature_matrix.get_matrix().index) >= 10 else len(feature_matrix.get_matrix().index)]))

    intersect_genomes_phenotypes = phenotype_matrix.get_intersected_genomes(feature_matrix.file_df)
    intersect_genomes_features = feature_matrix.get_intersected_genomes(phenotype_matrix.file_df)

    feature_matrix_subset = feature_matrix.create_subset(intersect_genomes_features)
    phenotype_matrix_subset = phenotype_matrix.create_subset(intersect_genomes_phenotypes)
    logger.debug("feature matrix subset size: " + str(feature_matrix_subset.shape[0]) + " x " + str(feature_matrix_subset.shape[1]))
    logger.debug("phenotype matrix subset size: " + str(len(phenotype_matrix_subset)))
    return feature_matrix_subset, phenotype_matrix_subset


def machine_learning(unparsed_args: argparse.Namespace, output_dir: str, debug=False):
    """
    Perform machine learning analysis using provided feature and phenotype matrices.
    Args:
        args (argparse.Namespace): Command line arguments which include configuration for machine learning.
    """
    from migenpro.ml.machine_learning_main import command_line_interface_ml, \
        MachineLearningModels

    ml_args = command_line_interface_ml(unparsed_args)
    feature_matrix_subset, phenotype_matrix_subset = load_feature_matrix_and_phenotype_matrix(ml_args.feature_matrix, ml_args.phenotype_matrix, output_dir)

    # Create an instance of MachineLearningModels with the parsed arguments
    if ml_args.param_grids:
        parameter_search_machine_learning = ParameterOptimisation(
            output_dir=output_dir,
            debug=debug
        )
        parameter_search_machine_learning.infer_datasets_from_observations(observed_values=feature_matrix_subset,
                                                                           observed_results=phenotype_matrix_subset,
                                                                           sampling_type=ml_args.sampling_type,
                                                                           threads=ml_args.threads,
                                                                           min_variance=ml_args.min_variance,
                                                                           label=ml_args.label,
                                                                           per_phenotype_frequency=ml_args.abs_frequency)
        with open(ml_args.param_grids, "r") as json_file:
            loaded_param_grids = json.load(json_file)

        optimised_params = parameter_search_machine_learning.perform_halving_grid_search_search(param_grids=loaded_param_grids)

        optimised_params_file_path = os.path.join(output_dir, "optimised_params.json")
        # Write optimised params to file
        with open(optimised_params_file_path, "w") as json_file:
            json.dump(optimised_params, json_file, indent=4)

        machine_learning = MachineLearningModels(output_dir=output_dir, parameter_dictionary=optimised_params,
                                                 debug=debug)
    else:
        machine_learning = MachineLearningModels(dt_depth=ml_args.dt_depth, rf_depth=ml_args.rf_depth,
                                                 gb_depth=ml_args.gb_depth, rf_n_estimators=ml_args.rf_n_estimators,
                                                 gb_n_estimators=ml_args.gb_n_estimators, output_dir=output_dir,
                                                 proportion_train=ml_args.proportion_train,
                                                 rf_min_leaf=ml_args.rf_min_leaf, rf_min_split=ml_args.rf_min_split,
                                                 gb_min_samples=ml_args.gb_min_samples,
                                                 gb_learning_rate=ml_args.gb_learning_rate, debug=debug)

    machine_learning.infer_datasets_from_observations(observed_values=feature_matrix_subset,
                                                      observed_results=phenotype_matrix_subset,
                                                      sampling_type=ml_args.sampling_type, threads=ml_args.threads,
                                                      min_variance=ml_args.min_variance, label=ml_args.label,
                                                      per_phenotype_frequency=ml_args.abs_frequency)

    if ml_args.train:
        machine_learning.train_models()
        machine_learning.save_models()
    elif ml_args.load_model:
        machine_learning.load_model(ml_args.load_model)

    if ml_args.predict:
        logger.info("Starting prediction")
        machine_learning.predict_models_test()
        machine_learning.predict_models_train()


def feature_importance(unparsed_args: argparse.Namespace, output_dir: str, debug=False):
    """
    Perform feature importance analysis on previously created machine learning models.
    Args:
        args (argparse.Namespace): Command line arguments which include configuration for machine learning.

    """
    import glob
    from migenpro.post_analysis.ml_model_analysis import LoadedMachineLearningModel, ModelAnalysis, \
        command_line_interface_model_analysis

    feature_importance_args = command_line_interface_model_analysis(unparsed_args)
    phenotype = "placeholder"
    feature_matrix_subset, phenotype_matrix_subset = load_feature_matrix_and_phenotype_matrix(feature_importance_args.feature_matrix,
                                                                                              feature_importance_args.phenotype_matrix,
                                                                                              output_dir)

    if isinstance(feature_matrix_subset, str):
        feature_matrix_subset = pd.DataFrame(feature_matrix_subset)
    if isinstance(phenotype_matrix_subset, str):
        phenotype_matrix_subset = pd.DataFrame(phenotype_matrix_subset)

    model_paths = glob.glob(os.path.join(output_dir, "**", "*.pkl"), recursive=True)
    if not model_paths:
        raise FileNotFoundError(f"No pickled models found in {output_dir}")

    for model_path in model_paths:
        model = LoadedMachineLearningModel(model_path)

        logger.info("Starting model analysis for " + model.model_name)
        parent_dir = os.path.dirname(model_path)
        model_analysis = ModelAnalysis(model, feature_matrix_subset, phenotype_matrix_subset)
        if model.gini:
            figure_gini_path = (
                    parent_dir
                    + os.sep
                    + f"gini_feature_importance_figure"
                    + model.model_name
                    + ".png"
            )

            gini_figure_summary_path = (
                    parent_dir
                    + os.sep
                    + f"gini_feature_importance_summary_"
                    + model.model_name
                    + ".tsv"
            )
            model_analysis.gini_feature_importance(figure_gini_path, gini_figure_summary_path)
        else:
            print(f"Feature importance analysis for {model.model_name} did not run because model does not "
                         f"have gini feature importance")

def data_formatting(previously_unparsed_args: argparse.Namespace, output_dir: str, debug=False):
    """
    Formats phenotype data by executing queries and processing the output.

    Args:
       args (argparse.Namespace): Command line arguments including output directory and
                           optionally a phenotype HDT file path. 
    """
    from migenpro.querying.query_executor import QueryExecutor, command_line_interface_query_executor
    from migenpro.querying.query_parser import QueryParser

    phenotype_file_path = os.path.join(output_dir, "phenotype.tsv")
    qe_args = command_line_interface_query_executor(previously_unparsed_args)
    qe = QueryExecutor(qe_args.phenotype_query_file, qe_args.sapp_jar, debug=debug)
    qe.execute_sapp_locally_file(hdt_file=qe_args.phenotype_hdt_file, output_file=phenotype_file_path)

    phenotype_output = QueryParser(file_path=phenotype_file_path)
    if qe_args.rel_frequency:
        phenotype_output.filter_by_relative_frequency(qe_args.rel_frequency)
    if qe_args.abs_frequency:
        phenotype_output.filter_by_absolute_frequency(qe_args.abs_frequency)

    phenotype_output.filter_by_species_frequency(qe_args.species_frequency)
    phenotype_output.convert_to_phenotype_matrix()

    if qe_args.phenotype_matrix:
        phenotype_matrix_output_file = qe_args.phenotype_matrix
    else:
        phenotype_matrix_output_file = phenotype_file_path.replace("phenotype.tsv", "phenotype_matrix.tsv")
    phenotype_output.write_phenotype_matrix_to_file(phenotype_matrix_output_file)

def genome_querying(previously_unparsed_args: argparse.Namespace, output_dir: str,debug =False):
    """
    Query hdt(.gz) genomes using SPARQL.

    Args:
       args (argparse.Namespace): Command line arguments including output directory and
                           optionally a phenotype HDT file path.
    """
    from migenpro.querying.query_executor import QueryExecutor, command_line_interface_query_executor

    # Query the various genome hdt files.
    qe_args = command_line_interface_query_executor(previously_unparsed_args)

    genome_dir = qe_args.genome_dir
    qe = QueryExecutor(qe_args.genome_query_file, qe_args.sapp_jar, debug=debug)
    individual_genome_feature_paths = qe.execute_sapp_locally_directory(genome_dir, threads = qe_args.threads)
    # Summarise the various feature results
    # feature_matrix_path = os.path.join(output_dir, "feature_matrix.tsv")
    feature_matrix_path = qe_args.feature_matrix if (qe_args.feature_matrix) else os.path.join(output_dir, "feature_matrix.tsv")
    qe.summarise_feature_files(individual_genome_feature_paths, feature_matrix_path, qe_args.threads)
    logger.info(f"Genome querying successful and summarised to {feature_matrix_path}")
    print(f"Genome querying successful and summarised to {feature_matrix_path}")

def summarise_ml(output_dir: str, debug=False):
    from migenpro.post_analysis.ml_summarise import MachineLearningData, SummaryGraphs

    machine_learning_output_data = MachineLearningData(output_dir)
    for scenario in ["test", "train"]:
        summary_graphs = SummaryGraphs(machine_learning_output_data, output_dir, debug=debug, scenario=scenario)
        summary_graphs.analyse_classifiers()
        summary_graphs.make_method_summary_graphs()
        summary_graphs.output_scores_to_table()
    logger.info(f"Summarised results are located in {output_dir}.")

def main(args: list[str] = None):
    """
    This function sets up the environment, runs queries, processes phenotypes,
    and performs machine learning analysis.
    """
    # Set the working directory to the script's directory
    print("\n\t\t################\n\t\t### MiGenPro ###\n\t\t################\n")
    args, unparsed_args = argument_parser(args)
    os.makedirs(args.output, exist_ok=True)
    if args.df:
        data_formatting(unparsed_args, args.output, args.debug)
    if args.annotation:
        logger.info("Starting genome annotation workflow.")
        annotation(unparsed_args, args.output, args.debug)
    if args.gq:
        logger.info("Starting genome querying workflow.")
        genome_querying(unparsed_args, args.output, args.debug)
    if args.ml:
        logger.info("Starting machine learning workflow.")
        machine_learning(unparsed_args, args.output, args.debug)
    if args.fi:
        logger.info("Starting feature importance analysis.")
        feature_importance(unparsed_args, args.output, args.debug)
    if args.summarise:
        logger.info("Starting summarising machine learning workflow.")
        summarise_ml(args.output, args.debug)

if __name__ == "__main__":
    main()
