#ifndef __ADT_SCALES_H
#define __ADT_SCALES_H

#include "NN/{{MODEL_NAME}}_project.h"

namespace hls4ml_{{MODEL_NAME}} {

typedef ap_fixed<5,5> ad_shift_t;
typedef ap_fixed<10,10> ad_offset_t;

const ad_shift_t ad_shift[{{N_INPUTS}}] = {
    {{AD_SHIFT}}
};

const ad_offset_t ad_offsets[{{N_INPUTS}}] = {
    {{AD_OFFSETS}}
};

} // namespace hls4ml_{{MODEL_NAME}}
#endif
