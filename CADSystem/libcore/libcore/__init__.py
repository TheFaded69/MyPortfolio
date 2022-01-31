import warnings

from . import cmap
from . import dicom
from . import geometry
from . import image
from . import mesh
from . import display
from . import utils

from .image import Image
from .mesh import Mesh


from .geometry import Plane
from .display import PolyActor

# Выключаем навязчивые предупреждения vtk
warnings.simplefilter(action='ignore', category=FutureWarning)
