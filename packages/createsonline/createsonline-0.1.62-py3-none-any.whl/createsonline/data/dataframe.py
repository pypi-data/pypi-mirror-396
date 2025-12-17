"""
CREATESONLINE DataFrame Implementation

Pure Python dataframe data structure.
Lightweight alternative to Pandas DataFrame.
"""

import json
from typing import Any, Dict, List, Optional, Union, Iterator, Callable, Tuple
from .series import CreatesonlineSeries

# Optional numpy import with fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    NDArrayType = np.ndarray
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    NDArrayType = Any  # Fallback type


class CreatesonlineDataFrame:
    """
    CREATESONLINE DataFrame - Two-dimensional data structure
    
    Pure Python implementation of a dataframe similar to Pandas DataFrame
    but with zero external dependencies (except numpy for numerical operations).
    """
    
    def __init__(
        self,
        data: Union[Dict[str, List[Any]], List[Dict[str, Any]], List[List[Any]]] = None,
        columns: Optional[List[str]] = None,
        index: Optional[List[str]] = None
    ):
        """
        Initialize CREATESONLINE DataFrame
        
        Args:
            data: DataFrame data as dict of columns, list of rows, or list of lists
            columns: Column names
            index: Row index labels
        """
        if data is None:
            self._data = {}
            self._columns = columns or []
            self._index = index or []
        elif isinstance(data, dict):
            # Dict of {column: [values]}
            self._columns = list(data.keys())
            self._data = {col: list(values) for col, values in data.items()}
            
            # Ensure all columns have same length
            if self._columns:
                expected_length = len(self._data[self._columns[0]])
                for col in self._columns:
                    if len(self._data[col]) != expected_length:
                        raise ValueError(f"All columns must have same length. Column '{col}' has length {len(self._data[col])}, expected {expected_length}")
                
                self._index = index or list(range(expected_length))
            else:
                self._index = []
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            # List of {column: value} dicts (rows)
            all_columns = set()
            for row in data:
                all_columns.update(row.keys())
            
            self._columns = columns or sorted(list(all_columns))
            self._data = {col: [] for col in self._columns}
            
            for row in data:
                for col in self._columns:
                    self._data[col].append(row.get(col, None))
            
            self._index = index or list(range(len(data)))
        elif isinstance(data, list) and data and isinstance(data[0], list):
            # List of lists (rows)
            if not columns:
                raise ValueError("columns parameter required for list of lists")
            
            self._columns = list(columns)
            self._data = {col: [] for col in self._columns}
            
            for row in data:
                if len(row) != len(self._columns):
                    raise ValueError(f"Row length {len(row)} doesn't match columns length {len(self._columns)}")
                
                for i, val in enumerate(row):
                    self._data[self._columns[i]].append(val)
            
            self._index = index or list(range(len(data)))
        else:
            raise ValueError("Invalid data format")
        
        # Ensure index length matches data length
        if self._columns and len(self._index) != len(self._data[self._columns[0]]):
            if index is None:
                self._index = list(range(len(self._data[self._columns[0]])))
            else:
                raise ValueError("Index length must match data length")
    
    def __len__(self) -> int:
        """Return number of rows"""
        return len(self._index)
    
    def __getitem__(self, key: Union[str, List[str], slice, int]) -> Union[CreatesonlineSeries, 'CreatesonlineDataFrame']:
        """Get column(s) or row(s)"""
        if isinstance(key, str):
            # Single column
            if key not in self._columns:
                raise KeyError(f"Column '{key}' not found")
            return CreatesonlineSeries(
                data=self._data[key],
                index=self._index,
                name=key
            )
        elif isinstance(key, list):
            # Multiple columns
            for col in key:
                if col not in self._columns:
                    raise KeyError(f"Column '{col}' not found")
            
            new_data = {col: self._data[col] for col in key}
            return CreatesonlineDataFrame(
                data=new_data,
                index=self._index
            )
        elif isinstance(key, (int, slice)):
            # Row(s) by position
            if isinstance(key, int):
                if key < 0:
                    key = len(self._index) + key
                if not (0 <= key < len(self._index)):
                    raise IndexError("Row index out of range")
                
                row_data = {col: self._data[col][key] for col in self._columns}
                return CreatesonlineSeries(
                    data=list(row_data.values()),
                    index=self._columns,
                    name=self._index[key]
                )
            else:
                # Slice
                new_data = {col: self._data[col][key] for col in self._columns}
                return CreatesonlineDataFrame(
                    data=new_data,
                    index=self._index[key]
                )
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
    
    def __setitem__(self, key: str, value: Union[List[Any], CreatesonlineSeries, Any]):
        """Set column values"""
        if isinstance(value, CreatesonlineSeries):
            if len(value) != len(self._index):
                raise ValueError("Series length must match DataFrame length")
            self._data[key] = value.values
        elif isinstance(value, list):
            if len(value) != len(self._index):
                raise ValueError("List length must match DataFrame length")
            self._data[key] = list(value)
        else:
            # Scalar value - broadcast to all rows
            self._data[key] = [value] * len(self._index)
        
        if key not in self._columns:
            self._columns.append(key)
    
    def __delitem__(self, key: str):
        """Delete column"""
        if key not in self._columns:
            raise KeyError(f"Column '{key}' not found")
        
        self._columns.remove(key)
        del self._data[key]
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over column names"""
        return iter(self._columns)
    
    def __str__(self) -> str:
        """String representation"""
        if not self._columns or not self._index:
            return "Empty CreatesonlineDataFrame"
        
        # Calculate column widths
        col_widths = {}
        for col in self._columns:
            col_widths[col] = max(
                len(str(col)),
                max(len(str(val)) for val in self._data[col][:20])  # Limit to first 20
            )
        
        # Build header
        header = "".join(f"{col:<{col_widths[col] + 2}}" for col in self._columns)
        lines = [header]
        lines.append("-" * len(header))
        
        # Build rows (limit to 20)
        for i, idx in enumerate(self._index[:20]):
            row = "".join(
                f"{str(self._data[col][i]):<{col_widths[col] + 2}}" 
                for col in self._columns
            )
            lines.append(row)
        
        if len(self._index) > 20:
            lines.append("...")
            lines.append(f"[{len(self._index)} rows x {len(self._columns)} columns]")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """String representation"""
        return self.__str__()
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Get DataFrame shape (rows, columns)"""
        return (len(self._index), len(self._columns))
    
    @property
    def size(self) -> int:
        """Get total number of elements"""
        return len(self._index) * len(self._columns)
    
    @property
    def columns(self) -> List[str]:
        """Get column names"""
        return self._columns.copy()
    
    @property
    def index(self) -> List[str]:
        """Get row index"""
        return self._index.copy()
    
    @property
    def values(self) -> List[List[Any]]:
        """Get DataFrame values as list of lists"""
        return [
            [self._data[col][i] for col in self._columns]
            for i in range(len(self._index))
        ]
    
    def head(self, n: int = 5) -> 'CreatesonlineDataFrame':
        """Get first n rows"""
        return self[:n]
    
    def tail(self, n: int = 5) -> 'CreatesonlineDataFrame':
        """Get last n rows"""
        return self[-n:]
    
    def copy(self) -> 'CreatesonlineDataFrame':
        """Create a copy of the DataFrame"""
        return CreatesonlineDataFrame(
            data={col: values.copy() for col, values in self._data.items()},
            index=self._index.copy()
        )
    
    def info(self) -> Dict[str, Any]:
        """Get DataFrame info"""
        return {
            'shape': self.shape,
            'columns': len(self._columns),
            'non_null_count': {
                col: sum(1 for val in self._data[col] if val is not None)
                for col in self._columns
            },
            'dtypes': {
                col: type(self._data[col][0]).__name__ if self._data[col] else 'object'
                for col in self._columns
            },
            'memory_usage': f"{self.size * 8} bytes"  # Rough estimate
        }
    
    def describe(self) -> 'CreatesonlineDataFrame':
        """Descriptive statistics for numeric columns"""
        stats = {}
        
        for col in self._columns:
            series = self[col]
            col_stats = series.describe()
            stats[col] = col_stats
        
        # Transpose to get stats as rows
        stat_names = list(next(iter(stats.values())).keys())
        result_data = {}
        
        for stat in stat_names:
            result_data[stat] = [stats[col].get(stat, None) for col in self._columns]
        
        return CreatesonlineDataFrame(
            data=result_data,
            columns=self._columns,
            index=stat_names
        )
    
    def sort_values(
        self, 
        by: Union[str, List[str]], 
        ascending: bool = True
    ) -> 'CreatesonlineDataFrame':
        """Sort DataFrame by column(s)"""
        if isinstance(by, str):
            by = [by]
        
        # Check columns exist
        for col in by:
            if col not in self._columns:
                raise KeyError(f"Column '{col}' not found")
        
        # Create list of (row_data, original_index) for sorting
        rows_with_index = []
        for i in range(len(self._index)):
            row_data = [self._data[col][i] for col in by]
            rows_with_index.append((row_data, i))
        
        # Sort by the specified columns
        rows_with_index.sort(
            key=lambda x: x[0],
            reverse=not ascending
        )
        
        # Extract sorted indices
        sorted_indices = [original_i for _, original_i in rows_with_index]
        
        # Create new DataFrame with sorted data
        new_data = {}
        for col in self._columns:
            new_data[col] = [self._data[col][i] for i in sorted_indices]
        
        new_index = [self._index[i] for i in sorted_indices]
        
        return CreatesonlineDataFrame(
            data=new_data,
            index=new_index
        )
    
    def sort_index(self, ascending: bool = True) -> 'CreatesonlineDataFrame':
        """Sort DataFrame by index"""
        index_with_position = [(idx, i) for i, idx in enumerate(self._index)]
        index_with_position.sort(key=lambda x: x[0], reverse=not ascending)
        
        sorted_indices = [i for _, i in index_with_position]
        
        new_data = {}
        for col in self._columns:
            new_data[col] = [self._data[col][i] for i in sorted_indices]
        
        new_index = [self._index[i] for i in sorted_indices]
        
        return CreatesonlineDataFrame(
            data=new_data,
            index=new_index
        )
    
    def reset_index(self, drop: bool = True) -> 'CreatesonlineDataFrame':
        """Reset index to default integer index"""
        if drop:
            return CreatesonlineDataFrame(
                data=self._data.copy(),
                columns=self._columns
            )
        else:
            new_data = {'index': self._index.copy()}
            new_data.update(self._data)
            return CreatesonlineDataFrame(data=new_data)
    
    def set_index(self, column: str) -> 'CreatesonlineDataFrame':
        """Set a column as the index"""
        if column not in self._columns:
            raise KeyError(f"Column '{column}' not found")
        
        new_index = [str(val) for val in self._data[column]]
        new_data = {col: values for col, values in self._data.items() if col != column}
        new_columns = [col for col in self._columns if col != column]
        
        result = CreatesonlineDataFrame(data=new_data, index=new_index)
        result._columns = new_columns
        return result
    
    def drop(
        self, 
        labels: Union[str, List[str]] = None,
        columns: Union[str, List[str]] = None,
        index: Union[str, List[str]] = None
    ) -> 'CreatesonlineDataFrame':
        """Drop columns or rows"""
        result = self.copy()
        
        # Drop columns
        if columns is not None or labels is not None:
            cols_to_drop = columns or labels
            if isinstance(cols_to_drop, str):
                cols_to_drop = [cols_to_drop]
            
            for col in cols_to_drop:
                if col in result._columns:
                    del result[col]
        
        # Drop rows by index
        if index is not None:
            if isinstance(index, str):
                index = [index]
            
            indices_to_keep = []
            for i, idx in enumerate(result._index):
                if idx not in index:
                    indices_to_keep.append(i)
            
            new_data = {}
            for col in result._columns:
                new_data[col] = [result._data[col][i] for i in indices_to_keep]
            
            new_index = [result._index[i] for i in indices_to_keep]
            
            return CreatesonlineDataFrame(
                data=new_data,
                index=new_index
            )
        
        return result
    
    def dropna(self, axis: int = 0, how: str = 'any') -> 'CreatesonlineDataFrame':
        """Drop rows or columns with null values"""
        if axis == 0:  # Drop rows
            rows_to_keep = []
            for i in range(len(self._index)):
                row_values = [self._data[col][i] for col in self._columns]
                
                if how == 'any':
                    if not any(val is None for val in row_values):
                        rows_to_keep.append(i)
                elif how == 'all':
                    if not all(val is None for val in row_values):
                        rows_to_keep.append(i)
            
            new_data = {}
            for col in self._columns:
                new_data[col] = [self._data[col][i] for i in rows_to_keep]
            
            new_index = [self._index[i] for i in rows_to_keep]
            
            return CreatesonlineDataFrame(
                data=new_data,
                index=new_index
            )
        else:  # Drop columns
            cols_to_keep = []
            for col in self._columns:
                col_values = self._data[col]
                
                if how == 'any':
                    if not any(val is None for val in col_values):
                        cols_to_keep.append(col)
                elif how == 'all':
                    if not all(val is None for val in col_values):
                        cols_to_keep.append(col)
            
            return self[cols_to_keep]
    
    def fillna(self, value: Any) -> 'CreatesonlineDataFrame':
        """Fill null values with specified value"""
        new_data = {}
        for col in self._columns:
            new_data[col] = [val if val is not None else value for val in self._data[col]]
        
        return CreatesonlineDataFrame(
            data=new_data,
            index=self._index
        )
    
    def apply(
        self, 
        func: Callable,
        axis: int = 0
    ) -> Union['CreatesonlineDataFrame', CreatesonlineSeries]:
        """Apply function along axis"""
        if axis == 0:  # Apply to each column
            results = {}
            for col in self._columns:
                series = self[col]
                results[col] = func(series)
            
            # If results are scalar, return Series
            if all(not hasattr(val, '__iter__') or isinstance(val, str) for val in results.values()):
                return CreatesonlineSeries(
                    data=list(results.values()),
                    index=self._columns,
                    name='applied'
                )
            else:
                return CreatesonlineDataFrame(data=results, index=self._index)
        else:  # Apply to each row
            results = []
            for i in range(len(self._index)):
                row = CreatesonlineSeries(
                    data=[self._data[col][i] for col in self._columns],
                    index=self._columns,
                    name=self._index[i]
                )
                results.append(func(row))
            
            return CreatesonlineSeries(
                data=results,
                index=self._index,
                name='applied'
            )
    
    def groupby(self, by: Union[str, List[str]]) -> 'DataFrameGroupBy':
        """Group DataFrame by column(s)"""
        return DataFrameGroupBy(self, by)
    
    def merge(
        self,
        other: 'CreatesonlineDataFrame',
        on: Optional[Union[str, List[str]]] = None,
        left_on: Optional[Union[str, List[str]]] = None,
        right_on: Optional[Union[str, List[str]]] = None,
        how: str = 'inner'
    ) -> 'CreatesonlineDataFrame':
        """
        Merge DataFrames with comprehensive join support
        
        Args:
            other: DataFrame to merge with
            on: Column(s) to join on (must be present in both DataFrames)
            left_on: Column(s) to join on for left DataFrame
            right_on: Column(s) to join on for right DataFrame  
            how: Type of merge ('inner', 'left', 'right', 'outer')
        
        Returns:
            Merged DataFrame
        """
        # Validate join type
        valid_joins = {'inner', 'left', 'right', 'outer'}
        if how not in valid_joins:
            raise ValueError(f"Invalid join type '{how}'. Must be one of: {valid_joins}")
        
        # Determine join keys
        if on is not None:
            if left_on is not None or right_on is not None:
                raise ValueError("Cannot specify 'on' with 'left_on' or 'right_on'")
            left_on = right_on = on
        elif left_on is None or right_on is None:
            raise ValueError("Must specify either 'on' or both 'left_on' and 'right_on'")
        
        # Ensure keys are lists
        if isinstance(left_on, str):
            left_on = [left_on]
        if isinstance(right_on, str):
            right_on = [right_on]
        
        # Validate that join keys exist
        for col in left_on:
            if col not in self._columns:
                raise KeyError(f"Left join key '{col}' not found in DataFrame")
        for col in right_on:
            if col not in other._columns:
                raise KeyError(f"Right join key '{col}' not found in DataFrame")
        
        # Build lookup dictionaries
        left_lookup = {}
        for i in range(len(self._index)):
            key = tuple(self._data[col][i] for col in left_on)
            if key not in left_lookup:
                left_lookup[key] = []
            left_lookup[key].append(i)
        
        right_lookup = {}
        for i in range(len(other._index)):
            key = tuple(other._data[col][i] for col in right_on)
            if key not in right_lookup:
                right_lookup[key] = []
            right_lookup[key].append(i)
        
        # Perform merge based on join type
        merged_rows = []
        
        if how == 'inner':
            # Inner join: only matching keys
            for key in left_lookup:
                if key in right_lookup:
                    for left_i in left_lookup[key]:
                        for right_i in right_lookup[key]:
                            merged_rows.append(self._create_merged_row(left_i, right_i, other))
        
        elif how == 'left':
            # Left join: all left keys, matching right keys
            for key in left_lookup:
                if key in right_lookup:
                    for left_i in left_lookup[key]:
                        for right_i in right_lookup[key]:
                            merged_rows.append(self._create_merged_row(left_i, right_i, other))
                else:
                    for left_i in left_lookup[key]:
                        merged_rows.append(self._create_merged_row(left_i, None, other))
        
        elif how == 'right':
            # Right join: all right keys, matching left keys  
            for key in right_lookup:
                if key in left_lookup:
                    for right_i in right_lookup[key]:
                        for left_i in left_lookup[key]:
                            merged_rows.append(self._create_merged_row(left_i, right_i, other))
                else:
                    for right_i in right_lookup[key]:
                        merged_rows.append(self._create_merged_row(None, right_i, other))
        
        elif how == 'outer':
            # Outer join: all keys from both sides
            all_keys = set(left_lookup.keys()) | set(right_lookup.keys())
            
            for key in all_keys:
                left_indices = left_lookup.get(key, [])
                right_indices = right_lookup.get(key, [])
                
                if left_indices and right_indices:
                    for left_i in left_indices:
                        for right_i in right_indices:
                            merged_rows.append(self._create_merged_row(left_i, right_i, other))
                elif left_indices:
                    for left_i in left_indices:
                        merged_rows.append(self._create_merged_row(left_i, None, other))
                else:
                    for right_i in right_indices:
                        merged_rows.append(self._create_merged_row(None, right_i, other))
        
        return CreatesonlineDataFrame(data=merged_rows)
    
    def _create_merged_row(self, left_i: Optional[int], right_i: Optional[int], other: 'CreatesonlineDataFrame') -> Dict[str, Any]:
        """Helper method to create a merged row"""
        row = {}
        
        # Add left columns
        if left_i is not None:
            for col in self._columns:
                row[col] = self._data[col][left_i]
        else:
            for col in self._columns:
                row[col] = None
        
        # Add right columns (handle name conflicts)
        if right_i is not None:
            for col in other._columns:
                if col not in row:
                    row[col] = other._data[col][right_i]
                else:
                    row[f"{col}_y"] = other._data[col][right_i]
                    if f"{col}_x" not in row:
                        row[f"{col}_x"] = row[col]
                        del row[col]
        else:
            for col in other._columns:
                if col not in row:
                    row[col] = None
                else:
                    row[f"{col}_y"] = None
                    if f"{col}_x" not in row:
                        row[f"{col}_x"] = row[col]
                        del row[col]
        
        return row
    
    def concat(self, other: 'CreatesonlineDataFrame', axis: int = 0) -> 'CreatesonlineDataFrame':
        """Concatenate DataFrames"""
        if axis == 0:  # Concatenate rows
            # Get all columns
            all_columns = list(set(self._columns + other._columns))
            
            new_data = {col: [] for col in all_columns}
            
            # Add data from self
            for i in range(len(self._index)):
                for col in all_columns:
                    if col in self._columns:
                        new_data[col].append(self._data[col][i])
                    else:
                        new_data[col].append(None)
            
            # Add data from other
            for i in range(len(other._index)):
                for col in all_columns:
                    if col in other._columns:
                        new_data[col].append(other._data[col][i])
                    else:
                        new_data[col].append(None)
            
            new_index = self._index + other._index
            
            return CreatesonlineDataFrame(
                data=new_data,
                index=new_index
            )
        else:  # Concatenate columns
            if len(self._index) != len(other._index):
                raise ValueError("DataFrames must have same number of rows for column concatenation")
            
            new_data = self._data.copy()
            
            for col in other._columns:
                if col in new_data:
                    # Handle duplicate column names
                    new_col = f"{col}_1"
                    counter = 1
                    while new_col in new_data:
                        counter += 1
                        new_col = f"{col}_{counter}"
                    new_data[new_col] = other._data[col]
                else:
                    new_data[col] = other._data[col]
            
            return CreatesonlineDataFrame(
                data=new_data,
                index=self._index
            )
    
    def to_dict(self, orient: str = 'dict') -> Union[Dict[str, List[Any]], List[Dict[str, Any]]]:
        """Convert DataFrame to dictionary"""
        if orient == 'dict':
            return self._data.copy()
        elif orient == 'records':
            return [
                {col: self._data[col][i] for col in self._columns}
                for i in range(len(self._index))
            ]
        elif orient == 'list':
            return {col: list(values) for col, values in self._data.items()}
        else:
            raise ValueError(f"Invalid orient: {orient}")
    
    def to_json(self, orient: str = 'records', indent: Optional[int] = None) -> str:
        """Convert DataFrame to JSON string"""
        data = self.to_dict(orient=orient)
        return json.dumps(data, indent=indent, default=str)
    
    def to_numpy(self) -> Any:
        """Convert DataFrame to numpy array"""
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for to_numpy(). Install with: pip install numpy")
        return np.array(self.values)


class DataFrameGroupBy:
    """GroupBy functionality for CreatesonlineDataFrame"""
    
    def __init__(self, df: CreatesonlineDataFrame, by: Union[str, List[str]]):
        self.df = df
        self.by = by if isinstance(by, list) else [by]
        self._groups = self._create_groups()
    
    def _create_groups(self) -> Dict[tuple, List[int]]:
        """Create groups dictionary"""
        groups = {}
        
        for i in range(len(self.df._index)):
            key = tuple(self.df._data[col][i] for col in self.by)
            if key not in groups:
                groups[key] = []
            groups[key].append(i)
        
        return groups
    
    def get_group(self, key: tuple) -> CreatesonlineDataFrame:
        """Get specific group"""
        if key not in self._groups:
            raise KeyError(f"Group {key} not found")
        
        indices = self._groups[key]
        new_data = {}
        for col in self.df._columns:
            new_data[col] = [self.df._data[col][i] for i in indices]
        
        new_index = [self.df._index[i] for i in indices]
        
        return CreatesonlineDataFrame(
            data=new_data,
            index=new_index
        )
    
    def agg(self, func: Union[str, Callable, Dict[str, Union[str, Callable]]]) -> CreatesonlineDataFrame:
        """Aggregate groups"""
        if isinstance(func, str):
            # Single function name with proper null/NaN handling
            results = {}
            for col in self.df._columns:
                if col not in self.by:
                    results[col] = []
            
            group_keys = []
            
            for key, indices in self._groups.items():
                group_keys.append(key)
                for col in self.df._columns:
                    if col not in self.by:
                        col_values = [self.df._data[col][i] for i in indices]
                        
                        if func == 'count':
                            # Count excludes None/NaN values
                            results[col].append(len([v for v in col_values if v is not None]))
                        elif func == 'mean':
                            # Mean calculation excludes None/NaN
                            numeric_values = [v for v in col_values if isinstance(v, (int, float)) and v is not None]
                            if numeric_values:
                                results[col].append(sum(numeric_values) / len(numeric_values))
                            else:
                                results[col].append(None)
                        elif func in ['sum', 'min', 'max']:
                            # These operations exclude None/NaN
                            numeric_values = [v for v in col_values if isinstance(v, (int, float)) and v is not None]
                            if numeric_values:
                                if func == 'sum':
                                    results[col].append(sum(numeric_values))
                                elif func == 'min':
                                    results[col].append(min(numeric_values))
                                elif func == 'max':
                                    results[col].append(max(numeric_values))
                            else:
                                results[col].append(None)
                        else:
                            raise ValueError(f"Unknown aggregation function: {func}")
            
            # Create index from group keys
            if len(self.by) == 1:
                index = [str(key[0]) for key in group_keys]
            else:
                index = [str(key) for key in group_keys]
            
            return CreatesonlineDataFrame(
                data=results,
                index=index
            )
        
        elif callable(func):
            # Single function
            results = {}
            for col in self.df._columns:
                if col not in self.by:
                    results[col] = []
            
            group_keys = []
            
            for key, indices in self._groups.items():
                group_keys.append(key)
                for col in self.df._columns:
                    if col not in self.by:
                        col_values = [self.df._data[col][i] for i in indices]
                        results[col].append(func(col_values))
            
            if len(self.by) == 1:
                index = [str(key[0]) for key in group_keys]
            else:
                index = [str(key) for key in group_keys]
            
            return CreatesonlineDataFrame(
                data=results,
                index=index
            )
        
        elif isinstance(func, dict):
            # Different functions for different columns
            results = {}
            group_keys = []
            
            for key, indices in self._groups.items():
                group_keys.append(key)
                
                for col, col_func in func.items():
                    if col not in self.df._columns:
                        continue
                    
                    if col not in results:
                        results[col] = []
                    
                    col_values = [self.df._data[col][i] for i in indices]
                    
                    if isinstance(col_func, str):
                        func_map = {'sum': sum, 'mean': lambda x: sum(x) / len(x), 'count': len, 'min': min, 'max': max}
                        if col_func in func_map:
                            numeric_values = [v for v in col_values if isinstance(v, (int, float))]
                            if numeric_values:
                                results[col].append(func_map[col_func](numeric_values))
                            else:
                                results[col].append(None)
                        else:
                            results[col].append(None)
                    elif callable(col_func):
                        results[col].append(col_func(col_values))
                    else:
                        results[col].append(None)
            
            if len(self.by) == 1:
                index = [str(key[0]) for key in group_keys]
            else:
                index = [str(key) for key in group_keys]
            
            return CreatesonlineDataFrame(
                data=results,
                index=index
            )
        
        else:
            raise TypeError("func must be string, callable, or dict")
    
    def sum(self) -> CreatesonlineDataFrame:
        """Sum of groups"""
        return self.agg('sum')
    
    def mean(self) -> CreatesonlineDataFrame:
        """Mean of groups"""
        return self.agg('mean')
    
    def count(self) -> CreatesonlineDataFrame:
        """Count of groups"""
        return self.agg('count')
    
    def min(self) -> CreatesonlineDataFrame:
        """Minimum of groups"""
        return self.agg('min')
    
    def max(self) -> CreatesonlineDataFrame:
        """Maximum of groups"""
        return self.agg('max')