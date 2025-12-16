
def get_predicted_label(model, outputs):
    """Return predicted label for sigmoid or softmax classifier."""
    if model.classification == "sigmoid":
        prob = outputs[0].data
        return 1 if prob >= 0.5 else 0

    elif model.classification == "softmax":
        probs = [v.data for v in outputs]
        return probs.index(max(probs))

    else:
        raise ValueError("Unknown classification type")


def evaluate(model, X, y, loss_fn):
    """
    Generic evaluation function.
    Handles both classification and regression.
    """
    n = len(X)
    correct = 0
    total_loss = 0.0

    for inputs, target in zip(X, y):
        outputs = model.predict(inputs)

        if model.classification != "none":
            pred = get_predicted_label(model, outputs)
            if pred == target:
                correct += 1

        loss = loss_fn(outputs, target)
        total_loss += loss.data

    avg_loss = total_loss / n

    if model.classification != "none":
        accuracy = correct / n
        return accuracy, avg_loss
    return avg_loss