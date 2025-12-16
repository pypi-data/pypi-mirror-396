#cython: language_level=3

cdef double[:] _scale(double[:] out, double[:] source, double fromlow, double fromhigh, double tolow, double tohigh, bint log)
cdef double[:] _scaleinplace(double[:] out, double fromlow, double fromhigh, double tolow, double tohigh, bint log)
cpdef list scale(list source, double fromlow=*, double fromhigh=*, double tolow=*, double tohigh=*, bint log=*)
cdef list _snap_pattern(list source, list pattern)
cdef list _snap_mult(list source, double mult)
cpdef list snap(list source, double mult=*, object pattern=*)
cpdef rotate(list l, int offset=*)
