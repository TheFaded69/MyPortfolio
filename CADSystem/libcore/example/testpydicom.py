import pydicom


# filenames = ['data/D0001',
#              '../data/dicom/rooster/IM000000',
#              '797cda64jj3j03001000.dcm',
#               'IM1']

filenames = ['D0022']


def print_params(filename):
    ds = pydicom.dcmread(filename)
    print(ds.PatientName)
    #print('Last^First^mid^pre')
    #print(ds.dir("setup"))
    #print(ds.PatientSetupSequence[0])
    print(ds)

for filename in filenames:
    print('Filename:\t\t'.format(filename))
    print_params(filename)