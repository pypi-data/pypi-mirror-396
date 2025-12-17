"""
CREATESONLINE Data I/O Operations

Pure Python data input/output operations.
CSV and JSON reading/writing functionality.
"""

import json
import csv
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from .dataframe import CreatesonlineDataFrame


def read_csv(
    filepath: Union[str, Path],
    sep: str = ',',
    header: Union[int, str, None] = 0,
    index_col: Optional[Union[int, str]] = None,
    usecols: Optional[List[Union[int, str]]] = None,
    skiprows: Optional[Union[int, List[int]]] = None,
    nrows: Optional[int] = None,
    encoding: str = 'utf-8'
) -> CreatesonlineDataFrame:
    """
    Read CSV file into CreatesonlineDataFrame
    
    Args:
        filepath: Path to CSV file
        sep: Field separator
        header: Row to use as column names (0 for first row, None for no header)
        index_col: Column to use as row index
        usecols: Columns to read
        skiprows: Rows to skip
        nrows: Number of rows to read
        encoding: File encoding
    
    Returns:
        CreatesonlineDataFrame with CSV data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding=encoding, newline='') as f:
        # Handle skiprows
        if skiprows:
            if isinstance(skiprows, int):
                for _ in range(skiprows):
                    next(f, None)
            else:
                lines_to_skip = set(skiprows)
                for i, line in enumerate(f):
                    if i not in lines_to_skip:
                        f.seek(0)
                        for _ in range(i):
                            next(f)
                        break
        
        reader = csv.reader(f, delimiter=sep)
        
        # Read all rows
        rows = []
        for i, row in enumerate(reader):
            rows.append(row)
            if nrows and i >= nrows - 1:
                break
        
        if not rows:
            return CreatesonlineDataFrame()
        
        # Handle header
        if header == 0 or header is True:
            columns = rows[0]
            data_rows = rows[1:]
        elif isinstance(header, int):
            columns = rows[header]
            data_rows = rows[header + 1:]
        elif header is None:
            columns = [f'col_{i}' for i in range(len(rows[0]))]
            data_rows = rows
        else:
            raise ValueError("Invalid header parameter")
        
        # Handle usecols
        if usecols:
            if all(isinstance(col, str) for col in usecols):
                # Column names
                col_indices = [columns.index(col) for col in usecols if col in columns]
                columns = [columns[i] for i in col_indices]
            else:
                # Column indices
                col_indices = [i for i in usecols if i < len(columns)]
                columns = [columns[i] for i in col_indices]
            
            data_rows = [[row[i] for i in col_indices] for row in data_rows]
        
        # Convert to appropriate types
        data = {}
        for i, col in enumerate(columns):
            col_data = []
            for row in data_rows:
                if i < len(row):
                    value = row[i].strip()
                    # Try to convert to number
                    if value == '':
                        col_data.append(None)
                    elif value.lower() in ('true', 'false'):
                        col_data.append(value.lower() == 'true')
                    else:
                        try:
                            if '.' in value:
                                col_data.append(float(value))
                            else:
                                col_data.append(int(value))
                        except ValueError:
                            col_data.append(value)
                else:
                    col_data.append(None)
            
            data[col] = col_data
        
        df = CreatesonlineDataFrame(data=data)
        
        # Handle index_col
        if index_col is not None:
            if isinstance(index_col, str):
                df = df.set_index(index_col)
            elif isinstance(index_col, int):
                col_name = columns[index_col]
                df = df.set_index(col_name)
        
        return df


def to_csv(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    sep: str = ',',
    index: bool = True,
    header: bool = True,
    encoding: str = 'utf-8'
) -> None:
    """
    Write CreatesonlineDataFrame to CSV file
    
    Args:
        df: DataFrame to write
        filepath: Output file path
        sep: Field separator
        index: Whether to write row index
        header: Whether to write column header
        encoding: File encoding
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f, delimiter=sep)
        
        # Write header
        if header:
            header_row = []
            if index:
                header_row.append('index')
            header_row.extend(df.columns)
            writer.writerow(header_row)
        
        # Write data rows
        for i in range(len(df.index)):
            row = []
            if index:
                row.append(df.index[i])
            
            for col in df.columns:
                value = df._data[col][i]
                row.append('' if value is None else str(value))
            
            writer.writerow(row)


def read_json(
    filepath: Union[str, Path],
    orient: str = 'records',
    encoding: str = 'utf-8'
) -> CreatesonlineDataFrame:
    """
    Read JSON file into CreatesonlineDataFrame
    
    Args:
        filepath: Path to JSON file
        orient: JSON orientation ('records', 'dict', 'list')
        encoding: File encoding
    
    Returns:
        CreatesonlineDataFrame with JSON data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding=encoding) as f:
        data = json.load(f)
    
    if orient == 'records':
        # List of {column: value} dicts
        return CreatesonlineDataFrame(data=data)
    elif orient == 'dict':
        # {column: [values]} dict
        return CreatesonlineDataFrame(data=data)
    elif orient == 'list':
        # {column: [values]} dict (same as dict)
        return CreatesonlineDataFrame(data=data)
    else:
        raise ValueError(f"Invalid orient: {orient}")


def to_json(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    orient: str = 'records',
    indent: Optional[int] = None,
    encoding: str = 'utf-8'
) -> None:
    """
    Write CreatesonlineDataFrame to JSON file
    
    Args:
        df: DataFrame to write
        filepath: Output file path
        orient: JSON orientation ('records', 'dict', 'list')
        indent: JSON indentation
        encoding: File encoding
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = df.to_dict(orient=orient)
    
    with open(filepath, 'w', encoding=encoding) as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)


def read_excel(
    filepath: Union[str, Path],
    sheet_name: Union[str, int] = 0,
    header: Union[int, None] = 0,
    index_col: Optional[Union[int, str]] = None,
    usecols: Optional[List[Union[int, str]]] = None,
    skiprows: Optional[Union[int, List[int]]] = None,
    nrows: Optional[int] = None
) -> CreatesonlineDataFrame:
    """
    Read Excel file into CreatesonlineDataFrame
    
    Note: This is a basic implementation that reads Excel files as CSV.
    For full Excel support, users should save as CSV first.
    
    Args:
        filepath: Path to Excel file
        sheet_name: Sheet name or index
        header: Row to use as column names
        index_col: Column to use as row index
        usecols: Columns to read
        skiprows: Rows to skip
        nrows: Number of rows to read
    
    Returns:
        CreatesonlineDataFrame with Excel data
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Try to import pandas for Excel support
    try:
        import pandas as pd
        logger.info("Using pandas for Excel reading")
        
        # Use pandas to read Excel
        df_pandas = pd.read_excel(
            filepath,
            sheet_name=sheet_name,
            header=header,
            index_col=index_col,
            usecols=usecols,
            skiprows=skiprows,
            nrows=nrows
        )
        
        # Convert pandas DataFrame to CreatesonlineDataFrame
        data = {}
        for col in df_pandas.columns:
            data[col] = df_pandas[col].tolist()
        
        return CreatesonlineDataFrame(data=data, index=df_pandas.index.tolist())
        
    except ImportError:
        logger.warning("Pandas not available for Excel reading. Attempting CSV fallback.")
        
        # Fallback: Try to find a CSV version of the file
        filepath = Path(filepath)
        csv_path = filepath.with_suffix('.csv')
        
        if csv_path.exists():
            logger.info(f"Found CSV version: {csv_path}")
            return read_csv(
                csv_path,
                header=header,
                index_col=index_col,
                usecols=usecols,
                skiprows=skiprows,
                nrows=nrows
            )
        else:
            # Create an informative error message with suggestions
            error_msg = (
                f"Excel reading requires pandas library. Install with: pip install pandas openpyxl\n"
                f"Alternatively, save '{filepath}' as CSV and use read_csv() instead.\n"
                f"Expected CSV path: {csv_path}"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)


def to_excel(
    df: CreatesonlineDataFrame,
    filepath: Union[str, Path],
    sheet_name: str = 'Sheet1',
    index: bool = True,
    header: bool = True
) -> None:
    """
    Write CreatesonlineDataFrame to Excel file
    
    Note: This is a basic implementation that saves as CSV.
    For full Excel support, users can convert CSV to Excel manually.
    
    Args:
        df: DataFrame to write
        filepath: Output file path
        sheet_name: Sheet name
        index: Whether to write row index
        header: Whether to write column header
    """
    # Convert to CSV instead
    csv_path = Path(filepath).with_suffix('.csv')
    to_csv(df, csv_path, index=index, header=header)


# Utility functions for data conversion
def from_dict(data: Dict[str, List[Any]]) -> CreatesonlineDataFrame:
    """Create DataFrame from dictionary"""
    return CreatesonlineDataFrame(data=data)


def from_records(records: List[Dict[str, Any]]) -> CreatesonlineDataFrame:
    """Create DataFrame from list of records"""
    return CreatesonlineDataFrame(data=records)


def concat(
    dataframes: List[CreatesonlineDataFrame],
    axis: int = 0,
    ignore_index: bool = False
) -> CreatesonlineDataFrame:
    """
    Concatenate multiple DataFrames
    
    Args:
        dataframes: List of DataFrames to concatenate
        axis: Axis to concatenate along (0=rows, 1=columns)
        ignore_index: Reset index in result
    
    Returns:
        Concatenated DataFrame
    """
    if not dataframes:
        return CreatesonlineDataFrame()
    
    result = dataframes[0].copy()
    
    for df in dataframes[1:]:
        result = result.concat(df, axis=axis)
    
    if ignore_index:
        result = result.reset_index(drop=True)
    
    return result


# Data validation utilities
def validate_dataframe(df: CreatesonlineDataFrame) -> Dict[str, Any]:
    """
    Validate DataFrame and return diagnostics
    
    Args:
        df: DataFrame to validate
    
    Returns:
        Dictionary with validation results
    """
    return {
        'shape': df.shape,
        'columns': df.columns,
        'null_counts': {
            col: sum(1 for val in df._data[col] if val is None)
            for col in df.columns
        },
        'data_types': {
            col: type(df._data[col][0]).__name__ if df._data[col] else 'empty'
            for col in df.columns
        },
        'memory_usage_estimate': f"{df.size * 8} bytes",
        'duplicate_rows': 0,  # Would need to implement duplicate detection
        'is_valid': True
    }


def sample_data(df: CreatesonlineDataFrame, n: int = 5, random_state: Optional[int] = None) -> CreatesonlineDataFrame:
    """
    Sample n rows from DataFrame
    
    Args:
        df: DataFrame to sample from
        n: Number of rows to sample
        random_state: Random seed for reproducibility
    
    Returns:
        DataFrame with sampled rows
    """
    import random
    
    if random_state:
        random.seed(random_state)
    
    if n >= len(df):
        return df.copy()
    
    indices = random.sample(range(len(df)), n)
    indices.sort()
    
    new_data = {}
    for col in df.columns:
        new_data[col] = [df._data[col][i] for i in indices]
    
    new_index = [df.index[i] for i in indices]
    
    return CreatesonlineDataFrame(
        data=new_data,
        index=new_index
    )