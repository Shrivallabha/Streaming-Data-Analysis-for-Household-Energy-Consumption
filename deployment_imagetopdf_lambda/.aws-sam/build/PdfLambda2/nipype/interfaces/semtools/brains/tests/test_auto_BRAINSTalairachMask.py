# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from ..segmentation import BRAINSTalairachMask


def test_BRAINSTalairachMask_inputs():
    input_map = dict(
        args=dict(
            argstr="%s",
        ),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        expand=dict(
            argstr="--expand ",
        ),
        hemisphereMode=dict(
            argstr="--hemisphereMode %s",
        ),
        inputVolume=dict(
            argstr="--inputVolume %s",
            extensions=None,
        ),
        outputVolume=dict(
            argstr="--outputVolume %s",
            hash_files=False,
        ),
        talairachBox=dict(
            argstr="--talairachBox %s",
            extensions=None,
        ),
        talairachParameters=dict(
            argstr="--talairachParameters %s",
            extensions=None,
        ),
    )
    inputs = BRAINSTalairachMask.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value


def test_BRAINSTalairachMask_outputs():
    output_map = dict(
        outputVolume=dict(
            extensions=None,
        ),
    )
    outputs = BRAINSTalairachMask.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value