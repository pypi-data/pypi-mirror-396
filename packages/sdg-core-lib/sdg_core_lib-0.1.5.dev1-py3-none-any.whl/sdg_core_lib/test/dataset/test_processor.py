import numpy as np
import pytest

from sdg_core_lib.dataset.datasets import Table, TableProcessor
from sdg_core_lib.dataset.columns import Numeric, Categorical, Column


@pytest.fixture(scope="module")
def test_data_dir(tmp_path_factory):
    """Create a temporary directory for test outputs that persists for all tests."""
    return tmp_path_factory.mktemp("test_outputs")


@pytest.fixture
def numeric_column():
    """Create a sample numeric column."""
    return Numeric(
        "age", "int", 0, np.array([25, 30, 35, 40, 45]).reshape(-1, 1), "continuous"
    )


@pytest.fixture
def categorical_column():
    """Create a sample categorical column."""
    return Categorical(
        "gender",
        "str",
        1,
        np.array(["M", "F", "M", "F", "M"]).reshape(-1, 1),
        "categorical",
    )


@pytest.fixture
def table_processor(test_data_dir):
    """Create a TableProcessor instance with a temporary output directory."""
    return TableProcessor(str(test_data_dir))


class TestTableProcessor:
    """Test suite for TableProcessor class."""

    def test_initialization(self, table_processor, test_data_dir):
        """Test that TableProcessor initializes correctly."""
        assert table_processor.dir_path == str(test_data_dir)
        assert table_processor.steps == {}

    def test_process_numeric_data(self, table_processor, numeric_column):
        """Test processing numeric data."""
        processed = table_processor.process([numeric_column])
        assert len(processed) == 1
        assert isinstance(processed[0], Numeric)
        assert processed[0].values.shape == (5, 1)

    def test_process_categorical_data(self, table_processor, categorical_column):
        """Test processing categorical data."""
        processed = table_processor.process([categorical_column])
        assert len(processed) == 1
        assert isinstance(processed[0], Categorical)
        # Should be one-hot encoded (2 categories -> 2 columns)
        assert processed[0].values.shape == (5, 2)

    def test_inverse_process(self, table_processor, numeric_column, categorical_column):
        """Test inverse processing of data."""
        # Process data first
        processed = table_processor.process([numeric_column, categorical_column])

        # Inverse process
        inverse_processed = table_processor.inverse_process(processed)

        # Verify results
        assert len(inverse_processed) == 2
        assert isinstance(inverse_processed[0], Column)
        assert isinstance(inverse_processed[1], Categorical)

        # Check numeric values are approximately equal
        np.testing.assert_allclose(
            inverse_processed[0].values.astype(float),
            numeric_column.values.astype(float),
            rtol=1e-6,
        )

    def test_empty_columns(self, table_processor):
        """Test processing with empty columns list."""
        with pytest.raises(ValueError):
            table_processor.process([])


class TestTableIntegration:
    """Integration tests for Table and TableProcessor."""

    @pytest.fixture
    def sample_table(self, test_data_dir, numeric_column, categorical_column):
        """Create a sample table for testing."""
        processor = TableProcessor(str(test_data_dir))
        return Table([numeric_column, categorical_column], processor)

    def test_table_preprocess(self, sample_table):
        """Test table preprocessing."""
        processed = sample_table.preprocess()
        assert len(processed.columns) == 2
        # Numeric column should be scaled
        assert not np.array_equal(
            processed.columns[0].values, sample_table.columns[0].values
        )
        # Categorical column should be one-hot encoded
        assert processed.columns[1].values.shape[1] > 1

    def test_table_postprocess(self, sample_table):
        """Test table postprocessing."""
        processed = sample_table.preprocess()
        restored = processed.postprocess()

        # Check numeric values are approximately equal
        np.testing.assert_allclose(
            restored.columns[0].values.astype(float),
            sample_table.columns[0].values.astype(float),
            rtol=1e-6,
        )

    def test_empty_table_initialization(self, test_data_dir):
        """Test creating a table with no columns."""
        with pytest.raises(ValueError, match="No columns provided for processing"):
            table = Table([], TableProcessor(str(test_data_dir)))
            table.preprocess()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_column_type(self, table_processor):
        """Test processing with invalid column type."""

        class InvalidColumn(Column):
            pass

        invalid_col = InvalidColumn("test", "int", 0, np.array([1, 2, 3]), "invalid")

        with pytest.raises(NotImplementedError):
            table_processor.process([invalid_col])

    def test_save_and_load_processor(self, test_data_dir, numeric_column):
        """Test saving and loading a processor."""
        # Create and save processor state
        processor = TableProcessor(str(test_data_dir))
        cols = processor.process([numeric_column])
        processor._save_all()

        # Create new processor and load state
        new_processor = TableProcessor(str(test_data_dir))
        new_processor.inverse_process(cols)

        # Verify loaded state
        assert len(new_processor.steps) == 1
        assert 0 in new_processor.steps
        assert len(new_processor.steps[0]) == 1
