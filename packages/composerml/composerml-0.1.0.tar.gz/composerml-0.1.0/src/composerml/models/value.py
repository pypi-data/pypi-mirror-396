from math import tanh, exp, log


class Value:
    def __init__(self, data, _children = (),_op= '' , label = '' ):
        self.data = data
        self.grad = 0
        self._backward = lambda: None #containing the function that calculate the gradients of its children
        self._prev = set(_children) #containing pointers to children 
        self._op = _op
        self.label = label 
        
    def __repr__(self):
        return f"Value: {self.data}, Grad: {self.grad}"
    
    @staticmethod
    def _as_value(x):
        """Convert to Value if not already a Value"""
        return x if isinstance(x, Value) else Value(x)
    
    
    #arithmetic operations
    def __add__(self, other):
        other = Value._as_value(other)
        out = Value(self.data + other.data, (self, other), '+')
        
        def _backward():
            self.grad += 1 * out.grad
            other.grad += 1 * out.grad
        
        out._backward = _backward    
        return out
    
    def __radd__(self, other):
        return self + other
    
    #-------------------------------
    def __mul__(self,other):
        other = Value._as_value(other)
        out = Value(self.data * other.data, (self, other), "*")
        
        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        
        out._backward = _backward
        
        return out
            
    def __rmul__(self, other):
        return self * other
    
    #-------------------------------
    def __neg__(self):
        out = Value(-self.data, (self,), 'neg')
        
        def _backward():
            self.grad += -1 * out.grad
        out._backward = _backward
        
        return out
        
    def __sub__(self, other):
        other = Value._as_value(other)
        return self + (-other)
    
    def __rsub__(self,other):
        other = Value._as_value(other)
        return other + (-self)
    
    #-------------------------------
    def __truediv__(self, other):
        other = Value._as_value(other)
        return self * (other ** -1)
    
    def __rtruediv__(self, other):
        other = Value._as_value(other)
        return other * (self ** -1)
    #-------------------------------
    
    def __pow__(self, other):
        assert isinstance(other, (int,float)), "power must be int/float"
        
        out = Value(self.data ** other, (self,), f"**")
        
        def _backward():
            self.grad += other * (self.data ** (other - 1)) * out.grad
        
        out._backward = _backward
        return out
    
    
    #-------------------------------
        
    def tanh(self):
        out = Value(tanh(self.data), (self,), "tanh")
        
        def _backward():
            self.grad += (1 - out.data**2) * out.grad
        
        out._backward = _backward
        
        return out
    
    def exp(self):
        out  = Value(exp(self.data), (self,), "exp")
        
        def _backward():
            self.grad += out.data * out.grad
        out._backward = _backward
        
        return out
    
    def relu(self):
        out = Value(0 if self.data < 0 else self.data, (self,), "ReLU")
        
        def _backward():
            self.grad += (out.data > 0) * out.grad
        
        out._backward = _backward
        
        return out
    
    def log(self):
        out = Value(log(self.data), (self,), "log")
        
        def _backward():
            self.grad += (1 / self.data) * out.grad
        
        out._backward = _backward
        
        return out
    
    def clamp(self):
        """Avoid 0 or 1 values for numerical stability in log/sigmoid"""
        epsilon = 1e-15
        if self.data < epsilon:
            return Value(epsilon)
        elif self.data > 1 - epsilon:
            return Value(1 - epsilon)
        else:
            return self
    

    #-------------------------------
    #Call this on the output node
    def backward(self):
        """Calculate the gradients of all nodes in the graph using backpropagation"""
        # Use topological sort to calculate all the gradients backwards 
        topo = []
        visited = set()

        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)
            

        build(self)
        topo.reverse()

        # Intialize the output at the output node
        self.grad = 1.0

        # 3. Traverse in reverse topological order and propagate gradients
        for v in topo:
            v._backward()