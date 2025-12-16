
from __future__ import print_function


"""
Futures interface

We want to write code that runs on various different parallel backends.
We want our code to be independent of the backend. It will import this
and get back an executor following the concurrent.futures interface.


with select_executor( ) as executor:
    futures = [executor.submit(func, arg) for arg in args]
    for future in as_completed(futures):
        _ = future.result()

# Logic for backend selection adapted from suggestions by Google Gemini.
# Some naming suggested by chatgpt
#
# The human blame for this is Jon Wright.
"""


"""
For pyslurmutils:

export SLURM_URL=http://slurm-api.yoursite.com:6820
export SLURM_TOKEN="$(scontrol token lifespan=3600)"
"""

import sys
import os
import warnings
import threading
import multiprocessing
from contextlib import contextmanager

# On python2.7 concurrent.futures is installed via our requirements:
try:
    import concurrent.futures
except ImportError:
    concurrent = None

DEFAULT_BACKENDS = ('loky', 'fork', 'thread')

# --- Configuration Context Handling ---
_local_config = threading.local()

def _get_config():
    """Ensure the thread has a configuration state."""
    if not hasattr(_local_config, 'backends'):
        _local_config.backends = DEFAULT_BACKENDS
        _local_config.kwargs = {}
    return _local_config

@contextmanager
def executor_context(backends=None, **kwargs):
    """
    Context manager to set default backends and inject constructor arguments.
    """
    conf = _get_config()
    old_backends = conf.backends
    old_kwargs = conf.kwargs.copy()
    
    if backends is not None:
        conf.backends = backends
    conf.kwargs.update(kwargs)
    try:
        yield
    finally:
        conf.backends = old_backends
        conf.kwargs = old_kwargs

def set_default_backends(backends=None, **kwargs):
    """Sets backend preference globally for the current thread."""
    conf = _get_config()
    if backends is not None:
        conf.backends = backends
    conf.kwargs.update(kwargs)

def reset_defaults():
    """Resets the current thread's configuration to baseline."""
    if hasattr(_local_config, 'backends'):
        del _local_config.backends
    if hasattr(_local_config, 'kwargs'):
        del _local_config.kwargs

# --- Helper to reduce Copy+Paste ---
def _filter_kwargs(kwds, allowed_keys):
    """Returns a new dict containing only keys present in allowed_keys."""
    return {k: v for k, v in kwds.items() if k in allowed_keys}

# --- Safety Checks ---
def forkbad_for_tbb():
    """Returns True if TBB is loaded (Fork Unsafe)."""
    maps_path = "/proc/%s/maps" % (os.getpid())
    if os.path.exists(maps_path):
        try:
            with open(maps_path, 'r') as f:
                content = f.read()
                if "libtbb" in content:
                    warnings.warn("Intel TBB is loaded, 'fork' backend is unsafe.")
                    return True
        except IOError:
            pass
    return False

def forkbad_for_openh5():
    """Returns True if HDF5 objects are open (Fork Unsafe)."""
    if 'h5py' in sys.modules:
        import h5py
        try:
            from h5py import h5f
            """
            "H5F_OBJ_FILE" — Return number of open file identifiers.
            "H5F_OBJ_DATASET" — Return number of open dataset identifiers.
            "H5F_OBJ_GROUP" — Return number of open group identifiers.
            "H5F_OBJ_DATATYPE" — Return number of open named datatype identifiers.
            "H5F_OBJ_ATTR" — Return number of open attribute identifiers.
            "H5F_OBJ_ALL" — Return number of all open object types.
            """
            check = h5f.OBJ_FILE | h5f.OBJ_DATASET | h5f.OBJ_GROUP | h5f.OBJ_ATTR
            count = h5f.get_obj_count(h5f.OBJ_ALL, check)
            if count > 0:
                warnings.warn("Found %d open HDF5 objects. 'fork' backend is unsafe." % count)
                return True
        except (ImportError, AttributeError):
            pass      
    return False

# --- Backend Implementations ---

def get_loky(kwds):
    """Returns the loky class and kwargs to create it."""
    # Check imports first
    try:
        from loky import ProcessPoolExecutor
    except ImportError:
        try:
            from joblib.externals.loky import ProcessPoolExecutor
        except ImportError:
            return None, None
            
    # Loky accepts specific extra args like timeout/kill_workers
    known = {'max_workers', 'initializer', 'initargs', 'timeout', 'kill_workers'}
    return ProcessPoolExecutor, _filter_kwargs(kwds, known)

def get_fork(kwds):
    """Standard multiprocessing via fork."""
    if forkbad_for_tbb() or forkbad_for_openh5():
        return None, None
        
    known = {'max_workers', 'initializer', 'initargs'}
    run_kwargs = _filter_kwargs(kwds, known)
    
    # Inject context if supported (Python 3+)
    if hasattr(multiprocessing, 'get_context'):
        try:
            run_kwargs['mp_context'] = multiprocessing.get_context('fork')
        except ValueError:
            # Fallback for systems without fork (e.g. Windows)
            return None, None
            
    return concurrent.futures.ProcessPoolExecutor, run_kwargs

def get_thread(kwds):
    """Standard ThreadPoolExecutor."""
    known = {'max_workers', 'initializer', 'initargs'}
    
    # Python < 3.7 ThreadPoolExecutor does NOT support initializer
    if sys.version_info < (3, 7):
        if kwds.get('initializer') is not None:
            warnings.warn("Initializer ignored for 'thread' backend (requires Python 3.7+)")
        known = {'max_workers'}
        
    return concurrent.futures.ThreadPoolExecutor, _filter_kwargs(kwds, known)

def get_forkserver(kwds):
    """Multiprocessing via forkserver."""
    if sys.version_info < (3, 4) or forkbad_for_tbb() or forkbad_for_openh5():
        return None, None
        
    known = {'max_workers', 'initializer', 'initargs'}
    run_kwargs = _filter_kwargs(kwds, known)
    
    if hasattr(multiprocessing, 'get_context'):
        try:
            run_kwargs['mp_context'] = multiprocessing.get_context('forkserver')
        except ValueError:
            return None, None
    else:
        return None, None
            
    return concurrent.futures.ProcessPoolExecutor, run_kwargs

def get_spawn(kwds):
    """Multiprocessing via spawn."""
    if sys.version_info < (3, 4):
        return None, None
        
    known = {'max_workers', 'initializer', 'initargs'}
    run_kwargs = _filter_kwargs(kwds, known)
    
    if hasattr(multiprocessing, 'get_context'):
        try:
            run_kwargs['mp_context'] = multiprocessing.get_context('spawn')
        except ValueError:
            return None, None
    else:
        return None, None

    return concurrent.futures.ProcessPoolExecutor, run_kwargs

def get_interpreters(kwds):
    if hasattr(concurrent.futures, 'InterpreterPoolExecutor'):
        known = {'max_workers', 'initializer', 'initargs', 'mp_context'}
        executor_cls = concurrent.futures.InterpreterPoolExecutor
        run_kwargs = _filter_kwargs(kwds, known)
        return executor_cls, run_kwargs
    return None, None
    
# Helper Map
BACKENDS = {
    'loky': get_loky,
    'thread': get_thread,
    'fork': get_fork,
    'forkserver': get_forkserver,
    'spawn': get_spawn,
    'interpreters': get_interpreters,
}

# --- Factory Function ---
def select_executor(max_workers=None, initializer=None, initargs=(), 
                    backends=None, **override_kwargs):
    """
    Factory that returns a concurrent.futures compatible Executor.
    Merges defaults from executor_context with arguments passed here.
    """
    if concurrent is None:
        raise ImportError("concurrent.futures module not found. Please 'pip install futures'")

    # 1. Resolve Configuration
    conf = _get_config()
    selected_backends = backends if backends is not None else conf.backends
    
    # 2. Merge Kwargs
    final_kwargs = conf.kwargs.copy()
    final_kwargs.update(override_kwargs)
    
    # Ensure core args are set
    final_kwargs['max_workers'] = max_workers
    # Only set initializer if explicitly provided, otherwise let backend decide defaults
    if initializer is not None:
        final_kwargs['initializer'] = initializer
        final_kwargs['initargs'] = initargs

    executor_cls = None
    clean_kwds = {}
    name = None
    
    # Copy list to consume safely
    mybackends = list(selected_backends)

    # 3. Selection Loop
    while executor_cls is None and len(mybackends) > 0:
        name = mybackends.pop(0)
        
        # Look up the handler function in the BACKENDS dict
        handler = BACKENDS.get(name)
        if handler is None:
            # If we don't know it, maybe it's a custom/future backend?
            # For now, just warn and skip
            warnings.warn("Unknown backend '%s' requested." % name)
            continue
            
        # Call the handler to get class + filtered kwargs
        executor_cls, clean_kwds = handler(final_kwargs)

    # 4. Instantiation
    if executor_cls is not None:
        try:
            obj = executor_cls(**clean_kwds)
            obj.backend = name
            return obj
        except TypeError:
            # Fallback: Retry without initializer if arguments caused crash
            # (Last ditch effort for weird Python version mismatches)
            if 'initializer' in clean_kwds:
                clean_kwds.pop('initializer')
                clean_kwds.pop('initargs')
                obj = executor_cls(**clean_kwds)
                obj.backend = name
                return obj
            raise

    raise RuntimeError("No working backend found from options: %s" % str(selected_backends))

__all__ = [
    "get_executor", 
    "executor_context", 
    "set_default_backend", 
    "reset_defaults", 
    "BACKENDS"
]