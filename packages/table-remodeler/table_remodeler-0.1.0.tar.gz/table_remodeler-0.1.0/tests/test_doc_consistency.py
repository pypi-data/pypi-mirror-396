import unittest
import os
import re
import glob
import remodel
from remodel.operations.valid_operations import valid_operations


class TestDocConsistency(unittest.TestCase):
    def setUp(self):
        self.current_dir = os.path.dirname(__file__)
        self.docs_root = os.path.abspath(os.path.join(self.current_dir, "..", "docs", "api"))

    def test_operations_are_documented(self):
        """
        Ensure all operations in valid_operations are listed in docs/api/operations.rst.
        This preserves manual organization while ensuring completeness.
        """
        docs_path = os.path.join(self.docs_root, "operations.rst")

        # Read the documentation file
        with open(docs_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract all class names documented via autoclass
        # Matches: .. autoclass:: remodel.operations.some_module.ClassName
        documented_classes = set()
        pattern = r"\.\.\s+autoclass::\s+[\w\.]+\.(\w+)"

        for match in re.finditer(pattern, content):
            documented_classes.add(match.group(1))

        # Check against the source of truth
        missing_ops = []
        for _op_name, op_class in valid_operations.items():
            class_name = op_class.__name__
            if class_name not in documented_classes:
                missing_ops.append(class_name)

        # Fail if anything is missing
        if missing_ops:
            self.fail(
                "\nThe following operations are defined in valid_operations but missing from operations.rst:\n"
                + "\n".join(f"- {op}" for op in missing_ops)
                + "\n\nPlease add them to docs/api/operations.rst under the appropriate section."
            )

    def test_core_is_documented(self):
        """
        Ensure all classes exported in remodel/__init__.py are documented in docs/api/core.rst.
        """
        docs_path = os.path.join(self.docs_root, "core.rst")

        # Read the documentation file
        with open(docs_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get exported classes from remodel/__init__.py
        # We filter for classes that are actually defined in the package (not modules)
        exported_classes = [
            name for name in dir(remodel) if not name.startswith("_") and isinstance(getattr(remodel, name), type)
        ]

        # Extract documented classes
        documented_classes = set()
        pattern = r"\.\.\s+autoclass::\s+[\w\.]+\.(\w+)"

        for match in re.finditer(pattern, content):
            documented_classes.add(match.group(1))

        missing_classes = []
        for cls_name in exported_classes:
            if cls_name not in documented_classes:
                missing_classes.append(cls_name)

        if missing_classes:
            self.fail(
                "\nThe following core classes are exported by remodel but missing from core.rst:\n"
                + "\n".join(f"- {cls}" for cls in missing_classes)
                + "\n\nPlease add them to docs/api/core.rst."
            )

    def test_cli_is_documented(self):
        """
        Ensure all CLI scripts in remodel/cli/ are documented in docs/api/cli.rst.
        """
        docs_path = os.path.join(self.docs_root, "cli.rst")
        cli_dir = os.path.abspath(os.path.join(self.current_dir, "..", "remodel", "cli"))

        # Read the documentation file
        with open(docs_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all python files in cli directory, excluding __init__.py
        cli_files = glob.glob(os.path.join(cli_dir, "*.py"))
        cli_modules = [
            os.path.basename(f)[:-3] for f in cli_files if os.path.basename(f) != "__init__.py"  # remove .py extension
        ]

        # Extract documented modules
        # Matches: .. automodule:: remodel.cli.module_name
        documented_modules = set()
        pattern = r"\.\.\s+automodule::\s+remodel\.cli\.(\w+)"

        for match in re.finditer(pattern, content):
            documented_modules.add(match.group(1))

        missing_modules = []
        for module in cli_modules:
            if module not in documented_modules:
                missing_modules.append(module)

        if missing_modules:
            self.fail(
                "\nThe following CLI modules are present in remodel/cli/ but missing from cli.rst:\n"
                + "\n".join(f"- {mod}" for mod in missing_modules)
                + "\n\nPlease add them to docs/api/cli.rst."
            )
