Cocoremover is a simple tool for the removal of contaminant contigs from bacterial genome assemblies. 

## How to use 🎬

1. Build a fresh, updated reference database (eg using 36 cores):

    `cocoremover -c 36 --makedb`
    
2. Run the decontamination of a genome (eg using 36 cores):

    `cocoremover -c 36 -i GCA_948938835.1.fna -t 1598 -d cocoremover.db`
    
The required parameter `-t`/`--taxid` is the species-level NCBI Taxonomy ID for the input genome assembly. Please use `cocoremover --help` to read the full user guide. 

Output files will be created: 

* `{assembly}.counts`: shows, for each contig, the number of genes for each detected species. If the species with the highest number of genes is different from the one specified with `--taxid`, then the contig is assumed as contaminant. 
* `{assembly}.CT.{ext}`: FASTA file containing contigs marked as contaminant.
* `{assembly}.OK.{ext}`: original genome assembly with the contaminating contigs removed.


## How to install ⚙️

    pip install cocoremover
    
Cocoremover has several dependencies that need to be satisfied beforehand. They are all easily installable through [conda](https://www.anaconda.com/docs/getting-started/miniconda/main)/[mamba](https://mamba.readthedocs.io/en/latest/). If dependencies are not found at the startup, the user will be notified.

* `diamond`: [GitHub](https://github.com/bbuchfink/diamond) - [Paper](https://doi.org/10.1038/s41592-021-01101-x) - [conda](https://anaconda.org/bioconda/diamond)
* `esearch`, `esummary`, `xtract`: [Link](https://www.ncbi.nlm.nih.gov/books/NBK179288/) - [conda](https://anaconda.org/bioconda/entrez-direct)
* `wget`: [conda](https://anaconda.org/conda-forge/wget) 
* `tar`: [conda](https://anaconda.org/conda-forge/tar)
* `parallel`: [Link](https://www.gnu.org/software/parallel/) - [conda](https://anaconda.org/conda-forge/parallel)
* `prodigal`: [GitHub](https://github.com/hyattpd/Prodigal) - [Paper](https://doi.org/10.1186/1471-2105-11-119) - [conda](https://anaconda.org/bioconda/prodigal)
* `gzip`: [conda](https://anaconda.org/conda-forge/gzip)


## How to cite ✍🏼

Lazzari G., Felis G. E., Salvetti E., Calgaro M., Di Cesare F., Teusink B., Vitulo N. _Gempipe: a tool for drafting, curating, and analyzing pan and multi-strain genome-scale metabolic models_. **mSystems**. December 2025. https://doi.org/10.1128/msystems.01007-25

If you use this tool in your work, remember to specify its version.