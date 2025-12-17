import shutil
from pathlib import Path

import numpy as np
import pytest
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from sdg_core_lib.dataset.steps import (
    ScalerWrapper,
    NoneStep,
    OrdinalEncoderWrapper,
    OneHotEncoderWrapper,
)


@pytest.fixture
def temp_dir():
    """Create and clean up a temporary directory for test files."""
    test_dir = Path("test_temp_dir")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    shutil.rmtree(test_dir, ignore_errors=True)


class TestScalerWrapper:
    """Test suite for ScalerWrapper class."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample test data."""
        return np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)

    @pytest.mark.parametrize(
        "mode,expected_scaler_type",
        [("standard", StandardScaler), ("minmax", MinMaxScaler)],
    )
    def test_initialization(self, mode, expected_scaler_type):
        """Test that ScalerWrapper initializes with correct parameters."""
        step = ScalerWrapper(position=0, col_name="test_col", mode=mode)
        assert step.type_name == "scaler"
        assert step.mode == mode
        assert step.position == 0
        assert step.col_name == "test_col"
        assert step.filename == f"0_test_col_{mode}_scaler.skops"

    def test_fit_transform(self, sample_data):
        """Test fit_transform method."""
        step = ScalerWrapper(position=0, col_name="test_col", mode="standard")
        transformed = step.fit_transform(sample_data)
        assert transformed.shape == sample_data.shape
        assert step.operator is not None
        assert hasattr(step.operator, "transform")

    def test_inverse_transform(self, sample_data):
        """Test inverse_transform method."""
        step = ScalerWrapper(position=0, col_name="test_col", mode="minmax")
        transformed = step.fit_transform(sample_data)
        inverse_transformed = step.inverse_transform(transformed)
        np.testing.assert_allclose(inverse_transformed, sample_data, rtol=1e-6)

    def test_save_and_load(self, sample_data, temp_dir):
        """Test save and load functionality."""
        step = ScalerWrapper(position=0, col_name="test_col", mode="standard")
        step.fit_transform(sample_data)
        save_path = temp_dir / "test_scaler"
        step.save(str(save_path))
        assert (save_path / f"{step.filename}").exists()
        loaded_step = ScalerWrapper(position=0, col_name="test_col", mode="standard")
        loaded_step.load(str(save_path))
        assert isinstance(loaded_step.operator, StandardScaler)
        assert loaded_step.position == 0
        assert loaded_step.col_name == "test_col"


class TestNoneStep:
    """Test suite for NoneStep class."""

    @pytest.fixture
    def sample_data(self):
        """Generate sample test data."""
        return np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)

    def test_initialization(self):
        """Test that NoneStep initializes with correct parameters."""
        step = NoneStep(position=1)
        assert step.type_name == "none"
        assert step.position == 1
        assert step.col_name == ""

    def test_fit_transform_returns_same_data(self, sample_data):
        """Test that fit_transform returns the input data unchanged."""
        step = NoneStep(position=0)
        result = step.fit_transform(sample_data)
        np.testing.assert_array_equal(result, sample_data)

    def test_transform_returns_same_data(self, sample_data):
        """Test that transform returns the input data unchanged."""
        step = NoneStep(position=0)
        result = step.transform(sample_data)
        np.testing.assert_array_equal(result, sample_data)

    def test_inverse_transform_returns_same_data(self, sample_data):
        """Test that inverse_transform returns the input data unchanged."""
        step = NoneStep(position=0)
        result = step.inverse_transform(sample_data)
        np.testing.assert_array_equal(result, sample_data)


class TestLabelEncoderWrapper:
    """Test suite for LabelEncoderWrapper class."""

    @pytest.fixture
    def categorical_data(self):
        """Generate sample categorical data."""
        return np.array(["a", "b", "c", "a", "b"]).reshape(-1, 1)

    def test_fit_transform(self, categorical_data):
        """Test fit_transform with categorical data."""
        step = OrdinalEncoderWrapper(position=0, col_name="category")
        transformed = step.fit_transform(categorical_data)
        assert transformed.shape == categorical_data.shape  # Same number of samples
        assert set(transformed.flatten().tolist()) == {
            0,
            1,
            2,
        }  # Should encode to 0, 1, 2

    def test_inverse_transform(self, categorical_data):
        """Test inverse_transform to get back original categories."""
        step = OrdinalEncoderWrapper(position=0, col_name="category")
        transformed = step.fit_transform(categorical_data)
        inverse_transformed = step.inverse_transform(transformed)
        np.testing.assert_array_equal(inverse_transformed, categorical_data)


class TestOneHotEncoderWrapper:
    """Test suite for OneHotEncoderWrapper class."""

    @pytest.fixture
    def categorical_data(self):
        """Generate sample categorical data."""
        return np.array(["a", "b", "c", "a", "b"]).reshape(-1, 1)

    def test_fit_transform(self, categorical_data):
        """Test fit_transform with one-hot encoding."""
        step = OneHotEncoderWrapper(position=0, col_name="category")
        transformed = step.fit_transform(categorical_data)
        assert transformed.shape == (5, 3)  # 5 samples, 3 categories
        assert np.all(transformed.sum(axis=1) == 1)  # Each row sums to 1 (one-hot)
        assert set(transformed.flatten().tolist()) == {0.0, 1.0}  # Only 0s and 1s

    def test_inverse_transform(self, categorical_data):
        """Test inverse_transform to get back original categories."""
        step = OneHotEncoderWrapper(position=0, col_name="category")
        transformed = step.fit_transform(categorical_data)
        inverse_transformed = step.inverse_transform(transformed)
        np.testing.assert_array_equal(inverse_transformed, categorical_data)

    def test_handles_unknown_categories(self):
        """Test behavior with unknown categories during transform."""
        train_data = np.array(["a", "b", "c"]).reshape(-1, 1)
        test_data = np.array(["a", "d", "b"]).reshape(-1, 1)  # 'd' is unknown
        step = OneHotEncoderWrapper(position=0, col_name="category")
        step.fit_transform(train_data)
        with pytest.raises(ValueError):
            step.transform(test_data)
