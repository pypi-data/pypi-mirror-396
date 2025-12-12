# `bedrock-ge` examples

This folder contains example notebooks that guide you how to use Bedrock's Geotechnical Engineering Python package `bedrock-ge`.

## How to run the example notebooks

The notebooks are available as [marimo](https://marimo.io/) (`.py` extension) as well as [Jupyter](https://jupyter.org/) notebooks (`.ipynb` extension). However, it is **STRONGLY** recommended to use the marimo notebooks, as they are more user-friendly and have [several other advantages over Jupyter notebooks](https://docs.marimo.io/#highlights).

Both the marimo notebooks as well as the Jupyter notebooks can be run online, i.e. remotely, or on your own computer, i.e. locally.

### marimo

marimo notebooks are normal Python files, and therefore have the `.py` extension.

#### Remotely: marimo playground

marimo notebooks on GitHub can directly be run remotely in the [marimo playground](https://docs.marimo.io/guides/publishing/playground/#open-notebooks-hosted-on-github). To open the notebooks in this repository:

1. Navigate to one of them, e.g.  
   The Kai Tak, Hong Kong AGS 3 example: [hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.py](https://github.com/bedrock-engineer/bedrock-ge/blob/main/examples/hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.py)
2. Copy the GitHub URL of the notebook you want to try, e.g.  
    https://github.com/bedrock-engineer/bedrock-ge/blob/main/examples/hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.py
3. Open a new tab and go to `marimo.app/<Ctrl + V the copied GitHub URL>`, e.g.
    https://marimo.app/https://github.com/bedrock-engineer/bedrock-ge/blob/dev/examples/hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.py

#### Locally: on your own computer

Running the marimo notebooks in this repo locally is very easy if you're using [`uv`](https://docs.astral.sh/uv/) to manage Python. In case you're not usinng `uv` to manage Python yet, make sure to give it a try! (INCLUDE A LINK TO BEDROCK DOCS ON HOW TO INSTALL `uv`.)

Managing Python with `uv` will save you many many headaches w.r.t. managing virtual environments, Python packages, etc. etc. etc. Probably the greatest thing about `uv` is that you don't really need to understand what a virtual environment is...

To run a marimo notebook from this repo locally:

1. Download the notebook
2. Open the terminal
3. Navigate to the directory where you downloaded the marimo notebook with `cd` (change directory). On Windows this could be:
   ```bash
   cd %USERPROFILE%\Downloads
   ```
4. Run the marimo notebook with:
   ```bash
   uvx marimo edit --sandbox marimo_notebook.py
   ```

### Jupyter

Jupyter notebooks have the `.ipynb` extension, which is short for Interactive Python NoteBook.

#### Remotely: Google Colab

1. Navigate to one of them, e.g.  
   The Kai Tak, Hong Kong AGS 3 example: [hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.ipynb](https://github.com/bedrock-engineer/bedrock-ge/blob/main/examples/hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.ipynb)
2. Copy the GitHub URL of the notebook you want to try, e.g.  
    https://github.com/bedrock-engineer/bedrock-ge/blob/main/examples/hk_kaitak_ags3/hk_kaitak_ags3_to_brgi_geodb.ipynb
3. Navigate to [colab.research.google.com](https://colab.research.google.com/)
4. Paste the GitHub URL in the GitHub > Enter a GitHub URL... field

#### Locally: on your own computer

How much do we need to go into detail on how to run a Jupyter Notebook?

I think that if people don't know how to run a Jupyter notebook they should simply use the marimo notebook. The only reason to not use marimo, is when a company uses some deployed Jupyter service like Google Colab, Jupyter Hub or something like that, in which case they should run the Jupyter notebook remotely.

## Eporting marimo notebooks to other formats

### Jupyter Notebook

```bash
marimo export ipynb --sandbox --sort top-down --include-outputs hk_kaitak_ags3_to_brgi_geodb.py -o hk_kaitak_ags3_to_brgi_geodb.ipynb
```

After or before exporting a marimo notebook to a Jupyter notebook, the cell with the import statements and the cell(s) with function definitions have to be moved to the top of the Jupyter notebook for it to work. Additionally, in order for Google Colab to be able to run the notebook, you need to install `bedrock-ge` and a few other Python libraries by adding the following cell to the very top of the Jupyter notebook:

```bash
! pip install bedrock-ge folium mapclassify marimo --quiet
```

### HTML WebAssembly (WASM)

```bash
marimo export html-wasm --sandbox --mode edit hk_kaitak_ags3_to_brgi_geodb.py -o output
```
