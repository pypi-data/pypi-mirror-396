class ReduceLROnPlateau:
    def __init__(self, base_lr: float, factor: float = 0.1, patience: int = 10, min_lr: float = 0.0, threshold: float = 1e-4, mode: str = "min"):
        self.base_lr = base_lr
        self.factor = factor
        self.patience = patience
        self.min_lr = min_lr
        self.threshold = threshold
        self.mode = mode
        self.best = None
        self.num_bad = 0
        self.current_lr = base_lr

    def step(self, metric: float) -> float:
        if self.best is None:
            self.best = metric
            return self.current_lr
        improved = (metric < self.best - self.threshold) if self.mode == "min" else (metric > self.best + self.threshold)
        if improved:
            self.best = metric
            self.num_bad = 0
        else:
            self.num_bad += 1
            if self.num_bad >= self.patience:
                self.current_lr = max(self.min_lr, self.current_lr * self.factor)
                self.num_bad = 0
        return self.current_lr
