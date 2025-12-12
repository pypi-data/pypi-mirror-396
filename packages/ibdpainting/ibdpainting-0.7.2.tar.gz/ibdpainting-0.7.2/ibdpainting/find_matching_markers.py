import h5py
import numpy as np

def find_matching_markers(input: str, reference: str, sample_name: str) -> dict:
    """
    Prepare HDF5 files for further processing.

    Imports HDF5 files for the test and reference panels and run initial checks.
    This then compares the lists of SNPs in each panel and identifies those that
    are shared.

    Parameters
    ----------
    input : str
        Path to a an HDF5 file containing genotype data for one or more samples to check
    reference : str
        Path to a HDF5 file containing genotype data for a panel of reference individuals
        to compare the input indivual against.
    sample_name : str
        Sample name for the individual to check. This must be present in the samples
        in the input file.
    
    Returns
    -------
    A dictionary listing:
    samples : np.array
        A vector of strings giving the test individual and all reference
        individuals.
    chr : np.array
        Array of chromosome labels for shared SNPs
    pos : np.array
        Array of positions labels for shared SNPs
    """
    # Read in the data files
    input_hdf5 = h5py.File(input, mode='r')
    ref_hdf5  = h5py.File(reference, mode="r")

    # The HDF5 files contain byte strings
    # Convert them back to regular strings
    input_str_data = {
        'samples' : [ x.decode('utf-8') for x in input_hdf5['samples'][:] ],
        'chr'     : [ x.decode('utf-8') for x in input_hdf5['variants/CHROM'][:]]
    }
    ref_str_data = {
        'samples' : [ x.decode('utf-8') for x in ref_hdf5['samples'][:] ],
        'chr'     : [ x.decode('utf-8') for x in ref_hdf5['variants/CHROM'][:] ]
    }
    print(f"The test panel contains {len(ref_str_data['samples'])} samples and {len(ref_str_data['chr'])} loci.")
    print(f"The reference panel contains {len(input_str_data['samples'])} samples and {len(input_str_data['chr'])} loci.")

    if sample_name not in input_str_data['samples']:
        raise ValueError("The sample name is not in the list of samples in the input file.")
    else: 
        print(f"Sample {sample_name} identified correctly in the list of samples in the input file.")
        # Find the position of the individual to test
        sample_ix = np.where(
            [ sample_name == x for x in input_str_data['samples'] ]
            )[0][0]
        # Join vectors of sample names, with the test individual first
        new_samples = np.append(
            input_str_data['samples'][sample_ix], ref_str_data['samples']
            )

    # Check that contig labels match
    chr_labels = {
        'input' : np.unique(input_str_data['chr']),
        'ref'   : np.unique(ref_str_data['chr'])
    }
    if len(chr_labels['input']) != len(chr_labels['ref']):
        raise ValueError(
            "The number of unique contig labels do not match: the input an HDF5 has {}, but the reference panel has {}.".
            format( chr_labels['input'], chr_labels['ref'] )
        )
    elif any( chr_labels['input'] != chr_labels['ref'] ):
        raise ValueError(
            "Contig labels do not match between the input and reference files."
        )
    else:
        print("Contig labels seem to match between the input and reference panels.")

    # Make sure we only compare SNPs that are found in both datasets.
    # Concatenate chromosome labels and SNP positions
    snp_names = {
        'input' : [ str(chr) + ":" + str(pos) for chr,pos in zip(input_str_data['chr'], input_hdf5['variants/POS'][:]) ],
        'ref'   : [ str(chr) + ":" + str(pos) for chr,pos in zip(ref_str_data['chr'], ref_hdf5['variants/POS'][:]) ]
    }
    # Find the SNP position names that are common to both datasets
    matching_SNPs_in_both_files = set(set(snp_names['input']) & set(snp_names['ref']))
    which_SNPs_to_keep = {
        "input" : [ x in matching_SNPs_in_both_files for x in snp_names['input'] ],
        "ref"   : [ x in matching_SNPs_in_both_files for x in snp_names['ref'] ]
    }
    print(f"{len(matching_SNPs_in_both_files)} markers are found in both the input and reference panels.")

    output = {
        'sample_ix' : sample_ix,
        'input' : which_SNPs_to_keep['input'],
        'ref' : which_SNPs_to_keep['ref']
        }
    
    input_hdf5.close()
    ref_hdf5.close()

    return output
