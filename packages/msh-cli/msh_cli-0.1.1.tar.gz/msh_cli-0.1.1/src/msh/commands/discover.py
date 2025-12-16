"""
Auto-discovery command for msh.

Probes sources (REST APIs or SQL databases) and generates .msh file configurations.
"""
import os
import re
import yaml
import click
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse
from rich.console import Console
from rich.spinner import Spinner

console_output = Console()


def _detect_source_type(source: str) -> str:
    """
    Detects whether source is REST API or SQL database.
    
    Args:
        source: Source string (URL or connection string)
        
    Returns:
        "rest_api" or "sql_database"
    """
    # Check if it's a URL (http/https)
    if source.startswith(("http://", "https://")):
        return "rest_api"
    
    # Check if it's a SQL connection string (contains ://)
    if "://" in source:
        return "sql_database"
    
    # Default to REST API if unclear (let it fail gracefully)
    return "rest_api"


def _infer_column_types(sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Infers column types from sample data.
    
    Args:
        sample_data: List of dictionaries (sample rows)
        
    Returns:
        Dictionary mapping column names to inferred types
    """
    if not sample_data:
        return {}
    
    type_counts = {}
    
    # Analyze each column across all samples
    for row in sample_data:
        for col_name, value in row.items():
            if col_name not in type_counts:
                type_counts[col_name] = {}
            
            # Determine Python type
            if value is None:
                py_type = "null"
            elif isinstance(value, bool):
                py_type = "boolean"
            elif isinstance(value, int):
                py_type = "integer"
            elif isinstance(value, float):
                py_type = "number"
            elif isinstance(value, str):
                # Try to detect datetime strings
                if re.match(r'^\d{4}-\d{2}-\d{2}', value) or 'T' in value:
                    py_type = "datetime"
                else:
                    py_type = "string"
            elif isinstance(value, (list, dict)):
                py_type = "object"
            else:
                py_type = "string"
            
            type_counts[col_name][py_type] = type_counts[col_name].get(py_type, 0) + 1
    
    # Choose most common type for each column
    inferred_types = {}
    for col_name, types in type_counts.items():
        # Prefer non-null types
        non_null_types = {k: v for k, v in types.items() if k != "null"}
        if non_null_types:
            most_common = max(non_null_types.items(), key=lambda x: x[1])[0]
        else:
            most_common = "string"  # Default if all null
        
        inferred_types[col_name] = most_common
    
    return inferred_types


def _discover_rest_api(endpoint: str) -> Dict[str, Any]:
    """
    Probes REST API endpoint and infers schema.
    
    Args:
        endpoint: REST API URL
        
    Returns:
        Dictionary with schema information:
        - columns: List of column names
        - types: Dictionary mapping columns to types
        - resource_name: Inferred resource name
        - sample_data: Sample rows
    """
    try:
        from dlt.sources.rest_api import rest_api_source
    except ImportError:
        raise ImportError("dlt[rest_api] is not installed. Please install it: pip install dlt[rest_api]")
    
    # Parse URL
    parsed = urlparse(endpoint)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path
    if parsed.query:
        path += f"?{parsed.query}"
    
    # Generate resource name from path
    resource_name = path.strip("/").replace("/", "_").replace("-", "_") or "data"
    if resource_name.startswith("_"):
        resource_name = resource_name[1:]
    
    # Create simple REST API config
    rest_config = {
        "client": {
            "base_url": base_url
        },
        "resources": [
            {
                "name": resource_name,
                "endpoint": {
                    "path": path,
                }
            }
        ]
    }
    
    # Probe the API
    console_output.print(f"[cyan]Probing REST API: {endpoint}[/cyan]")
    
    try:
        source = rest_api_source(rest_config)
        resource = source.resources[resource_name]
        
        # Fetch sample data (first 100 rows or first page)
        sample_data = []
        count = 0
        max_samples = 100
        
        for row in resource:
            sample_data.append(row)
            count += 1
            if count >= max_samples:
                break
        
        if not sample_data:
            raise ValueError("No data returned from API endpoint")
        
        # Infer schema
        columns = list(sample_data[0].keys()) if sample_data else []
        types = _infer_column_types(sample_data)
        
        return {
            "columns": columns,
            "types": types,
            "resource_name": resource_name,
            "sample_data": sample_data[:5]  # Keep only first 5 for display
        }
        
    except Exception as e:
        raise ValueError(f"Failed to probe REST API: {e}") from e


def _discover_sql_database(connection_string: str, table_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Inspects SQL database table and infers schema.
    
    Args:
        connection_string: SQLAlchemy connection string
        table_name: Optional table name (if not provided, will list tables)
        
    Returns:
        Dictionary with schema information:
        - columns: List of column names
        - types: Dictionary mapping columns to SQL types
        - table_name: Table name
    """
    try:
        import sqlalchemy
        from sqlalchemy import inspect
    except ImportError:
        raise ImportError("sqlalchemy is not installed. Please install it: pip install sqlalchemy")
    
    console_output.print(f"[cyan]Connecting to SQL database...[/cyan]")
    
    try:
        engine = sqlalchemy.create_engine(connection_string)
        inspector = inspect(engine)
        
        # If no table name provided, list available tables
        if not table_name:
            tables = inspector.get_table_names()
            if not tables:
                raise ValueError("No tables found in database")
            
            # Use first table (or could prompt user)
            table_name = tables[0]
            console_output.print(f"[yellow]No table specified. Using first table: {table_name}[/yellow]")
            if len(tables) > 1:
                console_output.print(f"[dim]Available tables: {', '.join(tables)}[/dim]")
        
        # Get column information
        columns_info = inspector.get_columns(table_name)
        
        columns = []
        types = {}
        column_descriptions = {}
        
        for col_info in columns_info:
            col_name = col_info['name']
            col_type = col_info['type']
            
            columns.append(col_name)
            
            # Extract column comment/description if available
            col_comment = col_info.get('comment') or col_info.get('description')
            if col_comment:
                column_descriptions[col_name] = col_comment
            
            # Map SQLAlchemy types to YAML-friendly types
            type_str = str(col_type).upper()
            if 'INT' in type_str or 'SERIAL' in type_str:
                types[col_name] = "integer"
            elif 'DECIMAL' in type_str or 'NUMERIC' in type_str or 'FLOAT' in type_str or 'DOUBLE' in type_str:
                types[col_name] = "number"
            elif 'BOOL' in type_str:
                types[col_name] = "boolean"
            elif 'DATE' in type_str or 'TIME' in type_str or 'TIMESTAMP' in type_str:
                types[col_name] = "datetime"
            else:
                types[col_name] = "string"
        
        # Extract constraints
        constraints = {
            "primary_keys": [],
            "foreign_keys": [],
            "unique_constraints": []
        }
        
        try:
            # Get primary key constraint
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint and pk_constraint.get('constrained_columns'):
                constraints["primary_keys"] = pk_constraint['constrained_columns']
        except Exception:
            pass  # Some databases may not support this
        
        try:
            # Get foreign key constraints
            fk_constraints = inspector.get_foreign_keys(table_name)
            for fk in fk_constraints:
                constraints["foreign_keys"].append({
                    "columns": fk.get('constrained_columns', []),
                    "references_table": fk.get('referred_table'),
                    "references_columns": fk.get('referred_columns', [])
                })
        except Exception:
            pass  # Some databases may not support this
        
        try:
            # Get unique constraints
            unique_constraints = inspector.get_unique_constraints(table_name)
            for uc in unique_constraints:
                constraints["unique_constraints"].append({
                    "name": uc.get('name'),
                    "columns": uc.get('column_names', [])
                })
        except Exception:
            pass  # Some databases may not support this
        
        # Extract indexes
        indexes = []
        try:
            index_info = inspector.get_indexes(table_name)
            for idx in index_info:
                indexes.append({
                    "name": idx.get('name'),
                    "columns": idx.get('column_names', []),
                    "unique": idx.get('unique', False)
                })
        except Exception:
            pass  # Some databases may not support this
        
        # Fetch sample data and basic statistics
        sample_data = []
        statistics = {}
        with engine.connect() as conn:
            from sqlalchemy import text
            # Handle schema.table format properly
            if '.' in table_name:
                # Schema.table format - quote each part separately
                schema_part, table_part = table_name.split('.', 1)
                quoted_table = f'"{schema_part}"."{table_part}"'
            else:
                # Simple table name
                quoted_table = f'"{table_name}"'
            
            # Get row count
            try:
                count_result = conn.execute(text(f"SELECT COUNT(*) as row_count FROM {quoted_table}"))
                row_count = count_result.fetchone()[0]
                statistics["row_count"] = row_count
            except Exception:
                statistics["row_count"] = None
            
            # Get sample data (first 5 rows)
            result = conn.execute(text(f"SELECT * FROM {quoted_table} LIMIT 5"))
            for row in result:
                sample_data.append(dict(row._mapping))
            
            # Get enhanced statistics for each column (limited to first 10 columns for performance)
            for col_name in columns[:10]:
                col_stats = {}
                try:
                    # Get distinct count
                    distinct_result = conn.execute(
                        text(f"SELECT COUNT(DISTINCT {col_name}) as distinct_count FROM {quoted_table}")
                    )
                    distinct_count = distinct_result.fetchone()[0]
                    col_stats["distinct_count"] = distinct_count
                    
                    # Get null count and calculate null percentage
                    if row_count and row_count > 0:
                        null_result = conn.execute(
                            text(f"SELECT COUNT(*) as null_count FROM {quoted_table} WHERE {col_name} IS NULL")
                        )
                        null_count = null_result.fetchone()[0]
                        null_percentage = (null_count / row_count) * 100.0
                        col_stats["null_count"] = null_count
                        col_stats["null_percentage"] = round(null_percentage, 2)
                    
                    # Get min/max for numeric columns
                    col_type = types.get(col_name, "").lower()
                    if col_type in ("integer", "number", "float", "double", "decimal", "numeric", "bigint", "smallint"):
                        try:
                            min_result = conn.execute(
                                text(f"SELECT MIN({col_name}) as min_value FROM {quoted_table}")
                            )
                            min_value = min_result.fetchone()[0]
                            if min_value is not None:
                                col_stats["min_value"] = float(min_value) if isinstance(min_value, (int, float)) else str(min_value)
                            
                            max_result = conn.execute(
                                text(f"SELECT MAX({col_name}) as max_value FROM {quoted_table}")
                            )
                            max_value = max_result.fetchone()[0]
                            if max_value is not None:
                                col_stats["max_value"] = float(max_value) if isinstance(max_value, (int, float)) else str(max_value)
                        except Exception:
                            pass  # Skip min/max if not supported
                    
                    if col_stats:
                        statistics[col_name] = col_stats
                except Exception:
                    pass  # Skip if column statistics can't be computed
        
        return {
            "columns": columns,
            "types": types,
            "table_name": table_name,
            "sample_data": sample_data,
            "constraints": constraints,
            "indexes": indexes,
            "statistics": statistics,
            "column_descriptions": column_descriptions
        }
        
    except Exception as e:
        raise ValueError(f"Failed to probe SQL database: {e}")


def _parse_sql_source(source: str) -> Tuple[str, Optional[str]]:
    """
    Parses SQL source string to extract connection string and optional table name.
    
    Supports formats:
    - "postgresql://user:pass@host/db" (connection string only)
    - "postgresql://user:pass@host/db table:orders" (connection string + table)
    
    Args:
        source: Source string
        
    Returns:
        Tuple of (connection_string, table_name)
    """
    # Check if table name is specified
    if " table:" in source:
        parts = source.split(" table:", 1)
        connection_string = parts[0].strip()
        table_name = parts[1].strip()
        return connection_string, table_name
    
    return source, None


def _generate_asset_name(source_type: str, source_config: Dict[str, Any]) -> str:
    """
    Generates a default asset name from source configuration.
    
    Args:
        source_type: "rest_api" or "sql_database"
        source_config: Source configuration dictionary
        
    Returns:
        Asset name string
    """
    if source_type == "rest_api":
        endpoint = source_config.get("endpoint", "")
        resource_name = source_config.get("resource", "data")
        
        # Extract meaningful name from URL
        parsed = urlparse(endpoint)
        path_parts = [p for p in parsed.path.split("/") if p]
        
        if path_parts:
            # Use last meaningful part of path
            name = path_parts[-1].replace("-", "_").replace(".", "_")
        else:
            # Use domain name
            name = parsed.netloc.split(".")[-2] if "." in parsed.netloc else "api"
        
        # Combine with resource name if different
        if resource_name != "data" and resource_name != name:
            name = f"{name}_{resource_name}"
        
        return name
    
    elif source_type == "sql_database":
        table_name = source_config.get("table", "table")
        # Remove schema prefix if present
        if "." in table_name:
            table_name = table_name.split(".")[-1]
        return table_name
    
    return "discovered_asset"


def _generate_msh_yaml(
    asset_name: str,
    source_type: str,
    source_config: Dict[str, Any],
    schema: Dict[str, Any]
) -> str:
    """
    Generates .msh file YAML content.
    
    Args:
        asset_name: Asset name
        source_type: "rest_api" or "sql_database"
        source_config: Source configuration
        schema: Schema information (columns, types, etc.)
        
    Returns:
        YAML string
    """
    columns = schema.get("columns", [])
    types = schema.get("types", {})
    column_descriptions = schema.get("column_descriptions", {})
    constraints = schema.get("constraints", {})
    statistics = schema.get("statistics", {})
    
    # Build ingest block
    ingest_block = {
        "type": source_type
    }
    
    if source_type == "rest_api":
        ingest_block["endpoint"] = source_config["endpoint"]
        ingest_block["resource"] = source_config.get("resource", "data")
    elif source_type == "sql_database":
        ingest_block["credentials"] = source_config["credentials"]
        ingest_block["table"] = source_config["table"]
        
        # Add columns with descriptions if available
        if columns:
            ingest_columns = []
            for col_name in columns:
                col_dict = {
                    "name": col_name,
                    "type": types.get(col_name, "string")
                }
                if col_name in column_descriptions:
                    col_dict["description"] = column_descriptions[col_name]
                ingest_columns.append(col_dict)
            ingest_block["columns"] = ingest_columns
    
    # Build contract block with inferred schema
    contract_block = {
        "evolution": "evolve",  # Default: allow schema evolution
        "enforce_types": True,  # Enforce type consistency
        "required_columns": columns[:10] if columns and len(columns) > 10 else (columns if columns else [])  # First 10 columns as required, or all if <= 10
    }
    
    # Add constraints metadata if available
    metadata = {}
    if constraints.get("primary_keys"):
        metadata["primary_keys"] = constraints["primary_keys"]
    if constraints.get("foreign_keys"):
        metadata["foreign_keys"] = constraints["foreign_keys"]
    if statistics.get("row_count") is not None:
        metadata["row_count"] = statistics["row_count"]
    
    # Add column-level statistics
    column_statistics = {}
    for col_name in columns[:10]:  # Limit to first 10 columns
        if col_name in statistics and isinstance(statistics[col_name], dict):
            col_stats = statistics[col_name].copy()
            # Remove distinct_count from top-level if it exists (it's now in column stats)
            if col_stats:
                column_statistics[col_name] = col_stats
    if column_statistics:
        metadata["column_statistics"] = column_statistics
    
    # Build YAML structure
    yaml_content = {
        "name": asset_name,
        "description": f"Auto-discovered from {source_type}",
        "ingest": ingest_block,
        "contract": contract_block,
        "transform": "SELECT * FROM {{ source }}"
    }
    
    # Add metadata if available
    if metadata:
        yaml_content["metadata"] = metadata
    
    # Convert to YAML string
    yaml_str = yaml.dump(yaml_content, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return yaml_str


@click.command()
@click.argument('source')
@click.option('--name', help='Asset name (defaults to inferred name)')
@click.option('--output', '-o', help='Output file path (defaults to models/{name}.msh)')
@click.option('--write/--no-write', default=True, help='Write to file (default) or print only')
def discover(source: str, name: Optional[str], output: Optional[str], write: bool) -> None:
    """
    Auto-discover source schema and generate .msh file configuration.
    
    SOURCE: Source to probe. Can be:
    - REST API URL: https://api.github.com/repos/dlt-hub/dlt/issues
    - SQL connection: postgresql://user:pass@host/db
    - SQL with table: postgresql://user:pass@host/db table:orders
    
    Examples:
        msh discover https://api.github.com/repos/dlt-hub/dlt/issues
        msh discover postgresql://user:pass@localhost/db table:orders
        msh discover postgresql://user:pass@localhost/db --name my_orders
    """
    try:
        # Detect source type
        source_type = _detect_source_type(source)
        console_output.print(f"[green]Detected source type: {source_type}[/green]")
        
        # Discover schema
        schema_info = {}
        source_config = {}
        
        if source_type == "rest_api":
            schema_info = _discover_rest_api(source)
            source_config = {
                "endpoint": source,
                "resource": schema_info["resource_name"]
            }
        elif source_type == "sql_database":
            connection_string, table_name = _parse_sql_source(source)
            schema_info = _discover_sql_database(connection_string, table_name)
            source_config = {
                "credentials": connection_string,
                "table": schema_info["table_name"]
            }
        
        # Generate asset name
        asset_name = name or _generate_asset_name(source_type, source_config)
        
        # Validate and sanitize asset name
        if not asset_name or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', asset_name):
            # Sanitize: replace invalid chars with underscores, ensure starts with letter/underscore
            sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', asset_name)
            if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
                sanitized = '_' + sanitized
            asset_name = sanitized or "discovered_asset"
            console_output.print(f"[yellow]Warning: Sanitized asset name to: {asset_name}[/yellow]")
        
        # Generate YAML
        yaml_content = _generate_msh_yaml(asset_name, source_type, source_config, schema_info)
        
        # Print to console
        console_output.print(f"\n[bold green]Generated .msh configuration:[/bold green]\n")
        console_output.print(f"[dim]{'=' * 60}[/dim]")
        console_output.print(yaml_content)
        console_output.print(f"[dim]{'=' * 60}[/dim]")
        
        # Write to file if requested
        if write:
            # Determine output path
            if output:
                output_path = output
            else:
                models_dir = os.path.join(os.getcwd(), "models")
                if not os.path.exists(models_dir):
                    os.makedirs(models_dir)
                output_path = os.path.join(models_dir, f"{asset_name}.msh")
            
            # Check if file exists
            if os.path.exists(output_path):
                console_output.print(f"\n[yellow]Warning: File {output_path} already exists.[/yellow]")
                if not click.confirm("Overwrite?"):
                    console_output.print("[yellow]Skipped writing to file.[/yellow]")
                    return
            
            # Write file
            with open(output_path, "w") as f:
                f.write(yaml_content)
            
            console_output.print(f"\n[bold green]✓ Written to: {output_path}[/bold green]")
            console_output.print(f"[dim]You can now run: msh run {asset_name}[/dim]")
        
    except Exception as e:
        console_output.print(f"[bold red]Discovery failed: {e}[/bold red]")
        import sys
        sys.exit(1)

