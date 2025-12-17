"""
CREATESONLINE Series Implementation

Pure Python series data structure.
Lightweight alternative to Pandas Series.
"""

import json
from typing import Any, Dict, List, Optional, Union, Iterator, Callable

# Optional numpy import with fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
    NDArrayType = np.ndarray
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    NDArrayType = Any  # Fallback type


class CreatesonlineSeries:
    """
    CREATESONLINE Series - One-dimensional data structure
    
    Pure Python implementation of a series data structure similar to Pandas Series
    but with zero external dependencies (except numpy for numerical operations).
    """
    
    def __init__(
        self,
        data: Union[List[Any], Dict[str, Any]] = None,
        index: Optional[List[str]] = None,
        name: Optional[str] = None,
        dtype: Optional[str] = None
    ):
        """
        Initialize CREATESONLINE Series
        
        Args:
            data: Series data as list, array, or dict
            index: Index labels for the data
            name: Name of the series
            dtype: Data type hint
        """
        self.name = name
        self.dtype = dtype
        
        if data is None:
            self._data = []
            self._index = []
        elif isinstance(data, dict):
            self._index = list(data.keys())
            self._data = list(data.values())
        elif isinstance(data, (list, tuple)):
            self._data = list(data)
            self._index = index or list(range(len(self._data)))
        elif NUMPY_AVAILABLE and hasattr(data, 'tolist'):  # numpy array
            self._data = data.tolist()
            self._index = index or list(range(len(self._data)))
        else:
            self._data = [data]
            self._index = index or [0]
        
        # Ensure index and data have same length
        if len(self._index) != len(self._data):
            if index is None:
                self._index = list(range(len(self._data)))
            else:
                raise ValueError("Index length must match data length")
    
    def __len__(self) -> int:
        """Return length of series"""
        return len(self._data)
    
    def __getitem__(self, key: Union[str, int, slice, List[Union[str, int]]]) -> Union[Any, 'CreatesonlineSeries']:
        """Get item(s) from series"""
        if isinstance(key, (int, slice)):
            if isinstance(key, slice):
                return CreatesonlineSeries(
                    data=self._data[key],
                    index=self._index[key],
                    name=self.name
                )
            else:
                return self._data[key]
        elif isinstance(key, str):
            if key in self._index:
                idx = self._index.index(key)
                return self._data[idx]
            else:
                raise KeyError(f"Key '{key}' not found in series")
        elif isinstance(key, list):
            result_data = []
            result_index = []
            for k in key:
                if isinstance(k, str) and k in self._index:
                    idx = self._index.index(k)
                    result_data.append(self._data[idx])
                    result_index.append(k)
                elif isinstance(k, int) and 0 <= k < len(self._data):
                    result_data.append(self._data[k])
                    result_index.append(self._index[k])
                else:
                    raise KeyError(f"Key '{k}' not found in series")
            return CreatesonlineSeries(
                data=result_data,
                index=result_index,
                name=self.name
            )
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
    
    def __setitem__(self, key: Union[str, int], value: Any):
        """Set item in series"""
        if isinstance(key, int):
            if 0 <= key < len(self._data):
                self._data[key] = value
            else:
                raise IndexError("Index out of range")
        elif isinstance(key, str):
            if key in self._index:
                idx = self._index.index(key)
                self._data[idx] = value
            else:
                # Add new item
                self._index.append(key)
                self._data.append(value)
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
    
    def __iter__(self) -> Iterator[Any]:
        """Iterate over series values"""
        return iter(self._data)
    
    def __str__(self) -> str:
        """String representation"""
        lines = []
        for i, (idx, val) in enumerate(zip(self._index, self._data)):
            lines.append(f"{idx}    {val}")
            if i >= 20:  # Limit display
                lines.append("...")
                break
        
        if self.name:
            lines.append(f"Name: {self.name}")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """String representation"""
        return self.__str__()
    
    @property
    def values(self) -> List[Any]:
        """Get series values as list"""
        return self._data.copy()
    
    @property
    def index(self) -> List[str]:
        """Get series index"""
        return self._index.copy()
    
    @property
    def shape(self) -> tuple:
        """Get series shape"""
        return (len(self._data),)
    
    @property
    def size(self) -> int:
        """Get series size"""
        return len(self._data)
    
    def head(self, n: int = 5) -> 'CreatesonlineSeries':
        """Get first n elements"""
        return self[:n]
    
    def tail(self, n: int = 5) -> 'CreatesonlineSeries':
        """Get last n elements"""
        return self[-n:]
    
    def copy(self) -> 'CreatesonlineSeries':
        """Create a copy of the series"""
        return CreatesonlineSeries(
            data=self._data.copy(),
            index=self._index.copy(),
            name=self.name,
            dtype=self.dtype
        )
    
    def reset_index(self, drop: bool = True) -> 'CreatesonlineSeries':
        """Reset index to default integer index"""
        if drop:
            return CreatesonlineSeries(
                data=self._data.copy(),
                name=self.name,
                dtype=self.dtype
            )
        else:
            # Return DataFrame with old index as column
            from .dataframe import CreatesonlineDataFrame
            return CreatesonlineDataFrame({
                'index': self._index.copy(),
                self.name or 'value': self._data.copy()
            })
    
    def sort_values(self, ascending: bool = True) -> 'CreatesonlineSeries':
        """Sort series by values"""
        paired = list(zip(self._data, self._index))
        paired.sort(key=lambda x: x[0], reverse=not ascending)
        
        sorted_data, sorted_index = zip(*paired)
        return CreatesonlineSeries(
            data=list(sorted_data),
            index=list(sorted_index),
            name=self.name,
            dtype=self.dtype
        )
    
    def sort_index(self, ascending: bool = True) -> 'CreatesonlineSeries':
        """Sort series by index"""
        paired = list(zip(self._index, self._data))
        paired.sort(key=lambda x: x[0], reverse=not ascending)
        
        sorted_index, sorted_data = zip(*paired)
        return CreatesonlineSeries(
            data=list(sorted_data),
            index=list(sorted_index),
            name=self.name,
            dtype=self.dtype
        )
    
    def unique(self) -> 'CreatesonlineSeries':
        """Get unique values"""
        seen = set()
        unique_data = []
        unique_index = []
        
        for val, idx in zip(self._data, self._index):
            if val not in seen:
                seen.add(val)
                unique_data.append(val)
                unique_index.append(idx)
        
        return CreatesonlineSeries(
            data=unique_data,
            index=unique_index,
            name=self.name,
            dtype=self.dtype
        )
    
    def value_counts(self) -> 'CreatesonlineSeries':
        """Count occurrences of each value"""
        counts = {}
        for val in self._data:
            counts[val] = counts.get(val, 0) + 1
        
        return CreatesonlineSeries(
            data=list(counts.values()),
            index=list(counts.keys()),
            name='count'
        ).sort_values(ascending=False)
    
    def apply(self, func: Callable[[Any], Any]) -> 'CreatesonlineSeries':
        """Apply function to each element"""
        new_data = [func(val) for val in self._data]
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=self.name,
            dtype=self.dtype
        )
    
    def map(self, mapping: Union[Dict[Any, Any], Callable[[Any], Any]]) -> 'CreatesonlineSeries':
        """Map values using dictionary or function"""
        if callable(mapping):
            return self.apply(mapping)
        else:
            new_data = [mapping.get(val, val) for val in self._data]
            return CreatesonlineSeries(
                data=new_data,
                index=self._index.copy(),
                name=self.name,
                dtype=self.dtype
            )
    
    def filter(self, condition: Callable[[Any], bool]) -> 'CreatesonlineSeries':
        """Filter series based on condition"""
        filtered_data = []
        filtered_index = []
        
        for val, idx in zip(self._data, self._index):
            if condition(val):
                filtered_data.append(val)
                filtered_index.append(idx)
        
        return CreatesonlineSeries(
            data=filtered_data,
            index=filtered_index,
            name=self.name,
            dtype=self.dtype
        )
    
    def dropna(self) -> 'CreatesonlineSeries':
        """Drop null/None values"""
        return self.filter(lambda x: x is not None)
    
    def fillna(self, value: Any) -> 'CreatesonlineSeries':
        """Fill null/None values with specified value"""
        return self.map(lambda x: value if x is None else x)
    
    def isna(self) -> 'CreatesonlineSeries':
        """Check for null/None values"""
        return CreatesonlineSeries(
            data=[val is None for val in self._data],
            index=self._index.copy(),
            name=f'{self.name}_isna' if self.name else 'isna'
        )
    
    def sum(self) -> Union[float, int]:
        """Sum of numeric values"""
        numeric_values = [val for val in self._data if isinstance(val, (int, float))]
        return sum(numeric_values) if numeric_values else 0
    
    def mean(self) -> float:
        """Mean of numeric values"""
        numeric_values = [val for val in self._data if isinstance(val, (int, float))]
        return sum(numeric_values) / len(numeric_values) if numeric_values else 0.0
    
    def median(self) -> float:
        """Median of numeric values"""
        numeric_values = sorted([val for val in self._data if isinstance(val, (int, float))])
        n = len(numeric_values)
        if n == 0:
            return 0.0
        elif n % 2 == 0:
            return (numeric_values[n//2 - 1] + numeric_values[n//2]) / 2
        else:
            return numeric_values[n//2]
    
    def std(self) -> float:
        """Standard deviation of numeric values"""
        numeric_values = [val for val in self._data if isinstance(val, (int, float))]
        if len(numeric_values) < 2:
            return 0.0
        
        mean_val = self.mean()
        variance = sum((val - mean_val) ** 2 for val in numeric_values) / (len(numeric_values) - 1)
        return variance ** 0.5
    
    def min(self) -> Any:
        """Minimum value"""
        return min(self._data) if self._data else None
    
    def max(self) -> Any:
        """Maximum value"""
        return max(self._data) if self._data else None
    
    def describe(self) -> Dict[str, Any]:
        """Descriptive statistics"""
        numeric_values = [val for val in self._data if isinstance(val, (int, float))]
        
        if not numeric_values:
            return {
                'count': len(self._data),
                'unique': len(set(self._data)),
                'top': max(set(self._data), key=self._data.count) if self._data else None,
                'freq': max([self._data.count(val) for val in set(self._data)]) if self._data else 0
            }
        
        return {
            'count': len(numeric_values),
            'mean': self.mean(),
            'std': self.std(),
            'min': min(numeric_values),
            '25%': self._quantile(numeric_values, 0.25),
            '50%': self.median(),
            '75%': self._quantile(numeric_values, 0.75),
            'max': max(numeric_values)
        }
    
    def _quantile(self, values: List[Union[int, float]], q: float) -> float:
        """Calculate quantile"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        index = q * (n - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert series to dictionary"""
        return dict(zip(self._index, self._data))
    
    def to_list(self) -> List[Any]:
        """Convert series to list"""
        return self._data.copy()
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert series to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_numpy(self) -> NDArrayType:
        """Convert series to numpy array"""
        return np.array(self._data)
    
    # Mathematical operations
    def __add__(self, other: Union['CreatesonlineSeries', int, float]) -> 'CreatesonlineSeries':
        """Addition"""
        if isinstance(other, CreatesonlineSeries):
            if len(self) != len(other):
                raise ValueError("Series lengths must match")
            new_data = [a + b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val + other if isinstance(val, (int, float)) else val for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=self.name
        )
    
    def __sub__(self, other: Union['CreatesonlineSeries', int, float]) -> 'CreatesonlineSeries':
        """Subtraction"""
        if isinstance(other, CreatesonlineSeries):
            if len(self) != len(other):
                raise ValueError("Series lengths must match")
            new_data = [a - b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val - other if isinstance(val, (int, float)) else val for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=self.name
        )
    
    def __mul__(self, other: Union['CreatesonlineSeries', int, float]) -> 'CreatesonlineSeries':
        """Multiplication"""
        if isinstance(other, CreatesonlineSeries):
            if len(self) != len(other):
                raise ValueError("Series lengths must match")
            new_data = [a * b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val * other if isinstance(val, (int, float)) else val for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=self.name
        )
    
    def __truediv__(self, other: Union['CreatesonlineSeries', int, float]) -> 'CreatesonlineSeries':
        """Division"""
        if isinstance(other, CreatesonlineSeries):
            if len(self) != len(other):
                raise ValueError("Series lengths must match")
            new_data = [a / b if b != 0 else float('inf') for a, b in zip(self._data, other._data)]
        else:
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            new_data = [val / other if isinstance(val, (int, float)) else val for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=self.name
        )
    
    # Comparison operations
    def __eq__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Equality comparison"""
        if isinstance(other, CreatesonlineSeries):
            new_data = [a == b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val == other for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_eq' if self.name else 'eq'
        )
    
    def __ne__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Not equal comparison"""
        return ~(self == other)
    
    def __lt__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Less than comparison"""
        if isinstance(other, CreatesonlineSeries):
            new_data = [a < b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val < other if isinstance(val, (int, float)) else False for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_lt' if self.name else 'lt'
        )
    
    def __le__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Less than or equal comparison"""
        return (self < other) | (self == other)
    
    def __gt__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Greater than comparison"""
        if isinstance(other, CreatesonlineSeries):
            new_data = [a > b for a, b in zip(self._data, other._data)]
        else:
            new_data = [val > other if isinstance(val, (int, float)) else False for val in self._data]
        
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_gt' if self.name else 'gt'
        )
    
    def __ge__(self, other: Union['CreatesonlineSeries', Any]) -> 'CreatesonlineSeries':
        """Greater than or equal comparison"""
        return (self > other) | (self == other)
    
    def __invert__(self) -> 'CreatesonlineSeries':
        """Logical NOT for boolean series"""
        new_data = [not val for val in self._data]
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_not' if self.name else 'not'
        )
    
    def __or__(self, other: 'CreatesonlineSeries') -> 'CreatesonlineSeries':
        """Logical OR for boolean series"""
        if len(self) != len(other):
            raise ValueError("Series lengths must match")
        
        new_data = [a or b for a, b in zip(self._data, other._data)]
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_or' if self.name else 'or'
        )
    
    def __and__(self, other: 'CreatesonlineSeries') -> 'CreatesonlineSeries':
        """Logical AND for boolean series"""
        if len(self) != len(other):
            raise ValueError("Series lengths must match")
        
        new_data = [a and b for a, b in zip(self._data, other._data)]
        return CreatesonlineSeries(
            data=new_data,
            index=self._index.copy(),
            name=f'{self.name}_and' if self.name else 'and'
        )