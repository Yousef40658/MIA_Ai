import torch
import torch.nn as nn
import torch.optim as optim
from torchvision  import datasets, transforms
import torch.nn.functional as F

device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
print (f'Using device {device}')

#Model
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(28*28 , 128) #input layer -> hidden
        self.fc2 = nn.Linear(128,64)      #hidden layer
        self.fc3 = nn.Linear(64,10)        #hidden -> output

    def forward(self, x) :
        x = x.view(-1,28*28)                #reshape the 2D image into 1D vector
        x = F.relu(self.fc1(x))             #layer 1 relu  #returnes the output of layer 1 after reluing it
        x = F.relu(self.fc2(x))             #feed output of layer 1 to layer  2 relu
        x = self.fc3(x)
        return x



#compose takes a list of transoforms and chaing them together
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,),(0.5,))])

#downloading a data_set
train_dataset = datasets.MNIST\
(
    root = "./data",
    train=True,
    transform=transform,
    download=True
)

test_dataset = datasets.MNIST\
(
    root = "./data",
    train = False,
    transform = transform,
    download = True
)

#Dataloader to help with batch and shuffeling data
train_loader = torch.utils.data.DataLoader(
    dataset = train_dataset,
    batch_size = 64,
    shuffle = True
)

test_loader = torch.utils.data.DataLoader(
    dataset= test_dataset,
    batch_size= 64,
    shuffle= False
)

print ("Traning batches" , len(train_loader))
print ("Testing batches" , len(test_loader))

model = SimpleNet()
model = model.to(device)

print (model)

#loss function

criterion = nn.CrossEntropyLoss()

#optimizer 
optimizer =  optim.Adam(model.parameters() , lr= 0.001)

#training
num_epochs = 15

for epoch in range (num_epochs) :
    for batch_idx , (images,labels) in enumerate(train_loader) :
            images , labels = images.to(device), labels.to(device)  #pytorch models and tensors must be on the same device

            outputs = model(images)
            loss = criterion(outputs,labels)

            #zero previous gradients
            optimizer.zero_grad()
            #backward pass -> computing gradients
            loss.backward() 

            #update the weights
            optimizer.step()

            if ((batch_idx % 100) == 0) :
                    print(f'Epoch [{epoch+1}/{num_epochs}], Batch [{batch_idx}/{len(train_loader)}], Loss: {loss.item():.4f}')


#Testing
model.eval()
correct = 0 
total = 0 

with torch.no_grad():
     for images,labels in test_loader :
          images,labels = images.to(device) , labels.to(device)
          outputs = model(images)
          _, predicted = torch.max(outputs.data , 1)
          total += labels.size(0)
          correct += (predicted == labels).sum().item()

print(f'Test Accuracy: {100 * correct / total:.2f}%')