# Pyseter

Pyseter is a Python package for processing images before photo-identification. 

We expect that most people using Pyseter will be familiar with R, and completely new to Python. Regardless, we chose to release Pyseter as a Python package because it relies heavily on Pytorch, a deep learning library. If you're new to Python, please follow the steps under **Installation: No Python experience**. 

If you're already a Pythonista, or just already have Python and conda installed, proceed to **Installation: Python and conda already installed**.

## Installation: No Python experience

### Install conda 

Conda is an important tool for managing packages in Python. Unlike Python, R (for the most part) handles packages for you behind the scenes. Python requires a more hands on approach.

   - Download and install [Miniforge](https://conda-forge.org/download/) (a form of conda)

After installing, you can verify your installation by opening the **command line interface** (CLI), which will depend on your operating system. Are you on Windows? Open the "miniforge prompt" in your start menu. Are you on Mac? Open the Terminal application. Then, type the following command into the CLI and hit return. 

```bash
conda --version
```

You should see something like `conda 25.5.1`. Of course, Anaconda, miniconda, mamba, or any other form of conda will work too.

### Create a new environment

Then, you'll create an environment for the package will live in. Environments are walled off areas where we can install packages. This allows you to have multiple versions of the same package installed on your machine, which can help prevent conflicts. 

Enter the following two commands into the CLI:

``` bash
conda create -n pyseter_env
conda activate pyseter_env
```

Here, I name (hence the `-n`) the environment `pyseter_env`, but you can call it anything you like!

Now your environment is ready to go! Try installing your first package, pip. Pip is another way of installing Python packages, and will be helpful for installing PyTorch and Pyseter (see below). To do so, enter the following command into the CLI.

``` bash
conda install pip -y
```

Once this is working, you're ready to proceed to the next section.

## Installation: Python and conda already installed

### Install PyTorch

Installing PyTorch will allow users to extract features from images, i.e., identify individuals in images. This will be fast for users with an NVIDIA GPU or 16 GB Mac with Apple Silicon. **For all other users, extracting features from images will be extremely slow.** 

PyTorch installation can be a little finicky. I recommend following [these instructions](https://pytorch.org/get-started/locally/). Below is an example for Windows users. If you haven't already, open you're command line interface (e.g., the miniforge prompt). Then activate your environment before installing.

``` bash
conda activate pyseter_env
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```
PyTorch is pretty big (over a gigabyte), so this may take a few minutes.

### Install Pyseter

Now, install Pyseter. If you haven't already, activate your environment before installing.

``` bash
conda activate pyseter_env
pip3 install pyseter
```

Now you're ready to go! 

### AnyDorsal weights

Pyseter relies on the [AnyDorsal algorithm](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.14167) to extract features from images. The first time you use the `FeatureExtractor`, Pyseter will download the AnyDorsal weights from Hugging Face. The weights take up roughly 4.5 GB. As such, to use the `FeatureExtractor`, users must have enough storage space to accommodate the weights. 

## Getting Started: No Python Experience

### Install VS Code

Most users will interact with Pyseter via a Jupyter Notebook. There are many methods for opening, editing, running, and saving Jupyter Notebooks. We are personally biased towards VS Code. Of course, you are also welcome to use Jupyter Lab, or even Positron.

First, [download VS Code](https://code.visualstudio.com/download) from the webpage according to your operating system, then follow the installation instructions.

Open VS Code, then click "File -> Open Folder". Navigate to wherever you'd like to work, then click "New Folder." You can call this folder something like "learn-pyseter" or "pyseter-jobs". Open the new folder. Click "File -> New File" then select Jupyter Notebook. Click "Select Kernel" in the top right corner, select "Python environments" and then "pyseter_env", or whatever you named your environment. For more information, check out [this great overview](https://code.visualstudio.com/docs/datascience/jupyter-notebooks) of using Jupyter Notebooks in VS Code. 

Now you're ready to proceed to the next section. 

## Getting Started: Jupyter Notebook ready

Open a Jupyter Notebook and select the appropriate kernel (i.e., the environment you created above). Then, verify the Pyseter installation by running the following cell in your notebook.

``` python
import pyseter
pyseter.verify_pytorch()
```

If you're on a windows computer with an NVIDIA GPU, you should see something like

```
✓ PyTorch 2.7.1+cu126 detected
✓ CUDA GPU available: NVIDIA A30 MIG 2g.12gb
```

Once this is working, you're ready to check out the "General Overview" [notebook](https://github.com/philpatton/pyseter/blob/main/examples/general-overview.ipynb) in the examples folder of this repository! 

