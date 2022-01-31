from libcore.mixins import ViewportMixin
from libcore.image import Image
from libcore.dicom import read_metadata
from libcore.dicom import load_directory
from libcore.dicom import read_volume
from libcore.dicom import scan_directory
from libcore.widget import ImageView


class App(ViewportMixin):

    def __init__(self):
        super().__init__()
        self.meta = read_metadata('../data/dicom/skabeeva/D0001')
        self.image = load_directory('../data/dicom/skabeeva')
        if 'rightonleft' in self.meta:
            print('Right ON left!!!!!!j')
            print(self.meta['rightonleft'])

        self.image.flip(axis='x', inplace=True)
        self.widget = ImageView(interactor=self.interactor,
                                image=self.image)
        self.widget.show()

if __name__ == '__main__':
    app = App()
    app.run()