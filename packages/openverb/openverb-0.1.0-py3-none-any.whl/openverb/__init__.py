"""
OpenVerb - Helpers for working with OpenVerb verb libraries
Based on the OpenVerb specification v0.1
"""

import json
from typing import Dict, List, Any, Callable, Optional, Union
from pathlib import Path

__version__ = "0.1.0"


# Type aliases
VerbLibrary = Dict[str, Any]
Verb = Dict[str, Any]
VerbRegistry = Dict[str, Verb]
Action = Dict[str, Any]
ActionResult = Dict[str, Any]
VerbHandler = Callable[[Dict[str, Any]], ActionResult]


def load_library(source: Union[str, VerbLibrary, Path]) -> VerbLibrary:
    """
    Load a verb library from a JSON string, dict, or file path.
    
    Args:
        source: JSON string, dict, or Path to JSON file
        
    Returns:
        Loaded verb library dictionary
        
    Example:
        >>> library = load_library('{"namespace": "test", "verbs": [...]}')
        >>> library = load_library(Path('openverb.core.json'))
    """
    if isinstance(source, dict):
        return source
    elif isinstance(source, (str, Path)):
        if isinstance(source, str) and source.strip().startswith('{'):
            # It's a JSON string
            return json.loads(source)
        else:
            # It's a file path
            path = Path(source)
            with path.open('r', encoding='utf-8') as f:
                return json.load(f)
    else:
        raise TypeError(f"Unsupported source type: {type(source)}")


def build_registry(library: VerbLibrary) -> VerbRegistry:
    """
    Build a verb registry from a library for quick lookup.
    
    Args:
        library: Verb library dictionary
        
    Returns:
        Dictionary mapping verb names to verb definitions
        
    Example:
        >>> registry = build_registry(library)
        >>> verb_def = registry['create_item']
    """
    return {verb['name']: verb for verb in library['verbs']}


def validate_action(action: Action, verb_def: Optional[Verb]) -> Dict[str, Any]:
    """
    Validate an action against a verb definition.
    
    Args:
        action: Action dictionary with 'verb' and optional 'params'
        verb_def: Verb definition or None
        
    Returns:
        Dictionary with 'valid' boolean and optional 'error' message
        
    Example:
        >>> validation = validate_action(action, verb_def)
        >>> if not validation['valid']:
        ...     print(validation['error'])
    """
    if not verb_def:
        return {
            'valid': False,
            'error': f"Unknown verb: {action.get('verb')}"
        }
    
    # Check required params
    params = action.get('params', {})
    for param_name, param_def in (verb_def.get('params') or {}).items():
        if param_def.get('required') and param_name not in params:
            return {
                'valid': False,
                'error': f"Missing required param: {param_name}"
            }
    
    return {'valid': True}


def create_executor(library: VerbLibrary):
    """
    Create a simple executor with a handler registry.
    Similar to the examples in the OpenVerb repo.
    
    Args:
        library: Verb library dictionary
        
    Returns:
        Executor object with register() and execute() methods
        
    Example:
        >>> executor = create_executor(library)
        >>> executor.register('create_item', lambda params: {...})
        >>> result = executor.execute({'verb': 'create_item', 'params': {...}})
    """
    registry = build_registry(library)
    handlers: Dict[str, VerbHandler] = {}
    
    class Executor:
        def register(self, verb_name: str, handler: VerbHandler) -> None:
            """Register a handler for a verb."""
            if verb_name not in registry:
                raise ValueError(f"Verb '{verb_name}' not found in library")
            handlers[verb_name] = handler
        
        def execute(self, action: Action) -> ActionResult:
            """Execute an action."""
            verb = action.get('verb')
            verb_def = registry.get(verb)
            
            # Validate action
            validation = validate_action(action, verb_def)
            if not validation['valid']:
                return {
                    'verb': verb,
                    'status': 'error',
                    'error_message': validation['error']
                }
            
            # Get handler
            handler = handlers.get(verb)
            if not handler:
                return {
                    'verb': verb,
                    'status': 'error',
                    'error_message': f"No handler registered for verb: {verb}"
                }
            
            # Execute handler
            try:
                result = handler(action.get('params', {}))
                return result
            except Exception as e:
                return {
                    'verb': verb,
                    'status': 'error',
                    'error_message': str(e)
                }
        
        def get_registry(self) -> VerbRegistry:
            """Get the verb registry."""
            return registry.copy()
        
        def get_verbs(self) -> List[str]:
            """Get list of verb names."""
            return list(registry.keys())
        
        def get_verb(self, name: str) -> Optional[Verb]:
            """Get a specific verb definition."""
            return registry.get(name)
    
    return Executor()


def load_core_library() -> VerbLibrary:
    """
    Load the official openverb.core library.
    
    Returns:
        The openverb.core verb library
        
    Example:
        >>> core = load_core_library()
        >>> print(core['namespace'])  # 'openverb.core'
    """
    core_path = Path(__file__).parent / 'openverb.core.json'
    return load_library(core_path)


__all__ = [
    'load_library',
    'build_registry',
    'validate_action',
    'create_executor',
    'load_core_library',
    'VerbLibrary',
    'Verb',
    'VerbRegistry',
    'Action',
    'ActionResult',
    'VerbHandler',
]
