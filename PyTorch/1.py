import torch
import numpy as np

x = torch.tensor([[1, 2],[3,4]])
y = torch.from_numpy((np.array([1,2,3])))

zeros = torch.zeros(2, 3)
ones = torch.ones(2, 3,dtype=torch.float32)
rand = torch.rand(2, 3)
randn = torch.randn(2, 3)
print(x, y, zeros, ones, rand, randn)
print(x.dtype, y.dtype, zeros.dtype, ones.dtype, rand.dtype, randn.dtype)

if torch.cuda.is_available():
    device = torch.device("cuda")
    cuda_t = torch.tensor([1,2,3]).to('cuda')

t = torch.rand(2,3,dtype=torch.float64)
print(t.shape)
print(t.size())
print(t.dim())
print(t.device)
print(t.requires_grad)
print(t.dtype)


