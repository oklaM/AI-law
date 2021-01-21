import matplotlib
import matplotlib.pyplot as plt
import numpy as np


labels = ['linear', 'poly', 'rbf', 'sigmoid']
men_means = [55.48, 76.50, 75.80, 75.80]
women_means = [75.82, 77.29, 77.29, 77.29]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, men_means, width, label='2020/06')
rects2 = ax.bar(x + width/2, women_means, width, label='2020/12')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('F1 scores')
ax.set_title('F1 scores by kernel and data set time')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()


def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)
autolabel(rects2)

plt.ylim(0, 100)

fig.tight_layout()

plt.show()