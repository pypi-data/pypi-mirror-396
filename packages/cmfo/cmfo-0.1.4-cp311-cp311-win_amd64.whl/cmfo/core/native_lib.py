import ctypes
import os
import glob
import sys
import sysconfig

class NativeLib:
    _instance = None
    
    @staticmethod
    def _find_library():
        # Heuristic: verify if we are running in source or installed
        # Look for .pyd or .so in the same directory (inplace build) or site-packages
        
        # 1. Look in current directory (if built inplace)
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Common patterns for setuptools build
        # cmfo_core_native.cp39-win_amd64.pyd
        pattern = "cmfo_core_native*" + sysconfig.get_config_var("EXT_SUFFIX") if sysconfig.get_config_var("EXT_SUFFIX") else "cmfo_core_native*"
        
        # Search up to package root
        # bindings/python/cmfo/core -> bindings/python/cmfo -> bindings/python -> build/lib...
        
        # Attempt to import it using importlib to find path?
        # But it's an extension module.
        try:
            import cmfo_core_native
            return cmfo_core_native.__file__
        except ImportError:
            pass

        # Fallback: Search in local build directory (development)
        # ../../../build/lib*
        root_search = os.path.join(curr_dir, "..", "..", "..", "build", "lib*", "cmfo_core_native*")
        matches = glob.glob(root_search)
        if matches:
            return matches[0]
            
        return None

    @staticmethod
    def get():
        if NativeLib._instance:
            return NativeLib._instance
            
        lib_path = NativeLib._find_library()
        if not lib_path:
            # Fallback for development if file is manually placed or compiled with --inplace
            # Check current folder
            root = os.path.dirname(os.path.abspath(__file__))
            matches = glob.glob(os.path.join(root, "cmfo_core_native*")) # Loose match
            if matches:
                lib_path = matches[0]
        
        if not lib_path:
            raise RuntimeError("Could not locate cmfo_core_native library. Did you run 'pip install .'? \nWarning: C++ Extension not found.")

        try:
            lib = ctypes.CDLL(lib_path)
        except OSError as e:
            # Windows specific: add directory to DLL path?
            raise RuntimeError(f"Could not load library at {lib_path}: {e}")

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
