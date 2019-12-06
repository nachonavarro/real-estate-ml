def accuracy(y_true, y_pred, tolerance=0.1):
    score = 0
    for actual, pred in zip(y_true, y_pred):
        if (1 - tolerance) * actual < pred < (1 + tolerance) * actual:
            score += 1
    return score / len(y_true)
