import time
import numpy as np
import pandas as pd

from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    log_loss,
    brier_score_loss,
    confusion_matrix,
    classification_report,
)


def train_single_model(
    model,
    model_name,
    X_train,
    y_train,
    X_valid = None,
    y_valid = None,
    X_test = None,
    y_test = None,
    cv = 5,
    scoring = "accuracy",
    compute_train_metrics = False,
    compute_feature_importance = True,
    return_predictions = True,
):
    
    result = {
        "model_name": model_name,
        "model_type": model.__class__.__name__,
    }

    result["n_train_samples"] = len(X_train)
    result["n_features"] = X_train.shape[1]

    if hasattr(y_train, "nunique"):
        result["n_classes"] = y_train.nunique()
    else:
        result["n_classes"] = len(np.unique(y_train))
        
    train_start = time.perf_counter()

    model.fit(X_train, y_train)

    train_end = time.perf_counter()

    result["training_time_seconds"] = (
        train_end - train_start
    )

    result["estimator"] = model

    try:

        cv_scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv = cv,
            scoring = scoring,
            n_jobs = -1,
        )

        result["cross_validation"] = {
            "metric": scoring,
            "scores": cv_scores.tolist(),
            "mean": float(cv_scores.mean()),
            "std": float(cv_scores.std()),
            "min": float(cv_scores.min()),
            "max": float(cv_scores.max()),
        }

    except Exception as e:

        result["cross_validation"] = {
            "error": str(e)
        }
        
    if compute_feature_importance:

        try:

            feature_names = (
                X_train.columns
                if hasattr(X_train, "columns")
                else [f"Feature_{i}" for i in range(X_train.shape[1])]
            )

            if hasattr(model, "feature_importances_"):

                fi = pd.DataFrame({
                    "Feature": feature_names,
                    "Importance": model.feature_importances_
                })

                fi = fi.sort_values(
                    "Importance",
                    ascending=False
                )

                result["feature_importance"] = fi

            elif hasattr(model, "coef_"):

                coef = np.abs(model.coef_)

                if coef.ndim > 1:
                    coef = coef.mean(axis=0)

                fi = pd.DataFrame({
                    "Feature": feature_names,
                    "Importance": coef
                })

                fi = fi.sort_values(
                    "Importance",
                    ascending=False
                )

                result["feature_importance"] = fi

        except Exception:
            pass

    def evaluate_split(X, y, split_name):

        if X is None or y is None:
            return None

        prediction_start = time.perf_counter()

        y_pred = model.predict(X)

        prediction_end = time.perf_counter()

        metrics = {
            "prediction_time_seconds":
                prediction_end - prediction_start,

            "accuracy":
                accuracy_score(y, y_pred),

            "balanced_accuracy":
                balanced_accuracy_score(y, y_pred),

            "precision_macro":
                precision_score(
                    y,
                    y_pred,
                    average = "macro",
                    zero_division = 0
                ),

            "recall_macro":
                recall_score(
                    y,
                    y_pred,
                    average = "macro",
                    zero_division = 0
                ),

            "f1_macro":
                f1_score(
                    y,
                    y_pred,
                    average = "macro",
                    zero_division = 0
                ),

            "precision_weighted":
                precision_score(
                    y,
                    y_pred,
                    average = "weighted",
                    zero_division = 0
                ),

            "recall_weighted":
                recall_score(
                    y,
                    y_pred,
                    average = "weighted",
                    zero_division = 0
                ),

            "f1_weighted":
                f1_score(
                    y,
                    y_pred,
                    average = "weighted",
                    zero_division = 0
                ),

            "confusion_matrix":
                confusion_matrix(y, y_pred),

            "classification_report":
                classification_report(
                    y,
                    y_pred,
                    output_dict = True,
                    zero_division = 0
                )
        }

        classes = len(np.unique(y))

        if classes == 2:

            metrics["precision"] = precision_score(
                y,
                y_pred,
                zero_division=0
            )

            metrics["recall"] = recall_score(
                y,
                y_pred,
                zero_division=0
            )

            metrics["f1"] = f1_score(
                y,
                y_pred,
                zero_division = 0
            )

        y_prob = None

        try:

            y_prob = model.predict_proba(X)

            if classes == 2:

                positive_prob = y_prob[:, 1]

                metrics["roc_auc"] = roc_auc_score(
                    y,
                    positive_prob
                )

                metrics["pr_auc"] = (
                    average_precision_score(
                        y,
                        positive_prob
                    )
                )

                metrics["log_loss"] = log_loss(
                    y,
                    y_prob
                )

                metrics["brier_score"] = (
                    brier_score_loss(
                        y,
                        positive_prob
                    )
                )

            else:

                metrics["roc_auc"] = roc_auc_score(
                    y,
                    y_prob,
                    multi_class="ovr",
                    average="weighted"
                )

                metrics["log_loss"] = log_loss(
                    y,
                    y_prob
                )

        except Exception:
            pass

        if return_predictions:

            metrics["y_true"] = np.asarray(y)
            metrics["y_pred"] = np.asarray(y_pred)

            if y_prob is not None:
                metrics["y_prob"] = y_prob

        return metrics

    if compute_train_metrics:

        result["train"] = evaluate_split(
            X_train,
            y_train,
            "train"
        )
        
    if X_valid is not None and y_valid is not None:

        result["validation"] = evaluate_split(
            X_valid,
            y_valid,
            "validation"
        )

        result["n_validation_samples"] = len(X_valid)
        
    if X_test is not None and y_test is not None:

        result["test"] = evaluate_split(
            X_test,
            y_test,
            "test"
        )

        result["n_test_samples"] = len(X_test)

    return result

def run_all_models(
    models_dict,
    X_train,
    y_train,
    X_valid = None,
    y_valid = None,
    X_test = None,
    y_test = None,
    cv=5,
    scoring = "accuracy",
    compute_train_metrics = False,
    sort_by = "accuracy",
    comparison_split = "test",
):

    all_results = {}
    summary_rows = []

    print("=" * 60)
    print("Training Models")
    print("=" * 60)

    for model_name, model in models_dict.items():

        print(f"\nTraining: {model_name}")

        try:

            result = train_single_model(
                model = model,
                model_name = model_name,
                X_train = X_train,
                y_train = y_train,
                X_valid = X_valid,
                y_valid = y_valid,
                X_test = X_test,
                y_test = y_test,
                cv = cv,
                scoring = scoring,
                compute_train_metrics = compute_train_metrics,
            )

            all_results[model_name] = result
            
            split_result = result.get(comparison_split)

            row = {
                "Model": model_name,
                "CV Mean": result.get(
                    "cross_validation",
                    {}
                ).get("mean"),

                "CV Std": result.get(
                    "cross_validation",
                    {}
                ).get("std"),

                "Training Time (s)":
                    result.get(
                        "training_time_seconds"
                    )
            }

            if split_result:

                metrics_to_extract = [
                    "accuracy",
                    "balanced_accuracy",
                    "precision",
                    "recall",
                    "f1",
                    "roc_auc",
                    "pr_auc",
                    "log_loss",
                    "brier_score",
                ]

                for metric in metrics_to_extract:

                    if metric in split_result:
                        row[metric] = split_result[metric]

            summary_rows.append(row)

            print("✓ Completed")

        except Exception as e:

            print(f"✗ Failed: {e}")

            all_results[model_name] = {
                "error": str(e)
            }
            
    results_df = pd.DataFrame(summary_rows)

    if (
        sort_by in results_df.columns
        and not results_df.empty
    ):
        results_df = (
            results_df
            .sort_values(
                by=sort_by,
                ascending=False
            )
            .reset_index(drop=True)
        )

    return results_df, all_results
