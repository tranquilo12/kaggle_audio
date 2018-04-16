# frequency cutoff
def resample_wrt_b(b=0.08):
    # N = re-sampled according to new bandpass rate
    N = int(np.ceil((rate/b)))
    if not N % 2 : N = N + 1
    return N

def low_pass(fc, N, n):
    sinc_func = np.sinc(2 * fc * (n - (N - 1) / 2.))
    window = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) + 0.08 * np.cos(4 * np.pi * n / (N - 1))
    sinc_func = sinc_func * window
    sinc_func = sinc_func / np.sum(sinc_func)
    return sinc_func, window

def high_pass(fc, N, n):
    sinc_func = np.sinc(2 * fc * (n - (N - 1) / 2.))
    window = np.blackman(N)
    sinc_func = sinc_func * window
    sinc_func = sinc_func / np.sum(sinc_func)
    # reverse function
    sinc_func = -sinc_func
    sinc_func[int((N - 1) / 2)] += 1
    return window, sinc_func

fc = 0.5
N = resample_wrt_b(b = 0.08)
n = np.arange(N)

# low_pass_sinc, low_window = low_pass(fc, N, n)
# plt.plot(n, low_window, n, low_pass_sinc)

high_pass_sinc, high_window = high_pass(fc, N, n)

source = ColumnDataSource(data=dict(window = high_window, high_pass_sinc = high_pass_sinc))
plot = figure(y_range=(min(high_pass_sinc), max(high_pass_sinc)), plot_width=400, plot_height=400)
plot.line("window", "high_pass_sinc", source=source, line_width=3, line_alpha=0.6)

callback = CustomJS(args=dict(source=source), code="""
    var data = source.data;
    var A = amp.value;
    var k = freq.value;
    var phi = phase.value;
    var B = offset.value;
    x = data['x']
    y = data['y']
    for (i = 0; i < x.length; i++) {
        y[i] = B + A*Math.sin(k*x[i]+phi);
    }
    source.change.emit();
""")

amp_slider = Slider(start=0.1, end=10, value=1, step=.1,
                    title="Amplitude", callback=callback)
callback.args['amp'] = amp_slider

freq_slider = Slider(start=0.1, end=10, value=1, step=.1,
                     title="Frequency", callback=callback)
callback.args["freq"] = freq_slider

phase_slider = Slider(start=0, end=6.4, value=0, step=.1,
                      title="Phase", callback=callback)
callback.args["phase"] = phase_slider

offset_slider = Slider(start=-5, end=5, value=0, step=.1,
                       title="Offset", callback=callback)
callback.args["offset"] = offset_slider

layout = row(
    plot,
    widgetbox(amp_slider, freq_slider, phase_slider, offset_slider),
)
show(layout)
# plt.plot(n, high_window, n, high_pass_sinc)
# plt.plot(n, high_pass_sinc)
# plt.show()