# AUTO-GENERATED by tools/checkspecs.py - DO NOT EDIT
from ..model import MRISPreprocReconAll


def test_MRISPreprocReconAll_inputs():
    input_map = dict(
        args=dict(
            argstr="%s",
        ),
        copy_inputs=dict(),
        environ=dict(
            nohash=True,
            usedefault=True,
        ),
        fsgd_file=dict(
            argstr="--fsgd %s",
            extensions=None,
            xor=("subjects", "fsgd_file", "subject_file"),
        ),
        fwhm=dict(
            argstr="--fwhm %f",
            xor=["num_iters"],
        ),
        fwhm_source=dict(
            argstr="--fwhm-src %f",
            xor=["num_iters_source"],
        ),
        hemi=dict(
            argstr="--hemi %s",
            mandatory=True,
        ),
        lh_surfreg_target=dict(
            extensions=None,
            requires=["surfreg_files"],
        ),
        num_iters=dict(
            argstr="--niters %d",
            xor=["fwhm"],
        ),
        num_iters_source=dict(
            argstr="--niterssrc %d",
            xor=["fwhm_source"],
        ),
        out_file=dict(
            argstr="--out %s",
            extensions=None,
            genfile=True,
        ),
        proj_frac=dict(
            argstr="--projfrac %s",
        ),
        rh_surfreg_target=dict(
            extensions=None,
            requires=["surfreg_files"],
        ),
        smooth_cortex_only=dict(
            argstr="--smooth-cortex-only",
        ),
        source_format=dict(
            argstr="--srcfmt %s",
        ),
        subject_file=dict(
            argstr="--f %s",
            extensions=None,
            xor=("subjects", "fsgd_file", "subject_file"),
        ),
        subject_id=dict(
            argstr="--s %s",
            usedefault=True,
            xor=("subjects", "fsgd_file", "subject_file", "subject_id"),
        ),
        subjects=dict(
            argstr="--s %s...",
            xor=("subjects", "fsgd_file", "subject_file"),
        ),
        subjects_dir=dict(),
        surf_area=dict(
            argstr="--area %s",
            xor=("surf_measure", "surf_measure_file", "surf_area"),
        ),
        surf_dir=dict(
            argstr="--surfdir %s",
        ),
        surf_measure=dict(
            argstr="--meas %s",
            xor=("surf_measure", "surf_measure_file", "surf_area"),
        ),
        surf_measure_file=dict(
            argstr="--meas %s",
            extensions=None,
            xor=("surf_measure", "surf_measure_file", "surf_area"),
        ),
        surfreg_files=dict(
            argstr="--surfreg %s",
            requires=["lh_surfreg_target", "rh_surfreg_target"],
        ),
        target=dict(
            argstr="--target %s",
            mandatory=True,
        ),
        vol_measure_file=dict(
            argstr="--iv %s %s...",
        ),
    )
    inputs = MRISPreprocReconAll.input_spec()

    for key, metadata in list(input_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(inputs.traits()[key], metakey) == value


def test_MRISPreprocReconAll_outputs():
    output_map = dict(
        out_file=dict(
            extensions=None,
        ),
    )
    outputs = MRISPreprocReconAll.output_spec()

    for key, metadata in list(output_map.items()):
        for metakey, value in list(metadata.items()):
            assert getattr(outputs.traits()[key], metakey) == value