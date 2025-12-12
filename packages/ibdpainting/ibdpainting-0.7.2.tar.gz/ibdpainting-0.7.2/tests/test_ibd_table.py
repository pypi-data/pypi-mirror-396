import ibdpainting as ip


input = 'tests/test_data/panel_to_test.hdf5'
reference = 'tests/test_data/reference_panel.hdf5'
ref_vcf = 'tests/test_data/reference_panel.hdf5'
chr1 = 'tests/test_data/reference_panel_chr1.hdf5'

def test_ibd_table():
    ibd = ip.ibd_table(
        input=ref_vcf,
        reference=reference,
        sample_name='1158',
        window_size=1000
    )
    # Check the dataframe is the right shape
    assert ibd.shape == (202, 6)
    # Check that the column for the true parent is all zeroes or -9
    assert all(
        (ibd['1158'] == 0) | (ibd['1158'] == -9)
    )
    # Check that a non-parent are not all -9.
    assert any(ibd['8249'] != 0)

    # Heterozygosity should be between 0 and 1
    assert not any(ibd['heterozygosity'] < 0)
    assert not any(ibd['heterozygosity'] > 1)
