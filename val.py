
import torch
from tqdm import tqdm
from torch.utils.data import DataLoader
import torchvision.transforms as T

from dataset import VisualOdometryDataset
from model import VisualOdometryModel
from params import *


# Create the visual odometry model
model = VisualOdometryModel(hidden_size, num_layers)

transform = T.Compose([
    T.ToTensor(),
    model.resnet_transforms()
])


# TODO: Load dataset
val_loader = DataLoader(
    VisualOdometryDataset(
        "dataset/val",
        transform=transform,
        sequence_length=sequence_length
    ),
    batch_size=batch_size,
    shuffle=True
)


# val
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model.to(device)
model.load_state_dict(torch.load("vo.pt"))
model.eval()

validation_string = ""
position = [0.0] * 7

with torch.no_grad():
    for images, labels, timestamp in tqdm(val_loader, f"Validating:"):

        images = images.to(device)
        labels = labels.to(device)

        target = model(images).cpu().numpy().tolist()

        # TODO: add the results into the validation_string
        model_output = model(images).cpu().numpy().tolist()

        # Add the results into the validation_string
        for timestamp, target in zip(timestamp, model_output):
            position = [pos + delta for pos, delta in zip(position, target)]
            position_str = ' '.join(map(str, position))
            validation_string += f"{timestamp} {position_str}\n"


f = open("validation.txt", "a")
f.write(validation_string)
f.close()
