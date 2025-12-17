#include "NN/{{MODEL_NAME}}_project.h"
#include "emulator.h"
#include "NN/nnet_utils/nnet_common.h"
#include <any>
#include "ap_fixed.h"
#include "ap_int.h"
#include "scales.h"

using namespace hls4ml_{{MODEL_NAME}};

class {{MODEL_NAME}}_emulator : public hls4mlEmulator::Model {

private:
    typedef {{UNSCALED_TYPE}} unscaled_t;
    static const int N_INPUT_SIZE  = {{N_INPUTS}};
    static const int N_OUTPUT_SIZE = {{N_OUTPUTS}};

    unscaled_t _unscaled_input[N_INPUT_SIZE];
    {{MODEL_NAME}}::input_t  _scaled_input[N_INPUT_SIZE];
    {{MODEL_NAME}}::result_t _result[N_OUTPUT_SIZE];

    virtual void _scaleNNInputs(unscaled_t unscaled[N_INPUT_SIZE],
                                {{MODEL_NAME}}::input_t scaled[N_INPUT_SIZE])
    {
        for (int i = 0; i < N_INPUT_SIZE; i++) {
            unscaled_t tmp0 = unscaled[i] - hls4ml_{{MODEL_NAME}}::ad_offsets[i];
            {{MODEL_NAME}}::input_t tmp1 = tmp0 >> hls4ml_{{MODEL_NAME}}::ad_shift[i];
            scaled[i] = tmp1;
        }
    }

public:
    virtual void prepare_input(std::any input) override {
        unscaled_t* unscaled_input_p = std::any_cast<unscaled_t*>(input);

        for (int i = 0; i < N_INPUT_SIZE; i++) {
            _unscaled_input[i] = unscaled_input_p[i];
        }

        _scaleNNInputs(_unscaled_input, _scaled_input);
    }

    virtual void predict() override {
        {{MODEL_NAME}}::{{MODEL_NAME}}_project(_scaled_input, _result);
    }

    virtual void read_result(std::any result) override {
        {{MODEL_NAME}}::result_t* result_p =
            std::any_cast<{{MODEL_NAME}}::result_t*>(result);

        for (int i = 0; i < N_OUTPUT_SIZE; i++) {
            result_p[i] = _result[i];
        }
    }
};

extern "C" hls4mlEmulator::Model* create_model() {
    return new {{MODEL_NAME}}_emulator;
}

extern "C" void destroy_model(hls4mlEmulator::Model* m) {
    delete m;
}
