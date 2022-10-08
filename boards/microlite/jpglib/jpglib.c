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

/* Bytes per pixel of image output */
#define N_BPP (3 - JD_FORMAT)


/* Session identifier for input/output functions (name, members and usage are as user defined) */
typedef struct {
	mp_file_t *	 fp;	 // File pointer for input function
	uint8_t *	 fbuf;	 // Pointer to the frame buffer for output function
	unsigned int wfbuf;	 // Width of the frame buffer [pix]
} IODEV;

/*------------------------------*/
/* User defined input funciton  */
/*------------------------------*/

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

/*------------------------------*/
/* User defined output funciton */
/*------------------------------*/

static int out_crop( // 1:Ok, 0:Aborted
	JDEC * jd,		 // Decompression object
	void * bitmap,	 // Bitmap data to be output
	JRECT *rect)	 // Rectangular region of output image
{
	IODEV *	dev  = (IODEV *) jd->device;

	uint8_t *src, *dst;
    uint16_t y, bws;
    unsigned int bwd;

	/* Progress indicator */
    if (rect->left == 0) {
        printf("\r%lu%%", (rect->top << jd->scale) * 100UL / jd->height);
    }
	
	/* Copy the output image rectangle to the frame buffer */
    src = (uint8_t*)bitmap;                           /* Output bitmap */
    dst = dev->fbuf + N_BPP * (rect->top * dev->wfbuf + rect->left);  /* Left-top of rectangle in the frame buffer */
    bws = N_BPP * (rect->right - rect->left + 1);     /* Width of the rectangle [byte] */
    bwd = N_BPP * dev->wfbuf;                         /* Width of the frame buffer [byte] */
    for (y = rect->top; y <= rect->bottom; y++) {
        memcpy(dst, src, bws);   /* Copy a line */
        src += bws; dst += bwd;  /* Next line */
    }

    return 1;    /* Continue to decompress */
}

STATIC mp_obj_t jpglib_decompress_jpg(mp_obj_t name_param)
{
    const char *filename;
    void *work;                 // work buffer for jpg & png decoding
	size_t sz_work = 3500; /* Size of work area */
    mp_file_t *fp;				// file object
	uint16_t *i2c_buffer;		// resident buffer if buffer_size given
	mp_int_t x = 0, y = 0, width = 0, height = 0;
    
    filename = mp_obj_str_get_str(name_param);
    work = (void *) m_malloc(sz_work); // Pointer to the work area

    JRESULT res;						  // Result code of TJpgDec API
    JDEC	jdec;						  // Decompression object
    IODEV  devid;						  // User defined device identifier
    size_t bufsize = 0;

    fp = mp_open(filename, "rb");
    devid.fp = fp;
    if (devid.fp) {
        // Prepare to decompress
			res = jd_prepare(&jdec, in_func, work, sz_work, &devid);
			if (res == JDR_OK) {
				printf("Image size is %u x %u.\n%u bytes of work ares is used.\n", jdec.width, jdec.height, sz_work - jdec.sz_pool);
				width = jdec.width;
				height = jdec.height;

                // Initialize output device
                bufsize = N_BPP * jdec.width * jdec.height;	/* Create frame buffer for output image */
				i2c_buffer = m_malloc(bufsize);
				if (i2c_buffer) {
					memset(i2c_buffer, 0xBEEF, bufsize);
				} else {
					mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
				}

                devid.fbuf	= (uint8_t *)i2c_buffer;
				devid.wfbuf = jdec.width;

				res = jd_decomp(&jdec, out_crop, 0); /* Start to decompress with 1/1 scaling */
				if (res != JDR_OK) {
					mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
				}
            } else {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
            }
        mp_close(devid.fp);
    }
    m_free(work); // Discard work area
    mp_obj_t result[4] = {
			mp_obj_new_int(bufsize),
			mp_obj_new_bytearray(bufsize, (mp_obj_t *) i2c_buffer),
			mp_obj_new_int(width),
			mp_obj_new_int(height)
		};

    return mp_obj_new_tuple(4, result);
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

