import math as m
import numpy as np
from Team19CustomUtils import generalUtils

def calculate_sigmoid(z: any):
    """
    calculates the position of an input z according to a rational normalization function
    args:
        z (float): any input number
    returns:
        output (float): the value of the function 1/ (1 + e^-x). A small deviation is added to this value to prevent e^-x from inflating to infinity or diminishing to 0

    """
    e0 = 0.00000000465661287 #2^-31, a value small enough that it should not affect calculation results while staying within most common bounds of negative power floats
                             #it additionally has the benefit of being albe to be precisely represented as a power of 2, greatly reducing floating point error
                             #this value has been entered manually to avoid fallbacking on outside modules, which may introduce their own inconsistencies when constructing stabilizer values
    
    output = 1/(1+ m.exp((-1 * z) + e0))
    #e0 stabilizes the denominator and prevents division by 0
    
    return output

def predict_proba(X: list, w: list, b: float):
    """
    calculates the probability for all examples in a dataset
    args:
        X (2d arr): feature matrix in which len(X) returns the number of examples and len(X[0]) returns the number of features
        w (1d arr): weight vector where len(w) matches with len(X[0])
        b (float): bias factor
    returns:
        z (1d arr): probability array where len(z) matches with len(x)

                        matrix multiplication between two matrices x * y and y * z will return an output matrix of x * z
                        in this case, matrix multiplication is performed between one of shape m * n and one of shape n * 1,
                        resulting in an output shape of m * 1

                        this value is then normalized to the sigmoid function to complete the probability array
    """
    z = X @ w + b
    for i in range(0, len(z)):
        z[i] = calculate_sigmoid(z[i])


    print(np.shape(z))
    return z

def predict_labels(X: list, w: list, b: float, threshold = 0.5):
    """
    converts probabilities to binary class labels (0 or 1)
    args:
        X (2d arr): feature matrix in which len(X) returns the number of examples and len(X[0]) returns the number of features
        w (1d arr): weight vector where len(w) matches with len(X[0])
        b (float): bias factor
        threshold (float): pre-defined comparison threshold. values over this will be designated 1 and values under this will be designated 0
                           the break-even point is equivalent to threshold, so values exactly equivalent to this value will additionally be designated 1

    returns:
        z(1d array): binary classified probability array where len(z) matches with len(X)

                        matrix multiplication between two matrices x * y and y * z will return an output matrix of x * z
                        in this case, matrix multiplication is performed between one of shape m * n and one of shape n * 1,
                        resulting in an output shape of m * 1
    """
    z = predict_proba(X, w, b)
    for i in range(0, len(z)):
        if(z[i] < threshold): 
            z[i] = 0
        else:
            z[i] = 1
    
    return z

def compute_loss_and_grads(X: list, y_true: list, w: list, b: float):
    """
    calculates and applies gradient loss to input data
    args:
        X (2d arr): feature matrix in which len(X) returns the number of examples and len(X[0]) returns the number of features
        y_true (1d arr): true label values
        w (1d arr): weight vector where len(w) matches with len(X[0])
        b (float): bias factor
    returns:
        loss (float): a loss value indicating the inaccuracy of the model
        dw (1d arr): step distance of weight vectors
        db (float): step distance of bias
    """
    y_pred = predict_labels(X, w, b)
    loss = get_loss(y_true, y_pred)
    
    temp1, temp2, dw, db = gradient_loss(X, w, b, y_true)

    return loss, dw, db

def get_loss(y_true: list, y_pred: list):
    """
    calculates the loss by comparing true y to predicted y
    args:
        y_true (1d arr): true label of input values
        y_pred (1d arr): predicted labels of values
    returns:
        loss (float): multi-vector loss sum for the entire dataset
    """
    m = len(y_true)
    loss = -1 * 1/m
    sum = 0
    for i in range(0, m):
        sum += y_true[i] * m.log(y_pred[i], 10) + (1 - y_true[i]) * m.log((1-y_pred[i]), 10)

    loss += sum
    return loss

def gradient_loss(X: list, w: list, b: float, y_true: list):
    """
    updates the values of w and b according to gradient loss function
    args:
        X (2d arr): feature matrix in which len(X) returns the number of examples and len(X[0]) returns the number of features
        w (1d arr): weight vector array
        b (float): bias factor
        y_true (1d arr): true label of input values
    returns:
        w (1d arr): adjusted weight vector array
        b (float): adjusted bias factor
        dL_w (1d arr): step distance of weight vector array
        dL_b (float): step distance of bias factor

    """


    y_pred = predict_labels(X, w, b)
    a = 0.001
    X_t = generalUtils.transpose_matrix(X)
    m = len(X)
    dL_w = 1/m * X_t @ (y_pred - y_true)
    dL_b = 1/m 
    dsum = 0
    for i in range(0, len(y_true)):
        dsum += (y_pred[i] - y_true[i])
    dL_b *= dsum
    
    w -= (a * dL_w)
    b -= (a * dL_b)

    return w, b, dL_w, dL_b

def train_logistical_regression(X_train: list, y_train: list, a: float, num_iters: int):
    """
    trains the model using gradient descent
    args:
        X_train (2d arr): training feature matrix
        y_train (1d arr): training labels array
        a (float): learning rate
        num_iters: upper limit to update cycles
    returns:
        w(1d arr): finalized weight data
        b (float): finalized bias data
        loss_history (1d arr): record of previous loss values before final iteration
    """
    m, n = X_train.shape

    w = np.random.randn(n) * 0.01
    b = 0.0


    loss_history = [0] * num_iters
    for i in range(0, num_iters):
        loss, dw, db = compute_loss_and_grads(X_train, y_train, w, b)
        w -= a * dw
        b -= b * dw
        loss_history[i] = loss

    return w, b, loss_history

def calculate_metrics(y_pred: list, y_true: list):
    """
    calcultes the efficacy in which the prediction labels match true labels
    args:
        y_pred (1d arr): predicted labels array
        y_true (1d arr): true labels array
    returns:
        accuracy (float): the accuracy rate of predictions that match true values
        error_rate (float): the inverse of accuracy - a measurement of how many predictions deviate from true values
    """
    accuracy = np.mean(y_pred == y_true)
    error = 1 - accuracy

    return accuracy, error

def evaluate_logistical_regression(X: list, y: list, w: list, b: float):
    """
    evaluates the effectiveness of a trained dataset on new data
    args:
        X (2d arr): sample data to evaluate upon
        y (1d arr): sample labels to evaluate upon
        w (1d arr): finalized weight vectors
        b (float): finalized bias scalar
    returns:
        accuracy (float): a measurement of the amount of successful predictions
        error_rate (float): a measurement of the amount of unsuccessful predictions
    """
    y_pred = predict_labels(X, w, b)
    accuracy, error_rate = calculate_metrics(y_pred, y)

    return accuracy, error_rate

