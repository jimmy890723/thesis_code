import torch
tensor = torch.rand(3,4)
print(f"Device tensor is stored on: {tensor.device}")
# Device tensor is stored on: cpu

print(torch.cuda.is_available())
#True

print(torch.cuda.device_count())
#GPU数量， 1

print(torch.cuda.current_device()) #当前GPU的索引， 0

print(torch.cuda.get_device_name(0)) #输出GPU名称

tensor = tensor.to('cuda')
print(f"Device tensor is stored on: {tensor.device}")
# Device tensor is stored on: cuda:0


x = torch.tensor([1, 2, 3])
x = x.cuda(0)
print(x.device)