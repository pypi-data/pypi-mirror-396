#!/usr/bin/env python

"""Console script for ibdpainting."""

import argparse
from ibdpainting import __version__

def main():
    parser = argparse.ArgumentParser(description='ibdpainting')

    parser.add_argument('-i', '--input',
        help='Path to an HDF5 file containing genotype data for one or more samples to check. This should be the output of allel.vcf_to_hdf5().'
        )
    parser.add_argument('-n', '--sample_name',
        help ='Sample name for the individual to check. This must be present in the samples in the input file.'
    )
    parser.add_argument('-r', '--reference',
        help="Path to an HDF5 file containing genotype data for a panel of reference individuals to compare the input indivual against. This should be the output of allel.vcf_to_hdf5()."
    )
    parser.add_argument('-w', '--window_size',
        type=int, default=500000,
        help="Integer window size in base pairs. Defaults to 500000 bp."
    )
    parser.add_argument('--expected_match',
        help="Optional list of sample names in the reference panel that are expected to be ancestors of the test individual.",
        nargs = "+", required=False
    )
    parser.add_argument('--outdir',
        help="Directory to save the output."
    )
    parser.add_argument('--keep_ibd_table', 
        help="If set, write an intermediate text file giving genetic distance between the crossed individual and each candidate at each window in the genome. Defaults to False, because these can be quite large.",
        default=False,
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument('--max_to_plot', 
        help="Optional number of the best matching candidates to plot so that the HTML files do not get too large and complicated. Ignored if this is more than the number of samples. Defaults to 20.",
        type=int, default = 10
    )
    parser.add_argument('--interactive',
        help="If set, save the output plot as an interactive HTML plot including information on candidates within the plot.",
        default=True,
        action=argparse.BooleanOptionalAction
        )
    parser.add_argument('--height',
        help="Height in pixels of the output PNG file. Defaults to 675.",
        default=675
        )
    parser.add_argument('--width',
        help="Height in pixels of the output PNG file. Defaults to 900.",
        default=900)
    parser.add_argument('--plot_heterozygosity',
        help="If set, plot the heterozygosity of the test individual in the output plot.",
        default=True,
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument('--version',
        action='version',
        version=f'%(prog)s {__version__}'
        )
    
    args = parser.parse_args()

    # Only import and run analysis if actually needed
    if len(vars(args)) > 1:  # If there are actual arguments besides --help
        run_analysis(args)
    else:
        parser.print_help()

def run_analysis(args):
    import os
    
    from ibdpainting.ibd_table import ibd_table
    from ibdpainting.ibd_scores import ibd_scores
    from ibdpainting.plot_ibd_table import plot_ibd_table
    
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)

    # Data frame of IBD at all positions across the genome, and the plot of this
    itable = ibd_table(args.input, args.reference, args.sample_name, args.window_size)
    
    print("Calculating the ibd_scores table.")
    scores = ibd_scores(itable)
    scores.to_csv( args.outdir + "/" + args.sample_name + "_ibd_scores.csv", index=False)
       
    print("Creating the plot.")
    fig = plot_ibd_table(
        itable,
        args.sample_name,
        args.expected_match,
        args.max_to_plot,
        args.plot_heterozygosity
        )
    png_out = args.outdir + "/" + args.sample_name + "_plot_ibd.png"
    print(f"Writing to {png_out}")
    fig.write_image(
        png_out,
        height = args.height, width = args.width
        )
    
    if args.interactive:
        html_out = args.outdir + "/" + args.sample_name + "_plot_ibd.html"
        print(f"Writing an interactive plot to {html_out}.")
        fig.write_html(args.outdir + "/" + args.sample_name + "_plot_ibd.html")
                
    if args.keep_ibd_table:
        itable_path = args.outdir + "/" + args.sample_name + "_ibd_table.csv"
        print(f"Writing the full ibd_table to {itable_path}")
        itable.to_csv(itable_path, index=False)
    

if __name__ == '__main__':
    main()
