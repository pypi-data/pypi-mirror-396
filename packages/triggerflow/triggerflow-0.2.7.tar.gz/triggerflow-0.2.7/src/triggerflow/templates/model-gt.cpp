#include "{{MODEL_NAME}}_project.h"
#include "data_types.h"

namespace {{MODEL_NAME}} {

typedef {{OFFSET_TYPE}} offset_t;
typedef {{SHIFT_TYPE}}  shift_t;

static const offset_t NN_OFFSETS[{{N_INPUTS}}] = { {{NN_OFFSETS}} };
static const shift_t  NN_SHIFTS[{{N_INPUTS}}]  = { {{NN_SHIFTS}} };

static void scaleNNInputs(
    input_t unscaled[{{N_INPUTS}}],
    input_t scaled[{{N_INPUTS}}]
) {
    #pragma HLS pipeline
    for (int i = 0; i < {{N_INPUTS}}; i++) {
        #pragma HLS unroll
        input_t tmp0 = unscaled[i] - NN_OFFSETS[i];
        input_t tmp1 = tmp0 >> NN_SHIFTS[i];
        scaled[i] = tmp1;
    }
}

void {{MODEL_NAME}}_GT(
    Muon      muons[{{MUON_SIZE}}],
    Jet       jets[{{JET_SIZE}}],
    EGamma    egammas[{{EGAMMA_SIZE}}],
    Tau       taus[{{TAU_SIZE}}],
    ET        et,
    HT        ht,
    ETMiss    etmiss,
    HTMiss    htmiss,
    ETHFMiss  ethfmiss,
    HTHFMiss  hthfmiss,
    {{OUTPUT_TYPE}} {{OUTPUT_LAYER}}
) {
    #pragma HLS aggregate variable=muons compact=bit
    #pragma HLS aggregate variable=jets compact=bit
    #pragma HLS aggregate variable=egammas compact=bit
    #pragma HLS aggregate variable=taus compact=bit
    #pragma HLS aggregate variable=et compact=bit
    #pragma HLS aggregate variable=ht compact=bit
    #pragma HLS aggregate variable=etmiss compact=bit
    #pragma HLS aggregate variable=htmiss compact=bit
    #pragma HLS aggregate variable=ethfmiss compact=bit
    #pragma HLS aggregate variable=hthfmiss compact=bit

    #pragma HLS array_partition variable=muons complete
    #pragma HLS array_partition variable=jets complete
    #pragma HLS array_partition variable=egammas complete
    #pragma HLS array_partition variable=taus complete

    #pragma HLS pipeline II=1
    #pragma HLS latency min=2 max=2
    #pragma HLS inline recursive

    input_t input_unscaled[{{N_INPUTS}}];
    input_t input_scaled[{{N_INPUTS}}];
    int idx = 0;

    // Muons
    for (int i = 0; i < {{MUON_SIZE}}; i++) {
        #pragma HLS unroll
        {% for f in MUON_FEATURES %}
        input_unscaled[idx++] = muons[i].{{f}};
        {% endfor %}
    }

    // Jets
    for (int i = 0; i < {{JET_SIZE}}; i++) {
        #pragma HLS unroll
        {% for f in JET_FEATURES %}
        input_unscaled[idx++] = jets[i].{{f}};
        {% endfor %}
    }

    // EGammas
    for (int i = 0; i < {{EGAMMA_SIZE}}; i++) {
        #pragma HLS unroll
        {% for f in EGAMMA_FEATURES %}
        input_unscaled[idx++] = egammas[i].{{f}};
        {% endfor %}
    }

    // Taus
    for (int i = 0; i < {{TAU_SIZE}}; i++) {
        #pragma HLS unroll
        {% for f in TAU_FEATURES %}
        input_unscaled[idx++] = taus[i].{{f}};
        {% endfor %}
    }

    // Scalars / global objects
    {% for f in GLOBAL_FEATURES %}
    input_unscaled[idx++] = {{f}};
    {% endfor %}

    scaleNNInputs(input_unscaled, input_scaled);

    {{MODEL_NAME}}_project(input_scaled, {{OUT}});
}

} // namespace {{MODEL_NAME}}
