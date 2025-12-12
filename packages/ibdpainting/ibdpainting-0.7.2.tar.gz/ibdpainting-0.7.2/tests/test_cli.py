import subprocess


input = 'tests/test_data/panel_to_test.hdf5'
reference = 'tests/test_data/reference_panel.hdf5'
ref_vcf = 'tests/test_data/reference_panel.hdf5'
chr1 = 'tests/test_data/reference_panel_chr1.hdf5'

def test_cli_version():
    result = subprocess.run(
        ['ibdpainting', '--version'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "ibdpainting" in result.stdout

"""
ibdpainting \
    --input tests/test_data/reference_panel.hdf5 \
    --reference tests/test_data/reference_panel.hdf5 \
    --sample_name 1158 \
    --window_size 1000 \
    --outdir tests/test_output \
    --expected_match 1158 \
    --no-interactive
"""