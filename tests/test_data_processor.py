"""
Basic tests for data processor
"""
import pytest
from src.utils.data_processor import DataProcessor
from pathlib import Path


def test_data_processor_initialization():
    """Test DataProcessor can be initialized"""
    data_path = Path(__file__).parent.parent / 'Dataset'
    processor = DataProcessor(data_path)
    assert processor.data_path.exists()


def test_clean_numeric_column():
    """Test numeric column cleaning"""
    import pandas as pd
    from src.utils.data_processor import DataProcessor
    
    data_path = Path(__file__).parent.parent / 'Dataset'
    processor = DataProcessor(data_path)
    
    test_series = pd.Series(['1,234', '5,678', '9.99%'])
    result = processor.clean_numeric_column(test_series)
    
    assert result[0] == 1234
    assert result[1] == 5678
    assert result[2] == 9.99
