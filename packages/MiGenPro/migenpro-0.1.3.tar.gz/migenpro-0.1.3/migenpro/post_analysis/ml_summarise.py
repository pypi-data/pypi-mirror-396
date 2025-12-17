"""Summarise machine learning outputs and generate performance graphs.

This module parses ML result TSV files, computes metrics, and produces
summary plots. Changes focus on linting without altering functionality.
"""
# Standard library imports
import argparse
import glob
import logging
from os import path, sep, makedirs

# Third-party imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    precision_score,
    recall_score,
    matthews_corrcoef,
    precision_recall_curve,
    roc_curve,
    auc,
    confusion_matrix,
    roc_auc_score,
)

from migenpro.logger_utils import get_logger

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.INFO)

class MachineLearningData:
    """
    A class for parsing machine learning output files and extracting data.

    Attributes:
        output_dir_path (str): The directory path where the output files are located.
        characteristic (str): A characteristic of the machine learning data.
    """

    def __init__(self, output_dir_path: str):
        """
        Initializes a MachineLearningData object.

        Args:
            output_dir_path (str): The directory path where the output files are located.
        """
        self.output_dir_path = output_dir_path
        self.characteristic = "machine_learning_summary"
        self.classifiers = self.list_output_classifiers(self.output_dir_path)

    @staticmethod
    def list_output_classifiers(output_dir: str):
        """
        List the classifier directories in the output directory, excluding certain subdirectories.

        Args:
            output_dir (str): The path to the output directory.

        Returns:
            list: A list of classifier directory names.
        """


        # Use glob to find all directories that end with "Classifier"
        pattern = path.join(output_dir, "**", "*Classifier")
        classifiers = glob.glob(pattern, recursive=True)

        # Filter out non-directories
        return list({d.split(sep)[-1] for d in classifiers if path.isdir(d)})

    @staticmethod
    def output_file_data_parsing(list_of_files: list) -> dict:
        """
        Parses output files in the specified directory and extracts relevant data.

        Returns:
            dict: A dictionary containing the following keys:
            - 'observed_values' (pd.Series): Series of observed values from the files
            - 'predicted_values' (pd.Series): Series of predicted values from the files  
            - 'observed_values_string' (pd.Series): Series of observed values as strings
            - 'probability_classes' (pd.DataFrame): DataFrame containing probability class data
        """
        observed_values = pd.Series(dtype="float64")
        observed_values_string = pd.Series(dtype="str")
        predicted_values = pd.Series(dtype="float64")
        probability_classes = pd.DataFrame()
        source_files = []

        for file in list_of_files:
            try:
                source_files.append(file)
                ml_output_df = pd.read_csv(file, delimiter="\t", header=0)
                columns = ml_output_df.columns

                # Check for required columns
                if not all(col in columns for col in ["Observation", "Prediction", "ObservedString"]):
                    logger.error("Skipping file %s: Missing required columns", file)
                    continue

                # Append data
                observed_values = pd.concat([observed_values, ml_output_df["Observation"]], ignore_index=True)
                predicted_values = pd.concat([predicted_values, ml_output_df["Prediction"]], ignore_index=True)
                observed_values_string = pd.concat(
                    [observed_values_string, ml_output_df["ObservedString"]], ignore_index=True
                )


                # Check length consistency
                if len(ml_output_df["Observation"]) != len(ml_output_df["Prediction"]):
                    logger.error("Warning: Mismatch between observed and predicted values in file: %s", file)

                # Get class names (columns 6 to second-to-last)
                class_names = ml_output_df.columns[6:-1]
                if len(class_names) > 0:
                    # Only include columns that actually exist
                    valid_class_names = [col for col in class_names if col in ml_output_df.columns]
                    if valid_class_names:
                        new_prob_classes = ml_output_df[valid_class_names]
                        probability_classes = pd.concat([probability_classes, new_prob_classes], ignore_index=True)

            except Exception as e:
                logger.error("Error processing file %s: %s", file, str(e))
                continue

        # Reset indexes for Series
        observed_values = observed_values.reset_index(drop=True)
        predicted_values = predicted_values.reset_index(drop=True)
        observed_values_string = observed_values_string.reset_index(drop=True)

        # Return results as a dictionary
        return {
            'source_files': source_files,
            'observed_values': observed_values,
            'predicted_values': predicted_values,
            'observed_values_string': observed_values_string,
            'probability_classes': probability_classes
        }

    def get_results_for_method(self, method: str, test:  str="scenario") -> dict:
        """
        Retrieves results for a method used from the output files.

        Args:
            method (str): The method for which results are requested.
            test (bool): default is True, whether you only to have only the scenario case if False uses the train output.
        Returns:
            Tuple: A tuple containing observed values, predicted values, observed values,
                   and probability classes for the specified method.
        Raises:
            ValueError: If the method file is not present.

        """
        # Support both historical naming ("*-{scenario}-output.tsv") and simpler ("*-{scenario}.tsv")
        patterns = [f"*-{test}-output.tsv", f"*-{test}.tsv"]
        matched_files = []
        for file_search in patterns:
            matched_files.extend(
                [
                    output_file
                    for output_file in glob.glob(path.join(self.output_dir_path, "**", file_search), recursive=True)
                    if method in output_file
                ]
            )

        if not matched_files:
            raise FileNotFoundError(
                "No output files were found for method '{}' using patterns {}.".format(method, ", ".join(patterns))
            )

        return self.output_file_data_parsing(matched_files)


class SummaryGraphs:
    def __init__(self, machine_learning_output_data: MachineLearningData, output_dir: str, scenario: str = 'test', debug=False):
        self.machine_learning_output_data = machine_learning_output_data
        self.scenario = scenario
        self._init_metrics_storage()
        self._setup_directories(output_dir)
        self._init_plotting_resources()
        if debug:
            logger.setLevel(logging.DEBUG)

    def _init_metrics_storage(self):
        """Initialize all metric storage containers"""
        self.metrics = []
        self.roc_data = []
        self.prc_data = []
        self.classifiers = self.machine_learning_output_data.classifiers

    def _setup_directories(self, output_dir):
        """Create required output directories"""
        self.output_dir = output_dir
        self.graph_output_dir = path.join(output_dir, "graphs")
        self._create_directory(self.graph_output_dir)

    def _init_plotting_resources(self):
        """Initialize plotting-related resources"""
        self.hatch_gradients = [
            '/', '\\', '|', '---', '+', 'x', 'o', '.', '-', '//',
            'xx', '\\\\', '--', '..', '++', 'oooo', '....', '\\\\\\\\',
            '//..', 'o++x', '--oo', '|xx+', '\\\\\\|', 'x.x.', '++//',
            '|\\--', 'o--|', '.o\\x', '+.oo', 'o//o', '|++|', '.x--',
            '+\\\\+', '.-x-', '\\x\\o', 'xxxx', '----', '\\\\//', '||++'
        ]

    def _create_directory(self, dir_path):
        """Utility for safe directory creation"""
        if not path.exists(dir_path):
            makedirs(dir_path)

    def output_scores_to_table(self):
        """Export metrics to TSV file"""
        if not self.metrics:
            self.analyse_classifiers()

        output_file = path.join(self.graph_output_dir, f"{self.scenario}-summary.tsv")
        pd.DataFrame(self.metrics).to_csv(output_file, index=False)

    def make_method_summary_graphs(self):
        """Generate all summary bar charts"""
        metrics_df = pd.DataFrame(self.metrics)
        self._create_bar_chart(metrics_df, "f1_score", "F1", color=["black", "red", "green", "blue", "cyan"])
        self._create_bar_chart(metrics_df, "accuracy", "Accuracy", hatch=True)
        self._create_bar_chart(metrics_df, "auc", "AUC", hatch=True)
        self._create_bar_chart(metrics_df, "mcc", "Matthew Correlation Coefficient", hatch=True)

    def _create_bar_chart(self, metrics_df, metric, title, color="grey", hatch=False):
        """Generic bar chart creation"""
        fig, ax = plt.subplots(figsize=(10, 6))

        if hatch:
            hatches = self.hatch_gradients[:len(metrics_df)]
            ax.bar(self.classifiers, metrics_df[metric], color=color, hatch=hatches)
        else:
            ax.bar(self.classifiers, metrics_df[metric], color=color)

        ax.set_title(f"{title} Chart")
        ax.set_ylabel(title)
        ax.set_ylim(0.5, 1)
        plt.xticks(rotation=55, horizontalalignment="center")

        self._save_figure(fig, f"BarChart{metric.upper()}")

    def _save_figure(self, fig, chart_type):
        """Save figure with standardized naming"""
        fig.savefig(
            path.join(self.graph_output_dir,
                      f"Summary_{self.machine_learning_output_data.characteristic}_{chart_type}.png"),
            bbox_inches="tight",
            dpi=1200
        )
        plt.close(fig)

    def analyse_classifiers(self):
        """Main analysis entry point"""
        for classifier in self.classifiers:
            self._process_classifier(classifier)

        self._plot_classifiers_performance(
            pd.DataFrame(self.metrics),
            pd.DataFrame(self.roc_data),
            pd.DataFrame(self.prc_data)
        )

    def _process_classifier(self, classifier: str):
        """Process individual classifier results"""
        results = self.machine_learning_output_data.get_results_for_method(classifier, self.scenario)

        if results.get("observed_values").empty:
            raise FileNotFoundError(f"Missing results for {classifier}")

        metrics = self._calculate_basic_metrics(results)
        self._process_probability_data(classifier, results, metrics)
        self.metrics.append(metrics)

    def _create_classifier_directory(self, classifier):
        """Create classifier-specific output directory"""
        classifier_dir = path.join(self.graph_output_dir, classifier)
        self._create_directory(classifier_dir)
        return classifier_dir

    # @staticmethod
    def _get_true_probability(self, results):
        """
        Extracts the probabilities for each class. This method ensures the output
        is suitable for `roc_auc_score` with `multi_class='ovr'`, expecting a 2D array
        where each column corresponds to the probability of a specific class.
        """
        probability_classes = pd.DataFrame(results["probability_classes"].columns.values)
        observed_values = results['observed_values']

        # Validate input lengths
        if len(probability_classes) != len(observed_values):
            raise ValueError(
                f"Length mismatch: probability_classes={len(probability_classes)}, observed_values={len(observed_values)}")

        try:
            observed_values_str = observed_values.astype(
                str) if not observed_values.dtype == 'object' else observed_values

            probability_true_class = [
                probability_classes.iloc[idx].get(str(true_class), 0.0)
                for idx, true_class in enumerate(observed_values_str)
            ]
            if all(p is None or p == 0.0 for p in probability_true_class):
                logger.warning("No valid probabilities found for true classes. AUC will be set to 0.0")
                probability_true_class = [0.0] * len(observed_values)
        except Exception as e:
            logger.error("Error extracting probabilities: %s", e)
            probability_true_class = [0.0] * len(observed_values)

        return probability_true_class

    def _calculate_basic_metrics(self, results):
        """Calculate basic classification metrics"""
        # probability_true_class = self._get_true_probability(results)
        if len(pd.DataFrame(results["probability_classes"].columns.values)) > 2:
            probs = results['probability_classes']
            auc_score = roc_auc_score(results["observed_values"], probs, multi_class='ovr')
        else:
            probs = results['probability_classes']
            auc_score = roc_auc_score(results["observed_values"], probs.iloc[:, 1])

        return {
            "classifier": results["source_files"],
            "f1_score": f1_score(results["observed_values"], results["predicted_values"], average="micro"),
            "accuracy": accuracy_score(results["observed_values"], results["predicted_values"]),
            "precision": precision_score(results["observed_values"], results["predicted_values"], average="micro"),
            "recall": recall_score(results["observed_values"], results["predicted_values"], average="micro"),
            "mcc": matthews_corrcoef(results["observed_values"], results["predicted_values"]),
            'auc': auc_score
        }

    def _process_probability_data(self, classifier, results, metrics):
        """Handle probability-based metrics and curves"""
        if len(results["probability_classes"].columns) > 2:
            self._process_multiclass_case(classifier, results)
        else:
            self._process_binary_case(classifier, results, metrics)

    def _process_multiclass_case(self, classifier, results):
        """Handle multiclass classification metrics"""
        for i, class_name in enumerate(results["probability_classes"].columns):
            observed_binary = [1 if class_name == obs else 0 for obs in results["observed_values_string"]]
            self._calculate_curve_metrics(classifier, class_name, observed_binary,
                                          results["probability_classes"].iloc[:, i])

    def _process_binary_case(self, classifier, results, metrics):
        """Handle binary classification metrics"""
        tn, fp, _, _ = confusion_matrix(results["observed_values"], results["predicted_values"]).ravel()
        metrics["specificity"] = tn / (tn + fp)
        positive_class = results["probability_classes"].columns[1]
        observed_binary = [1 if positive_class == obs else 0 for obs in results["observed_values_string"]]
        self._calculate_curve_metrics(classifier, positive_class, observed_binary,
                                      results["probability_classes"].iloc[:, 1])

    def _calculate_curve_metrics(self, classifier, class_name, observed_binary, probabilities):
        """Calculate ROC and PRC metrics"""
        precision, recall, _ = precision_recall_curve(observed_binary, probabilities)
        fpr, tpr, _ = roc_curve(observed_binary, probabilities)
        auc_value = auc(fpr, tpr)

        self.roc_data.append({
            "classifier": classifier,
            "class": class_name,
            "fpr": fpr,
            "tpr": tpr,
            "auc": auc_value
        })

        self.prc_data.append({
            "classifier": classifier,
            "class": class_name,
            "precision": precision,
            "recall": recall
        })

    def _plot_classifiers_performance(self, metrics_df, roc_data_df, prc_data_df):
        """Coordinate performance plotting"""
        self._plot_roc_curves(roc_data_df)
        self._plot_prc_curves(prc_data_df)
        self._plot_metric_summary(metrics_df)

    def _plot_roc_curves(self, roc_data_df):
        """Plot ROC curves for all classifiers"""
        fig, ax = plt.subplots(figsize=(10, 6))
        for _, row in roc_data_df.iterrows():
            ax.plot(row["fpr"], row["tpr"],
                    label=f"{row['classifier']} ({row['class']}, AUC={row['auc']:.3f})")
        ax.plot([0, 1], [0, 1], "k--", label="Chance (AUC=0.5)")
        self._finalize_plot(fig, ax, "ROC Curve", "False Positive Rate (FPR)",
                            "True Positive Rate (TPR)", "roc_curve_all_classifiers.png")

    def _plot_prc_curves(self, prc_data_df):
        """Plot Precision-Recall curves for all classifiers"""
        fig, ax = plt.subplots(figsize=(10, 6))
        for _, row in prc_data_df.iterrows():
            ax.plot(row["recall"], row["precision"],
                    label=f"{row['classifier']} ({row['class']})")
        self._finalize_plot(fig, ax, "Precision-Recall Curve", "Recall",
                            "Precision", "precision_recall_curve_all_classifiers.png")

    def _plot_metric_summary(self, metrics_df):
        """Plot summary metric comparison"""
        fig, ax = plt.subplots(figsize=(10, 6))
        metrics_df.plot(x="classifier", y=["f1_score", "accuracy", "auc", "mcc"],
                        kind="bar", ax=ax)
        self._finalize_plot(fig, ax, "Performance Metrics by Classifier",
                            "Classifier", "Score", "classifier_metrics_summary.png")

    def _finalize_plot(self, fig, ax, title, xlabel, ylabel, filename):
        """Common plot finalization tasks"""
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend(loc="best")
        fig.savefig(path.join(self.output_dir, filename), dpi=300)
        plt.close(fig)


def determineAccuracy(observed_values, predicted_values):
    """
    Calculate the accuracy of predictions.

    Args:
        observed_values (pd.Series or list): The actual observed values.
        predicted_values (pd.Series or list): The predicted values.

    Returns:
        float: The accuracy of the predictions as a ratio of correct predictions to total predictions.
    """
    observed_values = observed_values if type(observed_values) == list else observed_values.tolist()
    predicted_values = predicted_values if type(predicted_values) == list else predicted_values.tolist()
    correct = incorrect = 0
    for i in range(0, len(observed_values)):
        if bool(observed_values[i] == predicted_values[i]):
            correct += 1
        else:
            incorrect += 1
    return correct / (correct + incorrect)


def mutliclassResultsToBinary(observed_values, predicted_values):
    """
    Convert multiclass prediction results to binary format.

    Args:
        observed_values (pd.Series or list): The actual observed values.
        predicted_values (pd.Series or list): The predicted values.

    Returns:
        list: A list of binary values where 1 indicates a correct prediction and 0 indicates an incorrect prediction.
    """
    observed_values = observed_values if type(observed_values) == list else observed_values.tolist()
    predicted_values = predicted_values if type(predicted_values) == list else predicted_values.tolist()

    binary_predicted = []
    for index, value in enumerate(observed_values):
        # If the predicted value matches the observed value, append 1, else append 0.
        if predicted_values[index] == value:
            binary_predicted.append(1)
        else:
            binary_predicted.append(0)
    return binary_predicted


def probability_divider(observed_values_string, name_probability: str, single_characteristic_probability):
    """
    Divide probabilities into correct and incorrect predictions.

    Args:
        observed_values_string (pd.Series or list): The actual observed values as strings.
        name_probability (str) The value of te given probabiliy class.
        single_characteristic_probability (pd.Series or list): The probabilities of a single characteristic.

    Returns:
        tuple: Two lists, one with probabilities of correctly predicted values and one with probabilities of incorrectly predicted values.
    """
    observed_values_string = observed_values_string.to_numpy().flatten()  # 1D numpy array
    single_characteristic_probability = single_characteristic_probability.to_numpy().flatten()  # 1D numpy array.
    true_df = []
    false_df = []
    for index, value in enumerate(observed_values_string):
        if value == name_probability:
            true_df.append(single_characteristic_probability[index])
        else:
            false_df.append(single_characteristic_probability[index])
    return true_df, false_df
