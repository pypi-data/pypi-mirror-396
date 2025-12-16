from .loss import Loss


class CrossEntropyLoss(Loss):
    def __call__(self,predicted, label):
        log_preds = [p.clamp().log() for p in predicted]
        return -log_preds[label]