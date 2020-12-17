# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from ..utilities import HistogramMatchingFilter


def test_HistogramMatchingFilter_inputs():
    input_map = dict(
        args=dict(
            argstr="%s",
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        histogramAlgorithm=dict(
            argstr="--histogramAlgorithm %s",
        ),
        inputBinaryVolume=dict(
            argstr="--inputBinaryVolume %s",
            extensions=None,
        ),
        inputVolume=dict(
            argstr="--inputVolume %s",
            extensions=None,
        ),
        numberOfHistogramBins=dict(
            argstr="--numberOfHistogramBins %d",
        ),
        numberOfMatchPoints=dict(
            argstr="--numberOfMatchPoints %d",
        ),
        outputVolume=dict(
            argstr="--outputVolume %s",
            hash_files=False,
        ),
        referenceBinaryVolume=dict(
            argstr="--referenceBinaryVolume %s",
            extensions=None,
        ),
        referenceVolume=dict(
            argstr="--referenceVolume %s",
            extensions=None,
        ),
        verbose=dict(
            argstr="--verbose ",
        ),
        writeHistogram=dict(
            argstr="--writeHistogram %s",
        ),
    )
    inputs = HistogramMatchingFilter.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value


def test_HistogramMatchingFilter_outputs():
    output_map = dict(
        outputVolume=dict(
            extensions=None,
        ),
    )
    outputs = HistogramMatchingFilter.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value