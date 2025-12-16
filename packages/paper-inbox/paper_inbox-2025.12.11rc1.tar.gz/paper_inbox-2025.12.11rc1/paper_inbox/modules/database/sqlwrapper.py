import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple, TypeAlias, Union

from paper_inbox.modules.database.formatters import convert_entity_type_to_table_name

## type aliases
DBFilter = Tuple[str, str, Any]
DBFilterList = List[DBFilter]



class SQLiteWrapper:
    # Special fields that will be added to all entities
    TIMESTAMP_FIELDS = {
        'created_at': 'INTEGER',  # Unix timestamp (seconds since epoch)
        'updated_at': 'INTEGER'   # Unix timestamp (seconds since epoch)
    }

    def __init__(self, db_path: Path, debug: bool = False):
        """Initialize database connection"""
        self.db_path = str(db_path)
        self.debug = debug

        # Enable foreign key support
        conn = self._get_connection()
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('PRAGMA journal_mode = WAL')
        conn.execute('PRAGMA busy_timeout = 5000')  # 5 second timeout
        conn.close()

        self._ensure_metadata_table()

    def _get_connection(self):
        """Get a database connection with row factory"""
        conn = sqlite3.connect(self.db_path, timeout=20)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_metadata_table(self):
        """Create metadata table to track schemas"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS _metadata (
                entity_type TEXT PRIMARY KEY,
                schema TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _get_current_timestamp(self) -> int:
        """Get current timestamp as Unix epoch (seconds since 1970-01-01)"""
        return int(datetime.now(timezone.utc).timestamp())

    def list_tables(self):
        # Connect to the SQLite database
        conn = self._get_connection()
        cursor = conn.cursor()

        # Execute a query to get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch all the results
        tables = cursor.fetchall()

        # Print the names of the tables
        for table in tables:
            print(table[0])

        # Close the database connection
        conn.close()

    def create_entity_type(self, entity_type: str, fields: Dict[str, str]):
        """
        Create a new entity type (table) with automatic timestamp fields
        """
        table_name = convert_entity_type_to_table_name(entity_type)
        # Add timestamp fields to the schema
        full_fields = {**fields, **self.TIMESTAMP_FIELDS}

        conn = self._get_connection()
        cursor = conn.cursor()

        # Store schema in metadata
        cursor.execute('INSERT OR REPLACE INTO _metadata VALUES (?, ?)',
                       (entity_type, json.dumps(full_fields)))
        
        ## Extract any composite UNIQUE constraints
        composite_unique = fields.pop('UNIQUE', None)

        # Create table with specified fields plus timestamps
        field_defs = [f"{name} {dtype}" for name, dtype in full_fields.items()]
        # Changed to explicitly use AUTOINCREMENT to prevent ID reuse
        field_defs.append("id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL")

        ## Add any composite UNIQUE constraints
        if composite_unique:
            for unique_combo in composite_unique:
                field_defs.append(f"UNIQUE({unique_combo})")

        create_query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(field_defs)}
            )
        '''

        if self.debug:
            print(f"Creating table with query: {create_query}")

        cursor.execute(create_query)
        conn.commit()
        conn.close()

    def _build_filter_query(self, entity_type: str, filters: List[Any]) -> Tuple[str, List, str]:
        """Convert filters to SQLite WHERE clause with support for dot notation joins and OR groups"""
        if not filters:
            return "", [], ""

        table_name = convert_entity_type_to_table_name(entity_type)
        conditions = []
        values = []
        joins = set()

        for filter_item in filters:
            # Handle OR groups, e.g., {'or': [['field1', 'is', 'val1'], ['field2', 'is', 'val2']]}
            if isinstance(filter_item, dict) and 'or' in filter_item:
                or_filters = filter_item['or']
                or_conditions = []
                or_values = []
                for field, operator, value in or_filters:
                    # NOTE: This simple OR implementation does not handle joins inside the OR clause.
                    # It assumes fields are on the main entity_type table.
                    field_name = f"{table_name}.{field}"
                    if operator == 'is':
                        or_conditions.append(f"{field_name} = ?")
                        or_values.append(value)
                    else:
                        # You could expand this to support other operators within an OR clause if needed
                        # For now, we'll stick to 'is' for your use case.
                        pass
                if or_conditions:
                    conditions.append(f"({ ' OR '.join(or_conditions) })")
                    values.extend(or_values)
                continue

            # Standard AND condition processing
            field, operator, value = filter_item
            # Handle dot notation for joins
            if '.' in field:
                parts = field.split('.')
                if len(parts) == 3:  # Format: local_key.ForeignTable.foreign_field
                    local_key, foreign_entity_type, foreign_field = parts
                    foreign_table_name = convert_entity_type_to_table_name(foreign_entity_type)
                    join_clause = f"LEFT JOIN {foreign_table_name} ON {table_name}.{local_key} = {foreign_table_name}.id"
                    joins.add(join_clause)
                    field = f"{foreign_table_name}.{foreign_field}"
                else:
                    # Keep original field if format doesn't match
                    field = f"{table_name}.{field}"
            else:
                field = f"{table_name}.{field}"

            # Handle NULL values
            if value is None and operator == 'is':
                conditions.append(f"{field} IS NULL")
                continue
            elif value is None and operator == 'is_not':
                conditions.append(f"{field} IS NOT NULL")
                continue

            # Handle different operators
            if operator == 'is':
                conditions.append(f"{field} = ?")
                values.append(value)
            elif operator == 'is_not':
                conditions.append(f"{field} != ?")
                values.append(value)
            elif operator == 'contains':
                conditions.append(f"{field} LIKE ?")
                values.append(f"%{value}%")
            elif operator == 'not_contains':
                conditions.append(f"{field} NOT LIKE ?")
                values.append(f"%{value}%")
            elif operator == 'starts_with':
                conditions.append(f"{field} LIKE ?")
                values.append(f"{value}%")
            elif operator == 'ends_with':
                conditions.append(f"{field} LIKE ?")
                values.append(f"%{value}")
            elif operator == 'in':
                if isinstance(value, (list, tuple)) and value:
                    placeholders = ','.join(['?' for _ in value])
                    conditions.append(f"{field} IN ({placeholders})")
                    values.extend(value)
                else:
                    # If empty list provided, condition will always be false
                    conditions.append("1=0")
            elif operator == 'not_in':
                if isinstance(value, (list, tuple)) and value:
                    placeholders = ','.join(['?' for _ in value])
                    conditions.append(f"{field} NOT IN ({placeholders})")
                    values.extend(value)
                else:
                    # If empty list provided, condition will always be true
                    conditions.append("1=1")
            elif operator in ['greater_than', 'less_than', 'greater_than_or_equal_to', 'less_than_or_equal_to']:
                sql_ops = {
                    'greater_than': '>',
                    'less_than': '<',
                    'greater_than_or_equal_to': '>=',
                    'less_than_or_equal_to': '<='
                }
                conditions.append(f"{field} {sql_ops[operator]} ?")
                values.append(value)

        where_clause = " AND ".join(conditions)
        joins_clause = " ".join(joins)
        return where_clause, values, joins_clause

    def find(self, entity_type: str,
          filters: DBFilterList | None = None,
          fields: List[str] | None = None,
          order: List[Tuple[str, str]] | None = None,
          limit: int | None = None,
          after_id: int | None = None) -> List[Dict]:
        """Find entities using cursor-based pagination with guaranteed limit"""
        conn = self._get_connection()
        cursor = conn.cursor()
        table_name = convert_entity_type_to_table_name(entity_type)

        # Ensure limit is an integer or None
        limit = int(limit) if limit is not None else None

        # Always include id in fields
        if fields:
            if 'id' not in fields:
                fields.append('id')
            select_fields = ', '.join(f"{table_name}.{field}" for field in fields)
        else:
            select_fields = f"{table_name}.*"

        # Start building the query
        query = f"""
            WITH filtered_results AS (
                SELECT {select_fields}
                FROM {table_name}
                WHERE 1=1  -- This allows us to always add conditions with AND
        """

        values = []
        
        # Handle cursor-based pagination
        if after_id is not None:
            # Get the reference point for pagination
            ref_query = f"SELECT created_at FROM {table_name} WHERE id = ?"
            cursor.execute(ref_query, [after_id])
            ref_row = cursor.fetchone()
            
            if ref_row:
                ref_timestamp = ref_row[0]
                # Get items with:
                # 1. Same timestamp but higher ID, OR
                # 2. Earlier timestamp
                query += """
                    AND (
                        (strftime('%s', created_at) = strftime('%s', ?) AND id > ?)
                        OR strftime('%s', created_at) < strftime('%s', ?)
                    )
                """
                values.extend([ref_timestamp, after_id, ref_timestamp])

        # Add any additional filters
        if filters:
            where_clause, filter_values, joins_clause = self._build_filter_query(entity_type, filters)
            if joins_clause:
                query += f" {joins_clause}"
            if where_clause:
                query += f" AND {where_clause}"
                values.extend(filter_values)

        # Add order clause
        if order:
            order_clauses = []
            for field, direction in order:
                if field in ['created_at', 'updated_at']:
                    order_clauses.append(f"strftime('%s', {table_name}.{field}) {direction.upper()}")
                else:
                    order_clauses.append(f"{table_name}.{field} {direction.upper()}")
            query += f" ORDER BY {', '.join(order_clauses)}, {table_name}.id {order[0][1].upper()}"
        else:
            query += f" ORDER BY strftime('%s', {table_name}.created_at) DESC, {table_name}.id DESC"

        # Close the CTE and select from it
        query += ")\nSELECT * FROM filtered_results"

        # Add limit clause if specified
        if limit is not None:
            # Add a buffer to the limit to account for filtered out records
            buffered_limit = limit * 2  # Double the limit to ensure we get enough records
            query += f" LIMIT {buffered_limit}"

        if self.debug:
            print(f"Query: {query}")
            print(f"Values: {values}")

        cursor.execute(query, values)
        rows = cursor.fetchall()

        # Convert rows to dictionaries
        results = []
        for row in rows:
            row_dict = dict(row)
            for key, value in row_dict.items():
                if isinstance(value, str):
                    try:
                        row_dict[key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass
            results.append(row_dict)

        # Apply the actual limit after fetching
        if limit is not None:
            results = results[:limit]

        conn.close()
        return results
    
    def find_one(self, entity_type: str,
                 filters: DBFilterList | None = None,
                 fields: List[str] | None = None) -> Dict | None:
        """Find a single entity, return None if not found"""
        results = self.find(entity_type, filters, fields, limit=1)
        return results[0] if results else None

    def create(self, entity_type: str, data: Dict[str, Any]) -> int:
        """Create a new entity with timestamps
        
        Args:
            entity_type: Type of entity to create
            data: Dictionary of entity data
            return_entity: If True, returns the full entity dict instead of just the ID
            
        Returns:
            Either the entity ID (int) or full entity dict depending on return_entity parameter
        """
        table_name = convert_entity_type_to_table_name(entity_type)

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Add timestamps
            current_time = self._get_current_timestamp()
            data_with_timestamps = {
                **data,
                'created_at': current_time,
                'updated_at': current_time
            }

            # Handle JSON fields and datetime objects
            data_copy = data_with_timestamps.copy()
            for key, value in data_copy.items():
                if isinstance(value, (dict, list)):
                    data_copy[key] = json.dumps(value)
                elif isinstance(value, datetime):
                    # Convert datetime to Unix timestamp (integer)
                    data_copy[key] = int(value.timestamp())
                # elif value is None:
                #     data_copy[key] = '' ## convert None to empty string
                # else:
                #     data_copy[key] = str(value) ## convert all other values to strings

            fields = ', '.join(data_copy.keys())
            placeholders = ', '.join(['?' for _ in data_copy])
            query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

            if self.debug:
                print(f"Insert Query: {query}")
                print(f"Values: {list(data_copy.values())}")

            cursor.execute(query, list(data_copy.values()))
            entity_id = cursor.lastrowid

            conn.commit()
            conn.close()
            return entity_id

        except sqlite3.IntegrityError as e:
            conn.close()
            if "UNIQUE constraint failed" in str(e):
                # Extract the field name from the error message
                field = str(e).split('.')[-1]
                raise ValueError(f"Unique constraint violation: {field} already exists in {table_name}")
            raise e

    def update(self, entity_type: str, entity_id: int, data: Dict[str, Any], return_entity: bool = False):
        """Update an entity with automatic timestamp update"""
        table_name = convert_entity_type_to_table_name(entity_type)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Add updated_at timestamp
        data_with_timestamp = {
            **data,
            'updated_at': self._get_current_timestamp()
        }

        # Handle JSON fields
        data_copy = data_with_timestamp.copy()
        for key, value in data_copy.items():
            if isinstance(value, (dict, list)):
                data_copy[key] = json.dumps(value)

        set_clause = ', '.join([f"{k} = ?" for k in data_copy.keys()])
        values = list(data_copy.values())
        values.append(entity_id)

        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"

        if self.debug:
            print(f"Update Query: {query}")
            print(f"Values: {values}")

        cursor.execute(query, values)

        conn.commit()
        if return_entity:
            entity = self.find_one(entity_type, [('id', 'is', entity_id)])
            conn.close()
            return entity
        else:
            conn.close()
            return entity_id

    def delete(self, entity_type: str, entity_id: int, force: bool = False):
        """Delete an entity by ID"""
        table_name = convert_entity_type_to_table_name(entity_type)

        conn = self._get_connection()
        cursor = conn.cursor()

        if not force:
            # Check for references in other tables
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='table' AND name != ? AND sql LIKE ?
            """, (table_name, f'%REFERENCES {table_name}%'))
            referring_tables = cursor.fetchall()

            for table_info in referring_tables:
                table_name = table_info[0]
                # Find the actual foreign key column name from the table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                fk_columns = [col[1] for col in columns if f"REFERENCES {table_name}" in str(col).lower()]
                
                for fk_column in fk_columns:
                    # Check if there are any references to this ID
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name} 
                        WHERE {fk_column} = ?
                    """, (entity_id,))
                    if cursor.fetchone()[0] > 0:
                        conn.close()
                        raise ValueError(
                            f"Cannot delete {table_name} with ID {entity_id} "
                            f"because it is referenced in table {table_name}. "
                            "Use force=True to delete anyway."
                        )

        query = f"DELETE FROM {table_name} WHERE id = ?"

        if self.debug:
            print(f"Delete Query: {query}")
            print(f"Values: {[entity_id]}")

        cursor.execute(query, (entity_id,))
        conn.commit()
        conn.close()

    def update_timestamps(self, entity_type: str, entity_id: int, timestamp: Union[str, datetime]):
        """Update both created_at and updated_at timestamps for an entity
        
        Args:
            entity_type: Type of entity to update
            entity_id: ID of the entity to update
            timestamp: Can be:
                - datetime object
                - ISO format string
                - YYMMDD format string (e.g., '241105' for Nov 5, 2024)
        """
        # Convert YYMMDD format to datetime if needed
        if isinstance(timestamp, str) and len(timestamp) == 6:
            year = int(f"20{timestamp[:2]}")  # Assumes 20xx years
            month = int(timestamp[2:4])
            day = int(timestamp[4:6])
            timestamp = datetime(year, month, day)
        
        # Convert datetime to ISO string if needed
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        table_name = convert_entity_type_to_table_name(entity_type)
        query = f"""
            UPDATE {table_name} 
            SET created_at = ?, updated_at = ?
            WHERE id = ?
        """
        
        if self.debug:
            print(f"Update Timestamps Query: {query}")
            print(f"Values: [{timestamp}, {timestamp}, {entity_id}]")
        
        cursor.execute(query, (timestamp, timestamp, entity_id))
        conn.commit()
        conn.close()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        exists = cursor.fetchone()[0] > 0
        conn.close()
        return exists
    
    def drop_table(self, table_name: str, check_exists: bool = True) -> bool:
        """Drop a table from the database
        
        Args:
            table_name: Name of the table to drop
            check_exists: If True, checks if table exists before attempting to drop
            
        Returns:
            bool: True if table was dropped, False if table didn't exist
        """
        if check_exists and not self.table_exists(table_name):
            return False
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Also remove the table's schema from metadata
        cursor.execute('DELETE FROM _metadata WHERE entity_type = ?', (table_name,))
        
        # Drop the table
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
        
        conn.commit()
        conn.close()
        return True
    
    def add_column(self, table_name: str, column_name: str, column_type: str, references: str | None = None, on_delete: str | None = None, not_null: bool = False, default_value: Any | None = None):
        """Add a new column to an existing table
        
        Args:
            table_name: Name of the table to alter
            column_name: Name of the new column
            column_type: SQLite type for the new column (e.g., 'TEXT', 'INTEGER')
            references: Optional table to reference (for foreign keys)
            on_delete: Optional ON DELETE behavior ('CASCADE', 'RESTRICT', etc.)
            not_null: Whether the column should be NOT NULL
            default_value: Optional default value for existing rows
            
        Example:
            # Add a simple column
            db.add_column('Song', 'genre', 'TEXT', default_value='unknown')
            
            # Add a foreign key column
            db.add_column('Song', 'channel_id', 'INTEGER', 
                        references='Channel', 
                        on_delete='RESTRICT',
                        not_null=True)
        """
        if not self.table_exists(table_name):
            raise ValueError(f"Table {table_name} does not exist")
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build the ALTER TABLE statement
        alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        # Add NOT NULL if specified
        if not_null:
            if default_value is None:
                raise ValueError("NOT NULL columns must have a default value when adding to existing table")
            alter_stmt += " NOT NULL"
        
        # Add DEFAULT clause if a default value is provided
        if default_value is not None:
            if isinstance(default_value, str):
                alter_stmt += f" DEFAULT '{default_value}'"
            else:
                alter_stmt += f" DEFAULT {default_value}"
        
        # Add REFERENCES clause if specified
        if references:
            alter_stmt += f" REFERENCES {references}(id)"
            if on_delete:
                alter_stmt += f" ON DELETE {on_delete}"
        
        if self.debug:
            print(f"Alter Table Query: {alter_stmt}")
        
        cursor.execute(alter_stmt)
        
        # Update the schema in _metadata
        cursor.execute('SELECT schema FROM _metadata WHERE entity_type = ?', (table_name,))
        result = cursor.fetchone()
        if result:
            schema = json.loads(result[0])
            # Store the complete column definition in the schema
            column_def = column_type
            if not_null:
                column_def += " NOT NULL"
            if references:
                column_def += f" REFERENCES {references}(id)"
                if on_delete:
                    column_def += f" ON DELETE {on_delete}"
            schema[column_name] = column_def
            cursor.execute('UPDATE _metadata SET schema = ? WHERE entity_type = ?',
                        (json.dumps(schema), table_name))
        
        conn.commit()
        conn.close()

    def rename_column(self, table_name: str, old_column_name: str, new_column_name: str):
        """Rename an existing column in a table.
        
        This also updates the internal schema metadata.
        
        Args:
            table_name: The name of the table to alter.
            old_column_name: The current name of the column.
            new_column_name: The new name for the column.
            
        Raises:
            ValueError: If the table or old column doesn't exist, or if the new column name is already in use.
        """
        if not self.table_exists(table_name):
            raise ValueError(f"Table '{table_name}' does not exist.")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if old column exists and new one doesn't
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row['name'] for row in cursor.fetchall()]
            if old_column_name not in columns:
                raise ValueError(f"Column '{old_column_name}' does not exist in table '{table_name}'.")
            if new_column_name in columns:
                raise ValueError(f"Column '{new_column_name}' already exists in table '{table_name}'.")

            # 1. Rename the actual column
            rename_stmt = f"ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name}"
            if self.debug:
                print(f"Rename Column Query: {rename_stmt}")
            cursor.execute(rename_stmt)
            
            # 2. Update the schema in _metadata
            cursor.execute('SELECT schema FROM _metadata WHERE entity_type = ?', (table_name,))
            result = cursor.fetchone()
            if result:
                schema = json.loads(result[0])
                if old_column_name in schema:
                    # Preserve the value (column definition) under the new key
                    schema[new_column_name] = schema.pop(old_column_name)
                    cursor.execute('UPDATE _metadata SET schema = ? WHERE entity_type = ?',
                                (json.dumps(schema), table_name))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def remove_column(self, table_name: str, column_name: str):
        """Remove a column from an existing table
        
        Args:
            table_name: Name of the table to alter
            column_name: Name of the column to remove
            
        Example:
            db.remove_column('Song', 'genre')
        """
        if not self.table_exists(table_name):
            raise ValueError(f"Table {table_name} does not exist")
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get current table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Filter out the column we want to remove
        remaining_columns = [col[1] for col in columns if col[1] != column_name]
        if len(remaining_columns) == len(columns):
            raise ValueError(f"Column {column_name} does not exist in table {table_name}")
        
        # Create new table
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_sql = cursor.fetchone()[0]
        
        # Create temporary table
        temp_table = f"{table_name}_temp"
        new_create_sql = create_sql.replace(table_name, temp_table)
        
        # Remove the column definition from CREATE statement
        col_pattern = rf",?\s*{column_name}\s+[^,)]+|{column_name}\s+[^,)]+"
        import re
        new_create_sql = re.sub(col_pattern, '', new_create_sql, flags=re.IGNORECASE)
        
        cursor.execute(new_create_sql)
        
        # Copy data
        columns_str = ', '.join(remaining_columns)
        cursor.execute(f"INSERT INTO {temp_table} SELECT {columns_str} FROM {table_name}")
        
        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}")
        
        # Rename new table
        cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
        
        # Update the schema in _metadata
        cursor.execute('SELECT schema FROM _metadata WHERE entity_type = ?', (table_name,))
        result = cursor.fetchone()
        if result:
            schema = json.loads(result[0])
            if column_name in schema:
                del schema[column_name]
                cursor.execute('UPDATE _metadata SET schema = ? WHERE entity_type = ?',
                            (json.dumps(schema), table_name))
        
        conn.commit()
        conn.close()

    def rename_table(self, old_name: str, new_name: str):
        """Rename an existing table.
        
        This also updates the internal schema metadata.
        
        Args:
            old_name: The current name of the table.
            new_name: The new name for the table.
            
        Raises:
            ValueError: If the old table doesn't exist or the new table name is already in use.
        """
        if not self.table_exists(old_name):
            raise ValueError(f"Table '{old_name}' does not exist.")
        if self.table_exists(new_name):
            raise ValueError(f"Table name '{new_name}' is already in use.")

        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Rename the actual table
            rename_stmt = f"ALTER TABLE {old_name} RENAME TO {new_name}"
            if self.debug:
                print(f"Rename Table Query: {rename_stmt}")
            cursor.execute(rename_stmt)
            
            # 2. Update the name in the _metadata table
            update_meta_stmt = "UPDATE _metadata SET entity_type = ? WHERE entity_type = ?"
            if self.debug:
                print(f"Update Metadata Query: {update_meta_stmt}")
                print(f"Values: [{new_name}, {old_name}]")
            cursor.execute(update_meta_stmt, (new_name, old_name))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
 
