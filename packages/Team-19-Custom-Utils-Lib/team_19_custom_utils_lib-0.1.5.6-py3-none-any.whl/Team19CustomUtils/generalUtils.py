import numpy as np

def get_ratio(num1, num2):
    """
    calculates the ratio between two numbers
    Args:
        num1: first number
        num2: second number
    Returns: 
        _: the ratio between the greater and lesser number (lesser/greater)
        state: a variable indicating which number is larger

    Dependencies: 
        None
    """

    if(num1 > num2):
        state = 1
        return ((num2/num1), state)

    elif(num2 > num1):
        state = 2
        return ( (num1/num2), state)

    else:
        return 0

def a_sum(input):
    """
    calculates the sum of an array
    Args:
        input: a one-dimensional array
    Returns: 
        sum: the sum of all values in the array

    Dependencies: 
        None
    """
    sum = 0
    for i in range (0, len(input)):
            sum += input[i]

    return sum

def a_mean(input):
    """
    calculates the mean of an array
    Args:
        input: a one-dimensional array
    Returns: 
        the mean of the one-dimensional array

    Dependencies: 
        None
    """
    return ( a_sum(input) / len(input) )

def transpose_matrix(input: list):
    """
    transposes an input matrix
    args:
        input (2d arr): input matrix which will be transposed
    returns:
        m_transposed (2d arr): transposition of input matrix
    """
    m_transposed = input.copy()
    for i in range(0, len(input)):
        for j in range(0, len(input[0])):
            m_transposed[i][j] = input[j][i]
    
    return m_transposed

def a_reduceDims(input:list):
    output = [0] * ( len(input) * len(input[0]) )
    k = 0
    for i in range(0, len(input)):
        for j in range(0, len(input[0])):
            output[k] = input[i][j]
            k += 1
    
    return output
            
def a_snip(input:list):
    l = 0
    for i in range(0, len(input)):
        if(input[i] != 0):
            l += 1

    output = [0] * l
    for i in range(0, output):
        output[i] = input[i]

    return output


def contains(input:list, target):

    dims = np.ndim(input)
    if dims > 1:
        for i in range(dims, 1, - 1):
            input = a_reduceDims(input)
    
    for i in range(0, len(input)):
        if(input[i] == target):
            return 1
        
    return 0

def scanInput(mode:str, outputContainer, ranges:list, message: str):
    outputContainer = getI(outputContainer)
    print(message)
    match mode:
        case 'range':
            minVal = min(ranges)
            maxVal = max(ranges)

            while (outputContainer < minVal) or (outputContainer > maxVal):
                print('Invalid input, please try again.')
                print('Valid inputs range from', minVal, 'to', maxVal )
                print(message)

                outputContainer = getI(outputContainer)
        case 'match': 
            while contains(ranges, outputContainer) == 0:
                
                print('Invalid input, please try again.')
                print('Valid inputs are', ranges)
                print(message)

                outputContainer = getI(outputContainer)
        
        case _:
            return ValueError("unspecified or invalid mode declaration")
        
        
def getI(outputContainer):
    if isinstance(outputContainer, int) == True:
        outputContainer = int(input(''))
    elif isinstance(outputContainer, float) == True:
        outputContainer = float(input(''))
    else:
        return TypeError('Input container is not of int or float type')
    return outputContainer



    
        
    