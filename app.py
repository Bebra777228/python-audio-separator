import os
import tempfile
import gradio as gr

from audio_separator.separator import Separator

# Constants
MODEL_DIR = "/tmp/audio-separator-models/"
OUTPUT_DIR = "/content/output"
OUTPUT_FORMATS = ["wav", "flac", "mp3"]

# Model lists
ROFORMER_MODELS = {
    'BS-Roformer-Viperx-1297.ckpt': 'model_bs_roformer_ep_317_sdr_12.9755.ckpt',
    'BS-Roformer-Viperx-1296.ckpt': 'model_bs_roformer_ep_368_sdr_12.9628.ckpt',
    'BS-Roformer-Viperx-1053.ckpt': 'model_bs_roformer_ep_937_sdr_10.5309.ckpt',
    'BS-Roformer-De-Reverb.ckpt': 'deverb_bs_roformer_8_384dim_10depth.ckpt',
    'Mel-Roformer-Viperx-1143.ckpt': 'model_mel_band_roformer_ep_3005_sdr_11.4360.ckpt',
    'Mel-Roformer-Crowd-Aufr33-Viperx.ckpt': 'mel_band_roformer_crowd_aufr33_viperx_sdr_8.7144.ckpt',
    'Mel-Roformer-Karaoke-Aufr33-Viperx.ckpt': 'mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt',
    'Mel-Roformer-Denoise-Aufr33': 'denoise_mel_band_roformer_aufr33_sdr_27.9959.ckpt',
    'Mel-Roformer-Denoise-Aufr33-Aggr': 'denoise_mel_band_roformer_aufr33_aggr_sdr_27.9768.ckpt',
}
MDX23C_MODELS = [
    'MDX23C_D1581.ckpt',
    'MDX23C-8KFFT-InstVoc_HQ.ckpt',
    'MDX23C-8KFFT-InstVoc_HQ_2.ckpt',
]
MDXNET_MODELS = [
    'UVR-MDX-NET-Inst_full_292.onnx',
    'UVR-MDX-NET_Inst_187_beta.onnx',
    'UVR-MDX-NET_Inst_82_beta.onnx',
    'UVR-MDX-NET_Inst_90_beta.onnx',
    'UVR-MDX-NET_Main_340.onnx',
    'UVR-MDX-NET_Main_390.onnx',
    'UVR-MDX-NET_Main_406.onnx',
    'UVR-MDX-NET_Main_427.onnx',
    'UVR-MDX-NET_Main_438.onnx',
    'UVR-MDX-NET-Inst_HQ_1.onnx',
    'UVR-MDX-NET-Inst_HQ_2.onnx',
    'UVR-MDX-NET-Inst_HQ_3.onnx',
    'UVR-MDX-NET-Inst_HQ_4.onnx',
    'UVR_MDXNET_Main.onnx',
    'UVR-MDX-NET-Inst_Main.onnx',
    'UVR_MDXNET_1_9703.onnx',
    'UVR_MDXNET_2_9682.onnx',
    'UVR_MDXNET_3_9662.onnx',
    'UVR-MDX-NET-Inst_1.onnx',
    'UVR-MDX-NET-Inst_2.onnx',
    'UVR-MDX-NET-Inst_3.onnx',
    'UVR_MDXNET_KARA.onnx',
    'UVR_MDXNET_KARA_2.onnx',
    'UVR_MDXNET_9482.onnx',
    'UVR-MDX-NET-Voc_FT.onnx',
    'Kim_Vocal_1.onnx',
    'Kim_Vocal_2.onnx',
    'Kim_Inst.onnx',
    'Reverb_HQ_By_FoxJoy.onnx',
    'UVR-MDX-NET_Crowd_HQ_1.onnx',
    'kuielab_a_vocals.onnx',
    'kuielab_a_other.onnx',
    'kuielab_a_bass.onnx',
    'kuielab_a_drums.onnx',
    'kuielab_b_vocals.onnx',
    'kuielab_b_other.onnx',
    'kuielab_b_bass.onnx',
    'kuielab_b_drums.onnx',
]
VR_ARCH_MODELS = [
    '1_HP-UVR.pth',
    '2_HP-UVR.pth',
    '3_HP-Vocal-UVR.pth',
    '4_HP-Vocal-UVR.pth',
    '5_HP-Karaoke-UVR.pth',
    '6_HP-Karaoke-UVR.pth',
    '7_HP2-UVR.pth',
    '8_HP2-UVR.pth',
    '9_HP2-UVR.pth',
    '10_SP-UVR-2B-32000-1.pth',
    '11_SP-UVR-2B-32000-2.pth',
    '12_SP-UVR-3B-44100.pth',
    '13_SP-UVR-4B-44100-1.pth',
    '14_SP-UVR-4B-44100-2.pth',
    '15_SP-UVR-MID-44100-1.pth',
    '16_SP-UVR-MID-44100-2.pth',
    '17_HP-Wind_Inst-UVR.pth',
    'UVR-DeEcho-DeReverb.pth',
    'UVR-De-Echo-Normal.pth',
    'UVR-De-Echo-Aggressive.pth',
    'UVR-DeNoise.pth',
    'UVR-DeNoise-Lite.pth',
    'UVR-BVE-4B_SN-44100-1.pth',
    'MGM_HIGHEND_v4.pth',
    'MGM_LOWEND_A_v4.pth',
    'MGM_LOWEND_B_v4.pth',
    'MGM_MAIN_v4.pth',
]
DEMUCS_MODELS = [
    'htdemucs_ft.yaml',
    'htdemucs_6s.yaml',
    'htdemucs.yaml',
    'hdemucs_mmi.yaml',
]

def roformer_separator(audio, model, seg_size, overlap, model_dir, out_dir, out_format, norm_thresh, amp_thresh):
    """Separate audio using Roformer model."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        separator = Separator(
            model_file_dir=model_dir,
            output_dir=tmp_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            mdxc_params={
                "batch_size": 1,
                "segment_size": seg_size,
                "overlap": overlap,
            }
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)

        stem1_file = os.path.join(out_dir, os.path.basename(separation[0]))
        stem2_file = os.path.join(out_dir, os.path.basename(separation[1]))
        os.rename(separation[0], stem1_file)
        os.rename(separation[1], stem2_file)

        return stem1_file, stem2_file

def mdx23c_separator(audio, model, seg_size, overlap, model_dir, out_dir, out_format, norm_thresh, amp_thresh):
    """Separate audio using MDX23C model."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        separator = Separator(
            model_file_dir=model_dir,
            output_dir=tmp_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            mdxc_params={
                "batch_size": 1,
                "segment_size": seg_size,
                "overlap": overlap,
            }
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)

        stem1_file = os.path.join(out_dir, os.path.basename(separation[0]))
        stem2_file = os.path.join(out_dir, os.path.basename(separation[1]))
        os.rename(separation[0], stem1_file)
        os.rename(separation[1], stem2_file)

        return stem1_file, stem2_file

def mdx_separator(audio, model, hop_length, seg_size, overlap, denoise, model_dir, out_dir, out_format, norm_thresh, amp_thresh):
    """Separate audio using MDX-NET model."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        separator = Separator(
            model_file_dir=model_dir,
            output_dir=tmp_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            mdx_params={
                "batch_size": 1,
                "hop_length": hop_length,
                "segment_size": seg_size,
                "overlap": overlap,
                "enable_denoise": denoise,
            }
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)

        stem1_file = os.path.join(out_dir, os.path.basename(separation[0]))
        stem2_file = os.path.join(out_dir, os.path.basename(separation[1]))
        os.rename(separation[0], stem1_file)
        os.rename(separation[1], stem2_file)

        return stem1_file, stem2_file

def vr_separator(audio, model, window_size, aggression, tta, post_process, post_process_threshold, high_end_process, model_dir, out_dir, out_format, norm_thresh, amp_thresh):
    """Separate audio using VR ARCH model."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        separator = Separator(
            model_file_dir=model_dir,
            output_dir=tmp_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            vr_params={
                "batch_size": 1,
                "window_size": window_size,
                "aggression": aggression,
                "enable_tta": tta,
                "enable_post_process": post_process,
                "post_process_threshold": post_process_threshold,
                "high_end_process": high_end_process,
            }
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)

        stem1_file = os.path.join(out_dir, os.path.basename(separation[0]))
        stem2_file = os.path.join(out_dir, os.path.basename(separation[1]))
        os.rename(separation[0], stem1_file)
        os.rename(separation[1], stem2_file)

        return stem1_file, stem2_file

def demucs_separator(audio, model, seg_size, shifts, overlap, segments_enabled, model_dir, out_dir, out_format, norm_thresh, amp_thresh):
    """Separate audio using Demucs model."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        separator = Separator(
            model_file_dir=model_dir,
            output_dir=tmp_dir,
            output_format=out_format,
            normalization_threshold=norm_thresh,
            amplification_threshold=amp_thresh,
            demucs_params={
                "segment_size": seg_size,
                "shifts": shifts,
                "overlap": overlap,
                "segments_enabled": segments_enabled,
            }
        )

        separator.load_model(model_filename=model)
        separation = separator.separate(audio)

        stem1_file = os.path.join(out_dir, os.path.basename(separation[0]))
        stem2_file = os.path.join(out_dir, os.path.basename(separation[1]))
        stem3_file = os.path.join(out_dir, os.path.basename(separation[2]))
        stem4_file = os.path.join(out_dir, os.path.basename(separation[3]))
        os.rename(separation[0], stem1_file)
        os.rename(separation[1], stem2_file)
        os.rename(separation[2], stem3_file)
        os.rename(separation[3], stem4_file)

        return stem1_file, stem2_file, stem3_file, stem4_file

with gr.Blocks(title="🎵 Audio Separator 🎵", css="footer{display:none !important}") as app:
    with gr.Accordion("General settings", open=False):
        model_file_dir = gr.Textbox(value=MODEL_DIR, label="Directory for storing model files", placeholder=MODEL_DIR)
        with gr.Row():
            output_dir = gr.Textbox(value=OUTPUT_DIR, label="File output directory", placeholder=OUTPUT_DIR)
            output_format = gr.Dropdown(value="wav", choices=OUTPUT_FORMATS, label="Output Format")
        with gr.Row():
            norm_threshold = gr.Slider(value=0.9, step=0.1, minimum=0, maximum=1, label="Normalization", info="max peak amplitude to normalize input and output audio.")
            amp_threshold = gr.Slider(value=0.6, step=0.1, minimum=0, maximum=1, label="Amplification", info="min peak amplitude to amplify input and output audio.")

    with gr.Tab("Roformer"):
        with gr.Row():
            roformer_model = gr.Dropdown(label="Select the Model", choices=list(ROFORMER_MODELS.keys()))
        with gr.Row():
            roformer_seg_size = gr.Slider(minimum=32, maximum=4000, step=32, value=256, label="Segment Size", info="Larger consumes more resources, but may give better results.")
            roformer_overlap = gr.Slider(minimum=2, maximum=4, step=1, value=4, label="Overlap", info="Amount of overlap between prediction windows.")
        with gr.Row():
            roformer_audio = gr.Audio(label="Input Audio", type="numpy")
        with gr.Row():
            roformer_button = gr.Button("Separate!", variant="primary")
        with gr.Row():
            roformer_stem1 = gr.Audio(label="Stem 1", type="filepath", interactive=False)
            roformer_stem2 = gr.Audio(label="Stem 2", type="filepath", interactive=False)

    with gr.Tab("MDX23C"):
        with gr.Row():
            mdx23c_model = gr.Dropdown(label="Select the Model", choices=MDX23C_MODELS)
        with gr.Row():
            mdx23c_seg_size = gr.Slider(minimum=32, maximum=4000, step=32, value=256, label="Segment Size", info="Larger consumes more resources, but may give better results.")
            mdx23c_overlap = gr.Slider(minimum=2, maximum=50, step=1, value=8, label="Overlap", info="Amount of overlap between prediction windows.")
        with gr.Row():
            mdx23c_audio = gr.Audio(label="Input Audio", type="numpy")
        with gr.Row():
            mdx23c_button = gr.Button("Separate!", variant="primary")
        with gr.Row():
            mdx23c_stem1 = gr.Audio(label="Stem 1", type="filepath", interactive=False)
            mdx23c_stem2 = gr.Audio(label="Stem 2", type="filepath", interactive=False)

    with gr.Tab("MDX-NET"):
        with gr.Row():
            mdx_model = gr.Dropdown(label="Select the Model", choices=MDXNET_MODELS)
        with gr.Row():
            mdx_hop_length = gr.Slider(minimum=0.001, maximum=0.999, step=0.001, value=0.25, label="Hop Length")
            mdx_seg_size = gr.Slider(minimum=32, maximum=4000, step=32, value=256, label="Segment Size", info="Larger consumes more resources, but may give better results.")
            mdx_overlap = gr.Slider(minimum=0.001, maximum=0.999, step=0.001, value=0.25, label="Overlap")
            mdx_denoise = gr.Checkbox(value=True, label="Denoise", info="Enable denoising during separation.")
        with gr.Row():
            mdx_audio = gr.Audio(label="Input Audio", type="numpy")
        with gr.Row():
            mdx_button = gr.Button("Separate!", variant="primary")
        with gr.Row():
            mdx_stem1 = gr.Audio(label="Stem 1", type="filepath", interactive=False)
            mdx_stem2 = gr.Audio(label="Stem 2", type="filepath", interactive=False)

    with gr.Tab("VR ARCH"):
        with gr.Row():
            vr_model = gr.Dropdown(label="Select the Model", choices=VR_ARCH_MODELS)
        with gr.Row():
            vr_window_size = gr.Dropdown(minimum=320, maximum=1024, step=32, value=512, label="Window Size")
            vr_aggression = gr.Slider(minimum=1, maximum=50, step=1, value=5, label="Agression", info="Intensity of primary stem extraction.")
            vr_tta = gr.Checkbox(value=True, label="TTA", info="Enable Test-Time-Augmentation; slow but improves quality.")
            vr_post_process = gr.Checkbox(value=True, label="Post Process", info="Enable post-processing.")
            vr_post_process_threshold = gr.Slider(minimum=0.1, maximum=0.3, step=0.1, value=0.2, label="Post Process Threshold", info="Threshold for post-processing.")
            vr_high_end_process = gr.Checkbox(value=False, label="High End Process", info="Mirror the missing frequency range of the output.")
        with gr.Row():
            vr_audio = gr.Audio(label="Input Audio", type="numpy")
        with gr.Row():
            vr_button = gr.Button("Separate!", variant="primary")
        with gr.Row():
            vr_stem1 = gr.Audio(label="Stem 1", type="filepath", interactive=False)
            vr_stem2 = gr.Audio(label="Stem 2", type="filepath", interactive=False)

    with gr.Tab("Demucs"):
        with gr.Row():
            demucs_model = gr.Dropdown(label="Select the Model", choices=DEMUCS_MODELS)
        with gr.Row():
            demucs_seg_size = gr.Slider(minimum=1, maximum=100, step=1, value=50, label="Segment Size")
            demucs_shifts = gr.Slider(minimum=0, maximum=20, step=1, value=2, label="Shifts", info="Number of predictions with random shifts, higher = slower but better quality.")
            demucs_overlap = gr.Slider(minimum=0.001, maximum=0.999, step=0.001, value=0.25, label="Overlap")
            demucs_segments_enabled = gr.Checkbox(value=True, label="Segment-wise processing")
        with gr.Row():
            demucs_audio = gr.Audio(label="Input Audio", type="numpy")
        with gr.Row():
            demucs_button = gr.Button("Separate!", variant="primary")
        with gr.Row():
            demucs_stem1 = gr.Audio(label="Stem 1", type="filepath", interactive=False)
            demucs_stem2 = gr.Audio(label="Stem 2", type="filepath", interactive=False)
        with gr.Row():
            demucs_stem3 = gr.Audio(label="Stem 3", type="filepath", interactive=False)
            demucs_stem4 = gr.Audio(label="Stem 4", type="filepath", interactive=False)

    roformer_button.click(
        roformer_separator,
        inputs=[
            roformer_audio,
            roformer_model,
            roformer_seg_size,
            roformer_overlap,
            model_file_dir,
            output_dir,
            output_format,
            norm_threshold,
            amp_threshold,
        ],
        outputs=[roformer_stem1, roformer_stem2],
    )
    mdx23c_button.click(
        mdx23c_separator,
        inputs=[
            mdx23c_audio,
            mdx23c_model,
            mdx23c_seg_size,
            mdx23c_overlap,
            model_file_dir,
            output_dir,
            output_format,
            norm_threshold,
            amp_threshold,
        ],
        outputs=[mdx23c_stem1, mdx23c_stem2],
    )
    mdx_button.click(
        mdx_separator,
        inputs=[
            mdx_audio,
            mdx_model,
            mdx_hop_length,
            mdx_seg_size,
            mdx_overlap,
            mdx_denoise,
            model_file_dir,
            output_dir,
            output_format,
            norm_threshold,
            amp_threshold,
        ],
        outputs=[mdx_stem1, mdx_stem2],
    )
    vr_button.click(
        vr_separator,
        inputs=[
            vr_audio,
            vr_model,
            vr_window_size,
            vr_aggression,
            vr_tta,
            vr_post_process,
            vr_post_process_threshold,
            vr_high_end_process,
            model_file_dir,
            output_dir,
            output_format,
            norm_threshold,
            amp_threshold,
        ],
        outputs=[vr_stem1, vr_stem2],
    )
    demucs_button.click(
        demucs_separator,
        inputs=[
            demucs_audio,
            demucs_model,
            demucs_seg_size,
            demucs_shifts,
            demucs_overlap,
            demucs_segments_enabled,
            model_file_dir,
            output_dir,
            output_format,
            norm_threshold,
            amp_threshold,
        ],
        outputs=[demucs_stem1, demucs_stem2, demucs_stem3, demucs_stem4],
    )

app.launch(share=True)
