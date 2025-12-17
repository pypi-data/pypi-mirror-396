"""
Iterator operators for the execution pipeline.
"""

from sqlglot import expressions as exp
from .evaluator import evaluate_expression


class ScanIterator:
    """Scans rows from a source function."""
    
    def __init__(
        self,
        source_fn,
        table_name,
        alias,
        required_columns=None,
        debug=False
    ):
        """
        Args:
            source_fn: Function that returns iterator of rows
            table_name: Name of the table
            alias: Table alias
            required_columns: Set of column names to read (None = all columns)
            debug: Enable debug output
        """
        self.source_fn = source_fn
        self.table_name = table_name
        self.alias = alias or table_name
        self.required_columns = required_columns  # Set of column names (without prefix)
        self._iterator = None
        self.debug = debug
        self._row_count = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._iterator is None:
            self._iterator = iter(self.source_fn())
            if self.debug:
                if self.required_columns:
                    print(f"      Started reading from {self.table_name} (columns: {len(self.required_columns)})")
                else:
                    print(f"      Started reading from {self.table_name}")
        
        row = next(self._iterator)
        self._row_count += 1
        
        # Column pruning: only include required columns
        if self.required_columns:
            # Filter row to only include required columns
            filtered_row = {k: v for k, v in row.items() if k in self.required_columns}
            row = filtered_row
        
        # Prefix all columns with table alias (optimized: use dict comprehension)
        prefixed_row = {f"{self.alias}.{key}": value for key, value in row.items()}
        
        if self.debug and self._row_count % 10000 == 0:
            print(f"      Scanned {self._row_count:,} rows from {self.table_name}")
        
        return prefixed_row


class FilterIterator:
    """Filters rows based on WHERE expression."""
    
    def __init__(
        self,
        source,
        where_expr,
        debug=False
    ):
        self.source = source
        self.where_expr = where_expr
        self.debug = debug
        self._rows_processed = 0
        self._rows_passed = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while True:
            row = next(self.source)
            self._rows_processed += 1
            
            if evaluate_expression(self.where_expr, row):
                self._rows_passed += 1
                if self.debug and self._rows_passed % 10000 == 0:
                    print(f"      Filter: {self._rows_passed:,} passed / {self._rows_processed:,} processed")
                return row
            # Row filtered out - continue loop


class ProjectIterator:
    """Applies SELECT projection to rows."""
    
    def __init__(
        self,
        source,
        projections,
        debug=False
    ):
        self.source = source
        self.projections = projections
        self.debug = debug
        self._row_count = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        row = next(self.source)
        self._row_count += 1
        
        if self.debug and self._row_count % 10000 == 0:
            print(f"     Projected {self._row_count:,} result rows")
        
        result = {}
        
        for expr in self.projections:
            if isinstance(expr, exp.Alias):
                # SELECT col AS alias
                alias = expr.alias
                value = evaluate_expression(expr.this, row)
                result[alias] = value
            elif isinstance(expr, exp.Column):
                # SELECT alias.col
                col_name = f"{expr.table}.{expr.name}" if expr.table else expr.name
                if col_name in row:
                    # Use column name as key (or last part if no alias)
                    key = expr.name
                    result[key] = row[col_name]
                else:
                    raise KeyError(f"Column {col_name} not found in row")
            else:
                # Simple expression - use string representation as key
                value = evaluate_expression(expr, row)
                key = str(expr)
                result[key] = value
        
        return result


class LookupJoinIterator:
    """
    Performs join by building a lookup index on the right side.
    """
    
    def __init__(
        self,
        left_source,
        right_source_fn,
        left_key,
        right_key,
        join_type,
        right_table,
        right_alias,
        required_columns=None,
        debug=False,
        first_match_only=False
    ):
        self.left_source = left_source
        self.right_source_fn = right_source_fn
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type
        self.right_table = right_table
        self.right_alias = right_alias or right_table
        self.required_columns = required_columns  # Set of column names (for column pruning)
        self.debug = debug
        self.first_match_only = first_match_only  # If True, only return first match per left key
        
        # Build lookup index
        self.lookup_index = {}
        if self.debug:
            if required_columns:
                print(f"      Building lookup index for {right_table} (columns: {len(required_columns)})...")
            else:
                print(f"      Building lookup index for {right_table}...")
            if first_match_only:
                print(f"      ⚡ First-match-only mode: Will deduplicate right side and return only first match per left key")
        self._build_index(deduplicate=first_match_only)
        
        self._left_row = None
        self._right_matches = []
        self._match_index = 0
        self._join_count = 0
    
    def _build_index(self, deduplicate=False):
        """Build lookup index from right side table.
        
        Args:
            deduplicate: If True, only keep first match per key (prevents cartesian products)
        """
        right_table_col = _extract_column_from_key(self.right_key)
        index_size = 0
        duplicate_count = 0
        
        for row in self.right_source_fn():
            # Skip None or invalid rows
            if not row or not isinstance(row, dict):
                continue
            
            # Column pruning: only include required columns
            if self.required_columns:
                row = {k: v for k, v in row.items() if k in self.required_columns}
                
            # Prefix columns with right alias (optimized: use dict comprehension)
            prefixed_row = {f"{self.right_alias}.{key}": value for key, value in row.items()}
            
            # Index by join key value
            key_value = row.get(right_table_col)
            # Skip rows with None join keys (can't join on None)
            if key_value is None:
                continue
            
            if key_value not in self.lookup_index:
                self.lookup_index[key_value] = []
                self.lookup_index[key_value].append(prefixed_row)
                index_size += 1
            else:
                # Key already exists
                if deduplicate:
                    # Skip duplicates - only keep first match
                    duplicate_count += 1
                else:
                    # Keep all matches (normal SQL behavior)
                    self.lookup_index[key_value].append(prefixed_row)
                    index_size += 1
        
        if self.debug:
            print(f"      Index built: {index_size:,} rows, {len(self.lookup_index):,} unique keys")
            if deduplicate and duplicate_count > 0:
                print(f"      ⚠️  Deduplicated: {duplicate_count:,} duplicate keys removed (kept first match only)")
    
    def __iter__(self):
        return self
    
    def __next__(self):
        while True:
            # Get next left row if needed
            if self._left_row is None:
                try:
                    self._left_row = next(self.left_source)
                except StopIteration:
                    raise StopIteration
            
            # Get join key value from left row
            try:
                left_key_value = self._get_key_value(self._left_row, self.left_key)
            except KeyError:
                # Join key not found in left row, skip this row
                self._left_row = None
                continue
            
            # Skip rows with None join keys (can't join on None)
            if left_key_value is None:
                if self.join_type == "INNER":
                    # INNER JOIN: skip rows with None keys
                    self._left_row = None
                    continue
                else:
                    # LEFT JOIN: yield left row with no match
                    result = self._left_row.copy()
                    self._left_row = None
                    self._join_count += 1
                    return result
            
            # Get matching right rows
            if self._match_index == 0:
                matches = self.lookup_index.get(left_key_value, [])
                # Filter out None or invalid rows
                self._right_matches = [m for m in matches if m is not None and isinstance(m, dict)]
                
                # If first_match_only mode, only take first match
                if self.first_match_only and len(self._right_matches) > 1:
                    self._right_matches = self._right_matches[:1]
            
            # Handle INNER JOIN
            if self.join_type == "INNER":
                if not self._right_matches:
                    # No match, skip this left row
                    self._left_row = None
                    continue
                
                # Yield current match
                if self._match_index < len(self._right_matches):
                    right_row = self._right_matches[self._match_index]
                    
                    # Safety check: skip None or invalid rows
                    if right_row is None or not isinstance(right_row, dict):
                        self._match_index += 1
                        continue
                    
                    # Safety check: ensure left_row is still valid
                    if self._left_row is None or not isinstance(self._left_row, dict):
                        # Left row became invalid, skip to next
                        self._left_row = None
                        self._match_index = 0
                        continue
                    
                    # Store left_row before potentially resetting it
                    left_row_copy = self._left_row.copy()
                    self._match_index += 1
                    
                    # If we've exhausted matches, reset for next left row
                    if self._match_index >= len(self._right_matches):
                        self._left_row = None
                        self._match_index = 0
                    
                    self._join_count += 1
                    if self.debug and self._join_count % 10000 == 0:
                        print(f"      Merge join: {self._join_count:,} rows matched")
                    return {**left_row_copy, **right_row}
            
            # Handle LEFT JOIN
            else:  # LEFT JOIN
                if not self._right_matches:
                    # No match, yield left row with NULLs
                    result = self._left_row.copy()
                    self._left_row = None
                    self._join_count += 1
                    if self.debug and self._join_count % 10000 == 0:
                        print(f"      Join {self._join_count:,} rows (LEFT JOIN with NULLs)")
                    return result
                
                # Yield current match
                if self._match_index < len(self._right_matches):
                    right_row = self._right_matches[self._match_index]
                    
                    # Safety check: skip None or invalid rows
                    if right_row is None or not isinstance(right_row, dict):
                        self._match_index += 1
                        continue
                    
                    # Safety check: ensure left_row is still valid
                    if self._left_row is None or not isinstance(self._left_row, dict):
                        # Left row became invalid, skip to next
                        self._left_row = None
                        self._match_index = 0
                        continue
                    
                    # Store left_row before potentially resetting it
                    left_row_copy = self._left_row.copy()
                    self._match_index += 1
                    
                    # If we've exhausted matches, reset for next left row
                    if self._match_index >= len(self._right_matches):
                        self._left_row = None
                        self._match_index = 0
                    
                    self._join_count += 1
                    if self.debug and self._join_count % 10000 == 0:
                        print(f"      Merge join: {self._join_count:,} rows matched")
                    return {**left_row_copy, **right_row}
    
    def _get_key_value(self, row, key):
        """Extract join key value from a row."""
        if key in row:
            return row[key]
        raise KeyError(f"Join key {key} not found in row")
    
    
class MergeJoinIterator:
    """
    Performs join using merge algorithm when both sides are sorted.
    Note: This is a simplified implementation that works best when keys are unique.
    For duplicate keys, it may not produce all combinations efficiently.
    """
    
    def __init__(
        self,
        left_source,
        right_source_fn,
        left_key,
        right_key,
        join_type,
        right_table,
        right_alias,
        debug=False
    ):
        self.left_source = left_source
        self.right_source_fn = right_source_fn
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type
        self.right_table = right_table
        self.right_alias = right_alias or right_table
        self.debug = debug
        
        # Initialize right iterator
        self.right_iterator = iter(self.right_source_fn())
        self._right_row = None
        self._join_count = 0
        self._left_row = None
        
        # Buffer for right rows with same key (handles duplicates)
        self._right_buffer = []
        self._right_buffer_index = 0
        self._current_right_key = None
    
    def __iter__(self):
        return self
    
    def _advance_right(self) -> bool:
        """Advance right iterator and return True if successful."""
        try:
            raw_right = next(self.right_iterator)
            # Prefix columns
            self._right_row = {}
            for key, value in raw_right.items():
                prefixed_key = f"{self.right_alias}.{key}"
                self._right_row[prefixed_key] = value
            return True
        except StopIteration:
            self._right_row = None
            return False
    
    def _fill_right_buffer(self, target_key):
        """Fill right buffer with all rows matching target_key."""
        self._right_buffer = []
        self._right_buffer_index = 0
        
        if self._right_row is None:
            if not self._advance_right():
                return
        
        right_key_value = self._get_key_value(self._right_row, self.right_key)
        
        # Collect all right rows with matching key
        while right_key_value == target_key:
            self._right_buffer.append(self._right_row)
            if not self._advance_right():
                break
            right_key_value = self._get_key_value(self._right_row, self.right_key)
    
    def __next__(self):
        while True:
            # Get next left row if needed
            if self._left_row is None:
                try:
                    self._left_row = next(self.left_source)
                except StopIteration:
                    # For LEFT JOIN, check if we have any remaining unmatched rows
                    # (simplified - full implementation would track these)
                    raise StopIteration
            
            left_key_value = self._get_key_value(self._left_row, self.left_key)
            
            # Advance right until we're at or past left key
            while True:
                if self._right_row is None:
                    if not self._advance_right():
                        # Right exhausted
                        if self.join_type == "LEFT":
                            # Yield left with NULLs
                            result = self._left_row.copy()
                            self._left_row = None
                            return result
                        # For INNER, skip remaining left rows
                        raise StopIteration
                
                right_key_value = self._get_key_value(self._right_row, self.right_key)
                
                if right_key_value < left_key_value:
                    # Right is behind, advance
                    if not self._advance_right():
                        # Right exhausted
                        if self.join_type == "LEFT":
                            result = self._left_row.copy()
                            self._left_row = None
                            return result
                        raise StopIteration
                    continue
                elif right_key_value > left_key_value:
                    # Right has passed, no match for this left
                    if self.join_type == "LEFT":
                        result = self._left_row.copy()
                        self._left_row = None
                        return result
                    # For INNER, skip this left row
                    self._left_row = None
                    break
                else:
                    # Keys match
                    if self._current_right_key != left_key_value:
                        # New key, fill buffer
                        self._fill_right_buffer(left_key_value)
                        self._current_right_key = left_key_value
                    
                    if not self._right_buffer:
                        # No matches (shouldn't happen, but handle it)
                        if self.join_type == "LEFT":
                            result = self._left_row.copy()
                            self._left_row = None
                            return result
                        self._left_row = None
                        break
                    
                    # Yield current combination
                    right_row = self._right_buffer[self._right_buffer_index]
                    self._right_buffer_index += 1
                    
                    # Save left_row before potentially clearing it
                    result = {**self._left_row, **right_row}
                    
                    # If we've exhausted right buffer, move to next left row
                    if self._right_buffer_index >= len(self._right_buffer):
                        self._right_buffer_index = 0
                        self._left_row = None
                    
                    self._join_count += 1
                    if self.debug and self._join_count % 10000 == 0:
                        print(f"      Merge join: {self._join_count:,} rows matched")
                    return result
    
    def _get_key_value(self, row, key):
        """Extract join key value from a row."""
        if key in row:
            return row[key]
        raise KeyError(f"Join key {key} not found in row")


def _extract_column_from_key(key):
    """Extract column name from a key like 'alias.column'."""
    if "." in key:
        return key.split(".", 1)[1]
    return key

