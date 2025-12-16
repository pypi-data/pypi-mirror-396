from typing import Any

import numpy as np
from imblearn.base import BaseSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler


class RandomResampleToTarget:
    """Resample each class to an exact target count.

    - If a class has MORE samples than target → randomly undersample
    - If a class has FEWER samples than target → randomly oversample (with replacement)
    - If a class has EXACTLY the target → keep as is
    """

    def __init__(
        self,
        sampling_strategy: dict[Any, int] | None = None,
        random_state: int | None = None,
    ) -> None:
        self.sampling_strategy = sampling_strategy or {}
        self.random_state = random_state

    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.random_state)

        all_indices = []
        unique_classes = np.unique(y)

        for cls in unique_classes:
            cls_indices = np.where(y == cls)[0]
            n_samples = len(cls_indices)

            # Get target count for this class (default: keep original count)
            target = self.sampling_strategy.get(cls, n_samples)

            if target == n_samples:
                # Keep all samples
                selected = cls_indices
            elif target < n_samples:
                # Undersample: randomly select without replacement
                selected = rng.choice(cls_indices, size=target, replace=False)
            else:
                # Oversample: select all originals + sample with replacement to fill
                extra_needed = target - n_samples
                extra = rng.choice(cls_indices, size=extra_needed, replace=True)
                selected = np.concatenate([cls_indices, extra])

            all_indices.append(selected)

        sample_indices_ = np.concatenate(all_indices)

        # Shuffle the final indices
        rng.shuffle(sample_indices_)

        self.sample_indices_ = sample_indices_
        return X[sample_indices_], y[sample_indices_]


class ImbalancedSampler:
    def __init__(
        self,
        sampler_name: str,
        sampler_kwargs: dict[str, Any] | None = None,
        random_state: int | None = None,
        class_labels: dict[str, int] | None = None,
    ) -> None:
        self.sampler_name = sampler_name
        self.random_state = random_state

        if sampler_kwargs is None:
            sampler_kwargs = {}

        # Convert string keys in sampling_strategy to integer labels
        if sampler_name == "RandomResampleToTarget":
            if "sampling_strategy" not in sampler_kwargs:
                raise ValueError("Need sampling strategy for RandomResampleToTarget.")
            sampler_kwargs = sampler_kwargs.copy()
            sampler_kwargs["sampling_strategy"] = self._convert_strategy_keys(
                sampler_kwargs["sampling_strategy"], class_labels
            )
        else:
            if "sampling_strategy" in sampler_kwargs and type(sampler_kwargs["sampling_strategy"]) is not str:
                raise ValueError("Only string sampling strategy is supported, use RandomResampleToTarget instead.")

        self.sampler = self._get_sampler(sampler_kwargs)

    def _convert_strategy_keys(
        self, strategy: dict[str | int, int], class_labels: dict[str, int] | None
    ) -> dict[int, int]:
        """Convert string class names to integer labels in sampling_strategy."""
        if class_labels is None:
            raise ValueError("Need class labels for RandomResampleToTarget")

        converted: dict[int, int] = {}
        for key, value in strategy.items():
            if isinstance(key, str) and key in class_labels:
                converted[class_labels[key]] = value
            elif isinstance(key, int):
                # Keep as-is if already int
                converted[key] = value
        return converted

    def _get_sampler(self, sampler_kwargs: dict[str, Any]) -> BaseSampler | RandomResampleToTarget:
        if self.sampler_name == "RandomOverSampler":
            return RandomOverSampler(random_state=self.random_state, **sampler_kwargs)
        elif self.sampler_name == "RandomUnderSampler":
            return RandomUnderSampler(random_state=self.random_state, **sampler_kwargs)
        elif self.sampler_name == "RandomResampleToTarget":
            return RandomResampleToTarget(random_state=self.random_state, **sampler_kwargs)
        else:
            raise ValueError(f"Sampler {self.sampler_name} is not supported!")

    def fit(self, X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        return X_resampled, y_resampled

    def sample_indices(self) -> np.ndarray:
        return self.sampler.sample_indices_
