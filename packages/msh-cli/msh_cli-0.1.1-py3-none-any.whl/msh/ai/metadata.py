"""
Metadata extraction for msh assets.

Extracts schema information, lineage, and test definitions from assets
for AI context generation.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from msh.compiler.parser import MshParser
from msh.ai.ast_generator import AstGenerator
from msh.dependency import DependencyResolver


class MetadataExtractor:
    """Extracts metadata from .msh assets."""
    
    def __init__(self, msh_config: Optional[Dict[str, Any]] = None):
        """
        Initialize metadata extractor.
        
        Args:
            msh_config: Optional configuration dictionary from msh.yaml
        """
        self.msh_config = msh_config or {}
        self.parser = MshParser(msh_config=self.msh_config)
        self.ast_generator = AstGenerator()
        self.dependency_resolver = DependencyResolver()
    
    def extract_asset_metadata(
        self,
        file_path: str,
        project_root: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract complete metadata for a single asset.
        
        Args:
            file_path: Path to the .msh file
            project_root: Optional project root directory for resolving paths
            
        Returns:
            Dictionary matching asset_inspect schema
        """
        if project_root is None:
            project_root = os.getcwd()
        
        # Parse the asset file
        asset_data, content_hash = self.parser.parse_file(file_path)
        
        # Generate AST
        ast = self.ast_generator.generate_ast(asset_data, file_path)
        
        # Extract schema information
        schema = self._extract_schema(asset_data, ast)
        
        # Extract lineage
        lineage = self._extract_lineage(ast, project_root)
        
        # Extract tests
        tests = self._extract_tests(asset_data)
        
        # Build complete metadata structure
        metadata = {
            "id": ast["id"],
            "path": ast["path"],
            "blocks": ast["blocks"],
            "schema": schema,
            "tests": tests,
            "lineage": lineage,
            "content_hash": content_hash,
        }
        
        return metadata
    
    def _extract_schema(
        self,
        asset_data: Dict[str, Any],
        ast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract schema information from asset."""
        schema = {
            "columns": []
        }
        
        # Try to extract columns from transform block
        transform_block = ast.get("blocks", {}).get("transform", {})
        columns_referenced = transform_block.get("columns_referenced", [])
        
        # If we have column information from ingest block
        ingest_block = asset_data.get("ingest", {})
        if isinstance(ingest_block, dict):
            ingest_columns = ingest_block.get("columns")
            if ingest_columns:
                # Use ingest columns as source of truth
                for col in ingest_columns:
                    if isinstance(col, dict):
                        col_dict = {
                            "name": col.get("name", ""),
                            "type": col.get("type", "unknown"),
                            "description": col.get("description", ""),
                        }
                        # Add nullable flag if available
                        if "nullable" in col:
                            col_dict["nullable"] = col.get("nullable", True)
                        schema["columns"].append(col_dict)
                    elif isinstance(col, str):
                        schema["columns"].append({
                            "name": col,
                            "type": "unknown",
                            "description": "",
                        })
        
        # If no ingest columns, infer from transform
        if not schema["columns"] and columns_referenced:
            for col_name in columns_referenced[:20]:  # Limit to 20 columns
                schema["columns"].append({
                    "name": col_name,
                    "type": "unknown",  # Type inference would require SQL parsing
                    "description": "",
                })
        
        # Extract constraints and statistics from metadata block
        metadata = asset_data.get("metadata", {})
        if metadata:
            if metadata.get("primary_keys"):
                schema["constraints"] = {
                    "primary_keys": metadata["primary_keys"]
                }
            if metadata.get("foreign_keys"):
                if "constraints" not in schema:
                    schema["constraints"] = {}
                schema["constraints"]["foreign_keys"] = metadata["foreign_keys"]
            
            # Extract statistics
            stats = {}
            if metadata.get("row_count") is not None:
                stats["row_count"] = metadata["row_count"]
            
            # Extract column-level statistics
            column_statistics = metadata.get("column_statistics", {})
            if column_statistics:
                stats["columns"] = column_statistics
                # Also attach statistics to individual columns in schema
                for col in schema.get("columns", []):
                    col_name = col.get("name")
                    if col_name and col_name in column_statistics:
                        col_stats = column_statistics[col_name]
                        if "statistics" not in col:
                            col["statistics"] = {}
                        col["statistics"].update(col_stats)
            
            if stats:
                schema["statistics"] = stats
        
        # Extract column-level lineage from transform block
        transform_block = ast.get("blocks", {}).get("transform", {})
        column_lineage = transform_block.get("column_lineage", {})
        if column_lineage:
            schema["column_lineage"] = column_lineage
        
        return schema
    
    def _extract_lineage(
        self,
        ast: Dict[str, Any],
        project_root: str
    ) -> Dict[str, Any]:
        """Extract lineage information from AST."""
        transform_block = ast.get("blocks", {}).get("transform", {})
        dependencies = transform_block.get("dependencies", [])
        
        return {
            "upstream": dependencies,
            "downstream": [],  # Will be populated when building full project graph
        }
    
    def _extract_tests(self, asset_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract test definitions from asset."""
        tests = asset_data.get("tests", [])
        
        if not isinstance(tests, list):
            return []
        
        test_definitions = []
        for test in tests:
            if isinstance(test, dict):
                test_definitions.append({
                    "name": test.get("name", "unnamed_test"),
                    "type": test.get("type", "unknown"),
                    "config": test.get("config", {}),
                    "description": test.get("description", ""),
                })
            elif isinstance(test, str):
                test_definitions.append({
                    "name": test,
                    "type": "unknown",
                    "config": {},
                    "description": "",
                })
        
        return test_definitions

