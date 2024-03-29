import os
from os import path
import json
import pandas as pd
import numpy as np
from tqdm import tqdm
import shutil

folder = "Movement/mlp_runs/"

runs = [f.path for f in os.scandir(folder) if f.is_dir()]
runs = sorted(runs)

df = pd.DataFrame(columns=sorted(['seed', 'model', 'n_layers', 'n_lin_layers', 'hidden_dim', 'dropout', 'lin_dropout',
                           'bidirectional', 'epochs', 'batch_size', 'weighted_loss', 'optimizer',
                           'lr', 'final_lr', 'momentum', 'step_size', 'gamma', 'interpolated', 'folder', 'batch_norm']) + ['mean_train_loss', 'std_train_loss',
                           'mean_train_f1_score', 'std_train_f1_score', 'mean_val_loss', 'std_val_loss',
                           'mean_val_f1_score', 'std_val_f1_score'])


for run in tqdm(runs):
    try:
        with open(path.join(run, "log_file.json"), "r") as fp:
            json_log = json.load(fp)
            args = json_log["args"]
            args.pop("device")
            args["folder"] = run
            args = {k: args[k] for k in sorted(args.keys())}
            args = list(args.values())
            min_train_loss_per_fold = list(json_log["min_train_loss_per_fold"].values())
            min_val_loss_per_fold = list(json_log["min_val_loss_per_fold"].values())
            max_train_f1_score_per_fold = list(json_log["max_train_f1_score_per_fold"].values())
            max_val_f1_score_per_fold = list(json_log["max_val_f1_score_per_fold"].values())
            args += [np.mean(min_train_loss_per_fold), np.std(min_train_loss_per_fold)]
            args += [np.mean(max_train_f1_score_per_fold), np.std(max_train_f1_score_per_fold)]
            args += [np.mean(min_val_loss_per_fold), np.std(min_val_loss_per_fold)]
            args += [np.mean(max_val_f1_score_per_fold), np.std(max_val_f1_score_per_fold)]
            df.loc[-1] = args # adding a row
            df.index = df.index + 1  # shifting index
            df = df.sort_index()
    except FileNotFoundError as e:
        shutil.rmtree(run)

df.sort_values('mean_val_loss', inplace=True)
print("Best loss")
bl = df.iloc[0]
print(df.iloc[0])
df.sort_values('mean_val_f1_score', ascending=False, inplace=True)
print("Best F1-score")
print(df.iloc[0])
df.to_csv("{}summary.csv".format(folder), index=False)
print(df.iloc[0].compare(bl))
