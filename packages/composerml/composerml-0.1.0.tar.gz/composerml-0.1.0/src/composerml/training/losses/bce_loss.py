from .loss import Loss

class BCELoss(Loss):
    def __call__(self, predicted, label):
        predicted = predicted[0].clamp()
        return -(label*predicted.log() + (1-label)*(1-predicted).log())