import numpy as np

data = np.array([[80, 85, 82],
                 [78, 90, 85],
                 [85, 88, 90],
                 [80, 82, 84],
                 [78, 80, 82]])

reshaped_data = data.reshape(-1,1)#-1 representive all the rows,
                                  #1 representive one column
normalized_data = (data - data.mean()) / data.std()#。std求标准差

def min_max_scale(X):
    return(X-X.min()) / (X.max()-X.min())

def standardize(X):
    return (X-X.mean()) / X.std()

x =np.random.randn(100,20)
weights = np.random.randn(20,1)
predictions =np.dot(x,weights)

x_transposed = x.T

covariance = np.cov(x.T)#协方差矩阵?

def sigmoid(x):
    return 1 / (1+np.exp(-x))

def relu(x):
    np.maximum(0,x)

def softmax(x):
    exp_x = np.exp(x-np.max(x))
    return exp_x / exp_x.sum(axis=1,keepdims=True)

def forward_layer(x,w,b,activation_fn):
    z = np.dot(x,w)+b
    a = activation_fn(z)
    return a

def batch_generator(x,t,batch_size=32):
    n_samples = x.shape[0]
    indices = np.arange(n_samples)
    np.random.shuffle(indices)

    for start_idx in range(0,n_samples-batch_size+1,batch_size):
        batch_idx = indices[start_idx:start_idx+batch_size]
        yield x[batch_idx], t[batch_idx]

def accuracy(y_true,y_pred):
    return np.mean(np.argmax(y_true,axis=1) == np.argmax(y_pred,axis=1))

def random_rotation(x,max_angle=30):
    angle = np.random.uniform(-max_angle,max_angle)
    # return scipy.ndimage.rotate(x,angle,reshape=False)

def numerical_rotation(f,x,eps=1e-8):
    grad = np.zeros_like(x)
    for i in range(x.size):
        h = np.zeros_like(x)
        h.flat[i] =eps
        grad.flat[i] = (f(x+h)-f(x-h))/(2*eps)
    return grad


    
    




