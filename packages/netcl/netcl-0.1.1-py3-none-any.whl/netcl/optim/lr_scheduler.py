class WarmupCosine:
    def __init__(self, base_lr: float, max_epochs: int, warmup_epochs: int = 5, min_lr: float = 0.0):
        self.base_lr = base_lr
        self.max_epochs = max_epochs
        self.warmup_epochs = warmup_epochs
        self.min_lr = min_lr

    def lr(self, epoch: int) -> float:
        if epoch <= self.warmup_epochs:
            return self.base_lr * epoch / max(1, self.warmup_epochs)
        import math

        t = (epoch - self.warmup_epochs) / max(1, self.max_epochs - self.warmup_epochs)
        return self.min_lr + 0.5 * (self.base_lr - self.min_lr) * (1 + math.cos(math.pi * t))
