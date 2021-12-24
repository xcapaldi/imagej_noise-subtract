# ImageJ/FIJI Jython Plugin: Noise Subtraction
# MIT - Copyright (c) 2018 Xavier Capaldi

import time
from ij import IJ, ImagePlus, ImageStack
from ij.process import FloatProcessor, ByteProcessor
from ij.gui import GenericDialog

# currently this plugin does not save the metadata from the
# original image (microscope metadata).

def get_options():
    """ Get user options. """

    gd = GenericDialog("Options")
    gd.addCheckbox("3x3 boundary region", True)
    gd.addCheckbox("5x5 boundary region", True)
    # change the multiple of the standard deviation that is used
    # as a cutoff for the subtraction
    gd.addNumericField("N * sigma cutoff", 3.00, 2) # 2 decimals
    gd.showDialog()
    # check if user canceled operation
    if gd.wasCanceled():
        return
    # pull options
    close = gd.getNextBoolean()
    far = gd.getNextBoolean()
    cutoff = gd.getNextNumber()
    return close, far, cutoff

def initial_subtract(pixels, width, height):
    """
    Find the mean and sample standard deviation of border
    pixels. Subtract the mean intensity from every pixel.
    Return the sample standard deviation.
    """

    boundary = [0.] * (height + height + width + width - 4)

    # top and bottom boundaries
    boundary[:width] = pixels[:width]
    boundary[width:2*width] = pixels[-width:]

    # left and right boundaries
    for r in range(height-2):
        boundary[(2*width)+(r*2)] = pixels[width*(r+1)]
        boundary[(2*width)+(r*2)+1] = pixels[(width*(r+2))-1]

    # mean of boundary pixels
    mean = sum(boundary) / len(boundary)

    # sample standard deviation (sigma) of intensity for boundary pixels
    stddev = (sum((p - mean) ** 2 for p in boundary) /
              (len(boundary) - 1)) ** 0.5
    
    # iterate through pixels and substract mean intensity
    # negative values are rounded up to zero
    for i, p in enumerate(pixels):
        pixels[i] = (abs(p - mean) + (p - mean)) / 2
        
    return stddev

def fringe_mask(mask, width, fringe_width):
    """
    Given a mask which is initially all 255 and some
    distance from the borders which should be set to 0,
    set the fringe to 0 from the border to that distance.
    """

    for i, _ in enumerate(mask):
        if i % width < fringe_width:
            mask[i] = 0
        elif i % width >= width - fringe_width:
            mask[i] = 0

    mask[:fringe_width*width] = [0]*(fringe_width*width)
    mask[-(fringe_width*width):] = [0]*(fringe_width*width) 
    
def init_mask(pixels, mask):
    """
    Mask pixels which are already 0 after the initial
    background subtraction.
    """
    
    for i, p in enumerate(pixels):
        if p <= 0:
            mask[i] = 0

def close_subtract(pixels, mask, width, cutoff, stddev):
    """
    Check 3x3 region surrounding each pixel not already masked
    and check if the mean intensity of those surrounding pixels
    is less than some multiple of the sample standard deviation
    of the boundary pixels. If this is the case, set the pixel
    mask to 0 to indicate it is a background pixel.
    
    O O O O O O O
    O O O O O O O
    O O X X X O O
    O O X P X O O
    O O X X X O O
    O O O O O O O
    O O O O O O O
    """

    # create empty array for the mean intensities of the close pixels
    close_spot = [0.] * 8

    for i, _ in enumerate(pixels):
        if mask[i] == 255:
            close_spot[:3] = pixels[i-width-1:i-width+2]
            close_spot[3] = pixels[i-1]
            close_spot[4] = pixels[i+1]
            close_spot[5:] = pixels[i+width-1:i+width+2]
            if sum(close_spot)/8 < cutoff * stddev:
                mask[i] = 0
        else:
            pass

    return

def far_subtract(pixels, mask, width, cutoff, stddev):
    """
    Check 5x5 region surrounding each pixel not already masked
    and check if the mean intensity of those surrounding pixels
    is less than some multiple of the sample standard deviation
    of the boundary pixels. If this is the case, set the pixel
    mask to 0 to indicate it is a background pixel.
    
    O O O O O O O
    O X X X X X O
    O X O O O X O
    O X O P O X O
    O X O O O X O
    O X X X X X O
    O O O O O O O
    """

    # create empty array for the mean intensities of the close pixels
    far_spot = [0.] * 16
    for i, _ in enumerate(pixels):
        if mask[i] == 255:
            far_spot[:5] = pixels[i-(2*width)-2:i-(2*width)+3]
            far_spot[5] = pixels[i-width-2]
            far_spot[6] = pixels[i-width+2]
            far_spot[7] = pixels[i-2]
            far_spot[8] = pixels[i+2]
            far_spot[9] = pixels[i+width-2]
            far_spot[10] = pixels[i+width+2]
            far_spot[11:] = pixels[i+(2*width)-2:i+(2*width)+3]
            if sum(far_spot)/16 < cutoff * stddev:
                mask[i] = 0
        else:
            pass

    return

def apply_mask(pixels, mask):
    """
    Iterate through mask and for each 0, set the corresponding
    to 0 as well. Leave the unmasked values as significant data.
    """
    
    try:
    	len(pixels) == len(mask)
    except:
    	IJ.log('Image and mask are not same size')

    for i, m in enumerate(mask):
    	if m == 0:
    	    pixels[i] = 0
    	
def run_script(imp, close, far, cutoff):
    stack = imp.getImageStack()
    fin_stack = ImageStack(imp.width, imp.height)

    # iterate each slice in the stack
    for i in range(1, stack.getSize() + 1):
        # get progress
        IJ.showProgress(i, stack.getSize() + 1)
    
        # image processor converted to float to avoid byte problems
        ip = stack.getProcessor(i).convertToFloat()
        # pixels points to the array of floats
        pixels = ip.getPixels()

        # initial subtraction
        stddev = initial_subtract(pixels, imp.width, imp.height)

        mask = [255] * (imp.width*imp.height)

        # mask borders of image dependent on settings
        if far:
            fringe_mask(mask, imp.width, 2)
        elif close:
            fringe_mask(mask, imp.width, 1)
        else:
        	pass

        # update mask
        if close:
            init_mask(pixels, mask)
            close_subtract(pixels, mask, imp.width, cutoff, stddev)
        
        if far:
            init_mask(pixels, mask)
            far_subtract(pixels, mask, imp.width, cutoff, stddev)

        if close or far:
        	apply_mask(pixels, mask)
        
        fin_stack.addSlice(None, FloatProcessor(imp.width, imp.height, pixels, None))

    # create new image from final stack
    imp_fin = ImagePlus(imp.title[: -4] + "_background-subtracted.tif", fin_stack)
    # keep the same image calibration
    imp_fin.setCalibration(imp.getCalibration().copy())

    imp_fin.show()
    IJ.showProgress(1) # show progess bar
    
if __name__ in ['__builtin__','__main__']:
    options = get_options()
    if options is not None:
        close, far, cutoff = options
        imp  = IJ.getImage()
        start_time = time.time()
        run_script(imp, close, far, cutoff)
        total_time = time.time() - start_time
        IJ.log('Noise subtraction operation done in %.2f seconds' % total_time)
