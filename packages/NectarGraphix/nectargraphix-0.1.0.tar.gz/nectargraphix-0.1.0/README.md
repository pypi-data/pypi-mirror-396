# NectarGraphix

**NectarGraphix** is a powerful, local image generation studio powered by Stable Diffusion. Run cutting-edge AI models directly on your hardware—no cloud dependency, no usage limits. Generate stunning visuals from text prompts with full control over models, settings, and outputs.

![NectarGraphix Demo](https://via.placeholder.com/800x400/FFD700/000000?text=NectarGraphix+Demo) <!-- Replace with your actual screenshot -->

## ✨ Features

- **Local Stable Diffusion**: Run models like SDXL, SD 1.5, or custom fine-tunes offline.
- **Intuitive UI**: Drag-and-drop interface for prompts, images, and settings.
- **Model Management**: Download, switch, and organize models seamlessly.
- **Advanced Controls**: Negative prompts, samplers, CFG scale, steps, and resolution tweaking.
- **Batch Generation**: Create multiple images at once.
- **Hardware Optimization**: GPU/CPU detection with automatic optimizations (CUDA, ROCm, DirectML).
- **Extensions Support**: Compatible with popular LoRAs, ControlNet, and embeddings.

## 💻 Requirements

- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.10 or 3.11
- **GPU** (recommended):
  - NVIDIA: 4GB+ VRAM (GTX 1060 or newer)
  - AMD: ROCm-compatible (RX 5000+)
  - Apple Silicon: M1/M2/M3/M4
- **RAM**: 8GB+ (16GB recommended for larger models)
- **Disk**: 10GB+ free space for models and outputs

## 🚀 Quick Start

### 1. Clone & Install
git clone https://github.com/yourusername/NectarGraphix.git
cd NectarGraphix
pip install -r requirements.txt


### 2. Download Models
Launch once to auto-download a starter model (SD 1.5), or place models in `models/Stable-diffusion/`:

models/
├── Stable-diffusion/
│ └── v1-5-pruned-emaonly.safetensors
├── Lora/
└── VAE/


Popular sources: [Civitai](https://civitai.com), [Hugging Face](https://huggingface.co)

### 3. Run the App

python app.py

Or use the one-click launcher: `launch.bat` (Windows) / `launch.sh` (Linux/macOS).

The UI opens at `http://127.0.0.1:7860`.

## ⚙️ Configuration

Edit `config.yaml` for custom defaults:

webui:
port: 7860
share: false # Enable public URL (ngrok)
models:
default: "v1-5-pruned-emaonly.safetensors"
hardware:
gpu: auto # cuda, rocm, directml, cpu


## 📸 Example Usage

1. Enter prompt: `A cyberpunk cityscape at sunset, neon lights, highly detailed, 8k`
2. Negative prompt: `blurry, lowres, text, watermark`
3. Set: Steps=30, CFG=7, Sampler=Euler a, Size=512x512
4. Hit **Generate** → Save or upscale results.

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of VRAM | Reduce resolution or use `--medvram` flag |
| No GPU detected | Install CUDA 12.1+ or check `python detect_hardware.py` |
| Slow generation | Enable xformers: `pip install xformers` |
| Model not loading | Verify .safetensors checksum on Civitai |

**Logs**: Check `logs/app.log` for errors.

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/amazing-ui`
3. Commit changes: `git commit -m 'Add dark mode toggle'`
4. Push: `git push origin feature/amazing-ui`
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## 🙌 Support the Project

- ⭐ Star on GitHub
- Share your generations on socials with #NectarGraphix
- Buy me a coffee: [ko-fi.com/yourusername](https://ko-fi.com/yourusername)

---

**Built with ❤️ for local AI creators**
