import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output
from typing import List, Optional, Tuple, Union

class VolumeSlicer:
    """
    An interactive 3D volume visualizer for Jupyter Notebooks using ipympl.
    
    Features:
    - Orthogonal slicing (Sagittal, Coronal, Axial).
    - Correct aspect ratio handling for anisotropic spacing (e.g., CT/MRI).
    - Interactive Window/Level (Contrast) sliders per volume.
    - Mouse hover probe for coordinates and intensity values.
    - Responsive grid layout (max 3 volumes per row).

    Attributes:
        volumes (List[np.ndarray]): List of 3D numpy arrays (x, y, z).
        spacing (np.ndarray): Physical voxel spacing (x, y, z).
        names (List[str]): Volume display names.
        cmaps (List[str]): Colormaps for each volume.
        figsize (Tuple[int, int]): Size of individual subplot figures.
    """

    def __init__(
        self,
        volumes: Union[np.ndarray, List[np.ndarray]],
        names: Optional[List[str]] = None,
        cmaps: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (4, 4),
        spacing: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ):
        """
        Initialize the VolumeSlicer.

        Args:
            volumes: A single 3D numpy array or a list of 3D arrays.
                     Shape convention: (x, y, z).
            names: Optional list of names for the volumes.
            cmaps: Optional list of colormaps (e.g., 'gray', 'bone').
            figsize: Figure size (width, height) in inches.
            spacing: Voxel spacing in mm (x, y, z). Default is isotropic (1,1,1).
        """
        if isinstance(volumes, np.ndarray):
            self.vols = [volumes]
        else:
            self.vols = volumes

        # Basic validation
        if not all(v.ndim == 3 for v in self.vols):
            raise ValueError("All input volumes must be 3D numpy arrays.")

        self.names = names if names else [f"Vol {i+1}" for i in range(len(self.vols))]
        self.cmaps = cmaps if cmaps else ['gray'] * len(self.vols)
        self.figsize = figsize
        self.spacing = np.array(spacing)

        # Pre-calculate intensity ranges for contrast sliders
        self.ranges = [(np.nanmin(v), np.nanmax(v)) for v in self.vols]

    def _get_aspect_ratio(self, axis: int) -> float:
        """
        Calculates the visual aspect ratio based on physical spacing.
        
        Args:
            axis: 0 (Fixed X), 1 (Fixed Y), or 2 (Fixed Z).
        Returns:
            float: Aspect ratio (Height / Width) for Matplotlib.
        """
        sx, sy, sz = self.spacing
        
        # Axis 0 (Sagittal): Plane Y-Z. Height=Y, Width=Z.
        if axis == 0: return sy / sz
        # Axis 1 (Coronal): Plane X-Z. Height=X, Width=Z.
        if axis == 1: return sx / sz
        # Axis 2 (Axial): Plane X-Y. Height=X, Width=Y.
        if axis == 2: return sx / sy
        return 1.0

    def show(self):
        """
        Renders the interactive interface. 
        Note: Requires '%matplotlib widget' in the notebook.
        """
        # Close existing plots to avoid ghosting
        plt.close('all')
        plt.ioff()

        # --- 1. Global Controls ---
        axis_dropdown = widgets.Dropdown(
            options=[('Sagittal (Fix X)', 0), 
                     ('Coronal (Fix Y)', 1), 
                     ('Axial (Fix Z)', 2)],
            value=2, 
            description='View',
            layout=widgets.Layout(width='200px')
        )
        
        # Initialize slider based on Z-dimension of the first volume
        max_idx = self.vols[0].shape[2] - 1
        slice_slider = widgets.IntSlider(
            value=max_idx // 2, 
            min=0, max=max_idx, 
            description='Slice',
            layout=widgets.Layout(width='50%')
        )

        # --- 2. Build Volume Cards ---
        self.imgs = []
        self.figs = []
        self.contrast_sliders = []
        card_widgets = []

        for i, vol in enumerate(self.vols):
            # Create Figure
            fig = plt.figure(figsize=self.figsize)
            ax = fig.add_subplot(111)
            
            # Initial Plot (Axial placeholder)
            im = ax.imshow(
                vol[:, :, 0], 
                cmap=self.cmaps[i], 
                vmin=self.ranges[i][0], 
                vmax=self.ranges[i][1],
                origin='upper'
            )
            ax.set_title(self.names[i], fontsize=10, fontweight='bold', pad=8)
            ax.axis('off')
            
            # Smart Colorbar (matches image height)
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.ax.tick_params(labelsize=8)

            # Cleanup Matplotlib UI
            fig.canvas.header_visible = False
            fig.canvas.toolbar_visible = False
            fig.canvas.footer_visible = False
            fig.canvas.resizable = False 
            
            self.imgs.append(im)
            self.figs.append(fig)

            # Contrast Slider (Window/Level)
            vmin, vmax = self.ranges[i]
            contrast_slider = widgets.FloatRangeSlider(
                value=[vmin, vmax], 
                min=vmin, max=vmax,
                step=(vmax - vmin)/100 if vmax != vmin else 0.1,
                description='Contrast',
                continuous_update=False, 
                readout_format='.1f',
                layout=widgets.Layout(width='98%')
            )
            self.contrast_sliders.append(contrast_slider)
            
            # Probe Label
            probe_label = widgets.HTML(
                value="<div style='color:#999; font-size:11px; text-align:center'>Hover to probe</div>",
                layout=widgets.Layout(width='100%', height='20px')
            )

            # Mouse Hover Callback
            def create_hover_callback(volume, label, ax_ref):
                def hover(event):
                    if event.inaxes != ax_ref: return
                    try:
                        # Map 2D visual coords (col, row) to 3D volume coords (x, y, z)
                        c, r = int(event.xdata + 0.5), int(event.ydata + 0.5)
                        ax_idx, slc = axis_dropdown.value, slice_slider.value
                        
                        if ax_idx == 0:   x, y, z = slc, r, c
                        elif ax_idx == 1: x, y, z = r, slc, c
                        else:             x, y, z = r, c, slc

                        if (0 <= x < volume.shape[0] and 
                            0 <= y < volume.shape[1] and 
                            0 <= z < volume.shape[2]):
                            val = volume[x, y, z]
                            v_str = f"{val:.2f}" if isinstance(val, (float, np.floating)) else f"{val}"
                            label.value = (f"<div style='text-align:center; font-family:monospace; color:#333'>"
                                           f"XYZ:({x},{y},{z}) | Val:{v_str}</div>")
                        else:
                            label.value = "<div style='color:#ccc; text-align:center'>Out of bounds</div>"
                    except: pass
                return hover

            fig.canvas.mpl_connect('motion_notify_event', create_hover_callback(vol, probe_label, ax))
            plt.tight_layout()

            # Card Container
            card = widgets.VBox([
                contrast_slider,
                fig.canvas,
                probe_label
            ], layout=widgets.Layout(border='1px solid #ddd', padding='4px', margin='2px', align_items='center'))
            card_widgets.append(card)

        # --- 3. Update Logic ---
        def update_view(change=None):
            axis = axis_dropdown.value
            idx = slice_slider.value
            
            # Adjust slider limits for the new axis
            max_dim = self.vols[0].shape[axis] - 1
            if slice_slider.max != max_dim: slice_slider.max = max_dim
            if idx > max_dim: slice_slider.value = max_dim; idx = max_dim

            aspect = self._get_aspect_ratio(axis)

            for i, vol in enumerate(self.vols):
                # Extract Slice
                if axis == 0:   data = vol[idx, :, :]
                elif axis == 1: data = vol[:, idx, :]
                else:           data = vol[:, :, idx]
                
                self.imgs[i].set_data(data)
                self.imgs[i].set_clim(self.contrast_sliders[i].value)
                self.imgs[i].axes.set_aspect(aspect, adjustable='box')
                self.figs[i].canvas.draw_idle()

        # Link Events
        axis_dropdown.observe(update_view, names='value')
        slice_slider.observe(update_view, names='value')
        for s in self.contrast_sliders: s.observe(update_view, names='value')

        # --- 4. Final Grid Layout ---
        # Logic: Cap at 3 columns. If fewer volumes, match the number of volumes.
        n_cols = min(len(self.vols), 3)
        grid = widgets.GridBox(
            card_widgets,
            layout=widgets.Layout(
                grid_template_columns=f'repeat({n_cols}, 1fr)',
                grid_gap='10px',
                width='100%'
            )
        )
        
        display(widgets.VBox([
            widgets.HBox([axis_dropdown, slice_slider], layout=widgets.Layout(padding='0 0 10px 0')),
            grid
        ]))
        
        update_view()