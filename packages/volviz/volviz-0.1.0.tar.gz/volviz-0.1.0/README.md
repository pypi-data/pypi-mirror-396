# VolViz 🧊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI version](https://badge.fury.io/py/volviz.svg)](https://badge.fury.io/py/volviz)

**VolViz** is a lightweight, interactive 3D volume slicer designed for Jupyter Notebooks. It allows researchers and developers to visualize 3D numpy arrays (such as MRI, CT scans, or scientific simulations) directly within their workflow without needing heavy external software.

## ✨ Features

* **Orthogonal Slicing:** View volumes in Sagittal (X), Coronal (Y), and Axial (Z) planes.
* **Anisotropic Spacing:** Correctly renders volumes with non-cubic voxels (e.g., thick medical slices).
* **Interactive Contrast:** Adjust Window/Level (brightness/contrast) in real-time.
* **Data Probe:** Hover over images to see exact `(x, y, z)` coordinates and voxel intensity values.
* **Multi-Volume Support:** Compare multiple volumes side-by-side (up to 3 per row).
* **Fluid Performance:** Built on `ipympl` for smooth, GPU-accelerated 2D rendering.

## 📦 Installation

```bash
pip install volviz
```

### From Source (Development)
If you have cloned this repository, navigate to the root folder and run:

```bash
pip install .
````

### Dependencies

VolViz requires the following packages (installed automatically):

  * `numpy`
  * `matplotlib`
  * `ipywidgets`
  * `ipympl` (Crucial for interactivity)

## 🚀 Quick Start

VolViz is designed to work inside **Jupyter Notebook**, **JupyterLab**, or **VS Code Notebooks**.

**Important:** You must use the `%matplotlib widget` magic command at the start of your notebook.

```python
# 1. Enable interactive backend
%matplotlib widget

import numpy as np
from volviz import VolumeSlicer

# 2. Create some dummy 3D data (X, Y, Z)
# Let's create a 30x30x50 volume
vol = np.random.rand(30, 30, 50)

# 3. Visualize
# If your voxels are cubes (1mm x 1mm x 1mm), no extra config needed:
slicer = VolumeSlicer(vol)
slicer.show()
```

### Handling Medical Data (Anisotropy)

If your data has non-cubic voxels (e.g., a CT scan with high resolution in X/Y but thick slices in Z), use the `spacing` parameter to ensure the aspect ratio is correct.

```python
# Example: 1mm resolution in X/Y, but 3mm slice thickness in Z
slicer = VolumeSlicer(
    volumes=my_medical_scan, 
    spacing=(1.0, 1.0, 3.0)  # (x_mm, y_mm, z_mm)
)
slicer.show()
```

## 🎮 Controls

  * **View Dropdown:** Switch between Sagittal, Coronal, and Axial views.
  * **Slice Slider:** Navigate through the volume depth.
  * **Contrast Slider:** Drag the handles to change the black/white cut-off points (Window/Level).
  * **Mouse Hover:** Move your mouse over any image to see the probe data at the bottom of the card.
  * **Zoom/Pan:** Use the toolbar buttons (left of the image) to zoom into specific regions.

## 📂 Examples

  * [**demo.ipynb**](https://github.com/RJPaneque/volviz/blob/main/examples/demo.ipynb): A walkthrough showing multiple volumes and anisotropy handling.

## ☁️ Running on Google Colab

Google Colab requires a specific setup to render interactive widgets correctly.

1.  **Install the package:**
    ```python
    !pip install volviz
    ```

2.  **Restart the Runtime:**
    If you see a `ValueError: Key backend: 'module://ipympl.backend_nbagg' is not a valid value...`, go to **Runtime > Restart Session**.

3.  **Enable Widgets & Run:**
    You must enable the custom widget manager **before** importing the library:

    ```python
    from google.colab import output
    output.enable_custom_widget_manager() # <--- REQUIRED for Colab

    %matplotlib widget
    import numpy as np
    from volviz import VolumeSlicer

    vol = np.random.rand(30, 30, 30)
    slicer = VolumeSlicer(vol)
    slicer.show()
    ```

## 🛠 Troubleshooting

**The plot is blank or not interactive:**
Ensure you have `ipympl` installed and the magic command active:

1.  Run `pip install ipympl`
2.  Add `%matplotlib widget` as the first cell in your notebook.
3.  **Restart your kernel** and refresh the page.

**I see "Error: Failed to display Jupyter Widget":**
If you are using JupyterLab, you may need to install nodejs or the widget extension:

```bash
jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-matplotlib
```

*(Note: In modern JupyterLab 3.0+, simply pip installing `ipympl` is usually enough).*

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.