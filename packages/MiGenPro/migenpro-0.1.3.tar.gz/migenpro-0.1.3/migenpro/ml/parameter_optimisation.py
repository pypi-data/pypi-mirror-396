"""
A module for hyperparameter optimization of machine learning classifiers.
"""
import argparse
import inspect

import pandas as pd
# Enable experimental HalvingGridSearchCV before importing it
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.model_selection import HalvingGridSearchCV, GridSearchCV
from tqdm import tqdm

from migenpro.ml.machine_learning_main import MachineLearningModels


class ParameterOptimisation(MachineLearningModels):
    """
    A class for performing hyperparameter optimization on machine learning classifiers.

    This class extends MachineLearningModels to provide functionality for optimizing
    hyperparameters of machine learning models using various search strategies including
    grid search and successive halving grid search.

    The class supports multiple classifiers and allows for flexible parameter tuning
    with cross-validation to find optimal hyperparameters that maximize model performance.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _get_classifier_name(obj) -> str:
        """Return a stable classifier name for a class or instance."""
        return obj.__name__ if inspect.isclass(obj) else obj.__class__.__name__

    @staticmethod
    def _ensure_estimator(obj):
        """Return an estimator instance given a class or instance."""
        return obj() if inspect.isclass(obj) else obj

    def perform_hyperparameter_search(self, param_grids: dict, cv: int = 5, scoring: str = "matthews_corrcoef",
                                      search_method: str = "grid_search"):
        """
        Perform hyperparameter tuning for each classifier using either grid search or successive halving grid search.

        Args:
            param_grids (dict): A dictionary where keys are classifier names and values are parameter grids.
            cv (int): Number of cross-validation folds. Default is 5.
            scoring (str): Scoring metric for evaluating model performance. Default is "matthews_corrcoef".
            search_method (str): Method for hyperparameter search. Options are "grid_search" or "halving_grid_search". Default is "grid_search".

        Returns:
            dict: A dictionary with classifier names as keys and best parameter sets as values.
        """
        best_params = {}
        self.logger.debug("Performing hyperparameter search.")
        for classifier in tqdm(self.classifiers, desc=f"{search_method} parameter optimization"):
            classifier_name = self._get_classifier_name(classifier)

            if classifier_name in param_grids:
                self.logger.info(f"Performing {search_method} for {classifier_name}...")

                # Initialize the appropriate search method
                estimator = self._ensure_estimator(classifier)
                if search_method == "grid_search":
                    search = GridSearchCV(
                        estimator=estimator,
                        param_grid=param_grids[classifier_name],
                        cv=cv,
                        scoring=scoring,
                        n_jobs=10
                    )
                elif search_method == "halving_grid_search":
                    search = HalvingGridSearchCV(
                        estimator=estimator,
                        param_grid=param_grids[classifier_name],
                        cv=cv,
                        scoring=scoring,
                        n_jobs=10
                    )
                else:
                    raise Exception(f"Invalid search method: {search_method}. Options are 'grid_search' or 'halving_grid_search'.")

                search.fit(self.X_train, self.Y_train)

                # Save the best model and parameters
                self.clf_models.append(search.best_estimator_)
                best_params[classifier_name] = search.best_params_
                self.logger.info(f"Best params for {classifier_name}: {search.best_params_}")

        return best_params

    def perform_grid_search(self, param_grids: dict, cv: int = 5, scoring: str = "matthews_corrcoef"):
        """
        Perform grid search for hyperparameter tuning for each classifier.
        """
        self.logger.debug("Performing grid search.")
        return self.perform_hyperparameter_search(param_grids=param_grids, cv=cv, scoring=scoring, search_method="grid_search")

    def perform_halving_grid_search_search(self, param_grids: dict, cv: int = 5, scoring: str = "matthews_corrcoef") -> dict:
        """
        Perform successive halving grid search for hyperparameter tuning for each classifier.
        """
        self.logger.debug("Performing halving grid search for each classifier...")
        return self.perform_hyperparameter_search(param_grids=param_grids, cv=cv, scoring=scoring,
                                                  search_method="halving_grid_search")
