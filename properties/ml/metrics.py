import numpy as np
import matplotlib.pyplot as plt


def accuracy(y_true, y_pred, tolerance=0.1):
    score = 0
    for actual, pred in zip(y_true, y_pred):
        if (1 - tolerance) * actual < pred < (1 + tolerance) * actual:
            score += 1
    return score / len(y_true)

def plot_accuracy(y_true, y_pred, ranges, tolerance=0.1):
    accs = []
    num_properties = []
    for r in ranges:
        subset = [(y_t, y_p) for y_t, y_p in zip(y_true, y_pred) if r[0] < y_t < r[-1]]
        if subset:
            y_t, y_p = zip(*subset)
            num_properties.append(len(subset))
            accs.append(accuracy(y_t, y_p, tolerance))
        else:
            num_properties.append(0)
            accs.append(0)
    
    x = np.arange(len(ranges))
    plt.figure(figsize=(20, 5))
    plt.title('Accuracy of model by ranges')
    plt.xticks(x, [f'{_from:,}-{_to:,}$' for _from, _to in ranges])
    plt.ylim([0, 1])
    plt.plot(x, accs)
    for x_i, acc, num in zip(x, accs, num_properties):
        plt.annotate(f'{num} properties', xy=(x_i - 0.25, acc - 0.05))
    plt.show()
