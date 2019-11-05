import struct
import io
from collections import namedtuple
import PyPDF2
from PIL import Image,ImageOps
from pathlib import Path
img_modes = {'/DeviceRGB': 'RGB', '/DefaultRGB': 'RGB',
             '/DeviceCMYK': 'CMYK', '/DefaultCMYK': 'CMYK',
             '/DeviceGray': 'L', '/DefaultGray': 'L',
             '/Indexed': 'P'}

PdfImage = namedtuple('PdfImage', ['data', 'format','image_name'])

disk_dir=Path("C:/imgs/")
disk_dir.mkdir(parents=True, exist_ok=True)




def tiff_header_for_CCITT(width, height, img_size, CCITT_group=4):
    fields = 8
    tiff_header_struct = '<' + '2s' + 'H' + 'L' + 'H' + 'HHLL' * fields + 'L'
    return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                        42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       fields,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       # StripOffsets, LONG, 1, len of header
                       273, 4, 1, struct.calcsize(tiff_header_struct),
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, length
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )


    
def getColorSpace(obj):
    
    if '/ColorSpace' not in obj:
        mode = None
    elif obj['/ColorSpace'] == '/DeviceRGB':
        mode = "RGB"
    elif obj['/ColorSpace'] == '/DeviceCMYK':
        mode = "CMYK"
    elif obj['/ColorSpace'] == '/DeviceGray':
        mode = "P"
    else:
        if type(obj['/ColorSpace']) == PyPDF2.generic.ArrayObject:
            if obj['/ColorSpace'][0] == '/ICCBased':
                colorMap = obj['/ColorSpace'][1].getObject()['/N']
                if colorMap == 1:
                    mode = "P"
                elif colorMap == 3:
                    mode = "RGB"
                elif colorMap == 4:
                    mode = "CMYK"
                else:
                    mode = None
            else:
                mode = None
        else:
            mode = None
    return mode


if __name__ == '__main__':   
    pdf = "03_edge.pdf"
    inputx=open(pdf, "rb")
    input1 = PyPDF2.PdfFileReader(inputx)
    for i in range(0, input1.numPages):
        page = input1.getPage(i)
        if '/XObject' in page['/Resources']:
            xObject = page['/Resources']['/XObject'].getObject()
    
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    #print(xObject[obj])
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj].getData()
                
                    if '/Filter' in xObject[obj]:
                        if xObject[obj]['/Filter'] == '/DCTDecode' or '/DCTDecode' in xObject[obj]['/Filter']:
                            img = open(str(disk_dir)+"/"+obj[1:] + ".jpg", "wb")
                            img.write(data)
                        elif xObject[obj]['/Filter'] == '/FlateDecode' or '/FlateDecode' in xObject[obj]['/Filter']:
                            mode = getColorSpace(xObject[obj])
                            if mode != None:
                                img = Image.frombytes(mode, size, data)
                                if mode == "CMYK":
                                    img = img.convert("RGB")
                                img.save(str(disk_dir)+"/"+obj[1:] + ".png")
                        elif xObject[obj]['/Filter'] == '/JPXDecode':
                            img = open(str(disk_dir)+"/"+obj[1:] + ".jp2", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                            img = open(str(disk_dir)+"/"+obj[1:] + ".tiff", "wb")
                            img.write(data)
                            img.close()
                        elif '/CCITTFaxDecode' in xObject[obj]['/Filter']:
                            print("hello")
                            if xObject[obj]['/DecodeParms']['/K'] == -1:
                                CCITT_group = 4
                            else:
                                CCITT_group = 3
                            data = xObject[obj]._data 
                            img_size = len(data)
                            tiff_header = tiff_header_for_CCITT(
                            size[0], size[1], img_size, CCITT_group)
                            im = Image.open(io.BytesIO(tiff_header + data))

                            if xObject[obj].get('/BitsPerComponent') == 1:
                                im = ImageOps.flip(im)

                            imgByteArr = io.BytesIO()
                            img.save(imgByteArr,format='PNG')
                            img.close()
                    else:
                        img = Image.frombytes(mode, size, data)
                        img.save(str(disk_dir)+"/"+obj[1:] + ".png")
    exec(open('zipp.py').read())
