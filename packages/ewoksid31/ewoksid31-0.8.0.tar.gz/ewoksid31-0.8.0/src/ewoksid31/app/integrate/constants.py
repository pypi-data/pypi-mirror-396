FILE_EXTENSIONS = ".h5", ".hdf5", ".hdf", ".nx", ".nxs", ".nx5", ".nexus"

MONITOR_NAMES: tuple[str, str, str, str] = (
    "mondio",
    "scaled_detdio",
    "scaled_mondio",
    "srcur",
)

DETECTOR_NAMES: tuple[str, str, str, str, str] = (
    "p4",
    "p4_lima1",
    "p3",
    "de",
    "perkin",
)
INTEGRATION_METHODS: tuple[str, ...] = (
    "no_csr_cython",
    "bbox_csr_cython",
    "full_csr_cython",
    "no_csr_ocl_gpu",
    "bbox_csr_ocl_gpu",
    "full_csr_ocl_gpu",
    "no_histogram_cython",
    "bbox_histogram_cython",
    "full_histogram_ocl_gpu",
)
