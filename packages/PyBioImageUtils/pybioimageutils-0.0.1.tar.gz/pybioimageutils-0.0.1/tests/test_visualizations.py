import os
import numpy as np
import skimage
from matplotlib import pyplot as plt
from pybioimageutils import visualize
import pytest
# from visual.interface import VisualFixture, standardize

@pytest.fixture
def image_cells_fullstack():
    return skimage.io.imread('.\\tests\\datasets\\BBBC033_v1_dataset\\C0.tif')

@pytest.fixture
def image_cells_rgb(image_cells_fullstack):    
    return image_cells_fullstack[15, :, :, :].squeeze()

@pytest.fixture
def image_cells_gray(image_cells_fullstack):    
    return image_cells_fullstack[15, :, :, 1].squeeze()

@pytest.fixture
def image_nuclei_fullstack():
    return skimage.io.imread('.\\tests\\datasets\\BBBC033_v1_dataset\\C2.tif')

@pytest.fixture
def image_nuclei_rgb(image_nuclei_fullstack):    
    return image_nuclei_fullstack[15, :, :, :].squeeze()

@pytest.fixture
def image_nuclei_gray(image_nuclei_fullstack):
    return image_nuclei_fullstack[15, :, :, 2].squeeze()

@pytest.fixture
def mask_fullstack():
    return skimage.io.imread('.\\tests\\datasets\\BBBC033_v1_dataset\\BBBC033_v1_DatasetGroundTruth.tif')

@pytest.fixture
def mask_single(mask_fullstack):
    return mask_fullstack[15, :, :].squeeze()

# ---Test normalization---

def test_normalize_input_grayscale(image_cells_gray):

    norm_image = visualize.normalize(image_cells_gray)

    assert (np.max(norm_image) == 1) and (np.min(norm_image) == 0)

# def test_normalize_input_grayscale_visual(visual, image_cells_gray):

#     norm_image = visualize.normalize(image_cells_gray)

#     visual.images(norm_image)

def test_normalize_input_rgb(image_cells_rgb):

    norm_image = visualize.normalize(image_cells_rgb)

    assert (np.max(norm_image) == 1) and (np.min(norm_image) == 0)

def test_normalize_3d_by_layer_false():

    # Read in test images
    test_image_path = '.\\tests\\datasets\\BBBC033_v1_dataset'

    image_A = skimage.io.imread(os.path.join(test_image_path, 'C0.tif'))

    norm_image = visualize.normalize(image_A[15, :, :, :].squeeze(), by_layer=False)
    
    plt.figure()
    plt.imshow(norm_image)
    plt.show()

    assert (np.max(norm_image) == 1) and (np.min(norm_image) == 0)

def test_composite_inputs_gray(image_cells_gray, image_nuclei_gray):

    composite_image = visualize.composite(image_cells_gray,
                                          image_nuclei_gray)

    plt.figure()
    plt.imshow(composite_image)
    plt.show()

    composite_image = visualize.composite(image_cells_gray, image_nuclei_gray, color_A=[0, 0, 1], color_B=[1, 0, 1])

    plt.figure()
    plt.imshow(composite_image)
    plt.show()
    
    assert True

def test_composite_inputs_aIsRGB(image_cells_rgb, image_nuclei_gray):

    composite_image = visualize.composite(image_cells_rgb, image_nuclei_gray, color_A=[0, 0, 1], color_B=[1, 0, 1])

    plt.figure()
    plt.imshow(composite_image)
    plt.show()
    
    assert True

def test_composite_invalid_shapes():
    with pytest.raises(ValueError):
        overlay_image = visualize.composite(np.ones((11, 10)), np.ones((21, 10)))

def test_composite_invalid_color_too_high():
    with pytest.raises(ValueError):
        overlay_image = visualize.composite(np.ones((10,10)), np.ones((10, 10)), color_A=[2.0, 1, 1])

def test_composite_invalid_color_too_low():
    with pytest.raises(ValueError):
        overlay_image = visualize.composite(np.ones((10,10)), np.ones((10, 10)), color_B=[-256, 1, 1])

def test_mask_overlay(image_cells_rgb, mask_single):

    overlay_image = visualize.overlay_mask(image_cells_rgb, mask_single, plot_outlines=True)

    plt.figure()
    plt.imshow(overlay_image)
    plt.show()

    assert True