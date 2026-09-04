import torch
print("PyTorch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("PyTorch CUDA:", torch.version.cuda)
if torch.cuda.is_available():
    i = torch.cuda.current_device()
    print("GPU:", torch.cuda.get_device_name(i))
    print("VRAM GB:", round(torch.cuda.get_device_properties(i).total_memory / 1024**3, 2))
