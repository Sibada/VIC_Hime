import numpy as np
cimport numpy as np
from libc.math cimport pow
from libc.math cimport isnan

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

########################################################################################################################
#
# Inverse Distance Weight itp_c.
#
########################################################################################################################
def idw(np.ndarray[np.float64_t, ndim=2] data, np.ndarray[np.float64_t, ndim=2] coords,
        np.ndarray[np.float64_t, ndim=2] grids, DTYPE_t idp=2.0, DTYPE_t maxd=-1.0, int maxp=-1):

    cdef int nstns = coords.shape[0]
    cdef int ngrids = grids.shape[0]
    cdef int ndays = data.shape[0]

    cdef np.ndarray[np.float64_t, ndim=1] weight = np.zeros(nstns, dtype=DTYPE)
    cdef np.ndarray[np.int32_t, ndim=1] order = np.zeros(nstns, dtype=np.int32)

    cdef np.ndarray[np.float64_t, ndim=2] itp_data = np.zeros([ndays, ngrids], dtype=DTYPE)
    cdef double cx
    cdef double cy

    cdef double minw

    cdef double dp
    cdef double dis2

    cdef double value = 0.0
    cdef double value_b = 0.0
    cdef np.float64_t itpv

    cdef int c, s, d, i, j, key, p, ss

    for c in range(ngrids):
        cx = grids[c, 0]
        cy = grids[c, 1]
        for s in range(nstns):
            dis2 = (cx - coords[s, 0]) * (cx - coords[s, 0]) + \
                   (cy - coords[s, 1]) * (cy - coords[s, 1])
            if dis2 <= 1e-10:
                for ss in range(nstns):
                    weight[ss] = 0.0
                weight[s] = 1.0
                break
            weight[s] = 1.0 / ((cx - coords[s, 0]) * (cx - coords[s, 0]) +
                               (cy - coords[s, 1]) * (cy - coords[s, 1]))

        # Correct idp.
        if maxd > 0.0:
            minw = 1.0 / (maxd * maxd)
            for s in range(nstns):
                if weight[s] < minw:
                    weight[s] = 0.0

        if idp != 2.0:
            dp = idp / 2.0
            for s in range(nstns):
                weight[s] = pow(weight[s], dp)

        # Insertion sort to get the rank order of weights.
        for i in range(nstns):
            order[i] = i

        for i in range(nstns):
            key = order[i]
            j = i
            while j > 0 and weight[order[j-1]] < weight[key]:
                order[j] = order[j-1]
                j -= 1
            order[j] = key

        for d in range(ndays):
            value = 0.0
            value_b = 0.0
            p = 0
            for s in range(nstns):
                if p >= maxp > 0:
                    break
                itpv = data[d, order[s]]
                if isnan(itpv):
                    continue
                value += data[d, order[s]] * weight[order[s]]
                value_b += weight[order[s]]
                p += 1

            if value_b == 0.0:
                value = 0.0
            else:
                value = value / value_b

            itp_data[d, c] = value

    return itp_data