import ctypes
import os
import glob
import sys
import sysconfig

class NativeLib:
    _instance = None
    
    @staticmethod
    def _find_library():
        # Heuristic to find the compiled extension
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(curr_dir, "..", "..")) # bindings/python
        
        # 1. Try standard import (if installed via pip)
        try:
            import cmfo_core_native
            return cmfo_core_native.__file__
        except ImportError:
            pass

        # 2. Search in local build directory (pip install -e . or python setup.py build_ext --inplace)
        # Patterns to check
        patterns = [
            # Inplace build in root
            os.path.join(root_dir, "cmfo_core_native*.pyd"), 
            os.path.join(root_dir, "cmfo_core_native*.so"),
            # Build directory
            os.path.join(root_dir, "build", "lib*", "cmfo_core_native*.pyd"),
            os.path.join(root_dir, "build", "lib*", "cmfo_core_native*.so"),
             # Subdirectory build?
             os.path.join(root_dir, "*", "cmfo_core_native*.pyd"),
        ]
        
        for pattern in patterns:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
                
        # 3. Last resort: check if it's in the same folder as this file (hack)
        matches = glob.glob(os.path.join(curr_dir, "cmfo_core_native*"))
        if matches:
            return matches[0]
            
        return None

    @staticmethod
    def get():
        if NativeLib._instance:
            return NativeLib._instance
            
        lib_path = NativeLib._find_library()
        if not lib_path:
            # Silent fallback? Or warning?
            # We want to know if it's missing when debugging
            if os.environ.get("CMFO_DEBUG"):
                print("WARNING: CMFO Native Engine not found. Using pure Python fallback.")
            return None

        try:
            # On Windows, we might need to add directory to DLL path, but usually full path works
            if os.name == 'nt' and sys.version_info >= (3, 8):
                 try:
                     os.add_dll_directory(os.path.dirname(lib_path))
                 except:
                     pass
            lib = ctypes.CDLL(lib_path)
        except OSError as e:
            if os.environ.get("CMFO_DEBUG"):
                 print(f"WARNING: Failed to load native lib at {lib_path}: {e}")
            return None

        # Define Signatures
        lib.Matrix7x7_Create.restype = ctypes.c_void_p
        lib.Matrix7x7_Destroy.argtypes = [ctypes.c_void_p]
        
        lib.Matrix7x7_SetIdentity.argtypes = [ctypes.c_void_p]
        
        lib.Matrix7x7_Multiply.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        
        lib.Matrix7x7_Apply.argtypes = [
            ctypes.c_void_p, 
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), # Input Real/Imag
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)  # Output Real/Imag
        ]

        lib.Matrix7x7_Evolve.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), # In/Out Vec Real/Imag
            ctypes.c_int # steps
        ]

        lib.Matrix7x7_BatchEvolve.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), # Batch In/Out
            ctypes.c_int, # batch_size
            ctypes.c_int  # steps
        ]

        NativeLib._instance = lib
        return lib
