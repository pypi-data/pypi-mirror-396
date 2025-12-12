import h5py
import pandas as pd
import numpy as np
import warnings
import numpy.ma as ma
from tqdm import tqdm


from ibdpainting.find_matching_markers import find_matching_markers
# input    ="/groups/nordborg/projects/crosses/tom/03_processing/11_genotype_calls_pipeline/output/08_validation_pipeline/hdf5/test.hdf5"
# reference="/groups/nordborg/projects/crosses/tom/03_processing/11_genotype_calls_pipeline/output/08_validation_pipeline/hdf5/reference.hdf5"
# sample_name = "9408x9352_rep2"
# expected_match=['9408', '9352']
# window_size = 500000

def pairwise_distance(geno):
    """
    Calculate pairwise genetic distance between an input individual and all 
    reference individuals.

    The input individual is always the first in the list of samples. Genetic
    distance is the number of allelic differences at each locus between each
    pair, summed over all loci. The calculation is done using masked arrays to
    account for missing data.
    
    This actually returns one minus the genetic distances, so that perfect
    matches have a score of one.

    Returns
    =======
    Vector of one minus distances

    """
    masked_geno = ma.masked_array(geno, geno < 0)
    # Calculate differences at each locus
    per_locus_difference = abs(masked_geno.sum(2)[:,[0]] - masked_geno.sum(2)[:,1:]) / 2
    # Average over loci
    dxy = per_locus_difference.mean(0)
    
    return ma.filled(dxy, -9)


def get_heterozygosity(geno):
    """
    Calculate heterozygosity in the input individual.

    The calculation is done using masked arrays to account for missing data.

    Returns
    =======
    Float between zero and one.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        masked_geno = ma.masked_array(geno, geno < 0)
        per_locus_heterozygosity = masked_geno.sum(2)[:,0] == 1
        mean_heterozygosity = ma.filled(per_locus_heterozygosity.mean(), np.nan)
        
        return mean_heterozygosity

def genotype_calls_by_window(input_hdf5, ref_hdf5, chr, start, stop, matching_markers):
    """
    Extract a table of genotype calls for a single window.
    
    This indexes genotype calls from and entire HDF5 file using boolean arrays
    indexing chromosome, positions inside a window, and whether the SNPs are
    shared between the test and reference panels.
        
    Returns
    -------
    An NxMx2-dimensional array where
    - N is the number of SNPs in a single window
    - M is columns for the test individual followed by all reference
    - 2 indexes the two chromosomes.
    
    Missing data are coded as negative integers.
    """
    # Create a matrix of genotype data for the test and reference individuals.
    # Arrays of Booleans matching the current chromosome
    chr_ix_test = (input_hdf5['variants/CHROM'][:] == chr)
    chr_ix_ref  = (ref_hdf5['variants/CHROM'][:] == chr)
    # Arrays matching the current window.
    window_ix_test = (input_hdf5['variants/POS'][:] >= start) & (input_hdf5['variants/POS'][:] < stop)
    window_ix_ref  = (ref_hdf5['variants/POS'][:] >= start)   & (ref_hdf5['variants/POS'][:] < stop)
    # Match chromosome and window to shared SNPs
    input_ix_test = chr_ix_test & window_ix_test & matching_markers['input']
    input_ix_ref  = chr_ix_ref  & window_ix_ref  & matching_markers['ref']
    # Take shared SNPs in this window, for the test individual only.
    input_genotypes = input_hdf5['calldata/GT'][input_ix_test, matching_markers['sample_ix']]
    # Shared SNPs in this window for the whole test panel.
    ref_genotypes = ref_hdf5['calldata/GT'][input_ix_ref]
        
    if(ref_genotypes.shape[0] != input_genotypes.shape[0]):
        raise ValueError(f"The test panel at this window has {input_genotypes.shape[0]} loci , but the reference panel has {ref_genotypes.shape[0]}.")
    else:
        # Empty matrix to store genotype data.
        # The first row should contain genotypes for the test individual
        # Subsequent rows should contain genotypes for all reference indivdiduals.
        new_geno = np.empty((ref_genotypes.shape[0], ref_genotypes.shape[1] +1, 2), dtype=input_hdf5['calldata/GT'].dtype)
        new_geno[:, 0]  = input_genotypes
        new_geno[:, 1:] = ref_genotypes
    
    return new_geno

def ibd_table(input:str, reference:str, sample_name:str, window_size:int):
    """
    Compare allele sharing across the genome.

    Calculate genetic distance between a test individual and a panel of
    reference genomes.

    Parameters
    ==========
    input: str
        Path to an HDF5 file containing genotype data for one or more samples to
        test
    reference: str
        Path to an HDF5 file containing genotype data for a panel of reference
        individuals to compare the test individual against.
    sample_name: str
        Sample name for the individual to check.
        This must be present in the samples in the input HDF5 file.
    window_size: int
        Window size in base pairs.

    Returns
    =======
    DataFrame with a row for each window in the genome and a column for each 
    sample in the reference panel. Elements show genetic distance between the 
    test individual and each reference individual in a single window.
    """

    # Read in the data files
    input_hdf5 = h5py.File(input, mode='r')
    ref_hdf5  = h5py.File(reference, mode="r")
    
    # Identify markers that are shared between the test and reference panels
    matching_markers = find_matching_markers(
        input, reference, sample_name
    )
    
    # Vector of sample names for the reference panel
    ref_sample_names = [ x.decode('utf-8') for x in ref_hdf5['samples'][:]]
    # Header for the output dataframe
    genetic_distances_header = ['window','chr', 'start', 'stop'] + ref_sample_names + ['heterozygosity']
    
    # Empty dict to store genetic distances (vectors) and heterozygosity (floats)
    # Indexed by window_name
    genetic_distances = []
    for chr in np.unique(input_hdf5['variants/CHROM'][:]):
        print(f"Calculating genetic distances across {chr.decode('utf-8')}.")
        
        chr_size = ref_hdf5['variants/POS'][ref_hdf5['variants/CHROM'][:] == chr].max()
        start_positions = np.arange(0, chr_size, window_size)
        
        for start in tqdm(start_positions):
            stop  = start + window_size
            window = chr.decode('utf-8') + ":" + str(start) + "-" + str(stop)
            # Matrix of genotype calls
            geno = genotype_calls_by_window(input_hdf5, ref_hdf5, chr, start, stop,  matching_markers)
            # Vector of genetic distances from the test individual to every reference.
            distances = pairwise_distance(geno)
            # Float giving heterozygosity of the test individual
            heterozygosity = get_heterozygosity(geno)
            # Dataframe with a single row, giving window position, distances and heterozygosity
            genetic_distances.append(pd.DataFrame(
                [[window, chr.decode('utf-8'), start, stop] + distances.tolist() + [heterozygosity]],
                columns = genetic_distances_header
                )
            )
        
    # Create a single dataframe
    genetic_distances = pd.concat(genetic_distances)
    # Sort by chromosome and window position
    # This isn' really necessary here, but would be if I added multiprocessing later.
    genetic_distances = genetic_distances.sort_values(by=['chr', 'start'])
    
    # Column gymnastics to ensure we have columns 'window', then one col for each
    # reference individual, and 'heterozygosity'.
    genetic_distances = genetic_distances.drop(columns=['chr', 'start', 'stop'])
    
    input_hdf5.close()
    ref_hdf5.close()
    
    return genetic_distances

# ibd_tablex = ibd_table(input, reference, sample_name, window_size)
