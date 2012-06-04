import numpy as np
from numpy.testing import assert_array_almost_equal

from skimage.transform.geometric import _stackcopy
from skimage.transform import make_tform
from skimage.transform import homography, fast_homography
from skimage import transform as tf, data, img_as_float
from skimage.color import rgb2gray


SRC = np.array([
    [-12.3705, -10.5075],
    [-10.7865, 15.4305],
    [8.6985, 10.8675],
    [11.4975, -9.5715],
    [7.8435, 7.4835],
    [-5.3325, 6.5025],
    [6.7905, -6.3765],
    [-6.1695, -0.8235],
])
DST = np.array([
    [0, 0],
    [0, 5800],
    [4900, 5800],
    [4900, 0],
    [4479, 4580],
    [1176, 3660],
    [3754, 790],
    [1024, 1931],
])


def test_stackcopy():
    layers = 4
    x = np.empty((3, 3, layers))
    y = np.eye(3, 3)
    _stackcopy(x, y)
    for i in range(layers):
        assert_array_almost_equal(x[...,i], y)

def test_similarity():
    #: exact solution
    tform = make_tform('similarity', src=SRC[:2,:], dst=DST[:2,:])
    assert_array_almost_equal(tform.fwd(SRC[:2,:]), DST[:2,:])
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

    #: over-determined
    tform = make_tform('similarity', src=SRC, dst=DST)
    ref = np.array(
        [[2.3632898110e+02, -5.5876792257e+00, 2.5331569391e+03],
         [5.5876792257e+00, 2.3632898110e+02, 2.4358232635e+03],
         [0.0000000000e+00, 0.0000000000e+00, 1.0000000000e+00]])
    assert_array_almost_equal(tform.matrix, ref)
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

def test_affine():
    #: exact solution
    tform = make_tform('affine', src=SRC[:3,:], dst=DST[:3,:])
    assert_array_almost_equal(tform.fwd(SRC[:3,:]), DST[:3,:])
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

    #: over-determined
    tform = make_tform('affine', src=SRC, dst=DST)
    ref = np.array(
        [[2.2573930047e+02, 7.1588596765e+00, 2.5126622012e+03],
         [2.1234856855e+01, 2.4931019555e+02, 2.4143862183e+03],
         [0.0000000000e+00, 0.0000000000e+00, 1.0000000000e+00]])
    assert_array_almost_equal(tform.matrix, ref)
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

def test_projective():
    #: exact solution
    tform = make_tform('projective', src=SRC[:4,:], dst=DST[:4,:])
    ref = np.array(
        [[  1.9466901291e+02, -1.1888183994e+01, 2.2832379309e+03],
         [ -8.6910077540e+00,  2.2162069773e+02, 2.2211673699e+03],
         [ -1.2695966735e-02, -9.6053624285e-03, 1.0000000000e+00]])
    assert_array_almost_equal(tform.matrix, ref, 6)
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

    #: over-determined
    tform = make_tform('projective', src=SRC[:4,:], dst=DST[:4,:])
    ref = np.array(
        [[  1.9466901291e+02, -1.1888183994e+01, 2.2832379309e+03],
         [ -8.6910077540e+00,  2.2162069773e+02, 2.2211673699e+03],
         [ -1.2695966735e-02, -9.6053624285e-03, 1.0000000000e+00]])
    assert_array_almost_equal(tform.matrix, ref, 6)
    assert_array_almost_equal(tform.inv(tform.fwd(SRC)), SRC)

def test_polynomial():
    tform = make_tform('polynomial', src=SRC, dst=DST, order=10)
    assert_array_almost_equal(tform.fwd(SRC), DST, 6)

def test_homography():
    x = img_as_float(np.arange(9, dtype=np.uint8).reshape((3, 3)) + 1)
    theta = -np.pi/2
    M = np.array([[np.cos(theta),-np.sin(theta),0],
                  [np.sin(theta), np.cos(theta),2],
                  [0,             0,            1]])
    x90 = homography(x, M, order=1)
    assert_array_almost_equal(x90, np.rot90(x))

def test_fast_homography():
    img = rgb2gray(data.lena()).astype(np.uint8)
    img = img[:, :100]

    theta = np.deg2rad(30)
    scale = 0.5
    tx, ty = 50, 50

    H = np.eye(3)
    S = scale * np.sin(theta)
    C = scale * np.cos(theta)

    H[:2, :2] = [[C, -S], [S, C]]
    H[:2, 2] = [tx, ty]

    for mode in ('constant', 'mirror', 'wrap'):
        p0 = homography(img, H, mode=mode, order=1)
        p1 = fast_homography(img, H, mode=mode)
        p1 = np.round(p1)

        ## import matplotlib.pyplot as plt
        ## f, (ax0, ax1, ax2, ax3) = plt.subplots(1, 4)
        ## ax0.imshow(img)
        ## ax1.imshow(p0, cmap=plt.cm.gray)
        ## ax2.imshow(p1, cmap=plt.cm.gray)
        ## ax3.imshow(np.abs(p0 - p1), cmap=plt.cm.gray)
        ## plt.show()

        d = np.mean(np.abs(p0 - p1))
        assert d < 0.2

def test_swirl():
    image = img_as_float(data.checkerboard())

    swirl_params = {'radius': 80, 'rotation': 0, 'order': 2, 'mode': 'reflect'}
    swirled = tf.swirl(image, strength=10, **swirl_params)
    unswirled = tf.swirl(swirled, strength=-10, **swirl_params)

    assert np.mean(np.abs(image - unswirled)) < 0.01


if __name__ == "__main__":
    from numpy.testing import run_module_suite
    run_module_suite()
