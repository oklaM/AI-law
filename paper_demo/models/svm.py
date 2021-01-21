import os
import numpy as np
from os.path import abspath, dirname, join
from sklearn import svm
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score

X_y = np.load(join(os.getcwd(), "..", "data", "trains_06.npz"))
X = X_y["X"]
y = X_y["y"]
y = np.array(y == 5).astype(int)
n = np.size(y)
print("n = %d" % n)
X_train1 = X[:int(n*0.8)]
y_train1 = y[:int(n*0.8)]
X_test1 = X[int(n*0.8):]
y_test1 = y[int(n*0.8):]
X_y_test = np.load(join(os.getcwd(), "..", "data", "trains_12.npz"))
X = X_y_test["X"]
y = X_y_test["y"]
y = np.array(y == 5).astype(int)
n = np.size(y)
print("n = %d" % n)
X_train2 = X[:int(n*0.8)]
y_train2 = y[:int(n*0.8)]
X_test2 = X[int(n*0.8):]
y_test2 = y[int(n*0.8):]
# fit the model, don't regularize for illustration purposes

kernels = ["linear", "poly", "rbf", "sigmoid"]
Cs = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1000]
best_kernel = None
best_C = None
temp_f1score = 0
for kernel in kernels:
    print(kernel)
    for C in Cs:
        clf = svm.SVC(kernel=kernel, C=C)
        clf.fit(X_train1, y_train1)
        y_pred = clf.predict(X_test1)

        y_true = y_test1
        p = precision_score(y_true, y_pred, average='binary')
        r = recall_score(y_true, y_pred, average='binary')
        f1score = f1_score(y_true, y_pred, average='binary')

        print(p, r, f1score)
        if f1score > temp_f1score:
            best_kernel = kernel
            best_C = C
            temp_f1score = f1score
print(best_kernel, best_C)
print(80 * "_")
best_kernel = None
best_C = None
temp_f1score = 0
for kernel in kernels:
    print(kernel)
    for C in Cs:
        clf = svm.SVC(kernel=kernel, C=C)
        clf.fit(X_train2, y_train2)
        y_pred = clf.predict(X_test2)

        y_true = y_test2
        p = precision_score(y_true, y_pred, average='binary')
        r = recall_score(y_true, y_pred, average='binary')
        f1score = f1_score(y_true, y_pred, average='binary')

        print(p, r, f1score)
        if f1score > temp_f1score:
            best_kernel = kernel
            best_C = C
            temp_f1score = f1score
print(best_kernel, best_C)