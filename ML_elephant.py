import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from load_to_db import data_file_dir, read_data_from_csv

file_dir = data_file_dir()
df = read_data_from_csv(file_dir)


AM105 = df[df['tag_id'] == 'AM105']


# Data inspection with scatter plot
# plt.scatter(AM105['long'], AM105['lat'])
# plt.show()

## PREPROCESSING
# z-score normalization
scaler = StandardScaler()

AM105_normalized = scaler.fit_transform(AM105[['long', 'lat']])

print(AM105_normalized)
AM105_norm = pd.DataFrame(AM105_normalized, columns = ['long', 'lat'])
print(AM105_norm)

# Create empty model
km = KMeans(4, random_state = 8)

# Train the model
km.fit_predict(AM105_norm)

# Inspection of labels
print(km.labels_)


# Evaluate the result in a plot, the labels from our model correspond to 
# our samples and can be used to color the plot
plt.scatter(AM105_norm['long'], AM105_norm['lat'], c = km.labels_)
plt.show()




#%%
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn import metrics

db = DBSCAN(eps=0.1, min_samples=35).fit(AM105_norm)
labels = db.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print("Estimated number of clusters: %d" % n_clusters_)
print("Estimated number of noise points: %d" % n_noise_)

AM105_norm_np = AM105_norm.to_numpy()
print(AM105_norm_np)

unique_labels = set(labels)
core_samples_mask = np.zeros_like(labels, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True

colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = labels == k

    xy = AM105_norm_np[class_member_mask & core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=14,
    )

    xy = AM105_norm_np[class_member_mask & ~core_samples_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=6,
    )

plt.title(f"Estimated number of clusters: {n_clusters_}")
plt.show()



# # print(AM105.info())
# AM105['timestamp'] = pd.to_datetime(AM105['timestamp'])
# # AM105 = AM105.set_index(AM105.timestamp)

# print(AM105.info())