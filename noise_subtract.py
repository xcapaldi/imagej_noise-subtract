from ij import IJ, ImagePlus, ImageStack
from ij.process import FloatProcessor
from ij.gui import GenericDialog

# currently this plugin does not save the metadata from the
# original image (microscope metadata).

# give options for background subtraction
def getOptions():
    gd = GenericDialog("Options")
    gd.addCheckbox("3x3 boundary region", True) # use 3x3 region
    gd.addCheckbox("5x5 boundary region", True) # use 5x5 region
    # change the multiple of the standard deviation that is used
    # as a cutoff for the subtraction
    gd.addNumericField("N * sigma cutoff", 3.00, 2) # 2 decimals
    gd.showDialog()
    # pull options
    close = gd.getNextBoolean()
    far = gd.getNextBoolean()
    cutoff = gd.getNextNumber()
    return close, far, cutoff

close, far, cutoff = getOptions()

# pull the active image
imp  = IJ.getImage()
stack = imp.getImageStack()
subimg = [] # list of background subtracted slices

# define function to recursively divide pixels into nested array
def cutrows(pixels):
    if len(pixels) < width:
        return rows
    else:
        rows.append(pixels[:width])
        del pixels[:width]
        cutrows(pixels)

# iterate each slice in the stack
for i in range(1 ,imp.getNSlices() + 1):
    # get progress
    IJ.showProgress(i, imp.getNSlices() + 1)
    
    # image processor converted to float to avoid byte problems
    ip = stack.getProcessor(i).convertToFloat()
    # pixels points to the array of floats
    pixels = ip.getPixels()

    rows = [] # empty array to store rows of pixels
    width = imp.width
    
    # cut the image into rows of pixels
    cutrows(pixels)

    # now we find the height of the image
    height = len(rows)

    # INITIAL SUBTRACTION

    # we take the top and bottom edges of the image
    boundary = rows[0] + rows[height - 1]

    # iterate through the left and rightmost pixels
    # append them to the boundary array
    for g in range(1, height - 1):
        boundary.append(rows[g][0]) # left
        boundary.append(rows[g][-1]) # right


    # mean of boundary pixels
    mean = sum(boundary) / len(boundary)

    # sample standard deviation (sigma) of intensity for boundary pixels
    stddev = (sum((p - mean) ** 2 for p in boundary) /
              (len(boundary) - 1)) ** 0.5
    
    # iterate through each row of pixels and substract mean intensity
    # negative values are rounded up to zero
    initsub = []
    for h in range(0, len(rows)):
        initsub.append(list(map(
            lambda x: (abs(x - mean) + (x - mean)) / 2, rows[h])))

    # INDIVIDUAL NOISE SPOT REMOVAL
    # be aware that your final image will have a width and height
    # four pixels smaller than your original due to the noise
    # reduction algorithm

    # check 3x3 region surrounding pixel of interest and find mean intensity
    #
    # O O O O O O O
    # O O O O O O O
    # O O X X X O O
    # O O X P X O O
    # O O X X X O O
    # O O O O O O O
    # O O O O O O O
    #

    if close == True:
        # create empty array for the mean intensities of the close pixels
        closespot=[]
        for r in range(2, height - 2):
            closespot.append([]) # add new row
            for p in range (2, width - 2):
                closespot[r - 2].append((initsub[r - 1][p - 1]
                                         + initsub[r - 1][p]
                                         + initsub[r - 1][p + 1]
                                         + initsub[r][p - 1]
                                         + initsub[r][p + 1]
                                         + initsub[r + 1][p - 1]
                                         + initsub[r + 1][p]
                                         + initsub[r + 1][p + 1])
                                        / 8)

    # check 5x5 region surrounding pixel of interest and find the mean intensity
    #
    # O O O O O O O
    # O X X X X X O
    # O X O O O X O
    # O X O P O X O
    # O X O O O X O
    # O X X X X X O
    # O O O O O O O
    #

    if far == True:
        farspot=[]
        for r in range(2, height - 2):
            farspot.append([]) # add new row
            for p in range (2, width - 2):
                farspot[r - 2].append((initsub[r - 2][p - 2] 
                                   + initsub[r - 2][p - 1]
                                   + initsub[r - 2][p]
                                   + initsub[r - 2][p + 1]
                                   + initsub[r - 2][p + 2]
                                   + initsub[r - 1][p - 2]
                                   + initsub[r - 1][p + 2]
                                   + initsub[r][p - 2]
                                   + initsub[r][p + 2]
                                   + initsub[r + 1][p - 2]
                                   + initsub[r + 1][p + 2]
                                   + initsub[r + 2][p - 2]
                                   + initsub[r + 2][p - 1]
                                   + initsub[r + 2][p]
                                   + initsub[r + 2][p + 1]
                                   + initsub[r + 2][p + 2])
                                  / 16)
            
    # if either close or far regions are <(3*sigma) set the pixel value to zero
    # this will be a linear array again
    finimg=[]

    if (close == True) and (far == True):
        for r in range(2, height - 2):
            for p in range(2, width - 2):
                if (closespot[r - 2][p - 2] < (cutoff * stddev) or
                    farspot[r - 2][p - 2] < (cutoff * stddev)):
                    finimg.append(0)
                else:
                    finimg.append(initsub[r][p])
    elif (close == True) and (far == False):
        for r in range(2, height - 2):
            for p in range(2, width - 2):
                if closespot[r - 2][p - 2] < (cutoff * stddev):
                    finimg.append(0)
                else:
                    finimg.append(initsub[r][p])
    elif (close == False) and (far == True):
        for r in range(2, height - 2):
            for p in range(2, width - 2):
                if farspot[r - 2][p - 2] < (cutoff * stddev):
                    finimg.append(0)
                else:
                    finimg.append(initsub[r][p])
    else:
        for r in range(2, height - 2):
            for p in range(2, width - 2):
                    finimg.append(initsub[r][p])

    fp = FloatProcessor(width - 4, height - 4, finimg, None)

    subimg.append(fp)

# create new stack with substracted images
finstack = ImageStack(width - 4, height - 4)
for fp in subimg:
    finstack.addSlice(None, fp)

# create new image from final stack
impfin = ImagePlus(imp.title[: -4] + "_background-subtracted.tif", finstack)
# keep the same image calibration
impfin.setCalibration(imp.getCalibration().copy())

impfin.show()
IJ.showProgress(1) # show progess bar
