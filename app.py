import numpy as np
import gradio as gr
import matplotlib.pyplot as plt

sr = 44100
duration = 2.0  # seconds

# --- Waveform Generator ---
def generate_wave(freqs, amps, phases, wave_types):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    wave = np.zeros_like(t)
    for f, a, p, wtype in zip(freqs, amps, phases, wave_types):
        phase_radians = p * np.pi / 180
        if wtype == "Sine":
            partial = np.sin(2 * np.pi * f * t + phase_radians)
        elif wtype == "Square":
            partial = np.sign(np.sin(2 * np.pi * f * t + phase_radians))
        elif wtype == "Saw":
            partial = 2 * (t * f - np.floor(0.5 + t * f))
        else:
            partial = np.zeros_like(t)
        wave += a * partial
    wave /= np.max(np.abs(wave)) + 1e-8
    return (sr, wave.astype(np.float32)), wave

# --- UI Setup ---
with gr.Blocks() as demo:
    gr.Markdown("## 🎚️ Additive Synth with Phase, Waveform Type & Graph")

    num_waves = gr.Slider(1, 10, value=2, step=1, label="Number of Oscillators")
    regenerate_btn = gr.Button("🔁 Regenerate Controls")
    sliders_container = gr.Column()
    generate_btn = gr.Button("▶️ Generate Audio & Preview")
    audio_output = gr.Audio()
    waveform_plot = gr.Plot()
    current_wave_count = gr.State(2)

    # Prebuild sliders + controls
    max_sliders = 10
    all_inputs = []

    with sliders_container:
        for i in range(max_sliders):
            with gr.Row():
                freq = gr.Slider(20, 2000, value=440, label=f"Freq {i+1} (Hz)", visible=(i < 2))
                amp = gr.Slider(0.0, 1.0, value=0.5, label="Amp", visible=(i < 2))
                phase = gr.Slider(0, 360, value=0, label="Phase (°)", visible=(i < 2))
                wave_type = gr.Dropdown(choices=["Sine", "Square", "Saw"], value="Sine", label="Waveform", visible=(i < 2))
                all_inputs.extend([freq, amp, phase, wave_type])

    # Show/hide controls based on oscillator count
    def update_visibility(n):
        current_wave_count.value = n
        updates = []
        for i in range(max_sliders):
            visible = i < n
            updates.extend([gr.update(visible=visible)] * 4)  # freq, amp, phase, wave_type
        return updates + [n]

    regenerate_btn.click(fn=update_visibility, inputs=num_waves, outputs=all_inputs + [current_wave_count])

    # Generate audio and graph
    def collect_generate_plot(*args):
        *vals, wave_count = args
        wave_count = int(wave_count)
        freqs = vals[::4][:wave_count]
        amps = vals[1::4][:wave_count]
        phases = vals[2::4][:wave_count]
        wave_types = vals[3::4][:wave_count]

        audio, waveform = generate_wave(freqs, amps, phases, wave_types)

        # Plot the first 1000 samples
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(waveform[:1000])
        ax.set_title("Summed Waveform Preview")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        plt.tight_layout()

        return audio, fig

    generate_btn.click(
        fn=collect_generate_plot,
        inputs=all_inputs + [current_wave_count],
        outputs=[audio_output, waveform_plot]
    )

demo.launch()


