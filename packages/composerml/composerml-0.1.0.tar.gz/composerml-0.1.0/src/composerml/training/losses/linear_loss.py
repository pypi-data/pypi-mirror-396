from .loss import Loss


class LinearLoss(Loss):
    def __call__(self, predicted, target):
        """
        predicted: list[Value] length d
        target: list[float] length d
        """
        assert len(predicted) == len(target)
        d = len(predicted)
        
        loss = 0.0
        
        for p, t in zip(predicted, target):
            loss = loss + (p - t) ** 2

        return loss / d
    


