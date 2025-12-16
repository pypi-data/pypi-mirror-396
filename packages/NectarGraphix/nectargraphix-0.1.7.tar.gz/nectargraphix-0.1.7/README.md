# NectarGraphix

**NectarGraphix** is a powerful, local image generation studio powered by Stable Diffusion. Run cutting-edge AI models directly on your hardware—no cloud dependency, no usage limits. Generate stunning visuals from text prompts with full control over models, settings, and outputs.

![NectarGraphix UI](https://private-user-images.githubusercontent.com/167107185/525810999-3ebae1cd-8c46-4af4-bf4e-1d650aea313a.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjU1MzI5OTIsIm5iZiI6MTc2NTUzMjY5MiwicGF0aCI6Ii8xNjcxMDcxODUvNTI1ODEwOTk5LTNlYmFlMWNkLThjNDYtNGFmNC1iZjRlLTFkNjUwYWVhMzEzYS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjEyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIxMlQwOTQ0NTJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1jZTFlNzkzNDdhMmU4NWUzZjhlYWVmZWUxZjEzY2M4NzdhOGY4ZDJiMzEyYWQyZjc2NGJlYzQ1YzlkMjM5OTVlJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.9h0U0cMc2LlckHLTJdahtUok62A9diWNxWOqgrFVHFA)

## ✨ Features

- **Local Stable Diffusion**: Run models like SDXL, SD 1.5, or custom fine-tunes offline.
- **Intuitive UI**: Drag-and-drop interface for prompts, images, and settings.
- **Model Management**: Download, switch, and organize models seamlessly.
- **Advanced Controls**: Negative prompts, samplers, CFG scale, steps, and resolution tweaking.
- **Batch Generation**: Create multiple images at once.
- **Hardware Optimization**: GPU/CPU detection with automatic optimizations (CUDA, ROCm, DirectML).
- **Extensions Support**: Compatible with popular LoRAs, ControlNet, and embeddings.

## 💻 Requirements

- **OS**: Windows 10+
- **Python**: 3.11.0
- **GPU** (recommended):
  - NVIDIA: 4GB+ VRAM (GTX 1060 or newer)
- **RAM**: 8GB+ (16GB recommended for larger models)
- **Disk**: 10GB+ free space for models and outputs

### 2. Download Models

Model folder structure:

├── Stable-diffusion/
  └── v1-5-pruned-emaonly.safetensors
  ├── Lora/
  └── VAE/

![Model Folder Structure](https://private-user-images.githubusercontent.com/167107185/525817684-820b24a5-c24a-47d5-a503-1d510805d28b.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjU1MzI5OTIsIm5iZiI6MTc2NTUzMjY5MiwicGF0aCI6Ii8xNjcxMDcxODUvNTI1ODE3Njg0LTgyMGIyNGE1LWMyNGEtNDdkNS1hNTAzLTFkNTEwODA1ZDI4Yi5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUxMjEyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MTIxMlQwOTQ0NTJaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT00ZTA5YzUyYzM2M2FkZWQ0NTcwNDYxZWViMWE2YmM1Mzc1OGI4MWEyZTMwNzY3OTBkYWJlMDllZjcyMjMwNTMwJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.GxKhm3pdywR9_dJnjr5LN3AQ3vyn2w42eJ6phrREuxM)

Popular sources: [Civitai](https://civitai.com), [Hugging Face](https://huggingface.co)


## 📸 Example Usage

1. Enter prompt: `A cyberpunk cityscape at sunset, neon lights, highly detailed, 8k`
2. Negative prompt: `blurry, lowres, text, watermark`
3. Set: Steps=30, CFG=7, Sampler=Euler a, Size=512x512
4. Hit **Generate** → Save or upscale results.

## 📄 License

[LICENSE]([text](https://github.com/headlessripper/Nectar-X-Studio/blob/main/LICENSE)) for details.

## 🙌 Support the Project

- ⭐ Star on GitHub
- Share your generations on socials with #NectarGraphix
- Buy me a coffee: [ko-fi.com/zashiron](https://ko-fi.com/zashiron)

---

**Built with ❤️ for local AI creators**
