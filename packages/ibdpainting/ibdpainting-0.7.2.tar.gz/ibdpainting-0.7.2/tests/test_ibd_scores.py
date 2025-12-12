import ibdpainting as ip
import numpy as np


input = 'tests/test_data/panel_to_test.hdf5'
reference = 'tests/test_data/reference_panel.hdf5'
ref_vcf = 'tests/test_data/reference_panel.hdf5'
chr1 = 'tests/test_data/reference_panel_chr1.hdf5'

ibd = ip.ibd_table(
    input=input,
    reference=reference,
    sample_name='S2.06.002',
    window_size=1000
)

def test_ibd_scores_works():
    """Test basic functionality of ibd_scores
    """
    
    scores = ip.ibd_scores(ibd)
    assert scores.shape == (10,3)
    
def test_setting_rankthreshold_works():
    """Check that ibd_scores works when you mess with rank_threshold,
    """
    assert ip.ibd_scores(ibd, rank_threshold=1).shape == (1,3)
    assert ip.ibd_scores(ibd, rank_threshold=3).shape == (6,3)
    assert ip.ibd_scores(ibd, rank_threshold=4).shape == (10,3)
    assert ip.ibd_scores(ibd, rank_threshold=100).shape == (10,3)

def test_ibd_scores_propogates_NA():
    """
    Test that missing values inhereited from geneticDistance as -9 are
    propogated as NaN
    """
    ibd = ip.ibd_table(
        input=input,
        reference=reference,
        sample_name='S2.06.002',
        window_size=1000
    )
    # Set values for 1158 as missing
    ibd['1158'] = -9
    ibd = ibd.replace(-9, np.nan)
    
    scores = ip.ibd_scores(ibd)
    
    assert all(
        scores.loc[scores['parent1'] == "1158"]['min_IBD'].isna()
    )
