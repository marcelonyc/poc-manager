#!/usr/bin/env python3
"""
Script to enhance Python docstrings in route functions for MCP tool exposure.
Adds comprehensive documentation of purpose, inputs, outputs, and requirements.
"""

import re
import os
from pathlib import Path

# Define docstring enhancements for each route function
ENHANCEMENTS = {
    "backend/app/routers/products.py": [
        {
            "function": "def create_product",
            "old_doc": '"""Create a new product (Tenant Admin or Administrator)"""',
            "new_doc": '"""\n    Create a new product.\n    \n    Purpose: Add a new product/solution to tenant catalog for use in POCs.\n    \n    Args:\n        product_data: ProductCreate with name and description\n    \n    Returns:\n        ProductSchema with created product\n    \n    Requires: Tenant Admin or Administrator\n    \n    Raises:\n        403 Forbidden: Insufficient permissions\n    """',
        },
        {
            "function": "def list_products",
            "old_doc": '"""List all products for the current tenant"""',
            "new_doc": '"""\n    List all products for current tenant.\n    \n    Purpose: Retrieve all products available in tenant catalog.\n    \n    Returns:\n        List of ProductSchema objects\n    """',
        },
        {
            "function": "def get_product",
            "old_doc": '"""Get product details with usage information"""',
            "new_doc": '"""\n    Get product details with usage statistics.\n    \n    Purpose: Retrieve specific product and count how many POCs use it.\n    \n    Args:\n        product_id (int): Product identifier\n    \n    Returns:\n        ProductWithUsage schema with product and usage count\n    \n    Raises:\n        404 Not Found: Product not found\n    """',
        },
        {
            "function": "def update_product",
            "old_doc": '"""Update a product name (Tenant Admin or Administrator)"""',
            "new_doc": '"""\n    Update product details.\n    \n    Purpose: Modify product name or description.\n    \n    Args:\n        product_id (int): Product identifier\n        product_data: ProductUpdate with fields to modify\n    \n    Returns:\n        Updated ProductSchema\n    \n    Requires: Tenant Admin or Administrator\n    \n    Raises:\n        404 Not Found: Product not found\n        403 Forbidden: Insufficient permissions\n    """',
        },
        {
            "function": "def delete_product",
            "old_doc": '"""Delete a product (Tenant Admin or Administrator)"""',
            "new_doc": '"""\n    Delete a product.\n    \n    Purpose: Remove product from catalog. Only possible if no POCs use it.\n    \n    Args:\n        product_id (int): Product identifier\n    \n    Returns:\n        Dict with success message\n    \n    Requires: Tenant Admin or Administrator\n    \n    Raises:\n        404 Not Found: Product not found\n        403 Forbidden: Insufficient permissions or product in use\n    """',
        },
    ]
}


def enhance_docstrings():
    """Process all router files and enhance docstrings."""
    workspace_root = Path("/home/marcelo/poc-manager")

    for file_path, enhancements in ENHANCEMENTS.items():
        full_path = workspace_root / file_path

        if not full_path.exists():
            print(f"File not found: {full_path}")
            continue

        with open(full_path, "r") as f:
            content = f.read()

        for enhancement in enhancements:
            if enhancement["old_doc"] in content:
                content = content.replace(
                    enhancement["old_doc"], enhancement["new_doc"]
                )
                print(f"Enhanced {file_path}::{enhancement['function']}")
            else:
                print(
                    f"WARNING: Could not find docstring in {file_path}::{enhancement['function']}"
                )

        with open(full_path, "w") as f:
            f.write(content)

    print("\nDocstring enhancement complete!")


if __name__ == "__main__":
    enhance_docstrings()
