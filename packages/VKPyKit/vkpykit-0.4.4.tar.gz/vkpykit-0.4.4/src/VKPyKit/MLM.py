import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys

from sklearn import tree, metrics
from sklearn.tree import DecisionTreeClassifier
from IPython.display import display, HTML
import warnings
warnings.filterwarnings("ignore")


class MLM():
    
    def __init__(self): 
        super().__init__()
        pass
    

    RANDOM_STATE = 42
    NUMBER_OF_DASHES = 100

    """
    Decision Tree Classifier related visualizations
    To plot the confusion_matrix with percentages
    """

    @staticmethod
    # defining a function to compute different metrics to check performance of a classification model built using sklearn
    def model_performance_classification(
            model,
            predictors: pd.DataFrame,
            expected: pd.Series,
            printall: bool = False,
            title: str = 'DecisionTreeClassifier') -> pd.DataFrame:
        """
        Function to compute different metrics to check classification model performance
        model: classifier \n
        predictors: independent variables \n
        target: dependent variable \n
        return: dataframe of different performance metrics
        """

        # predicting using the independent variables
        predictions = model.predict(predictors)

        accuracy = metrics.accuracy_score(expected, predictions)  # to compute Accuracy
        recall = metrics.recall_score(expected, predictions)  # to compute Recall
        precision = metrics.precision_score(expected, predictions)  # to compute Precision
        f1 = metrics.f1_score(expected, predictions)  # to compute F1-score

        # creating a dataframe of metrics
        df_perf = pd.DataFrame(
            {
                "Accuracy": accuracy,
                "Recall": recall,
                "Precision": precision,
                "F1": f1,
            },
            index=[0],
        )
        if (printall):
            display(
                HTML(
                    f"<h3>Classification Model Performance Metrics : {title}</h3>"
                ))
            display(df_perf)

        return df_perf

        # END OF MODEL PERFORMANCE CLASSIFICATION FUNCTION
    @staticmethod
    def plot_confusion_matrix(
                              model,
                              predictors: pd.DataFrame,
                              expected: pd.Series,
                              title: str = "DecisionTreeClassifier") -> None:
        """
        To plot the confusion_matrix with percentages \n
        model: classifier \n
        predictors: independent variables  \n
        target: dependent variable \n
        return: None
        """
        # Predict the target values using the provided model and predictors
        predicted = model.predict(predictors)

        # Compute the confusion matrix comparing the true target values with the predicted values
        conf_matrix = metrics.confusion_matrix(expected, predicted)

        # Create labels for each cell in the confusion matrix with both count and percentage
        labels = np.asarray([[
            "{0:0.0f}".format(item) +
            "\n{0:.2%}".format(item / conf_matrix.flatten().sum())
        ] for item in conf_matrix.flatten()
                             ]).reshape(2, 2)  # reshaping to a matrix

        # Set the figure size for the plot
        plt.figure(figsize=(6, 4))
        plt.title("Confusion Matrix for " + title)
        # Plot the confusion matrix as a heatmap with the labels
        sns.heatmap(conf_matrix, annot=labels, fmt="")

        # Add a label to the y-axis
        plt.ylabel("True label")

        # Add a label to the x-axis
        plt.xlabel("Predicted label")
        plt.show()
        sys.stdout.flush()
        # END OF PLOT CONFUSION MATRIX FUNCTION
