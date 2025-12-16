import pytest

from darfix.core.moment_types import MomentType
from darfix.core.utils import NoDimensionsError


def test_apply_moments(dataset):

    with pytest.raises(NoDimensionsError):
        dataset.apply_moments(indices=[1, 2, 3, 4])

    dataset.find_dimensions()
    dataset.reshape_data()
    moments = dataset.apply_moments(indices=[1, 2, 3, 4])
    assert moments[0][MomentType.COM].shape == dataset.frame_shape
    assert moments[1][MomentType.SKEWNESS].shape == dataset.frame_shape
