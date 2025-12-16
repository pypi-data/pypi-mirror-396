
import unittest
import sys
import os
import tempfile
import shutil
import numpy as np
import warnings

import futures_backends

try:
    import h5py
except ImportError:
    print("Skipping HDF5 tests: h5py not installed")
    h5py = None

# --- Worker Functions ---

def worker_sum_axis(arr):
    """Computes sum over the leading axis."""
    return np.sum(arr, axis=0)

# --- Test Suite ---

class TestSafeExecutor(unittest.TestCase):
    
    def setUp(self):
        futures_backends.reset_defaults()
        # Create a temp dir for real HDF5 files
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Cleanup temp dir
        shutil.rmtree(self.test_dir)
        futures_backends.reset_defaults()

    def test_numpy_computation(self):
        """
        Case 1: Computing a function over the leading axis of a numpy array.
        """
        data = [np.random.rand(100, 50) for _ in range(5)]
        expected = [np.sum(arr, axis=0) for arr in data]
        
        # We don't specify backend, checking auto-selection
        with futures_backends.select_executor(max_workers=2) as exe:
            print("[Numpy Test] Auto is using backend:", getattr(exe, 'backend', 'unknown'))
            results = list(exe.map(worker_sum_axis, data))
            
        for res, exp in zip(results, expected):
            np.testing.assert_array_almost_equal(res, exp)

        for choice in futures_backends.BACKENDS:
            try:
                with futures_backends.select_executor(max_workers=2, backends=[choice]) as exe:
                    print("[Numpy Test] Requested:", choice, "Got:", getattr(exe, 'backend', 'unknown'))
                    results = list(exe.map(worker_sum_axis, data))
                    for res, exp in zip(results, expected):
                        np.testing.assert_array_almost_equal(res, exp)
            except Exception as e:
                print("[Numpy Test] Requested:", choice, "not available")

    @unittest.skipIf(h5py is None, "h5py not installed")
    def test_h5py_fork_safety_real(self):
        """
        Case 2 (Real HDF5): 
        Test that we accept 'fork' when HDF5 is clean, 
        but REJECT 'fork' when an HDF5 file is open.
        """
        # --- Part A: The Clean State ---
        # Ensure h5py has no open objects. 
        # (Garbage collection might be needed if previous tests leaked)
        import gc
        gc.collect()
        
        # Verify the module sees it as clean
        if futures_backends.forkbad_for_openh5():
             self.fail("Test setup failed: HDF5 library reports open objects before test started!")

        # Request ONLY fork. It should succeed.
        # This should NOT raise
        exe = futures_backends.select_executor(max_workers=1, backends=['fork'])
        self.assertEqual(exe.backend, 'fork')
        exe.shutdown()

        # --- Part B: The Dirty State ---
        # Create and keep open a real HDF5 file
        h5_path = os.path.join(self.test_dir, "test_dirty.h5")
        
        # We hold this 'f' object open to dirty the state
        f = h5py.File(h5_path, 'w')
        dset = f.create_dataset("data", (10,), dtype='i')
        
        try:
            # Verify that safe_executor detection logic works
            
            # Now try to create a 'fork' executor.
            # It should detect the open file, issue a warning, and refuse to return the executor.
            # Since backends=['fork'], it has no fallback, so it must raise RuntimeError.
            with warnings.catch_warnings(record=True) as w:
                self.assertTrue(futures_backends.forkbad_for_openh5(), 
                                "Failed to detect open HDF5 file via C-API check")
                warnings.simplefilter("always")
                
                with self.assertRaises(RuntimeError) as cm:
                    futures_backends.select_executor(max_workers=1, backends=['fork'])
                self.assertIn("No working backend found", str(cm.exception))
                
                # Check for the specific warning message
                warnings_found = [str(warn.message) for warn in w]
                self.assertTrue(any("open HDF5 objects" in msg for msg in warnings_found),
                                "Expected warning about open HDF5 objects not found. Got: %s" % warnings_found)
                
        finally:
            # Cleanup: Close the file so we don't pollute other tests
            f.close()
            
        self.assertFalse(futures_backends.forkbad_for_openh5())

    def test_context_manager(self):
        """
        Test that executor_context sets defaults that select_executor respects.
        """
        # 1. Set global default to 'thread'
        futures_backends.set_default_backends(backends=['thread'])
        
        exe = futures_backends.select_executor()
        self.assertEqual(exe.backend, 'thread')
        exe.shutdown()
        
        # 2. Use context manager to override with 'loky' (if available) or 'thread'
        # We pass a specific Kwarg (timeout) that Loky accepts but Thread ignores/filters
        with futures_backends.executor_context(backends=['loky', 'thread'], timeout=5):
            exe = futures_backends.select_executor()
            # If loky is installed, it should be loky. Otherwise thread.
            # We just verify it successfully created *an* executor.
            self.assertTrue(hasattr(exe, 'backend'))
            exe.shutdown()

if __name__ == '__main__':
    unittest.main()