"""Model analysis utilities for feature importance visualisation and summaries.

This module provides classes to load ML models and compute/visualise feature
importances using SHAP, Gini importance and RFE. Changes focused on linting
cleanups without altering functionality.
"""
# Generic imports
import argparse  # Argument parsing
import logging
from os import path, sep, makedirs
from re import sub  # Regex to remove json from uniprot API response

import matplotlib
# Use a non-interactive backend for headless/test environments
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt  # Plotting graphs
import numpy as np
import pandas as pd  # Initial format given for the dataset that will have to parsed.
import shap
from shap import TreeExplainer, Explainer, maskers
# Metrics
from sklearn import tree
from sklearn.feature_selection import RFE

from migenpro.ml.machine_learning_main import MachineLearningModels
from migenpro.ml.ml_functions import get_logger, load_model, feature_conversion
from migenpro.ml.ml_functions import parallel_backend
# Custom functions
from migenpro.post_analysis.uniprot_api_access import pfam_domain_call

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.INFO)

def command_line_interface_model_analysis(previously_unparsed_args: argparse.Namespace) -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    Raises:
        argparse.ArgumentError: If invalid arguments are provided
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--model",
        help="location of models to load",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--proportion_train",
        help="proportion of dataset that is used for training",
        default=0.7,
        type=float,
    )
    parser.add_argument('--phenotype_matrix', type=str, default=None,
                        help='Path to the phenotype matrix file.')
    parser.add_argument('--feature_matrix', type=str, default=None,
                        help='Path to the feature matrix file.')
    parser.add_argument("--rfe", help="Perform recursive feature importance. ", action="store_true")
    parser.add_argument("--shap", help="Perform Shapley feature importance. ", action="store_true")
    parser.add_argument("--gini", help="Perform gini feature importance. ", action="store_true")
    # Accept a provided argv list (from tests or callers) instead of always using sys.argv
    try:
        argv = list(previously_unparsed_args) if previously_unparsed_args is not None else None
    except TypeError:
        argv = None
    args, _ = parser.parse_known_args(argv)
    return args


class LoadedMachineLearningModel(MachineLearningModels):
    """
    Represents a single machine learning model.s

    Attributes:
        clf_model (object): The loaded classifier model.
        model_name (str): The name of the classifier model.
        gini (bool): Indicates if the model has feature importances based on Gini impurity.
    """
    def __init__(self, model: str):
        super().__init__()
        self.clf_model = load_model(model)
        self.model_name = self.clf_model.__class__.__name__
        self.module = getattr(self.clf_model, '__module__', '')
        self.gini = hasattr(self.clf_model, "feature_importances_")

class ModelAnalysis:
    """
    Analyzes the machine learning model.

    Attributes:
        clf_model (object): The classifier model.
        model_name (str): The name of the classifier model.
        X_test (pd.DataFrame): The test feature matrix.
        Y_test (pd.Series): The test labels.
        class_names (list): The class names.
    """
    def __init__(self, LoadedMachineLearningModel, feature_matrix_subset, phenotype_matrix_subset, debug=False):
        if debug:
            logger.setLevel(logging.DEBUG)
        self.clf_model = LoadedMachineLearningModel.clf_model
        self.model_name = LoadedMachineLearningModel.model_name
        feature_matrix_subset_clean = feature_conversion(clf=self.clf_model, feature_data=feature_matrix_subset) # Strips unseen features.

        self.X_test = feature_matrix_subset_clean
        self.Y_test = phenotype_matrix_subset

        self.class_names = self.clf_model.classes_

    def _calculate_devs(self, clf, importance_max_index: list, clf_importances: list):
        """
        Calculates standard deviations and importances.

        Args:
            clf (object): The classifier model.
            importance_max_index (list): Indices of the top features.
            clf_importances (list): Feature importances.

        Returns:
            tuple: Standard deviations and importances of the top features.
        """
        ######## Standard deviation calculations ##########
        std = np.std([tree.feature_importances_ for tree in clf.estimators_], axis=0)
        # Standard deviation for selected top features
        max_std = [std[x] for x in importance_max_index]

        return max_std


    def _feature_text_summary(self, clf_importances, output, max_std="", topn=10):
        """
        Generates a text summary of feature importances.

        Args:
            clf_importances_max (pd.Series): Top feature importances.
            output (str): Path to save the summary.
            max_std (str, optional): Standard deviations of the top features.
        """
        # Text summary
        domain_descriptions = []
        domains = clf_importances.index
        for domain in domains[:topn]:
            uniprot_data_map = pfam_domain_call(domain)
            # Get the description
            description = uniprot_data_map.get(
                "description"
            )  # This will work for the vast majority of featureRegex.
            if description is not None:
                # "*" is greedy and  "*?" is not greedy.
                domain_descriptions.append(
                    sub(r"<(.*?)>", "", description[0].get("text"))
                )  # remove js
            elif uniprot_data_map.get(
                    "wikipedia"
            ) is not None and "extract" in uniprot_data_map.get("wikipedia"):
                description = uniprot_data_map.get("wikipedia")["extract"]
                domain_descriptions.append(sub(r"<(.*?)>", "", description))  # remove js
            else:
                domain_descriptions.append("NA")

        # Append null for domains outside of topn
        for domain in domains[topn:]:
            domain_descriptions.append(None)
        # domain_enriched_list = self._enriched_for(clf_importances.index, self.X_test, self.Y_test, self.class_names)

        sum_df = pd.DataFrame()
        sum_df["feature_name"] = clf_importances.index
        sum_df["importance"] = clf_importances.reset_index(drop=True)
        if max_std != "":
            sum_df["standard_deviation"] = max_std
        # sum_df["domain_found_in"] = domain_enriched_list
        sum_df["description"] = domain_descriptions
        sum_df.to_csv(output, sep="\t")


    def _visualize_tree(self, clf, output: str, model_name: str, feature_names=None):
        """
        Visualizes a decision tree.

        Args:
            clf (object): The classifier model.
            output (str): Path to save the visualization.
            model_name (str) Name of model being analyzed.
            feature_names (list, optional): List of feature names.
        """
        fig = plt.figure(figsize=(25, 20))
        class_names = clf.classes_

        if feature_names is None:
            feature_names = clf.feature_names_in_

        _ = tree.plot_tree(clf, feature_names=feature_names, class_names=class_names)
        if not path.isdir(output + sep + "Trees"):
            makedirs(output + sep + "Trees")

        fig.savefig(output + sep + "Trees" + sep + self.model_name + "_decision_tree.svg")

    def _enriched_for(self, domains, X_test, Y_test, class_names):
        """
        Determines class enrichment for featureRegex.

        Args:
            domains (list): List of featureRegex.
            X_test (pd.DataFrame): The test feature matrix.
            Y_test (pd.Series): The test labels.
            class_names (list): The class names.

        Returns:
            list: Enriched classes for each domain.
        """
        # Determine by counter where a domain is more abundant.
        mode_results = []
        for domain in domains:
            count_result = []
            domain_presence_list = X_test[domain].tolist()
            for index, presence in enumerate(domain_presence_list):
                if presence == 1:
                    count_result.append(Y_test[index])
            mode_results.append(
                class_names[int(max(set(count_result), key=count_result.count))]
            )
        return mode_results

    def shap_feature_importance(self, output_fig_path: str, output_summary_path: str, topn=10):
        """
        Computes and plots the Shapley values used for feature importance for the given classifier.

        Args:
            output_fig_path (str): Path to save the output figure.
            output_summary_path (str): Path to save the output summary.
            topn (int): The number of top features to display.
        """
        max_samples = len(self.X_test.index) if len(self.X_test.index) < 1000 else 1000

        background = self.X_test[:max_samples]
        # Check if the model is a tree-based model
        if self.model_name in ['RandomForestClassifier', 'GradientBoostingClassifier', 'DecisionTreeClassifier']:
            # Use TreeExplainer for tree-based models
            explainer = TreeExplainer(self.clf_model, background)
        else:
            # Use Independent masker for other model types (like neural networks)
            masker = maskers.Independent(background, max_samples=max_samples)
            explainer = Explainer(self.clf_model, masker)

        # Compute SHAP values on the test set
        shap_values = explainer.shap_values(self.X_test)
        shap.summary_plot(shap_values, self.X_test, show=False, max_display=topn ,plot_type='bar')
        plt.savefig(output_fig_path, dpi=700)

        # Feature importance is the mean absolute value of Shapley values for each feature
        feature_importance = np.abs(shap_values.values).mean(axis=0)

        # Get the top N features
        top_indices = np.argsort(feature_importance)[-topn:]
        top_features = np.array(self.X_test.columns)[top_indices]  # Assuming X_test is a DataFrame
        top_importance = feature_importance[top_indices]

        # Save summary of feature importance
        with open(output_summary_path, 'w', encoding='utf-8') as f:
            for feature, importance in zip(top_features, top_importance):
                f.write(f"{feature}: {importance}\n")

        # Plot feature importance
        shap.summary_plot(shap_values, self.X_test, plot_type="bar", max_display=topn)



    def gini_feature_importance(self, output_fig_path: str, output_summary_path: str, topn=10):
        """
        Computes and plots the Gini-based feature importance for the given classifier.

        Args:
            output_fig_path (str): Path to save the output figure.
            output_summary_path (str): Path to save the output summary.
            topn (int): The number of top features to display.
        """
        # Impurity-based feature importances can be misleading for high cardinality features (many unique values).
        print("Start feature importance analysis for", self.model_name, "...")
        importances = self.clf_model.feature_importances_
        clf_importances = pd.Series(importances, index=self.clf_model.feature_names_in_)
        importance_max_index = np.argpartition(importances, -topn)[-topn:]
        clf_importances_max = pd.Series(clf_importances.iloc[importance_max_index]).sort_values(axis=0, ascending=False)

        fig, ax = plt.subplots(constrained_layout=True, figsize=(20, 20))

        ##################################### Plotting and data exportation ############################################
        # try:
        if self.model_name == "RandomForestClassifier":
            max_std = self._calculate_devs(self.clf_model, importance_max_index, clf_importances)
            ax.bar(
                clf_importances_max.index, clf_importances_max, yerr=max_std
            )
        else:
            ax.bar(clf_importances_max.index, clf_importances_max)

        fig.suptitle("Feature importances " + self.model_name, fontsize=37)
        ax.set_ylabel("Mean decrease in impurity", fontsize=35)
        plt.xticks(rotation=55, horizontalalignment="right", fontsize=35)
        plt.yticks(fontsize=35)
        fig.savefig(output_fig_path)

        if not path.isfile(output_summary_path):
            self._feature_text_summary(
                clf_importances=pd.Series(clf_importances).sort_values(axis=0, ascending=False),
                output=output_summary_path,
                topn=topn
            )
        print(f"Feature importance analysis for {self.model_name} has finished. Located in  {output_fig_path} and {output_summary_path} ")

    def rfe_feature_importance(self, output_fig, topn=10, n_jobs=1):
        """
        Performs Recursive Feature Elimination (RFE) to determine feature importance.

        Args:
            output_fig (str): Path to save the output figure.
            topn (int): The number of top features to display.
            n_jobs (int): Number of threads to use.

        Returns:
            pd.DataFrame: DataFrame containing feature names and their rankings.
        """
        with parallel_backend('threading', n_jobs=n_jobs):
            # Initialize RFE with the classifier and number of features to select
            rfe = RFE(estimator=self.clf_model, n_features_to_select=topn)
            rfe.fit(self.X_test, self.Y_test)

        # Get feature rankings and importance
        feature_ranking = pd.Series(rfe.ranking_, index=self.X_test.columns)
        top_features = feature_ranking[feature_ranking == 1].index

        # Plotting feature importances
        fig, ax = plt.subplots(figsize=(10, 10))
        top_feature_importances = pd.Series(rfe.estimator_.feature_importances_, index=top_features).sort_values()
        top_feature_importances.plot(kind='barh', ax=ax)
        ax.set_title('Top Feature Importances via RFE')
        ax.set_xlabel('Importance')
        ax.set_ylabel('Features')
        plt.tight_layout()
        plt.savefig(output_fig)
