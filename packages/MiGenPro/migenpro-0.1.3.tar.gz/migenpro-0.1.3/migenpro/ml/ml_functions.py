import argparse
import logging
import os
from pickle import load, dump

import pandas as pd
# Imbalanced-learn
from imblearn.over_sampling import (
    RandomOverSampler,
    SMOTE,
    SMOTEN,
    SMOTENC
)
from imblearn.under_sampling import RandomUnderSampler
from joblib import parallel_backend
# Scikit-learn
from sklearn.feature_selection import (
    VarianceThreshold,
    mutual_info_classif,
    SelectPercentile
)
from sklearn.utils import check_X_y

# Local application
from migenpro.logger_utils import get_logger

logger = get_logger(__name__, log_file="migenpro.log", error_log_file="migenpro_error.log", log_level=logging.INFO)



def to_java_output_folder(input_folder):
    """
    Converts the input folder path to the corresponding Java output folder path.
    """
    x = input_folder.split(os.sep)
    outputIndex = x.index("output")
    y = x[: outputIndex + 1]
    return os.sep.join(y)

def ordinalizer(df_features: pd.DataFrame):
    # Converts the string values inside a pandas dataframe to ordinal values.
    def name_changer(variable_names_inner):
        # Creates a dictionary to map variable names to ordinal values
        variable_dict = {name: index for index, name in enumerate(variable_names_inner)}
        # Converts an array with variable strings into an ordinalized array using the mapping
        return df_features.map(lambda value: variable_dict.get(value))

    # Get unique values from the dataframe
    variable_names = sorted(df_features.stack().unique())
    # Convert the values in the dataframe to ordinal values
    ordinal_values = name_changer(variable_names)

    return ordinal_values, variable_names

def filter_features_by_variance(X_train: pd.DataFrame, min_variance: float):
    """
    Filter features based on their variance.

    args:
        observed_values: The input DataFrame containing the features.
        min_variance: The minimum variance a feature must have to be included.

    returns:
        A DataFrame with features that have at least the specified variance.
    """
    selector = VarianceThreshold(threshold=min_variance)
    selector.fit(X_train)

    # Get the indices of the columns that meet the variance threshold
    selected_columns = X_train.columns[selector.get_support()]
    x_train_filtered = X_train[selected_columns]

    return x_train_filtered

def filter_features_by_mutual_info(X_train: pd.DataFrame, y_train: pd.Series, top_percentile: int = 50):
    """
    Filter features based on Mutual Information (MI) score.

    args:
        X_train: The input DataFrame containing the features.
        y_train: The target variable (required for MI calculation).
        top_percentile: The percentage of features to keep (e.g., 20 means keep top 20%).

    returns:
        A DataFrame with the highest ranking MI features.
    """
    # SelectPercentile is the robust strategy for MI
    selector = SelectPercentile(score_func=mutual_info_classif, percentile=top_percentile)

    # MI calculation can be computationally intensive
    selector.fit(X_train, y_train)

    # Get the indices of the columns that met the percentile cutoff
    selected_columns = X_train.columns[selector.get_support()]
    x_train_filtered = X_train[selected_columns]

    # Optional: Print how many features were kept
    print(f"Reduced features from {X_train.shape[1]} to {x_train_filtered.shape[1]} (Top {top_percentile}%)")

    return x_train_filtered

def save_model(model, path: str):
    # Save sklearn model.
    with open(path, "wb") as f:
        dump(model, f)


def load_model(model_path):
    # Load sklearn model.
    with open(model_path, "rb") as f:
        return load(f)


def feature_conversion(clf, feature_data):
    """
    Convert the feature columns in a dataset to match the feature names in a trained model, and handle missing features.

    This function ensures that the feature data passed to a classifier (clf) only contains the features that were used 
    during the training of the model. If any features in the dataset are not present in the model, they will be removed. 
    Additionally, if the model expects features that are missing from the dataset, these features will be added with 
    values set to zero. This is useful for aligning datasets with models that may have different or incomplete feature sets.

    Parameters
    ----------
    clf : scikitlearn ml model object
        The trained classifier or model object, which must have the attribute `feature_names_in_`, a list of feature names 
        used during training.
    
    feature_data : pandas.DataFrame
        The input dataframe containing feature data for prediction. The column names in this dataframe may not fully 
        match the model's expected features.

    Returns
    -------
    output_df : pandas.DataFrame
        A modified dataframe where:
        - Columns that do not match the model's expected features are removed.
        - Missing features expected by the model are added with values set to zero.
        The returned dataframe will match the feature set expected by the model.
    
    Raises
    ------
    AttributeError
        If the classifier does not have the attribute `feature_names_in_`.

    Notes
    -----
    - The function adds a "Genome" column to the resulting dataframe based on the index of `feature_data`.
    - This function is particularly useful for models with high-dimensional features (e.g., protein domains) that may not
      be present in every dataset.
    
    Examples
    --------
    > clf.feature_names_in_ = ['Feature1', 'Feature2', 'Feature3']
    > feature_data = pd.DataFrame({'Feature1': [0.5, 0.6], 'Feature2': [1.0, 0.8], 'FeatureX': [0.2, 0.3]})
    > result = feature_conversion(clf, feature_data)
    > print(result)
           Feature1  Feature2  Feature3  Genome
    0         0.5       1.0       0.0      0
    1         0.6       0.8       0.0      1

    """
    feature_names = list(clf.feature_names_in_)
    return feature_data.reindex(columns=feature_names, fill_value=0)


def str2bool(v):
    # Thanks to " https://stackoverflow.com/a/43357954 "
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def calculate_sampling_strategy(Y_train, factor=2, min_threshold=0.7):
    """Calculate sampling strategy for resampling."""
    class_counts = Y_train.value_counts()
    majority_count = class_counts.max()

    if len(class_counts) == 1:
        raise Exception("Only one class found in Y_train cannot perform resampling.")

    strategy = {}
    for cls, count in class_counts.items():
        # Ensure we work with plain Python ints/floats to avoid numpy scalar leakage
        count_int = int(count)
        max_allowed = int(majority_count)

        if count_int < (max_allowed * min_threshold):
            # Compute target and coerce to a plain Python int using round -> int
            target_val = min(count_int * float(factor), max_allowed)
            target = int(round(target_val))
        else:
            target = count_int

        # Defensive guard: target must be at least 1 and at most majority
        target = max(1, min(target, max_allowed))
        strategy[cls] = target
    return strategy


def validate_inputs(Y_train):
    """Validate input data requirements."""
    if len(Y_train.unique()) < 2:
        raise ValueError("Need at least 2 classes in Y_train")
    if Y_train.value_counts().min() == 1:
        raise ValueError("Least abundant class has only 1 sample")

def detect_feature_types(X):
    """
    Automatically detect categorical and numerical features in the dataset.

    Args:
        X (DataFrame): Feature matrix
        categorical_threshold (int): Maximum number of unique values for a feature to be considered categorical
        unique_ratio_threshold (float): Maximum ratio of unique values to total samples for categorical features

    Returns:
        dict: Contains 'categorical_indices', 'numerical_indices', 'feature_types', and 'is_mixed'
    """
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)

    n_samples = len(X)
    categorical_indices = []
    numerical_indices = []
    feature_types = {}

    for idx, col in enumerate(X.columns):
        unique_values = X[col].nunique()

        # Check if feature is categorical based on multiple criteria
        is_categorical = X[col].dtype == 'object' or X[col].dtype.name == 'category'

        if is_categorical:
            categorical_indices.append(idx)
            feature_types[col] = 'categorical'
        else:
            numerical_indices.append(idx)
            feature_types[col] = 'numerical'

    is_mixed = len(categorical_indices) > 0 and len(numerical_indices) > 0
    is_all_categorical = len(numerical_indices) == 0
    is_all_numerical = len(categorical_indices) == 0

    return {
        'categorical_indices': categorical_indices,
        'numerical_indices': numerical_indices,
        'feature_types': feature_types,
        'is_mixed': is_mixed,
        'is_all_categorical': is_all_categorical,
        'is_all_numerical': is_all_numerical
    }


def get_optimal_k_neighbors(Y_train, default_k=5):
    """
    Calculate optimal k_neighbors parameter based on minority class size.

    Args:
        Y_train: Target vector
        default_k (int): Default k value

    Returns:
        int: Optimal k_neighbors value
    """
    class_counts = pd.Series(Y_train).value_counts()
    min_class_size = class_counts.min()

    # k_neighbors should be less than the smallest class size
    # and at least 1
    optimal_k = min(default_k, max(1, min_class_size - 1))

    return optimal_k


def resample_data(X_train, Y_train, sampling_type: str = "SMOTEN", factor: float|int =1.5,
                  min_threshold=0.7, n_jobs=1, random_state=None,
                  **sampler_kwargs):
    """
    Automatically detect feature types and apply appropriate resampling strategy.

    Args:
        X_train (array-like or DataFrame): Feature matrix of shape (n_samples, n_features).
        Y_train (array-like or Series): Target vector of shape (n_samples,).
        sampling_type (str): Sampling strategy. Options:
            - "auto": Automatically detect and choose best method
            - "SMOTE": For numerical features
            - "SMOTEN": For categorical features
            - "SMOTENC": For mixed features
            - "oversample": RandomOverSampler
            - "undersample": RandomUnderSampler
            - "none": No resampling
        factor (float): Controls desired ratio of minority to majority class after resampling.
        min_threshold (float): Minimum class ratio before resampling is applied, default is 0.7 of the most abundant class.
        n_jobs (int): Number of parallel jobs.
        random_state (int, None): Random state for reproducibility. If None, uses random behavior.
        categorical_threshold (int): Max unique values for categorical detection.
        unique_ratio_threshold (float): Max unique ratio for categorical detection.
        **sampler_kwargs: Additional arguments for samplers.

    Returns:
        tuple: (X_train_resampled, Y_train_resampled)
    """

    # Validate inputs
    validate_inputs(Y_train)

    # Convert to DataFrame if needed for analysis
    if not isinstance(X_train, pd.DataFrame):
        X_train = pd.DataFrame(X_train)

    # Handle missing values
    X_train_filled = X_train.fillna(0)

    # Calculate sampling strategy
    sampling_strategy = calculate_sampling_strategy(Y_train, factor, min_threshold)

    # Final sanitization: imblearn expects integers for desired class sizes
    if isinstance(sampling_strategy, dict):
        sampling_strategy = {k: int(v) for k, v in sampling_strategy.items()}

    # If no resampling needed, return original data
    if sampling_type.lower() == "none" or not sampling_strategy:
        return X_train_filled, Y_train

    # Handle unknown strategy by returning unchanged data (for backward compatibility)
    if sampling_type.lower() not in ["smote", "smoten", "smotenc", "oversample", "undersample"]:
        return X_train_filled, Y_train

    # Configure sampler based on type
    if sampling_type.upper() == "SMOTE":
        # Optimize k_neighbors for SMOTE
        if 'k_neighbors' not in sampler_kwargs:
            sampler_kwargs['k_neighbors'] = get_optimal_k_neighbors(Y_train)

        sampler = SMOTE(
            sampling_strategy=sampling_strategy,
            random_state=random_state,
            **sampler_kwargs
        )

    elif sampling_type.upper() == "SMOTEN":
        if 'k_neighbors' not in sampler_kwargs:
            sampler_kwargs['k_neighbors'] = get_optimal_k_neighbors(Y_train)

        sampler = SMOTEN(
            sampling_strategy=sampling_strategy,
            random_state=random_state,
            **sampler_kwargs
        )

    elif sampling_type.upper() == "SMOTENC":
        # Ensure categorical_features is provided for SMOTENC
        if 'categorical_features' not in sampler_kwargs:
            feature_info = detect_feature_types(X_train_filled)
            sampler_kwargs['categorical_features'] = feature_info['categorical_indices']

        if 'k_neighbors' not in sampler_kwargs:
            sampler_kwargs['k_neighbors'] = get_optimal_k_neighbors(Y_train)

        sampler = SMOTENC(
            sampling_strategy=sampling_strategy,
            random_state=random_state,
            **sampler_kwargs
        )

    elif sampling_type.lower() == "oversample":
        sampler = RandomOverSampler(
            sampling_strategy=sampling_strategy,
            random_state=random_state
        )

    elif sampling_type.lower() == "undersample":
        sampler = RandomUnderSampler(
            sampling_strategy=sampling_strategy,
            random_state=random_state
        )

    else:
        raise ValueError(f"Unknown sampling strategy: {sampling_type}")

    try:
        with parallel_backend('threading', n_jobs=n_jobs):
            X_resampled, Y_resampled = sampler.fit_resample(X_train_filled, Y_train)

        logger.debug(f"Resampling completed: {len(X_train)} -> {len(X_resampled)} samples")
        return X_resampled, Y_resampled

    except Exception as e:
        raise Exception(f"Warning: Resampling failed with {sampling_type}: {str(e)}")
