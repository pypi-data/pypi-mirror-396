import argparse
import traceback
from os import path, makedirs, sep

import pandas as pd
from joblib import parallel_backend

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
# Enable experimental HalvingGridSearchCV before importing it
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from sklearn.tree import DecisionTreeClassifier

from migenpro.ml.ml_functions import *


class MachineLearningModels:
    """
    A class representing machine learning models for training and prediction.
    """

    def __init__(self,
                dt_depth: int = 5,
                rf_depth: int = 10,
                gb_depth: int = 5,
                rf_n_estimators: int = 100,
                gb_n_estimators: int = 1000,
                output_dir: str = "output/",
                proportion_train: float = 0.7,
                rf_min_leaf: int = 1,
                rf_min_split: int = 2,
                gb_min_samples: int = 2,
                gb_learning_rate: float = 0.1,
                parameter_dictionary: dict = None,
                debug=False):
        """
        Initializes a MachineLearningModels object.

        Args:
            dt_depth (int): Maximum depth for tree-based models.
            rf_n_estimators (int): Number of trees for ensemble models.
            gb_n_estimators (int): Maximum iterations for boosting models.
            feature_matrix (str): Path to the feature matrix file.
            output_dir (str): Path to save the output results.
            proportion_train (float): Proportion of data to use for training.
            rf_min_leaf (int): Minimum leaf size for random forest.
            rf_min_split (int): Minimum split size for random forest.
            gb_min_samples (int): Minimum number of samples for gradient boosting splits.
            gb_learning_rate (float): Learning rate for gradient boosting.
        """
        if parameter_dictionary:
            self.dt_depth = parameter_dictionary.get("DecisionTreeClassifier").get("max_depth")
            self.rf_depth = parameter_dictionary.get("RandomForestClassifier").get("max_depth")
            self.rf_n_estimators = parameter_dictionary.get("RandomForestClassifier").get("n_estimators")
            self.rf_min_leaf = parameter_dictionary.get("RandomForestClassifier").get("min_samples_leaf")
            self.rf_min_split = parameter_dictionary.get("RandomForestClassifier").get("min_samples_split")
            self.gb_depth = parameter_dictionary.get("GradientBoostingClassifier").get("max_depth")
            self.gb_n_estimators = parameter_dictionary.get("GradientBoostingClassifier").get("n_estimators")
            self.gb_min_samples = parameter_dictionary.get("GradientBoostingClassifier").get("min_samples_split")
            self.gb_learning_rate = parameter_dictionary.get("GradientBoostingClassifier").get("learning_rate")
        else:
            self.dt_depth = dt_depth
            self.rf_depth = rf_depth
            self.gb_depth = gb_depth
            self.rf_n_estimators = rf_n_estimators
            self.gb_n_estimators = gb_n_estimators
            self.rf_min_leaf = rf_min_leaf
            self.rf_min_split = rf_min_split
            self.gb_min_samples = gb_min_samples
            self.gb_learning_rate = gb_learning_rate

        self.classifiers = [RandomForestClassifier, GradientBoostingClassifier, DecisionTreeClassifier]
        self.class_names = []
        self.clf_models = [] # List of trained models
        self.features_used = None
        self.output = output_dir
        self.model_dir = path.join(output_dir)
        self.proportion_train = proportion_train
        self.X_test = pd.DataFrame()
        self.X_train = pd.DataFrame()
        self.Y_test = pd.Series(dtype="float64")
        self.Y_train = pd.Series(dtype="float64")
        self.pickled_models = []
        if debug:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                log_level=logging.DEBUG)
        else:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                     log_level=logging.INFO)
        self.debug = debug

    def infer_datasets_from_observations(self, observed_values: pd.DataFrame, observed_results: pd.DataFrame,
                                         sampling_type: str=None, threads=1, min_variance: int=None, top_percentile: int=None,
                                         label: str="protein_domain", per_phenotype_frequency: int=None):
        """
        Set the datasets that are to be used in the MachineLearningModels object.

        Args:
            per_phenotype_frequency: max phenotype frequency per phenotype.
            observed_values (pd.DataFrame): DataFrame containing the observed feature values.
            observed_results (pd.DataFrame): DataFrame containing the observed results (target values).
            sampling_type (str, optional): Type of sampling to apply. Defaults to None.
                Options include:
                - 'SMOTEN': Synthetic Minority Over-sampling Technique for Nominal and Continuous features.
                - 'undersampling': Randomly reduce the number of samples in the majority class.
                - 'oversampling': Randomly replicate samples from the minority class.
                - 'None': Don't do any over- or under sampling.
            threads (int, optional): Number of parallel threads to run for resampling. Defaults to 1.
            min_variance (int, optional): Minimum variance threshold for feature filtering. Features with variance below this threshold will be removed. Defaults to 1.
            label (str): Label output. Defaults to "protein_domain".

        """
        self.features_used = label
        self.logger.debug("Setting datasets.")
        if per_phenotype_frequency is not None:
            # Calculate the frequency of each phenotype
            phenotype_counts = observed_results.value_counts()
            self.logger.debug(phenotype_counts)
            valid_phenotypes = phenotype_counts[phenotype_counts >= per_phenotype_frequency].index
            self.logger.debug("valid_phenotypes:", valid_phenotypes)
            # Filter the data to include only valid phenotypes
            valid_indices = observed_results.isin(valid_phenotypes)
            observed_values = observed_values[valid_indices]
            observed_results = observed_results[valid_indices]

        observed_results.to_csv(os.path.join(self.output, "observed_results_before_train_test_split.tsv"), sep="\t")
        X_train_raw, self.X_test, Y_train_raw, self.Y_test = train_test_split(
            observed_values,
            observed_results,
            test_size = round(1 - self.proportion_train, 2),
            train_size = round(self.proportion_train, 2),
            stratify=observed_results,
        )
        if (min_variance):
            X_train_filtered = filter_features_by_variance(X_train_raw, min_variance)
        elif (top_percentile):
            X_train_filtered = filter_features_by_mutual_info(X_train_raw, Y_train_raw)
        else:
            X_train_filtered = X_train_raw
        if sampling_type:
            self.logger.info("Now oversampling data. ")
            self.X_train, self.Y_train = resample_data(X_train=X_train_filtered, Y_train=Y_train_raw, sampling_type=sampling_type, factor=1,  n_jobs=threads)
            self.logger.info("Finished oversampling data. ")
        else:
            self.X_train, self.Y_train = X_train_filtered, Y_train_raw

    def set_datasets(self, X_train, Y_train, X_test, Y_test):
        """
        Sets the training and testing datasets for use in the model. This method
        assigns the training and testing feature sets (X) and their corresponding
        labels (Y) to the respective class attributes.

        Args:
            X_train: Training feature set.
            Y_train: Labels corresponding to the training feature set.
            X_test: Testing feature set.
            Y_test: Labels corresponding to the testing feature set.
        """
        self.X_train = X_train
        self.Y_train = Y_train
        self.X_test = X_test
        self.Y_test = Y_test


    def get_datasets(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        return self.X_train, self.X_test, self.Y_train, self.Y_test

    def load_model(self, model_load_path: str):
        """
        Loads a pre-trained model from a file specified in the command-line arguments.

        args:
            model_load_path (str) path to model.
        """
        self.clf_models.append(load_model(model_load_path))

    def get_model_dir(self, classifier_name: str):
        if self.features_used not in self.model_dir:
            return path.join(self.model_dir, self.features_used, classifier_name, "")
        else:
            return path.join(self.model_dir, classifier_name, "")

    def save_models(self):
        """
        Saves trained models to files in the specified directory.
        """
        if len(self.clf_models) == 0:
            raise Exception("No machine learning models available to save. ")
        for clf_model in self.clf_models:
            classifier_name = clf_model.__class__.__name__
            specific_model_dir = self.get_model_dir(classifier_name)
            os.makedirs(specific_model_dir, exist_ok=True)
            model_file = os.path.join(specific_model_dir, classifier_name + "_" + self.features_used + ".pkl")
            save_model(clf_model, model_file)
            # logger.debug(f"Saved model to {model_file}.")
            self.logger.info(f"Saved model to {model_file}.")
            self.pickled_models.append(model_file)

    def train_models(self, n_jobs=1):
        """
        Train a machine learning model with the given X and Y training data
        """
        self.classifiers = [
            DecisionTreeClassifier(max_depth=self.dt_depth),
            RandomForestClassifier(max_depth=self.rf_depth, n_estimators=self.rf_n_estimators,
                                   min_samples_leaf=self.rf_min_leaf, min_samples_split=self.rf_min_split, n_jobs=n_jobs),
            GradientBoostingClassifier(n_estimators=self.gb_n_estimators, min_samples_split=self.gb_min_samples, learning_rate=self.gb_learning_rate, max_depth=self.gb_depth),
        ]

        for classifier in tqdm(self.classifiers, desc="Training models", leave = True):
            if self.debug:
                tqdm.write(f"Training model {classifier}. ")

            classifier_name = classifier.__class__.__name__
            specific_model_dir = self.get_model_dir(classifier_name)

            if not path.isdir(specific_model_dir):
                makedirs(specific_model_dir)

            self.logger.info("Now training model: " + classifier_name)
            with parallel_backend('threading', n_jobs=n_jobs):
                self.clf_models.append(classifier.fit(self.X_train, self.Y_train))
        logger.info("Finished training models.")

    def predict_models_train(self):
        """
        Performs a prediction on the datasets used for training
        """
        self.predict_models(self.X_train, self.Y_train, "train")
        logger.info(f"Results will of train prediction are saved to {self.output}")


    def predict_models_test(self):
        """
        Performs a prediction on the scenario dataset.
        """
        self.predict_models(self.X_test, self.Y_test, "scenario")
        logger.info(f"Results will of scenario prediction are saved to {self.output}")

    def predict_models(self, X_predict: pd.DataFrame, Y_observed: pd.Series, type: str):
        """
        Uses trained models to predict phenotype values for the scenario dataset.
        """
        self.logger.info(f"Predicting phenotype values for the scenario dataset: {type}. ")
        for clf_model in self.clf_models:
            specific_output_dir = self.get_model_dir(clf_model.__class__.__name__)
            output_file = os.path.join(specific_output_dir, clf_model.__class__.__name__ + f"-{type}.tsv")
            self.machine_learning_predict(clf_model=clf_model, output_file=output_file, X_predict=X_predict,
                                     Y_observed=Y_observed)

    def _get_merged_test_results(self, predictions_test, probability_test, class_names: list,
                                    X_predict: pd.DataFrame, Y_observed: pd.Series):
        """
        Merges prediction results with the scenario dataset.

        Args:
            predictions_test: Predicted values.
            probability_test: Predicted probabilities.
            class_names (list): Class names.

        Returns:
            pd.DataFrame: Merged results dataframe.

        """
        try:
            merged_result_test = pd.DataFrame(dtype="float64")
            merged_result_test["Genomes"] = X_predict.index.values
            merged_result_test["Observation"] = Y_observed.tolist()
            merged_result_test["ObservedString"] = Y_observed.tolist()
            merged_result_test["Prediction"] = predictions_test.tolist()
            merged_result_test["PredictedString"] = predictions_test

            # Store the various probability intervals for the different classes.
            _, columns = probability_test.shape
            for probability_column in range(0, columns):
                merged_result_test[class_names[probability_column]] = probability_test[:, probability_column].tolist()

            merged_result_test["ConfidencePrediction"] = merged_result_test.apply(lambda row: row[row['PredictedString']], axis=1).tolist()

        except Exception:
            logging.error(traceback.format_exc())
            raise Exception(f"Something went wrong while reading the results of a machine learning model. ")

        return merged_result_test

    def _save_merged_results(self, merged_result_test: pd.DataFrame, output_file: str):
        """
        Saves merged prediction results to a file.

        Args:
            merged_result_test (pd.DataFrame): Merged results dataframe.
            output_file (str): Path to the output file.
        """
        output_dir = sep.join(output_file.split(sep)[:-1])
        if not path.isdir(output_dir):
            makedirs(output_dir)

        try:
            merged_result_test.to_csv(output_file, sep="\t")
        except Exception as e:
            logging.error(traceback.format_exc())
            logging.error("Saving of the output failed for " + output_file)

    def machine_learning_predict(self, clf_model, output_file: str, X_predict: pd.DataFrame, Y_observed: pd.Series):
        """
        Predict phenotype values with the given models using X_test to predict and verify these result with Y_test the results are summarized and written to the output file in tsv format.

        Args:
            clf_model: Trained classifier model.
            output_file (str): Path to save the prediction results.
        """

        classifier_name = clf_model.__class__.__name__
        class_names = list(clf_model.classes_)

        # Remove any features not encountered while training the model.
        clean_X_test = feature_conversion(clf=clf_model, feature_data=X_predict)

        try:
            predictions_test = clf_model.predict(X=clean_X_test)
            probability_test = clf_model.predict_proba(X=clean_X_test)

            ############################ Data export ############################
            merged_result_test = self._get_merged_test_results(predictions_test, probability_test, class_names,
                                                               X_predict,
                                                               Y_observed)

            self._save_merged_results(merged_result_test, output_file)
            self.logger.info(f"Saved the merged results of {classifier_name} to {output_file}.")
        except Exception as e:
            logging.error(traceback.format_exc())
            self.logger.info("prediction failed for " + classifier_name)

    def get_pickled_models(self):
        return self.pickled_models

class MatrixFile:
    """
    A class representing a generic matrix file.

    Attributes:x
        file_path (str): The file path to the matrix file.
        file_df (DataFrame): The DataFrame containing the data loaded from the file.
    """

    def __init__(self, file_path: str, debug: bool = False):
        """
        Initializes a MatrixFile object.

        Args:
            file_path (str): The file path to the matrix file.
        """
        self.file_path = file_path
        if not path.exists(self.file_path):
            raise Exception(f"File {self.file_path} does not exist.")
        self.file_df = pd.DataFrame()
        if debug:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                log_level=logging.DEBUG)
        else:
            self.logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log",
                                     log_level=logging.INFO)

    def load_matrix(self):
        """
        Loads the matrix data from the file into the file_df attribute.
        """
        if self.file_path.endswith(".gz"):
            self.file_df = pd.read_csv(self.file_path, delimiter="\t", index_col=0, compression="gzip")
        else:
            self.file_df = pd.read_csv(self.file_path, delimiter="\t", index_col=0)
        self.file_df.index = self.file_df.index.str.strip()
        if "." in self.file_df.index[2]:
            self.file_df.index = [genome_id.split('.', 1)[0] for genome_id in self.file_df.index]

    def create_subset(self, indices):
        return self.file_df.loc[indices]

    def get_intersected_genomes(self, intersect_df):
        """
        Retrieves the intersected genomes between the phenotype matrix and a feature matrix.

        Args:
            intersect_df (DataFrame): A DataFrame to intersect with.

        Returns:
            list: A list of intersected genome IDs.
        """

        # Create dictionaries with stripped genome IDs as keys and full genome IDs as values
        intersect_df_dict = {genome[:13]: genome for genome in intersect_df.index.str.strip()}
        file_df_dict = {genome[:13]: genome for genome in self.file_df.index.str.strip()}
        common_keys = set(intersect_df_dict.keys()) & set(file_df_dict.keys())
        matched_genomes = [file_df_dict[key] for key in common_keys]

        return matched_genomes

    def get_matrix(self):
        return self.file_df

class FeatureMatrix(MatrixFile):
    """
    A class representing a feature matrix file.

    Attributes:
        features_used (str): The features used in the matrix.
    """

    def __init__(self, file_path):
        """
        Initializes a FeatureMatrix object.

        Args:
            file_path (str): The file path to the feature matrix file.
        """
        super().__init__(file_path)
        self.features_used = path.splitext(path.basename(self.file_path))[0]


class PhenotypeMatrix(MatrixFile):
    """
    A class representing a phenotype matrix file.
    """

    def __init__(self, file_path=""):
        """
        Initializes a PhenotypeMatrix object.

        Args:
            file_path (str, optional): The file path to the phenotype matrix file. Defaults to "".
        """
        super().__init__(file_path)

    def create_subset(self, row_names: list):
        """
        Returns the given indices rows from the file_df dataframe.
        """
        phenotype = self.file_df.columns[0]
        duplicates_mask = ~self.file_df.loc[row_names][phenotype].index.duplicated(keep='first')
        intermediate_df = self.file_df.loc[row_names][phenotype][duplicates_mask]
        intermediate_df.index = intermediate_df.index.str[:13]
        return intermediate_df

def command_line_interface_ml(previously_unparsed_args: argparse.Namespace) -> argparse.Namespace:
    """
    Parse and validate command-line arguments for the MachineLearningModels class.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Command-line interface for MachineLearningModels.')

    # Model parameters
    parser.add_argument('--dt_depth', type=int, default=5,
                        help='Maximum depth for decision tree models.')
    parser.add_argument('--rf_depth', type=int, default=10,
                        help='Maximum depth for random forest models.')
    parser.add_argument('--gb_depth', type=int, default=5,
                        help='Maximum depth for gradient boosting models.')
    parser.add_argument('--rf_n_estimators', type=int, default=100,
                        help='Number of trees for ensemble models.')
    parser.add_argument('--gb_n_estimators', type=int, default=1000,
                        help='Maximum iterations for boosting models.')
    parser.add_argument('--output', type=str, default="output/",
                        help='Path to save the output results.')
    parser.add_argument('--proportion_train', type=float, default=0.8,
                        help='Proportion of data to use for training.')
    parser.add_argument('--rf_min_leaf', type=int, default=1,
                        help='Minimum leaf size for random forest.')
    parser.add_argument('--rf_min_split', type=int, default=2,
                        help='Minimum split size for random forest.')
    parser.add_argument('--gb_min_samples', type=int, default=2,
                        help='Minimum number of samples for gradient boosting splits.')
    parser.add_argument('--gb_learning_rate', type=float, default=0.1,
                        help='Learning rate for gradient boosting.')


    # File paths
    parser.add_argument('--label', type=str, default='protein_domains',
                        help='Label of output directory')
    parser.add_argument('--abs_frequency', type=int, default=500,
        help='Absolute threshold for filtering phenotype. Default %(default)s')
    parser.add_argument('--min_variance', type=float, default=None, help="Variance threshold used for feature selection. ")
    parser.add_argument('--top_percentile', type=int, default=None, help="Percentage of top MI features to keep")
    parser.add_argument("--threads", type=int,  default=1,
        help="Number of parallel threads to use (default: %(default)s)")
    parser.add_argument('--load_model', type=str, default=None,
                        help='Machine learning model to load in pickle format from the scikit learn library. ')
    parser.add_argument('--train', action='store_true', help='Train new models.')
    parser.add_argument('--predict', action='store_true',
                        help='Let the machine learning classifiers predict the given phenotype matrix, if you want to provide your own models use the `--load_model` flag. ')
    phen_arg = parser.add_argument('--phenotype_matrix', type=str, default=None,
                        help='Path to the phenotype matrix file.')
    feat_arg = parser.add_argument('--feature_matrix', type=str, default=None,
                        help='Path to the feature matrix file.')
    parser.add_argument('--sampling_type', type=str, default='',
                        choices=['', 'oversample', 'undersample', 'SMOTEN', 'auto', 'smote', 'SMOTE', 'SMOTENC'], help='Type of sampling to apply.')
    parser.add_argument('--hyperparameter_search', type=str, default="halvingridsearch",
                        choices=['gridsearch', 'halvingridsearch'],
                        help='Type of hyperparameter search to perform.')
    param_grid_arg = parser.add_argument("--param_grids", type=str, default=None,
                        help="Enable parameter grid search and provide bounds for halving grid search. ", required=False)

    args, _ = parser.parse_known_args(previously_unparsed_args)
    if args.param_grids and not path.exists(args.param_grids):
        raise argparse.ArgumentError(argument=param_grid_arg,  message=", ".join([args.param_grids, "is not a valid file"]))
    if args.phenotype_matrix and not path.exists(args.phenotype_matrix):
        raise argparse.ArgumentError(argument=phen_arg,  message=", ".join([args.phenotype_matrix, "is not a valid file"]))
    if args.feature_matrix and not path.exists(args.feature_matrix):
        raise argparse.ArgumentError(argument=feat_arg,  message=", ".join([args.feature_matrix, "is not a valid file"]))
    if args.rf_min_split <= 1:
        raise argparse.ArgumentError(argument=feat_arg,  message=", ".join([str(args.rf_min_split), "You can only split with 2 or more files. "]))

    return args
