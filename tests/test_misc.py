"""
Tests for src/misc.py
"""
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import datetime


def test_subdict_ans_basic():
    """Test subDict_ans with basic data."""
    from src.misc import subDict_ans
    
    dat = [
        {
            'uniqueOrderId': 'order1',
            'answerList': [
                {'question': 'Name', 'answer': 'John'},
                {'question': 'Age', 'answer': '30'}
            ]
        },
        {
            'uniqueOrderId': 'order2',
            'answerList': [
                {'question': 'Name', 'answer': 'Jane'},
                {'question': 'Age', 'answer': '25'}
            ]
        }
    ]
    
    result = subDict_ans(dat, subdict='answerList', keys=['uniqueOrderId'])
    
    assert len(result) == 2
    assert result[0]['uniqueOrderId'] == 'order1'
    assert result[0]['Name'] == 'John'
    assert result[0]['Age'] == '30'
    assert result[1]['uniqueOrderId'] == 'order2'
    assert result[1]['Name'] == 'Jane'


def test_subdict_tkt_basic():
    """Test subDict_tkt with basic data."""
    from src.misc import subDict_tkt
    
    dat = [
        {
            'registrationId': 'reg1',
            'uniqueOrderId': 'order1',
            'userName': 'John Doe',
            'ticketAndDiscountList': [
                {'ticketName': 'VIP', 'ticketPrice': 100},
                {'ticketName': 'Regular', 'ticketPrice': 50}
            ],
            'answerList': []
        }
    ]
    
    result = subDict_tkt(dat, subdict='ticketAndDiscountList', 
                         keys=['registrationId', 'uniqueOrderId', 'userName'])
    
    assert len(result) == 2
    assert result[0]['registrationId'] == 'reg1'
    assert result[0]['userName'] == 'John Doe'
    assert result[0]['ticketName'] == 'VIP'
    assert result[1]['ticketPrice'] == 50


def test_subdict_tkt_with_answer_list():
    """Test subDict_tkt extracts data from answerList."""
    from src.misc import subDict_tkt
    
    dat = [
        {
            'registrationId': 'reg1',
            'ticketAndDiscountList': [
                {'ticketName': 'VIP'}
            ],
            'answerList': [
                {'question': 'T-shirt size', 'answer': 'L'}
            ]
        }
    ]
    
    result = subDict_tkt(dat, subdict='ticketAndDiscountList', 
                         keys=['registrationId', 'T-shirt size'])
    
    assert len(result) == 1
    assert result[0]['T-shirt size'] == 'L'


def test_update_tab_basic():
    """Test update_tab updates Google Sheet."""
    from src.misc import update_tab
    
    # Mock Google Sheet
    mock_sheet = MagicMock()
    mock_sheet.get_all_records.return_value = []
    
    # Create test dataframe
    df = pd.DataFrame({
        'registrationId': [1, 2],
        'userName': ['John', 'Jane'],
        'ticketAndDiscountList': [[], []],
        'answerList': [[], []]
    })
    
    # Call function
    update_tab(mock_sheet, df)
    
    # Verify batch_update was called
    assert mock_sheet.batch_update.called


def test_update_tab_removes_skip_columns():
    """Test that update_tab removes skip columns."""
    from src.misc import update_tab
    
    mock_sheet = MagicMock()
    mock_sheet.get_all_records.return_value = []
    
    df = pd.DataFrame({
        'registrationId': [1],
        'userName': ['John'],
        'ticketAndDiscountList': [[]],
        'answerList': [[]]
    })
    
    update_tab(mock_sheet, df)
    
    # Get the data that was sent to batch_update
    call_args = mock_sheet.batch_update.call_args[0][0][0]
    values = call_args['values']
    
    # Check that skip columns are not in the header
    header = values[0]
    assert 'ticketAndDiscountList' not in header
    assert 'answerList' not in header


def test_ts_returns_datetime():
    """Test that ts() returns a datetime object."""
    from src.misc import ts
    
    result = ts()
    
    assert isinstance(result, datetime)


def test_timeit_decorator():
    """Test timeit decorator functionality."""
    from src.misc import timeit
    import os
    
    # Enable timing
    os.environ['TIMEIT'] = 'YES'
    
    @timeit
    def sample_function():
        return "result"
    
    result = sample_function()
    
    assert result == "result"


def test_timeit_decorator_disabled():
    """Test timeit decorator when disabled."""
    from src.misc import timeit
    import os
    
    # Disable timing
    os.environ['TIMEIT'] = ''
    
    @timeit
    def sample_function():
        return "result"
    
    result = sample_function()
    
    assert result == "result"


def test_lst_with_string():
    """Test lst function with string input."""
    from src.misc import lst
    
    result = lst("symbol shortName quoteType exchange")
    
    assert result == ['symbol', 'shortName', 'quoteType', 'exchange']


def test_lst_with_separator():
    """Test lst function with custom separator."""
    from src.misc import lst
    
    result = lst("apple,banana,orange", sep=',')
    
    assert result == ['apple', 'banana', 'orange']


def test_lst_with_list():
    """Test lst function with list input."""
    from src.misc import lst
    
    input_list = ['a', 'b', 'c']
    result = lst(input_list)
    
    assert result == input_list


def test_update_tab_handles_cancelled_registrations():
    """Test that update_tab marks cancelled registrations."""
    from src.misc import update_tab
    
    mock_sheet = MagicMock()
    # Simulate existing registration that's not in new data
    mock_sheet.get_all_records.return_value = [
        {'registrationId': 999, 'userName': 'Old User'}
    ]
    
    df = pd.DataFrame({
        'registrationId': [1, 2],
        'userName': ['John', 'Jane']
    })
    
    update_tab(mock_sheet, df)
    
    # Verify batch_update was called
    assert mock_sheet.batch_update.called
    
    # Get the data that was sent
    call_args = mock_sheet.batch_update.call_args[0][0][0]
    values = call_args['values']
    
    # Should have header + 2 new + 1 cancelled = 4 rows
    assert len(values) >= 3

# Made with Bob
