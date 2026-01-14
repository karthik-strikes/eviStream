"""
DSPy Module Generator

Handles template-based generation of DSPy Module classes that wrap signatures.
Modules are pure boilerplate - no LLM needed!
"""

import json
from typing import Dict, Any
from .module_validator import ModuleValidator


class ModuleGenerator:
    """
    Generates async DSPy Module classes using deterministic templates.
    Fast, reliable, and cost-free!
    """

    def __init__(self, model_name: str = "google_genai:gemini-3-pro-preview"):
        """
        Initialize module generator.

        Args:
            model_name: Kept for backward compatibility (not used)
        """
        self.validator = ModuleValidator()

    def generate_module_code(
        self,
        signature_class_name: str,
        fallback_structure: Dict[str, Any],
    ) -> str:
        """
        Generate an Async DSPy Module using deterministic template.

        No LLM needed - modules are pure boilerplate!

        Args:
            signature_class_name: Name of the signature class to wrap
            fallback_structure: Dict of field_name -> default_value

        Returns:
            Complete Python code for the async module
        """
        module_class_name = f"Async{signature_class_name}Extractor"

        # Extract field names for result building
        field_names = list(fallback_structure.keys())

        # Format fallback structure for code
        fallback_json = json.dumps(fallback_structure, indent=12)

        # Build field extraction code with source grounding support
        # Each field is a Dict[str, Any] with "value" and "source_text" keys
        field_extraction = "{\n"
        for field in field_names:
            field_extraction += f'            "{field}": getattr(result, "{field}", {{"value": "NR", "source_text": "NR"}}),\n'
        field_extraction += "        }"

        # Generate module code using template
        code = f'''


class {module_class_name}(dspy.Module):
    """Async module to extract data using {signature_class_name} signature."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.extract = dspy.ChainOfThought({signature_class_name})

    async def __call__(self, markdown_content: str, **kwargs) -> Dict[str, Any]:
        """
        Extract data from markdown content.
        
        Args:
            markdown_content: Full markdown text to extract from
            **kwargs: Additional context fields if needed
            
        Returns:
            Dict with extracted field values
        """
        loop = asyncio.get_running_loop()

        def _extract():
            return self.extract(markdown_content=markdown_content, **kwargs)

        try:
            result = await loop.run_in_executor(None, _extract)
            # Extract all output fields from result
            return {field_extraction}
        except Exception as e:
            print(f"Error in {module_class_name}: {{e}}")
            # Return fallback structure with default values
            return {fallback_json}
'''

        return code

    def generate_module(
        self,
        signature_class_name: str,
        output_field_name: str,
        fallback_structure: Dict[str, Any],
        max_attempts: int = 1,  # No retry needed for templates!
    ) -> Dict[str, Any]:
        """
        Generate an async DSPy module that wraps a signature.

        Uses deterministic template - always succeeds on first try!

        Args:
            signature_class_name: Name of the signature class
            output_field_name: Name of output field (kept for compatibility, not used)
            fallback_structure: Default structure for error recovery
            max_attempts: Kept for compatibility (always 1)

        Returns:
            dict with 'code', 'is_valid', 'attempts', 'errors'
        """
        try:
            # Generate code using template - fast and deterministic!
            code = self.generate_module_code(
                signature_class_name=signature_class_name,
                fallback_structure=fallback_structure
            )

            # Show generated code for debugging
            print("\n--- Generated Module Code ---")
            print(code)
            print("--- End of Generated Code ---\n")

            # Validate (should always pass with template)
            is_valid, issues = self.validator.validate_module(code)

            return {
                "code": code,
                "is_valid": is_valid,
                "attempts": 1,
                "errors": [] if is_valid else issues,
                "warnings": issues if is_valid else [],
            }

        except Exception as e:
            return {
                "code": "",
                "is_valid": False,
                "attempts": 1,
                "errors": [f"Template generation failed: {str(e)}"],
            }

    def create_fallback_structure(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback structure for error recovery in modules.
        With source grounding, all fields return {"value": "NR", "source_text": "NR"}.

        Args:
            spec: Questionnaire spec with output_structure

        Returns:
            Fallback structure with default values
        """
        output_structure = spec.get("output_structure", {})

        if isinstance(output_structure, dict):
            # Create fallback with source grounding format
            fallback = {}
            for field_name in output_structure.keys():
                fallback[field_name] = {"value": "NR", "source_text": "NR"}
            return fallback
        else:
            return {"value": "NR", "source_text": "NR"}

    def assemble_modules_file(
        self,
        modules: list[str],
        task_name: str,
        signature_class_names: list[str] = None
    ) -> str:
        """
        Assemble complete modules.py file from generated module codes.

        Args:
            modules: List of module code strings
            task_name: Task name for imports and header
            signature_class_names: List of signature class names to import

        Returns:
            Complete modules.py file content
        """
        lines = [
            "import asyncio",
            "import json",
            "from typing import Dict, Any",
            "",
            "import dspy",
            "",
            "from utils.json_parser import safe_json_parse",
        ]

        # Add signature imports
        if signature_class_names:
            lines.append(
                f"from dspy_components.tasks.{task_name}.signatures import (")
            for sig_name in signature_class_names:
                lines.append(f"    {sig_name},")
            lines.append(")")
        else:
            # Fallback to placeholder if no names provided
            lines.extend([
                f"from dspy_components.tasks.{task_name}.signatures import (",
                "    # Import signatures here",
                ")",
            ])

        lines.extend([
            "",
            "",
            "# " + "=" * 76,
            f"# MODULES - {task_name.upper().replace('_', ' ')}",
            "# " + "=" * 76,
            "",
            "",
        ])

        for module_code in modules:
            lines.append(module_code)
            lines.append("\n\n")

        # Extract module class names and add __all__ export
        import re
        module_class_names = []
        full_modules_code = "\n".join(modules)
        class_pattern = r'class\s+(\w+)\s*\('
        for match in re.finditer(class_pattern, full_modules_code):
            class_name = match.group(1)
            module_class_names.append(class_name)

        if module_class_names:
            lines.extend(["", "", "__all__ = ["])
            for name in module_class_names:
                lines.append(f'    "{name}",')
            lines.append("]")

        return "\n".join(lines)


__all__ = ["ModuleGenerator"]
