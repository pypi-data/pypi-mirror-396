"""The valid operations for the remodeling tools."""

from remodel.operations.factor_column_op import FactorColumnOp
from remodel.operations.factor_hed_tags_op import FactorHedTagsOp
from remodel.operations.factor_hed_type_op import FactorHedTypeOp
from remodel.operations.merge_consecutive_op import MergeConsecutiveOp

from remodel.operations.remove_columns_op import RemoveColumnsOp
from remodel.operations.reorder_columns_op import ReorderColumnsOp
from remodel.operations.remap_columns_op import RemapColumnsOp
from remodel.operations.remove_rows_op import RemoveRowsOp
from remodel.operations.rename_columns_op import RenameColumnsOp
from remodel.operations.split_rows_op import SplitRowsOp
from remodel.operations.summarize_column_names_op import SummarizeColumnNamesOp
from remodel.operations.summarize_column_values_op import SummarizeColumnValuesOp
from remodel.operations.summarize_definitions_op import SummarizeDefinitionsOp
from remodel.operations.summarize_sidecar_from_events_op import SummarizeSidecarFromEventsOp
from remodel.operations.summarize_hed_type_op import SummarizeHedTypeOp
from remodel.operations.summarize_hed_tags_op import SummarizeHedTagsOp
from remodel.operations.summarize_hed_validation_op import SummarizeHedValidationOp

#: Dictionary mapping operation names to their implementation classes.
#: Each key is a string operation name used in JSON specifications,
#: and each value is the corresponding operation class.
valid_operations = {
    "factor_column": FactorColumnOp,
    "factor_hed_tags": FactorHedTagsOp,
    "factor_hed_type": FactorHedTypeOp,
    "merge_consecutive": MergeConsecutiveOp,
    "remap_columns": RemapColumnsOp,
    "remove_columns": RemoveColumnsOp,
    "remove_rows": RemoveRowsOp,
    "rename_columns": RenameColumnsOp,
    "reorder_columns": ReorderColumnsOp,
    "split_rows": SplitRowsOp,
    "summarize_column_names": SummarizeColumnNamesOp,
    "summarize_column_values": SummarizeColumnValuesOp,
    "summarize_definitions": SummarizeDefinitionsOp,
    "summarize_hed_tags": SummarizeHedTagsOp,
    "summarize_hed_type": SummarizeHedTypeOp,
    "summarize_hed_validation": SummarizeHedValidationOp,
    "summarize_sidecar_from_events": SummarizeSidecarFromEventsOp,
}
