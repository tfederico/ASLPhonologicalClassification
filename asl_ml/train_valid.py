def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from asl_ml.preprocessing import preprocess_dataset
from asl_ml.model_selection import select_best_models
import seaborn as sns


def print_labels_statistics(y):
    diff_y, counts = np.unique(y, return_counts=True)
    print(list(zip(diff_y, counts)))

# Possible labels
# Compound, Initialized, FingerspelledLoanSign, SignType, MajorLocation,
# MinorLocation, SelectedFingers, Flexion, Movement

# Labels that completely depend on hands/fingers
# Initialized, FingerspelledLoanSign, SelectedFingers, Flexion

# Labels that partially involve hands/fingers (usable -> with substitution)
# Compound, SignType (usable), MinorLocation (usable)

# Remaining
# MajorLocation, Movement

random_seed = 87342
metrics = ["f1_micro", "f1_macro"]
test_size = 0.15

drop_features_lr = ["Heel", "Knee", "Hip", "Toe", "Pinkie", "Ankle"]
drop_features_center = ["Hip.Center"]

labels = ["Movement", "MajorLocation", "SignType"]

for label in labels:
    print("Label {}".format(label))
    X, y, le = preprocess_dataset(label, drop_feat_lr=drop_features_lr,
                                    drop_feat_center=drop_features_center, different_length=True,
                                    trick_maj_loc=False)
    #print_labels_statistics(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_seed, shuffle=True, stratify=y)
    for metric in metrics:
        best_clfs, best_params, tr_scores, val_scores, best_indeces = select_best_models(X_train, y_train, random_seed, scoring=metric, n_jobs=-1)
        ncols = max(int(round(len(best_clfs)//2)), 1)
        nrows = min(2, len(best_clfs))

        for i, (name, clf) in enumerate(best_clfs.items()):
            y_pred = best_clfs[name].predict(X_test)
            cm = confusion_matrix(y_test, y_pred)
            cmn = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            f, ax = plt.subplots()
            sns.heatmap(cmn, vmin=0, vmax=1, annot=True, fmt='.2f', cmap="Blues",
                        square=True, xticklabels=le.classes_,
                        yticklabels=le.classes_, ax=ax)
            if name == "Dummy":
                title = name + " - " + best_params["Dummy"]["clf__strategy"]
            elif name == "SVM":
                title = name + " - " + best_params["SVM"]["clf__kernel"]
            else:
                title = name
            title += " (tr {:.02f}".format(tr_scores[name][best_indeces[name]])
            title += " val {:.02f})".format(val_scores[name][best_indeces[name]])

            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title(title)
            plt.savefig("valid_results/{}/{}_{}.pdf".format(name, label, metric), format="pdf")
        with open("valid_results/{}_{}.json".format(label, metric), "w") as fp:
            json.dump(best_params, fp)