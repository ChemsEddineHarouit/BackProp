import numpy as np
from matplotlib import pyplot as plt


class MLP(object):

    accus  = []
    errors = []

    def __init__(self, nodes_in, nodes_hi, nodes_ou, learning_rate):
        # Set number of nodes in input, hidden and output layers.
        self.nodes_in = nodes_in
        self.nodes_hi = nodes_hi
        self.nodes_ou = nodes_ou

        # Initialize weights
        self.W1 = np.random.normal(0.0, self.nodes_in**-0.5, 
                                       (self.nodes_in, self.nodes_hi))

        self.W2 = np.random.normal(0.0, self.nodes_hi**-0.5, 
                                       (self.nodes_hi, self.nodes_ou))
        self.lr = learning_rate
        
        self.activation_function = lambda x : 1/(1+np.exp(-x))  # Replace 0 with your sigmoid calculation.
                    


    def train_it(self, X, D, ITERATIONS = 1000):
        for i in range(ITERATIONS):
            self.train(X, D)
            if(i%100 == 0):
                print('Iteration : %d'% i)


    def train(self, X, D):
        N = X.shape[0]
        dW1 = np.zeros(self.W1.shape)
        dW2 = np.zeros(self.W2.shape)
        Y      = []
        for X, y in zip(X, D):
            C1 , C2  = self.forward_pass_train(X)
            Y.append(C2)
            dW1, dW2 = self.backpropagation(C1, C2, X, y, dW1, dW2)
        self.update_weights(dW1, dW2, N)
        self.errors.append(self.calc_error(D, Y))
        self.accus.append(self.calc_acc(D, Y))


    def forward_pass_train(self, X):
        Z1 = np.dot(X,self.W1) # signals into hidden layer
        C1 = self.activation_function(Z1) # signals from hidden layer

        Z2 = np.dot(C1,self.W2) # signals into final output layer
        C2 = Z2 # signals from final output layer
        
        return C1, C2

    def backpropagation(self, C1, C2, X, y, dW1, dW2):
        error2      = y-C2 
        error2_term = error2 
        dW2        += error2_term * C1[:,None]
        
        error1      = np.dot(error2, self.W2.T)
        error1_term = error1 * C1 * (1-C1)
        dW1        += error1_term *  X[:,None]
        
        return dW1, dW2

    def update_weights(self, dW1, dW2, N):
            self.W2 += self.lr * dW2 / N 
            self.W1 += self.lr * dW1 / N 

    def run(self, X, D):
        C1 , C2  = self.forward_pass_train(X)
        Y = C2
        self.accus.append(self.calc_acc(D, Y, verbose=True))
        self.errors.append(self.calc_error(D, Y))
        return C2

    def calc_error(self, D, Y):
        Y = np.squeeze(Y)
        error = 0.5 * np.sum(np.square(D - Y))
        return error
    
    def calc_acc(self, D, Y, verbose = False,):
        if(verbose):
            print('Predicted   Desired  Result')
        Y = np.round(np.squeeze(Y))
        D = np.squeeze(D)
        nbTrue = 0
        for i in range(len(D)):
            result = Y[i] == D[i]
            if(result):
                nbTrue += 1 
            if(verbose):
                print('%d ... %d ... %d'%(Y[i], D[i], result))
        if(verbose):
            print('Accuracy = %d / 100'% (100*(nbTrue / len(D))))
        return 100*(nbTrue / len(D))

  
    def plotErrors(self):
        plt.plot(self.errors)
        plt.title("IRIS Erros")
        plt.xlabel('iteration')
        plt.ylabel('Error')
        plt.show()
        
    def plotAcc(self):
        plt.plot(self.accus)
        plt.title("IRIS Accuracy")
        plt.xlabel('iteration')
        plt.ylabel('Accuracy')
        plt.show()