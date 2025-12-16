"""
This module provides visualization utilities, such as compositing images and masks.
"""
import skimage
import numpy as np

def composite(image_A, image_B, color_A=[1, 1, 1], color_B=[0, 0, 1], normalize_images=True, alpha=0.5):
    """
    Generates a composite RGB image by alpha blending.
    
    :param image_A: The first image
    :param image_B: The second image
    :param color_A: The desired color of image_A, specified as normalized (i.e., 0 to 1) RGB values.
    :param color_B: The desired color of image_B, specified as normalized (i.e., 0 to 1) RGB values.
    :param normalize_images: Whether images should be normalized prior to compositing. Defaults to True.
    :param alpha: Specifies alpha blending level, between 0 - 1. The higher the value, the more image_B appears over image_A.
    """

    #If image_A is RGB, ignore the color aspect
    if image_A.shape[:1] != image_B.shape[:1]:
        raise ValueError("Image shapes (height and width) are not the same.")
    
    if np.max(color_A) > 1 or np.min(color_A) < 0:
        raise ValueError("Expected values of color_A to be between 0 and 1.")
    
    if np.max(color_B) > 1 or np.min(color_B) < 0:
        raise ValueError("Expected values of color_B to be between 0 and 1.")
    

    if normalize_images:
        image_A = normalize(image_A)
        image_B = normalize(image_B)

    image_composite = np.zeros((image_A.shape[0], image_A.shape[1], 3))

    for c in range(3):

        if np.ndim(image_A) == 2:
            image_left = image_A
            color_left = color_A[c]
        elif np.ndim(image_A) == 3:
            image_left = image_A[:, :, c]
            color_left = 1

        if np.ndim(image_B) == 2:
            image_right = image_B
            color_right = color_B[c]
        elif np.ndim(image_B) == 3:
            image_right = image_B[:, :, c]
            color_right = 1

        image_composite[:, :, c] = (alpha * image_left * color_left) + ((1 - alpha) * image_right * color_right)

    return image_composite

def normalize(image, by_layer=True):

    #Assume all images are [h, w, color, maybe z-stack]
    if np.ndim(image) < 2:
        raise ValueError("Expect image to be at least a 2-D array")
    elif np.ndim(image) == 2:
        result = (image - np.min(image))/(np.max(image) - np.min(image))
    elif np.ndim(image) == 3:

        result = np.zeros(image.shape)

        if by_layer:
            for c in range(image.shape[2]):
                result[:, :, c] = normalize(image[:, :, c])
        else:
            result = (image - np.min(image)) / (np.max(image) - np.min(image))

    else:
        raise ValueError("Maximum number of dimensions for image is 3")
    
    return result

# Define function to generate overlay a mask
def overlay_mask(image, mask, mask_color=[0, 1, 0], plot_outlines=True, normalize_image=True):
    # Always assume that image_A is supposed to be an image
    # Image_B can be an image, binary mask, or label

    if normalize_image:
        image = normalize(image)
    
    if plot_outlines and (mask.ndim == 2):
        # If this is a label
        mask = skimage.segmentation.find_boundaries(mask)
    else:        
        mask = mask > 0

    image_out = np.zeros((image.shape[0], image.shape[1], 3))

    for c in range(3):

        if np.ndim(image) == 2:
            curr_slice = image
        elif np.ndim(image) == 3:
            curr_slice = image[:, :, c]     

        if len(mask_color) < 4:
            alpha = 1
        else:
            alpha = mask_color[3]
            
        curr_slice[mask] = (mask_color[c] * 255 * alpha) + ((1 - alpha) * curr_slice[mask])

        image_out[:, :, c] = curr_slice

    return image_out