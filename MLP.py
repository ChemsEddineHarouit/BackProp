import numpy as np
from decimal import Decimal
from matplotlib import pyplot as plt
from TimedProfile import calculate_time
from Utils import *

"""
the MultiLayerPerceptron has multiple parameters:
MAX_ITER        : is the number of training
                    the training is feedforward followed by backprop functions
learnin_rate    : is the rate changing of the weights
costs           : is a list of errors in cevery iteration and it's length is obviously MAX_ITER


to create a MLP we need :   X (data) D(desired output) neurons_Hi(list of numbers of neurons of hidden layers)
                            neurons_in (number of neurons of the input layer = number of columns of X)
                            neurons_ou (number of neurons of the output layer= number of rows of Y or D)
                            Y is the output calculated by the MLP (if Y = D then we have a 100% accuracy)
                            W1, W2, W3 are the weight matrices
                            b1, b2, b3 are the biases (we integrate b in the first column of W)
                            W are initialized in random numbers while the b are initialized with 0
                            C stands for Couche and that represents the layers of the MLP
the feedforward is calculated as : 
                            C(i) = sigmoid(W(i)*C(i-1) + b(i)) and C(0) = X the input data
                                but while the b is integrated in W we just need to calculate C(i) = sigmoid(W(i)*C(i-1))
                                and we have to add a row in C(i-1) before each operation
the backward prop is calculated as:
                            dZ(i) refers to the error of the layer "i" / C(i) = sigmoid(Z(i)) but we don't use this formula
                                dZ(i) = W(i).T * dZ(i+1) * sigmoid_derivative(C(i)) with dZ(last layer) = D - Y
                            dW(i) refers to the error done in the weights W(i)
                                dWi(i) = dZ(i) * C(i-1).T
                            we have to adjust weights
                                W(i) += learning_rate * dW(i)

Matrices Shapes:
    I= neurons_in ; H= neurons_hi ; O= neurons_ou; N: number of samples

    X (I, N)  D (1, N)
    W1(H, I)  W2(O, H)
    C1(H, N)  C2(O, N)
    when we add a column to a matrix we add _c in the name
    when we add a row to a matrix we add _r in the name
        NB: remember that we add rows of 1 in C(i) and X while we add columns of b permanently in the W(i)
    so:
    feedforward:
        C(i) = sigmoid(W_c(i)*C_r(i-1)) // you can verify the shapes
    backprop:
        dW(i) = dZ(i) * C_r(i-1).T
        dZ(i) = W(i+1).T * dZ(i+1) * sigmoid_derivative(C(i)) // notice that we use here (W and C) not (W_c and C_r) so we have to remove the 1 of C and the bias from W
        W_c(i) += learning_rate * dW(i)

"""

class MLP:
    
    costs = []
    accus = []
    W = []
    C = []


    def __init__(self, X, D, neurons_hidden_list, r=0.1, MAX_ITER = 1000):
        self.learning_rate = r
        self.MAX_ITER = MAX_ITER    
        self.X           = X.T
        neurons_in       = X.shape[1]
        neurons_ou       = 1
        neurons = neurons_hidden_list
        neurons.append(neurons_ou)

        for i, nb_neurons_out_of_layer in enumerate(neurons_hidden_list):
            nb_neurons_in_of_layer = 0
            if(i == 0):
                nb_neurons_in_of_layer = neurons_in
            elif (i == len(neurons_hidden_list)):
                nb_neurons_in_of_layer = neurons_ou
            else:
                nb_neurons_in_of_layer = neurons_hidden_list[i-1]
            W    = np.random.rand(nb_neurons_out_of_layer,nb_neurons_in_of_layer)
            b    = np.zeros((nb_neurons_out_of_layer, 1))
            self.W.insert(i, np.c_[b, W]) 

        self.D           = D


        self.Y          = np.zeros(self.D.shape)
        print(' ANN : %s'%(neurons_hidden_list))
        print(' Data : X:%s and D:%s'%(X.shape, D.shape))
        print(' Weights : ', end='')
        printShapes('W', self.W)
        print('\n------------------')

    def feedforward(self):
        for i, w in enumerate(self.W):
            layer_in = None
            if(i == 0):
                layer_in = self.X
            else:
                layer_in = self.C[i-1]
            self.C.insert(i, sigmoid(np.dot(w, add_1_r(layer_in))))
        self.Y = self.C[-1]

    def calc_cost(self, err):
        cost = 0.5 * np.sum(np.square(err))
        return cost

    def calc_error(self):
        err = ((self.D - self.Y))
        self.costs.append(self.calc_cost(err))
        self.accus.append(self.calc_acc())
        return err
    
    def calc_acc(self):
        Y = np.round(np.squeeze(self.Y))
        D = np.squeeze(self.D)
        nbTrue = 0
        for i in range(len(D)):
            result = Y[i] == D[i]
            if(result):
                nbTrue += 1 
        return 100*(nbTrue / len(D))

    def backprop(self):

        dZ =  {}
        dW = {}
        for i in range(len(self.W)-1, -1, -1):
            if(i == len(self.W) - 1):
                dZ[i] =  self.calc_error()
            else:
                dZ[i] = np.multiply(np.dot(rem_1st_c(self.W[i+1]).T, dZ[i+1]), sigmoid_deriv(self.C[i]))
            
            if(i == 0):
                inputLayer = self.X
            else:
                inputLayer = self.C[i-1]
            dW[i] = np.dot(dZ[i], add_1_r(inputLayer).T)

        r = self.learning_rate
        
        for i  in range(0, len(self.W)):
            self.W[i] = self.W[i] + r * dW[i] 

      
    @calculate_time
    def train(self):
        for i in range(self.MAX_ITER):
            self.feedforward()
            self.backprop()
            # print(self.W)
    
    def predict(self, X, D):
        self.X = X.T
        self.D = D
        self.feedforward()

        # print('Predicted   Desired  Result')
        Y = np.round(np.squeeze(self.Y))
        D = np.squeeze(self.D)
        nbTrue = 0
        for i in range(len(D)):
            result = Y[i] == D[i]
            if(result):
                nbTrue += 1 
        #     print('%d ... %d ... %d'%(Y[i], D[i], result))
        # print('Accuracy = %d / 100'% (100*(nbTrue / len(D))))
        return 100*(nbTrue / len(D))

    def plotErrors(self):
        errors = self.costs
        plt.plot(errors);
        plt.title("IRIS Erros")
        plt.xlabel('iteration')
        plt.ylabel('Error')
        plt.show()
        
    def plotAcc(self):
        accus = self.accus
        plt.plot(accus);
        plt.title("IRIS Accuracy")
        plt.xlabel('iteration')
        plt.ylabel('Accuracy')
        plt.show()



