"""
Data Component - Data processing and export.
"""

# Lazy imports
def export_data(*args, **kwargs):
    from curllm_core.data_export import export_data as _export
    return _export(*args, **kwargs)

def validate_result(*args, **kwargs):
    from curllm_core.validation_utils import should_validate as _validate
    return _validate(*args, **kwargs)

def store_result(*args, **kwargs):
    from curllm_core.result_store import store_result as _store
    return _store(*args, **kwargs)

__all__ = ['export_data', 'validate_result', 'store_result']
