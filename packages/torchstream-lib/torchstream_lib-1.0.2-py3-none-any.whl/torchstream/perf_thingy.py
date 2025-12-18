# Constructor with:
# - Input shape (-1 for seq) (Alternatively, function to yield inputs)
# - Max input length/size
# - Optional perf results (in size to time)
# - Optional in/out shape results or relation
# - Optional unit specification and fn to convert to seconds (in and out)
# - Optional rfield fn

# Benchmark fns for perfs & in/out shape
# Fn for rfield compute

# Description fn that prints model summary
# - Real time factor, lag, rfield


# TODO: make this a class property instead?
class StreamStats:
    def __init__(self, stream_cls, cons_kwargs, inputs):
        pass
