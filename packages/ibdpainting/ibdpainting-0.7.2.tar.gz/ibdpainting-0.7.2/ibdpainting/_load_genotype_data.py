import h5py
import numpy as np
from ibdpainting.geneticDistance import geneticDistance

def load_genotype_data(input: str, reference: str, sample_name: str) -> geneticDistance:
    """
    Import and merge test and reference data files.

    Import genotype data for one or more input samples and a panel of reference samples
    to compare to. Subset each so that the markers are really identical. Merge the
    arrays of genotype calls so that the data for the input appear first on the
    first axis of the genotype call arrays.

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

    Return
    ------
    An object of class geneticDistance.
    """
    # Read in the data files
    input_hdf5 = h5py.File(input, mode='r')
    ref_hdf5  = h5py.File(reference, mode="r")

    input_str_data = {
        'samples' : [ x.decode('utf-8') for x in input_hdf5['samples'][:] ],
        'chr'     : [ x.decode('utf-8') for x in input_hdf5['variants/CHROM'][:] ]
    }

    ref_str_data = {
        'samples' : [ x.decode('utf-8') for x in ref_hdf5['samples'][:] ],
        'chr'     : [ x.decode('utf-8') for x in ref_hdf5['variants/CHROM'][:] ]
    }

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
    which_SNPs_to_keep = { k : np.where(v)[0] for k,v in which_SNPs_to_keep.items()}
    print(f"{len(which_SNPs_to_keep)} markers are found in both the input and reference panels.")

    print("Concatenating the input and reference genotypes...")
    n_snps = len(matching_SNPs_in_both_files)
    n_samples = ref_hdf5['calldata/GT'].shape[1] + 1

    new_geno = np.empty((n_snps, n_samples, 2), dtype=input_hdf5['calldata/GT'].dtype)
    new_geno[:, 0] = input_hdf5['calldata/GT'][which_SNPs_to_keep['input'], sample_ix]
    new_geno[:, 1:] = ref_hdf5['calldata/GT'][which_SNPs_to_keep['ref']]
    print("Done.")

    # Vectors of chromosome and position labels.
    chr_vector = np.array(ref_str_data['chr'])[which_SNPs_to_keep['ref']]
    pos_vector = ref_hdf5['variants/POS'][:][which_SNPs_to_keep['ref']]

    print("Finished importing the data.")
    # Define an output before closing the Hdf5 file
    output = geneticDistance(
        samples = new_samples,
        chr = chr_vector,
        pos = pos_vector,
        geno = new_geno
    )

    ref_hdf5.close()

    return output