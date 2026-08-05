import numpy as np
import matplotlib.pyplot as plt

#simulation settings
n_layers = 50 
n_neurons = 100
n_samples = 100

#input
x = np.random.randn(n_samples,n_neurons) #matrix with size n_samples , n_neurons that randomizes values according to normalization

def for_back_pass(std_dev) :
    activations= [x] #store activations of each layer 
    layer_input = x.copy () 

    for _ in range(n_layers):
        W = np.random.randn(n_neurons,n_neurons) * std_dev #initialzing weights (n_in x n_out of the neuron layer)

        layer_output = np.dot(layer_input , W) #linear transoform

        layer_output = np.maximum(0,layer_output) #ReLU -> cuts negatives to zeros

        activations.append(layer_output)
        layer_input = layer_output #the output of the first layer is the input for the 2nd layer-

    
    activations_std = [a.std()for a in activations[1:]] #calculates std of each activation , ignoring first one as we set its std manually



    #Backward pass
    grad_output = np.ones_like(activations[-1]) #creats an array of all 1s with the same shape as passed
    #-1 to start for the last one
    grad_std = []

    for layer_index in reversed(range(n_layers)):
        #backprop through relu , caring only about values about 0 
        grad_output = grad_output * (activations[layer_index+1] > 0)

        #backprop through weights
        w = np.random.randn(n_neurons,n_neurons) * std_dev
        grad_output = np.dot(grad_output , W.T)

        grad_std.append(grad_output.std())
    
    grad_std.reverse() #now from layer 1 to last

    return activations_std , grad_std


act_small , grad_small = for_back_pass(0.01)

act_large , grad_large = for_back_pass(1.0)

good_std = np.sqrt(2.0 / n_neurons)
act_good , grad_good = for_back_pass(good_std)


##plotting 

plt.subplot(1,2,1)
plt.plot(act_small,label = 'Too small')
plt.plot(act_large, label = "too large")
plt.plot(act_good,label = "good")

plt.title("Activation std by layer")
plt.xlabel("Layer")
plt.ylabel("Std dev")
plt.legend()
plt.grid(True)


plt.subplot(1,2,2)
plt.plot(grad_small, label="Too small σ (0.01)")
plt.plot(grad_large, label="Too large σ (1.0)")
plt.plot(grad_good, label=f"He init σ ({good_std:.3f})")
plt.title("Gradient Std Dev by Layer")
plt.xlabel("Layer")
plt.ylabel("Std Dev")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()