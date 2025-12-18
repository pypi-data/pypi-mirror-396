# SPECIESFINDER

The SpeciesFinder tool identifies species from raw sequencing reads (FASTQ) or assembled genomes (FASTA) by comparing them against a k-mer database generated using the KMA program. It reports the best matching species, along with additional taxonomic information if that option is selected.

## From KmerFinder to SpeciesFinder - Migration guide

KmerFinder has undergone a major overhaul, and we are introducing a new and improved tool: **SpeciesFinder**.

The goal of this update is to improve the core functionality, stability, and long-term maintainability of the tool while preserving the underlying algorithm and user experience as much as possible.

### Why the change?

Legacy KmerFinder depended heavily on the ```-Sparse``` KMA flag. This mode skips full alignment and instead performs a sparse k-mer mapping where scoring is based on k-mer hits. While fast, this approach has limitations and reduces downstream compatibility with other workflows (e.g., phylogenetics).

SpeciesFinder replaces the sparse mapping mode with a more robust and reproducible approach:

* It uses KMA’s ```-mem_mode```, which bases ConClave scoring on mappings rather than full alignments—significantly reducing memory usage while maintaining accuracy.

* It also enables:

    * ```-nf``` — suppress creation of the fragment file

    * ```-na``` — suppress output of the alignment file (alignment is still performed internally)

    * ```-1t1``` — force each query to match to a single best template

This update not only improves performance and stability, but also enables future support for global phylogeny generation and other extensions.

### What has changed:

1. **Tool name** - SpeciesFinder
2. **Mapping strategy** - No more sparse k-mer mapping (```-Sparse```). SpeciesFinder now uses ```-mem_mode```.
3. **Command-line interface** - The way the tool is executed has changed (see README usage section).
4. **Repository name change** - SpeciesFinder

### What remains the same:

1. **Versioning scheme**
2. **Algorithmic principles** — still based on KMA and ConClave scoring
3. **Overall purpose** — identification of species from FASTQ/FASTA input

## Installation

Setting up SpeciesFinder program
```bash
# Go to wanted location for SpeciesFinder
cd /path/to/some/dir
# Clone and enter the SpeciesFinder directory
git clone https://bitbucket.org/genomicepidemiology/speciesfinder.git
cd speciesfinder
```

Build Docker image from Dockerfile
```bash
# Build container
docker build -t speciesfinder .
# Run test
docker run --rm -it \
       --entrypoint=/test/test.sh speciesfinder
```

## Download and install SpeciesFinder database(s)

You can find instructions on how to download and install SpeciesFinder databases [here](https://bitbucket.org/genomicepidemiology/speciesfinder_db/src/master/)
```bash
# Go to the directory where you have stored the SpeciesFinder database
cd /path/to/database/dir
SpeciesFinder_DB=$(pwd)
```

## Dependencies
In order to run SpeciesFinder without using docker, Python 3.5 (or newer) should be installed.

#### KMA
Additionally KMA should be installed.
The newest version of KMA can be installed from here:
```url
https://bitbucket.org/genomicepidemiology/kma
```

## How to run

### Docker

### Non Docker

## Web-server

A webserver implementing the methods is available at the [CGE website](http://www.genomicepidemiology.org/) and can be found here:
http://cge.cbs.dtu.dk/services/SpeciesFinder/

Citation
=======

When using the method please cite:

Benchmarking of Methods for Genomic Taxonomy. Larsen MV, Cosentino S,
Lukjancenko O, Saputra D, Rasmussen S, Hasman H, Sicheritz-Pontén T,
Aarestrup FM, Ussery DW, Lund O. J Clin Microbiol. 2014 Feb 26.
[Epub ahead of print]

Rapid whole genome sequencing for the detection and characterization of
microorganisms directly from clinical samples. Hasman H, Saputra D,
Sicheritz-Ponten T, Lund O, Svendsen CA, Frimodt-Møller N, Aarestrup FM.
J Clin Microbiol.  2014 Jan;52(1):139-46.

Rapid and precise alignment of raw reads against redundant databases with KMA Philip T.L.C. Clausen, Frank M. Aarestrup, Ole Lund.

License
=======


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.