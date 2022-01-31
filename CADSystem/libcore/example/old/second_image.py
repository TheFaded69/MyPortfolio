import vtk
from libcore.image import Image
from libcore.mixins import ViewportMixin
from libcore.widget import ImageView
import h5py
import cv2
import numpy as np
from vtk.util.numpy_support import numpy_to_vtk
from vtk.util.numpy_support import vtk_to_numpy

image = Image('../data/rooster.vti')
arr = vtk_to_numpy(image.GetPointData().GetScalars())
arr = arr.reshape((205, 512, 512))
arr = np.swapaxes(arr, 0, 2)

frame = arr[:, :, 100]
print(arr.shape)

frame = (frame - frame.min())
frame = frame / frame.max()
frame = frame * 255.0
frame = frame.astype(np.uint8)

cv2.imshow('win', frame)
cv2.waitKey(0)

# fd = h5py.File('../data/roo.hdf5', 'w')
# self.image.save_to_hdf(fd, 'image')
# fd.flush()
# fd.close()
#
# fd = h5py.File('../data/roo.hdf5', 'r')
# self.image = Image.from_hdf(fd, 'image')
#
# self.image_view = ImageView(self.interactor, self.image)
# self.image_view.contour_threshold = 200
# self.image_view.show()
#
# app = App()
# app.run()