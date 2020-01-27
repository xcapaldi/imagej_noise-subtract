# README

![Background subtraction](background-subtract.png?raw=true "Background subtraction")

This is a Python plugin for ImageJ/Fiji which implements an algorithm developed by Patrick Doyle's group at MIT. It performs a two-stage background removal on fluorescent microscopy data, particularly that of DNA. The algorithm is detailed (with small errors) in the supplementary information for the following journal article:

Revisiting the Conformation and Dynamics of DNA in Slitlike Confinement
Jing Tang, Stephen L. Levy, Daniel W. Trahan, Jeremy J. Jones, Harold G. Craighead, and Patrick S. Doyle
Macromolecules 2010 43 (17), 7368-7377
DOI: 10.1021/ma101157x

If you use this plugin to analyze data for publication, please cite this paper.

The algorithm itself has two steps. I've modified (corrected?) it from the original in the supplementary information. Be aware that the resulting image will be smaller by four pixels in both width and height due to the nature of the subtraction algorithm.

## Initial subtraction

The mean intensity of the pixels along the boundary of the image is subtracted from all the pixels in the image. In addition, the sample standard deviation (sigma) of the boundary pixels is calculated.

## Individual noise spot removal

Each pixel is iterated. The mean intensity of 8 pixels surrounding the target pixel in a 3x3 region is calcuated. The mean intensity of 16 pixels surrounding the target pixel in a 5x5 region is calculated. If either mean intensities are less than three times the sample standard deviation (sigma), the pixel is taken to be noise and set to an intensity of 0.

## Installation

In Gnu/Linux and Windows, place the noise_subtract.py file inside the Fiji.app/plugins folder (or any subfolder). In MacOSX go to the "Applications" folder in Finder, right-click on the Fiji icon and select "Show package contents" to find the plugins folder.

Then in Fiji go to Help -> Refresh Menus. You will have to restart Fiji and then the plugin will appear in the Plugins menu.

## TODO

Copy the metadata from the original image to the background subtracted image.
