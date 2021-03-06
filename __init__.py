# source: https://github.com/may42/machine_learning_helper_functions

import numpy as np
import matplotlib.pyplot as plt
from sklearn import model_selection, preprocessing


class FeaturePreparer:
    """Prepares features:
    1) Adds powers, permutations, logarithms and exponents;
    2) Normalizes all features mean and std;
    """

    def __init__(self, powers):
        self.powers = powers or [1]
        self.scaler = preprocessing.StandardScaler()
        self.__orig_std = None # needed for scaling features before taking exp
        self._non_boolean_features_mask = None # 1d mask array that needed for skipping redundant log and exp

    def apply_powers(self, x):
        f_list = []
        if 1 in self.powers:
            f_list += [x]
        non_boolean_features = x[:,self._non_boolean_features_mask]
        f_list += [non_boolean_features ** p for p in self.powers if type(p) is int and p != 1]
        if "perm" in self.powers:
            f_list += [x[:, i:i+1] * x[:, j:j+1] for i in range(x.shape[1]) for j in range(i + 1)]
        if "log" in self.powers:
            f_list += [np.log(non_boolean_features + 1)]
        if "exp" in self.powers:
            f_list += [np.exp(non_boolean_features / self.__orig_std)]
        return np.concatenate(f_list, axis=1) if len(f_list) > 1 else f_list[0]

    def __fit(self, x):
        self._non_boolean_features_mask = np.array([len(np.unique(col)) > 2 for col in x.T])
        non_boolean_features = x[:,self._non_boolean_features_mask]
        self.__orig_std = non_boolean_features.std(axis=0)
        x_new = self.apply_powers(x)
        self.scaler.fit(x_new)
        return x_new

    def fit(self, x):
        self.__fit(x)
        return self

    def transform(self, x):
        x_new = self.apply_powers(x)
        return self.scaler.transform(x_new)

    def fit_transform(self, x):
        x_new = self.__fit(x)
        return self.scaler.transform(x_new)

    def expand_columns_names_list(self, columns):
        non_boolean_columns = columns[self._non_boolean_features_mask]
        prefixes = [str(p) for p in self.powers if p != 1]
        additional_columns = np.array([pref + "_"+ col for pref in prefixes for col in non_boolean_columns])
        return np.concatenate([columns, additional_columns])


def plot_learning_curves(est, X, y, title, ylim=(.6, 1), cv=3, train_sizes=np.linspace(.05, 1, 10)):
    """
    plot the test and training learning curves
    est: estimator - must implement "fit" and "predict" methods
    X: features
    y: target
    title: title for the chart
    ylim: defines minimum and maximum yvalues plotted
    cv: cv strategy
    steps: train portions sizes
    """
    steps, train_sc, test_sc = model_selection.learning_curve(est, X, y, cv=cv, n_jobs=1, train_sizes=train_sizes)
    create_learning_curves_plot(steps, train_sc, test_sc, title, ylim).show()


def create_learning_curves_plot(train_sizes, train_scores, test_scores, title, ylim=(.55, 1.005)):
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.figure()
    plt.ylim(*ylim)
    plt.xlabel("number of tr. examples")
    plt.ylabel("score")
    plt.title("{} (accuracy={:.3f})".format(title, test_scores_mean[-1]))
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")

    plt.plot(train_sizes, train_scores_mean, '-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, '-', color="g", label="Cv score")

    plt.legend(loc="best")
    return plt
