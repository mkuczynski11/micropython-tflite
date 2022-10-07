#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "py/obj.h"
#include "py/objstr.h"
#include "py/objmodule.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "py/mphal.h"
#include "extmod/machine_spi.h"


#include "mpfile.h"
#include "tjpgd.h"


// User defined device identifier
typedef struct {
	mp_file_t *	 fp;	 // File pointer for input function
	uint8_t *	 fbuf;	 // Pointer to the frame buffer for output function
	unsigned int wfbuf;	 // Width of the frame buffer [pix]
	unsigned int left;	 // jpg crop left column
	unsigned int top;	 // jpg crop top row
	unsigned int right;	 // jpg crop right column
	unsigned int bottom; // jpg crop bottom row
} IODEV;

//
// file input function
//

static unsigned int in_func( // Returns number of bytes read (zero on error)
	JDEC *		 jd,		 // Decompression object
	uint8_t *	 buff,		 // Pointer to the read buffer (null to remove data)
	unsigned int nbyte)		 // Number of bytes to read/remove
{
	IODEV *		 dev = (IODEV *) jd->device; // Device identifier for the session (5th argument of jd_prepare function)
	unsigned int nread;

	if (buff) { // Read data from input stream
		nread = (unsigned int) mp_readinto(dev->fp, buff, nbyte);
		return nread;
	}

	// Remove data from input stream if buff was NULL
	mp_seek(dev->fp, nbyte, SEEK_CUR);
	return 0;
}

//
// output function for jpg_decode
//

static int out_crop( // 1:Ok, 0:Aborted
	JDEC * jd,		 // Decompression object
	void * bitmap,	 // Bitmap data to be output
	JRECT *rect)	 // Rectangular region of output image
{
	IODEV *	dev  = (IODEV *) jd->device;

	if (
		dev->left <= rect->right &&
		dev->right >= rect->left &&
        dev->top <= rect->bottom &&
		dev->bottom >= rect->top) {

		uint16_t  left		 = MAX(dev->left, rect->left);
		uint16_t  top		 = MAX(dev->top, rect->top);
		uint16_t  right		 = MIN(dev->right, rect->right);
		uint16_t  bottom	 = MIN(dev->bottom, rect->bottom);
		uint16_t  dev_width	 = dev->right - dev->left + 1;
		uint16_t  rect_width = rect->right - rect->left + 1;
		uint16_t  width 	 = (right - left + 1) * 2;
		uint16_t  row;

		for (row = top; row <= bottom; row++) {
			memcpy(
				(uint16_t *) dev->fbuf + ((row-dev->top) * dev_width) + left - dev->left,
				(uint16_t *) bitmap + ((row-rect->top) * rect_width) + left - rect->left,
				width
			);
		}
	}
	return 1; // Continue to decompress
}

STATIC mp_obj_t jpglib_decompress_jpg(mp_obj_t name_param)
{
    const char *filename;
    void *work;                 // work buffer for jpg & png decoding
    mp_file_t *fp;				// file object
	uint16_t *i2c_buffer;		// resident buffer if buffer_size given
	mp_int_t x = 0, y = 0, width = 0, height = 0;
    
    filename = mp_obj_str_get_str(name_param);
    work = (void *) m_malloc(3100); // Pointer to the work area

    JRESULT res;						  // Result code of TJpgDec API
    JDEC	jdec;						  // Decompression object
    IODEV  devid;						  // User defined device identifier
    size_t bufsize = 0;

    fp = mp_open(filename, "rb");
    devid.fp = fp;
    if (devid.fp) {
        // Prepare to decompress
			res = jd_prepare(&jdec, in_func, work, 3100, &devid);
			if (res == JDR_OK) {
				width = jdec.width;
				height = jdec.height;

                // Initialize output device
				devid.left	 = x;
				devid.top	 = y;
				devid.right	 = x + width - 1;
				devid.bottom = y + height - 1;

                bufsize = 2 * width * height;
				i2c_buffer = m_malloc(bufsize);
				if (i2c_buffer) {
					memset(i2c_buffer, 0xBEEF, bufsize);
				} else {
					mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
				}

                devid.fbuf	= (uint8_t *) i2c_buffer;
				devid.wfbuf = jdec.width;
				res = jd_decomp(&jdec, out_crop, 0); // Start to decompress with 1/1 scaling
				if (res != JDR_OK) {
					mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
				}
            } else {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
            }
        mp_close(devid.fp);
    }
    m_free(work); // Discard work area
    mp_obj_t result[3] = {
			mp_obj_new_bytearray(bufsize, (mp_obj_t *) i2c_buffer),
			mp_obj_new_int(width),
			mp_obj_new_int(height)
		};

    return mp_obj_new_tuple(3, result);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(jpglib_decompress_jpg_obj, jpglib_decompress_jpg);

STATIC const mp_map_elem_t jpglib_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_jpglib)},
    {MP_ROM_QSTR(MP_QSTR_decompress_jpg), (mp_obj_t) &jpglib_decompress_jpg_obj}
};

STATIC MP_DEFINE_CONST_DICT(mp_module_jpglib_globals, jpglib_module_globals_table);

const mp_obj_module_t mp_module_jpglib = {
	.base	 = {&mp_type_module},
	.globals = (mp_obj_dict_t *) &mp_module_jpglib_globals,
};

MP_REGISTER_MODULE(MP_QSTR_jpglib, mp_module_jpglib);

