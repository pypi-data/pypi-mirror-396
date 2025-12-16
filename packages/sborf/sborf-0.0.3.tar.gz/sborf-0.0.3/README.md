![logo](docs/_static/logo_small.png)

---

## About sborf



## Installation

Package installation should only take a few minutes with any of these methods (pip, source).

### Installing sborf with pip:

We suggest to create a local conda environment where to install sborf. it can be done with:

```sh
conda create -n sborf
```
and activated with

```sh
conda activate sborf
```

or

```sh
source activate sborf
```

We also suggest to install pytorch separately following the instructions from https://pytorch.org/get-started/locally/

```sh
pip install sborf
```

The procedure will install sborf in your computer.

### Installing sborf from source:

If you want to install sborf from this repository, you need to install the dependencies first.
First, install [PyTorch](https://pytorch.org/get-started/locally/) separately following the instructions from https://pytorch.org/get-started/locally/.

Then install the other required libraries:

```sh
pip install numpy scikit-learn requests
```

Finally, you can clone the repository with the following command:

```sh
git clone https://github.com/grogdrinker/sborf/
```

## Usage

the pip installation will install a script called sborf_standalone that is directly usable from command line (at least on linux and mac. Most probably on windows as well if you use a conda environemnt).

### Using the standalone
The script can take a fasta file or a sequence as input and provide a prediction as output

```sh
sborf_standalone AWESAMEPRTEINSEQENCEASINPT
```

or, for multiple sequences, do

```sh
sborf_standalone fastaFile.fasta
```

To write the output in a file, do

```sh
sborf_standalone fastaFile.fasta -o outputFilePath
```

### Using sborf into a python script

sborf can be imported as a python module

```python
from sborf.run_prediction import predict
proteinSeq1 = "ASDASDASDASDASDASDDDDASD"
proteinSeq2 = "ASDADDDDDDDDDDDDDASDASDDDDASD"
proteinSeq2 = "ASDADFFFFFFFFFDDDDDDDDFFFFFFFFFASD"
inputSequences = {"ID1":proteinSeq1,"ID2":proteinSeq2,"ID3":proteinSeq3}

sborf_output = predict(inputSequences) # which is a dict containig the predictions

```


## Help

For bug reports, features addition and technical questions please contact gabriele.orlando@kuleuven.be
