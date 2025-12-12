# ibdpainting

`ibdpainting` is a Python tool to visually validate the identity of crossed individuals
from genetic data.

## Contents

- [ibdpainting](#ibdpainting)
  - [Contents](#contents)
  - [Premise](#premise)
  - [Installation](#installation)
  - [Input data files](#input-data-files)
    - [Filter SNPs](#filter-snps)
    - [Convert to HDF5](#convert-to-hdf5)
  - [Usage](#usage)
  - [Output and interpretation](#output-and-interpretation)
    - [Plot of genetic distances across the genome](#plot-of-genetic-distances-across-the-genome)
    - [Scores for each pair](#scores-for-each-pair)
    - [Optional output files.](#optional-output-files)
  - [Author information](#author-information)
  - [Contributing](#contributing)

## Premise

`ibdpainting` addresses the situation where you have multiple individuals
derived from a crosses between individuals in a reference panel, and you want to
verify that the crosses really are the genotype you think they are. Taking the
simple example of a biparental cross, you would expect an offspring of the F2 
generation or later to be a mosaic of regions that are identical by descent (IBD)
to either parent, potentially interspersed with heterozygous regions, depending
on the generation.
`ibdpainting` is a tool to visualise this mosaic pattern by 'painting' the
pattern of IBD across the genome.

For examples of the output and the interpretation of different patterns, see [the examples here](https://ellisztamas.github.io/assets/06_ibdpainting_results.html).

## Installation

Install with `pip`:
```
pip install ibdpainting
```

## Input data files

The program requires two HDF5 files created from VCF files:

* **Input panel**: An HDF5 file containing SNPs for the crossed individual(s).
This can contain multiple individuals, but the program will only work on one at
a time.
* **Reference panel**: An HDF5 file conataining SNP information for a panel of
reference candidate parents.

### Filter SNPs

`ibdpainting` works best if you make sure than the SNPs in the offspring and 
progeny genotype files have been filtered to have roughly matching SNP positions,
and that these SNPs are syntenic.
Below is an example of how to do this for *A. thaliana*.
This is not the only way, and may or may not be appropriate for other systems.

Download the annotation file `TAIR10_GFF3_genes.gff` giving positions of coding
genes in the *A. thaliana* reference strain:
```bash
genes=https://www.arabidopsis.org/download/file?path=Genes/TAIR10_genome_release/TAIR10_gff3/TAIR10_GFF3_genes.gff
wget -P $genes
```

Get a list of SNPs segregating in the progeny, and filter that list for
positions inside genes.
Here I'm starting from the progeny because I know that the VCF file for the
progeny has fewer SNPs than the parents, but in principle this ought to work 
if you start from the parents as well.

```bash
# Get a list of SNP positions in the VCF for the progeny
bcftools view --min-ac 160 progeny.vcf.gz | 
    bcftools query -f"%CHROM\t%POS\n"  > progeny_snp_positions.txt
# Convert to BED format. Positions are given as Chr, Position, Position +1
awk '{print $1"\t"$2"\t"$2+1}' progeny_snp_positions.txt > $progeny_snp_positions.bed

# Select only features labelled as coding genes in the GFF, and convert to BED
grep "Note=protein_coding_gene" TAIR10_GFF3_genes.gff | awk -F'\t' '{print $1"\t"$4"\t"$5}' > annotated_genes.bed

# Get only those SNPs that are inside genes.
# Bedtools intersect finds the SNPs inside genes, and awk reformats for bcftools
# Example output: "Chr1 6063"
bedtools intersect -a $all_snps_bed -b annotated_genes.bed -wb | \
awk -F'\t' '{print $1"\t"$2}' | \
bgzip > snps_in_genes.bed
```

Use `bcftools` to subset full VCF files for the progent and parents to only contain SNPs inside genes.
It is also recommended to remove variants with duplicate positions (usually where a SNP and indel occur at the same location).

```bash
# Subset the VCF file parents.vcf.gz
bcftools view \
    -R snps_in_genes.bed \
    -v snps \
    -O z  \
    -o parents_subset.vcf.gz \
    parents.vcf.gz

# Subset the VCF file for the progeny
bcftools view \
    -R snps_in_genes.bed \
    -v snps \
    -O z \
    -o progeny_subset.vcf.gz \
    progeny.vcf.gz
```

### Convert to HDF5

`ibdpainting` requires VCF files be converted to HDF5 format.
The reason for using HDF5 is that it allows for loading data in chunks,
which is much quicker than loading an entire VCF file into memory every time you
want to check a single sample.

I recommend creating this using
[vcf_to_hdf5](https://scikit-allel.readthedocs.io/en/latest/io.html#allel.vcf_to_hdf5)
from `scikit-allel` in Python. For example:

```python
import allel
allel.vcf_to_hdf5('example.vcf', 'example.h5', fields='*', overwrite=True)
```

## Usage

After installing, `ibdpainting` can be run as a command line tool as follows

```
ibdpainting \
    --input input_file.hdf5 \
    --reference reference_panel.hdf5 \
    --window_size 500000 \
    --sample_name "my_cross" \
    --expected_match "mother" "father" \
    --outdir path/to/output/directory
```

Explanation of the parameters:

* `--input`: HDF5 file containing the crossed individuals. See [above](#input-data-files).
* `--reference`: HDF5 file containing the reference panel. See [above](#input-data-files).
* `--window_size`: Window size in base pairs.
* `--sample_name`: Name of the crossed individual to compare to the reference 
panel. This must be present in the input file - you can check the original VCF file with something
like `bcftools query -l $input_vcf.vcf.gz | grep "my_cross"`.
* `--expected_match`: List of one or more expected parents of the test individual.
These names should be among the samples in the reference panel. Names should be
separated by spaces.
* `--outdir`: Path to the directory to save the output.

See the output of `ibdpainting --help` for additional optional arguments.
Notably, `--plot_heterozygosity` adds a line showing the proportion of SNPs 
called as heterozygous in each window.

## Output and interpretation

`ibdpainting` creates two files for every sample by default, with further 
optional outputs.

For examples of the output and the interpretation of different patterns, see [the examples here](https://ellisztamas.github.io/assets/06_ibdpainting_results.html).


### Plot of genetic distances across the genome

The main results is an image file with the name of the sample name followed
by `_ibd.png` file.
This shows the position of windows along each chromomosome along the x-axis, and
the genetic distance from the progeny to each candidate along the y-axis.
If a candidate parent is IBD to the progeny, points on the 
y-axis should be zero, genotyping errors notwithstanding.
Candidate parents given as expected parents will be shown with coloured lines.
The next-closest other candidates are shown in grey.

Here is an example of a plot for an F9 individual from a cross between lines
1317 and 6276.
You can see that either the genetic distance from the F9 to one of the parents
(the red and blue lines) are close to zero in every window.
This indicates that the parents are correct, and the F9 is homozygous for one or
the other parental genotype across the genome.
The grey lines are for other candidate parents, and none are a good match.

![](1317x6276_rep1_plot_ibd.png)

It can be helpful or distracting to also plot the proportion of heterozygous
calls (i.e. `0/1` and `1/0` in the VCF file) in the offsping.
This can be set with the flag `--plot_heterozygosity`.

### Scores for each pair

The `ibd_score.csv` file lists possible combinations of candidate parents
and a score for each.
The score for a single pair is calculated by the minimum distance between the
offspring and either candidate in each window, divided by the number of non-NA
windows.
Scores close to zero indicate a better match.
A good match will ideally be an order of magnitude better than the next pair.
Only scores for pairs with the 100 most likely candidates are shown.

Here is an example for the F9 plotted above.

```
1317    6276    0.0030699561146607466
1317    6268    0.017195874394020087
1317    6255    0.017893302923832646
1317    9442    0.02333797771181973
9443    1317    0.024855297212255677
1317    6252    0.0280539612936829
9446    1317    0.02823563843279412
1317    9476    0.03288825690896675
1317    7517    0.04401124788115839
```

The first two columns list candidate parents, and the third the score for each.
You can see that the pair 1317x6276 have an order-of-magnitude better score than
any other candidate pairing.

### Optional output files.

* `plot_ibd.html`: An optional interactive version of the `png` file. Roll over points to see which candidate is which. These files are about ten times larger than the `png` files. Disable with `--no-interactive`.
* `ibd_table.csv`: An optional text file giving genetic distances from the progeny individual to every candidate in every window. These files are typically big, so are not created by default. Enable with `--keep_ibd_table`.

## Author information

Tom Ellis

## Contributing

I will repeat the following from the [documentation](https://scikit-allel.readthedocs.io/en/stable/) for `scikit-allel`:

> This is academic software, written in the cracks of free time between other commitments, by people who are often learning as we code. We greatly appreciate bug reports, pull requests, and any other feedback or advice. If you do find a bug, we’ll do our best to fix it, but apologies in advance if we are not able to respond quickly. If you are doing any serious work with this package, please do not expect everything to work perfectly first time or be 100% correct. Treat everything with a healthy dose of suspicion, and don’t be afraid to dive into the source code if you have to. Pull requests are always welcome.
