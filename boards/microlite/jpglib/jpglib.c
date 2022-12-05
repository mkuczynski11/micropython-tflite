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

#define DL_IMAGE_MIN(A, B) ((A) < (B) ? (A) : (B))
#define DL_IMAGE_MAX(A, B) ((A) < (B) ? (B) : (A))


// User defined device identifier
typedef struct {
	mp_file_t *	 fp;	 // File pointer for input function
	uint8_t *	 fbuf;	 // Pointer to the frame buffer for output function
	unsigned int wfbuf;	 // Width of the frame buffer [pix]
} IODEV;

/*------------------------------*/
/* User defined input funciton  */
/*------------------------------*/

static unsigned int file_in_func( // Returns number of bytes read (zero on error)
	JDEC		*jd,			  // Decompression object
	uint8_t		*buff,			  // Pointer to the read buffer (null to remove data)
	unsigned int nbyte)			  // Number of bytes to read/remove
{
	IODEV *dev = (IODEV *) jd->device; // Device identifier for the session (5th argument of jd_prepare function)
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
	IODEV *dev = (IODEV*)jd->device;   /* Session identifier (5th argument of jd_prepare function) */
    uint8_t *src, *dst;
    uint16_t y, bws;
    unsigned int bwd;


    /* Progress indicator */
    if (rect->left == 0) {
        printf("\r%lu%%", (rect->top << jd->scale) * 100UL / jd->height);
    }

    /* Copy the output image rectangle to the frame buffer */
    src = (uint8_t*)bitmap;                           /* Output bitmap */
    dst = dev->fbuf + 3 * (rect->top * dev->wfbuf + rect->left);  /* Left-top of rectangle in the frame buffer */
    bws = 3 * (rect->right - rect->left + 1);     /* Width of the rectangle [byte] */
    bwd = 3 * dev->wfbuf;                         /* Width of the frame buffer [byte] */
    for (y = rect->top; y <= rect->bottom; y++) {
        memcpy(dst, src, bws);   /* Copy a line */
        src += bws; dst += bwd;  /* Next line */
    }

    return 1;    /* Continue to decompress */
}


void image_zoom_in_twice(uint8_t *dimage,
                         int dw,
                         int dh,
                         int dc,
                         uint8_t *simage,
                         int sw,
                         int sc)
{
    for (int dyi = 0; dyi < dh; dyi++)
    {
        int _di = dyi * dw;

        int _si0 = dyi * 2 * sw;
        int _si1 = _si0 + sw;

        for (int dxi = 0; dxi < dw; dxi++)
        {
            int di = (_di + dxi) * dc;
            int si0 = (_si0 + dxi * 2) * sc;
            int si1 = (_si1 + dxi * 2) * sc;

            if (1 == dc)
            {
                dimage[di] = (uint8_t)((simage[si0] + simage[si0 + 1] + simage[si1] + simage[si1 + 1]) >> 2);
            }
            else if (3 == dc)
            {
                dimage[di] = (uint8_t)((simage[si0] + simage[si0 + 3] + simage[si1] + simage[si1 + 3]) >> 2);
                dimage[di + 1] = (uint8_t)((simage[si0 + 1] + simage[si0 + 4] + simage[si1 + 1] + simage[si1 + 4]) >> 2);
                dimage[di + 2] = (uint8_t)((simage[si0 + 2] + simage[si0 + 5] + simage[si1 + 2] + simage[si1 + 5]) >> 2);
            }
            else
            {
                for (int dci = 0; dci < dc; dci++)
                {
                    dimage[di + dci] = (uint8_t)((simage[si0 + dci] + simage[si0 + 3 + dci] + simage[si1 + dci] + simage[si1 + 3 + dci] + 2) >> 2);
                }
            }
        }
    }
    return;
}

void image_resize_linear(uint8_t *dst_image, uint8_t *src_image, int dst_w, int dst_h, int dst_c, int src_w, int src_h)
{ /*{{{*/
    float scale_x = (float)src_w / dst_w;
    float scale_y = (float)src_h / dst_h;

    int dst_stride = dst_c * dst_w;
    int src_stride = dst_c * src_w;

    if (fabs(scale_x - 2) <= 1e-6 && fabs(scale_y - 2) <= 1e-6)
    {
        image_zoom_in_twice(
            dst_image,
            dst_w,
            dst_h,
            dst_c,
            src_image,
            src_w,
            dst_c);
    }
    else
    {
        for (int y = 0; y < dst_h; y++)
        {
            float fy[2];
            fy[0] = (float)((y + 0.5) * scale_y - 0.5); // y
            int src_y = (int)fy[0];                     // y1
            fy[0] -= src_y;                             // y - y1
            fy[1] = 1 - fy[0];                          // y2 - y
            src_y = DL_IMAGE_MAX(0, src_y);
            src_y = DL_IMAGE_MIN(src_y, src_h - 2);

            for (int x = 0; x < dst_w; x++)
            {
                float fx[2];
                fx[0] = (float)((x + 0.5) * scale_x - 0.5); // x
                int src_x = (int)fx[0];                     // x1
                fx[0] -= src_x;                             // x - x1
                if (src_x < 0)
                {
                    fx[0] = 0;
                    src_x = 0;
                }
                if (src_x > src_w - 2)
                {
                    fx[0] = 0;
                    src_x = src_w - 2;
                }
                fx[1] = 1 - fx[0]; // x2 - x

                for (int c = 0; c < dst_c; c++)
                {
                    dst_image[y * dst_stride + x * dst_c + c] = round(src_image[src_y * src_stride + src_x * dst_c + c] * fx[1] * fy[1] + src_image[src_y * src_stride + (src_x + 1) * dst_c + c] * fx[0] * fy[1] + src_image[(src_y + 1) * src_stride + src_x * dst_c + c] * fx[1] * fy[0] + src_image[(src_y + 1) * src_stride + (src_x + 1) * dst_c + c] * fx[0] * fy[0]);
                }
            }
        }
    }
} /*}}}*/

STATIC mp_obj_t jpglib_resize_img(size_t n_args, const mp_obj_t *args)
{
	mp_buffer_info_t buf_info;
	mp_get_buffer_raise(args[0], &buf_info, MP_BUFFER_READ);
	mp_int_t out_w = mp_obj_get_int(args[1]);
	mp_int_t out_h = mp_obj_get_int(args[2]);
	mp_int_t src_w = mp_obj_get_int(args[3]);
	mp_int_t src_h = mp_obj_get_int(args[4]);

	int channels = 3;

	int resized_size = out_w*out_h*channels;
	uint8_t* resized_image = m_malloc(resized_size);
	if (!resized_image) {
		mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
	}

	image_resize_linear(resized_image, buf_info.buf, out_w, out_h, channels, src_w, src_h);

	mp_obj_t result = mp_obj_new_bytearray(resized_size, (mp_obj_t*) resized_image);

	m_free(resized_image);

	return result;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(jpglib_resize_img_obj, 5, 5, jpglib_resize_img);

STATIC mp_obj_t jpglib_decompress_jpg(mp_obj_t name_param)
{
    static unsigned int (*input_func)(JDEC*, uint8_t*, unsigned int) = NULL;
    IODEV  devid;

    void * work;
    mp_file_t * fp;
    uint8_t * buffer;

    const char *filename = mp_obj_str_get_str(name_param);
    fp = mp_open(filename, "rb");
    devid.fp = fp;
    input_func = file_in_func;

    mp_int_t x = 0, y = 0, width = 0, height = 0;

    work = (void *) m_malloc(3100); // Pointer to the work area

    JRESULT res;						  // Result code of TJpgDec API
    JDEC	jdec;						  // Decompression object
    size_t bufsize = 0;

    if(input_func && devid.fp) {
            // Prepare to decompress
			res = jd_prepare(&jdec, input_func, work, 3100, &devid);
            if (res == JDR_OK) {
                bufsize = 3 * jdec.width * jdec.height;
                buffer = m_malloc(bufsize);
				if (buffer) {
					memset(buffer, 0xBEEF, bufsize);
				} else {
					mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
				}

                devid.fbuf	= (uint8_t *) buffer;
				devid.wfbuf = jdec.width;
                res			= jd_decomp(&jdec, out_crop, 0); // Start to decompress with 1/1 scaling
                if (res != JDR_OK) {
					mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
				}
            } else {
				mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg prepare failed."));
			}
            if (fp) {
				mp_close(fp);
				fp = MP_OBJ_NULL;
			}
    }
    m_free(work); // Discard work area

    mp_obj_t result[3] = {
			mp_obj_new_bytearray(bufsize, (mp_obj_t *) buffer),
			mp_obj_new_int(width),
			mp_obj_new_int(height)
		};

    m_free(buffer);
    return mp_obj_new_tuple(3, result);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(jpglib_decompress_jpg_obj, jpglib_decompress_jpg);

STATIC const mp_map_elem_t jpglib_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_jpglib)},
    {MP_ROM_QSTR(MP_QSTR_decompress_jpg), (mp_obj_t) &jpglib_decompress_jpg_obj},
    {MP_ROM_QSTR(MP_QSTR_resize_img), (mp_obj_t) &jpglib_resize_img_obj}
};

STATIC MP_DEFINE_CONST_DICT(mp_module_jpglib_globals, jpglib_module_globals_table);

const mp_obj_module_t mp_module_jpglib = {
	.base	 = {&mp_type_module},
	.globals = (mp_obj_dict_t *) &mp_module_jpglib_globals,
};

MP_REGISTER_MODULE(MP_QSTR_jpglib, mp_module_jpglib);
