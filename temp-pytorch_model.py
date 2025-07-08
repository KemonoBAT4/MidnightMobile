import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
# Set random seed for reproducibility
torch.manual_seed(42)
# Check if CUDA (GPU support) is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
# --- Step 1: Data Loading and Preprocessing ---
# Transform images to tensors and normalize them
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST mean and std
])
# Download and load training dataset
train_dataset = datasets.MNIST(
    root='./data', 
    train=True, 
    download=True, 
    transform=transform
)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
# Download and load test dataset
test_dataset = datasets.MNIST(
    root='./data', 
    train=False, 
    download=True, 
    transform=transform
)
test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)


# --- Step 2: Define the Neural Network ---
class MNIST_Classifier(nn.Module):
    def __init__(self):
        super(MNIST_Classifier, self).__init__()
        self.fc1 = nn.Linear(28*28, 128)  # Flattened 28x28 image
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)     # Output for 10 digits (0-9)
    def forward(self, x):
        x = x.view(-1, 28*28)  # Flatten the input
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
model = MNIST_Classifier().to(device)


# --- Step 3: Loss Function and Optimizer ---
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
# --- Step 4: Train the Model ---
def train(model, device, train_loader, optimizer, criterion, epoch):
    model.train()
    train_loss = 0
    correct = 0
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        # Print progress every 100 batches
        if batch_idx % 100 == 0:
            print(f"Epoch: {epoch} | Batch: {batch_idx}/{len(train_loader)} | Loss: {loss.item():.4f}")
    train_acc = 100. * correct / len(train_loader.dataset)
    avg_loss = train_loss / len(train_loader)
    print(f"\nTraining Epoch: {epoch} | Avg Loss: {avg_loss:.4f} | Accuracy: {train_acc:.2f}%\n")

    print(f"\nTraining Epoch: {epoch} | Avg Loss: {avg_loss:.4f} | Accuracy: {train_acc:.2f}%\n")
# --- Step 5: Evaluate the Model ---
def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
    test_acc = 100. * correct / len(test_loader.dataset)
    avg_loss = test_loss / len(test_loader)
    print(f"Test Results - Loss: {avg_loss:.4f} | Accuracy: {test_acc:.2f}%")
# --- Step 6: Training Loop ---
num_epochs = 5
for epoch in range(1, num_epochs + 1):
    train(model, device, train_loader, optimizer, criterion, epoch)
    test(model, device, test_loader)
# (Optional) Save the trained model
torch.save(model.state_dict(), "mnist_model.pth")


# (Optional) Plot some predictions
def plot_predictions():
    model.eval()
    with torch.no_grad():
        data, target = next(iter(test_loader))
        data, target = data.to(device), target.to(device)
        output = model(data)
        pred = output.argmax(dim=1)
        fig, axes = plt.subplots(3, 3, figsize=(10, 10))
        for i, ax in enumerate(axes.flat):
            ax.imshow(data[i].cpu().numpy().squeeze(), cmap='gray')
            ax.set_title(f"Predicted: {pred[i].item()}, True: {target[i].item()}")
            ax.axis('off')
        plt.tight_layout()
        plt.show()
plot_predictions()
