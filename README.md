# ImageJ/Fiji Jython Plugin: Noise Subtraction

![Background subtraction](background-subtract.png?raw=true "Background subtraction")

This is a Python plugin for ImageJ/Fiji which implements an algorithm developed by Patrick Doyle's group at MIT.
It performs a two-stage background removal on fluorescent microscopy data, particularly that of DNA.
The algorithm is detailed in the supplementary information for the following journal article:

```BibTex
@article{tang-2010-revis-confor,
  author =       {Jing Tang and Stephen L. Levy and Daniel W. Trahan
                  and Jeremy J. Jones and Harold G. Craighead and
                  Patrick S. Doyle},
  title =        {Revisiting the Conformation and Dynamics of Dna in
                  Slitlike Confinement},
  journal =      {Macromolecules},
  volume =       43,
  number =       17,
  pages =        {7368-7377},
  year =         2010,
  doi =          {10.1021/ma101157x},
  url =          {https://doi.org/10.1021/ma101157x},
  DATE_ADDED =   {Mon Aug 17 22:44:34 2020},
}
```

If you use this plugin to analyze data for publication, please cite this paper.

The algorithm itself has two steps.
I've modified (corrected?) it from the original in the supplementary information.
Be aware that depending on the settings, the outermost pixels or two outermost pixels will be set to 0 as the boundary is assumed to be background.
For best results, crop your data such that no fluorescent information is crossing the borders of the image.

## Initial subtraction
The mean intensity of the pixels along the boundary of the image is subtracted from all the pixels in the image.
In addition, the sample standard deviation (sigma) of the boundary pixels is calculated.

## Individual noise spot removal
We iterate through each pixel of the image.
The mean intensity of 8 pixels surrounding the target pixel in a 3x3 region is calculated.
The mean intensity of 16 pixels surrounding the target pixel in a 5x5 region is calculated.
If either mean intensities are less than three times the sample standard deviation (sigma), the pixel is taken to be noise and set to an intensity of 0.

## Installation
In Gnu/Linux and Windows, place the `noise_subtract.py` file inside the `Fiji.app/plugins` folder (or any subfolder).
In MacOS go to the `Applications` folder in Finder, right-click on the Fiji icon and select `Show package contents` to find the plugins folder.

Then in Fiji go to `Help` -> `Refresh Menus`.
You will have to restart Fiji and then the plugin will appear in the Plugins menu.

## TODO
Copy the metadata from the original image to the background subtracted image.
