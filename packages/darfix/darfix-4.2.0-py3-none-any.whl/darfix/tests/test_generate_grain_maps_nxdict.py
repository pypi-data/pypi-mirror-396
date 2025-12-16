import tempfile

import h5py
import numpy
from silx.io.dictdump import dicttonx
from silx.io.nxdata import NXdata

from darfix.core.grainplot import MultiDimMomentType
from darfix.core.grainplot import OrientationDistData
from darfix.core.grainplot import generate_grain_maps_nxdict
from darfix.core.moment_types import MomentType

from .utils import createHDF5Dataset1D
from .utils import createHDF5Dataset3D


def test_generate_grain_maps_nxdict_1d():

    dset = createHDF5Dataset1D(numpy.random.rand(10, 10, 10))
    dset.find_dimensions()
    dset.apply_moments()
    nxdict = generate_grain_maps_nxdict(dset, None, None)

    for moment_type in MomentType:
        assert moment_type.value in nxdict["entry"]
        assert nxdict["entry"][moment_type.value][moment_type.value].shape == (10, 10)

    assert MultiDimMomentType.ORIENTATION_DIST.value not in nxdict["entry"]
    assert MultiDimMomentType.MOSAICITY.value not in nxdict["entry"]


def test_generate_grain_maps_nxdict_3d():
    dset = createHDF5Dataset3D(numpy.random.rand(5, 5, 5, 6, 6))
    dset.find_dimensions()
    dset.apply_moments()
    orientation_dist_data = OrientationDistData(dset, 0, 1, [0, 1], [0, 1], dset.zsum())
    mosa = numpy.zeros((10, 10))

    nxdict = generate_grain_maps_nxdict(dset, mosa, orientation_dist_data)

    for motor in ("motor1", "motor2", "motor3"):
        for moment_type in MomentType:
            assert moment_type.value in nxdict["entry"][motor]
            assert nxdict["entry"][motor][moment_type.value][
                moment_type.value
            ].shape == (6, 6)

    assert MultiDimMomentType.ORIENTATION_DIST.value in nxdict["entry"]
    assert MultiDimMomentType.MOSAICITY.value in nxdict["entry"]

    with tempfile.TemporaryFile() as f:
        dicttonx(nxdict, f)

        with h5py.File(f) as h5f:
            assert NXdata(
                h5f["entry"][MultiDimMomentType.ORIENTATION_DIST.value]["data"]
            ).is_image
            assert NXdata(
                h5f["entry"][MultiDimMomentType.ORIENTATION_DIST.value]["key"]
            ).is_image
            assert NXdata(h5f["entry"][MultiDimMomentType.MOSAICITY.value]).is_image
