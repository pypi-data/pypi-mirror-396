# hackwhiz

Tiny NumPy-based tensors, layers, and optimizers intended for teaching and quick experiments.

## Features
- Lightweight `Tensor` wrapper with handy creation helpers (`rand`, `randn`, `zeros`, `ones`, `eye`, `arange`) and NumPy interoperability.
- Minimal neural network pieces: `Linear`, `Relu`, `CrossEntropy`, and a simple `Module` interface.
- Straightforward SGD optimizer plus `Dataset` and `DataLoader` utilities for batching.
- Pure Python on top of NumPy, so it runs anywhere NumPy does.

## Installation
```bash
pip install hackwhiz
```

## Quickstart
```python
import hackwhiz as hw
from hackwhiz import nn, optim

hw.manual_seed(7)

class Model(nn.Module):
    def __init__(self):
        self.layers = [
            nn.Linear(2, 4),
            nn.Relu(),
            nn.Linear(4, 2),
        ]
        self.loss = nn.CrossEntropy()

    def forward(self, x, targ):
        for layer in self.layers:
            x = layer(x)
        return self.loss(x, targ)

    def backward(self):
        self.loss.backward()
        for layer in reversed(self.layers):
            layer.backward()

model = Model()
opt = optim.SGD(model.parameters(), lr=0.1)

x = hw.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [0.0, 0.0]])
y = hw.tensor([0, 1, 0, 1])

for _ in range(50):
    opt.zero_grad()
    loss = model(x, y)
    model.backward()
    opt.step()

print(f"final loss: {loss.item():.4f}")
```

## Development
- Create an environment and install in editable mode: `python -m venv .venv && source .venv/bin/activate && pip install -e .`.
- Run the example script above to sanity-check changes.
- Build a release: `pip install build twine && python -m build` then `twine check dist/*` and `twine upload dist/*`.
