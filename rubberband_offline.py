import ctypes,numpy as np,sys
lib=ctypes.CDLL('libffmpeg_dummy' if False else '/usr/lib/x86_64-linux-gnu/librubberband.so.2')
lib.rubberband_new.restype=ctypes.c_void_p
lib.rubberband_new.argtypes=[ctypes.c_uint,ctypes.c_uint,ctypes.c_int,ctypes.c_double,ctypes.c_double]
for n in ['rubberband_set_expected_input_duration','rubberband_study','rubberband_process','rubberband_retrieve','rubberband_available','rubberband_delete','rubberband_set_max_process_size']: pass
OPT_OFFLINE=0; ENGINE_FINER=0x20000000; WINDOW_SHORT=0x100000; PHASE_INDEP=0x2000; TRANS_CRISP=0
def stretch(x,sr,tempo,opts=ENGINE_FINER):
    h=lib.rubberband_new(sr,1,opts,1.0/tempo,1.0)
    lib.rubberband_set_expected_input_duration.argtypes=[ctypes.c_void_p,ctypes.c_uint]
    lib.rubberband_set_expected_input_duration(ctypes.c_void_p(h),len(x))
    lib.rubberband_study.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),ctypes.c_uint,ctypes.c_int]
    lib.rubberband_process.argtypes=lib.rubberband_study.argtypes
    lib.rubberband_available.argtypes=[ctypes.c_void_p]; lib.rubberband_available.restype=ctypes.c_int
    lib.rubberband_retrieve.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),ctypes.c_uint]; lib.rubberband_retrieve.restype=ctypes.c_uint
    x=np.ascontiguousarray(x,dtype=np.float32)
    B=1024; out=[]
    def run(fn):
        for i in range(0,len(x),B):
            blk=np.ascontiguousarray(x[i:i+B]); p=ctypes.cast(blk.ctypes.data,ctypes.POINTER(ctypes.c_float)); pp=(ctypes.POINTER(ctypes.c_float)*1)(p)
            fn(ctypes.c_void_p(h),pp,len(blk),1 if i+B>=len(x) else 0)
            if fn is lib.rubberband_process: drain()
    def drain():
        while True:
            n=lib.rubberband_available(ctypes.c_void_p(h))
            if n<=0: break
            buf=np.zeros(n,dtype=np.float32); p=ctypes.cast(buf.ctypes.data,ctypes.POINTER(ctypes.c_float)); pp=(ctypes.POINTER(ctypes.c_float)*1)(p)
            got=lib.rubberband_retrieve(ctypes.c_void_p(h),pp,n); out.append(buf[:got])
    run(lib.rubberband_study); run(lib.rubberband_process); drain()
    lib.rubberband_delete.argtypes=[ctypes.c_void_p]; lib.rubberband_delete(ctypes.c_void_p(h))
    return np.concatenate(out)
