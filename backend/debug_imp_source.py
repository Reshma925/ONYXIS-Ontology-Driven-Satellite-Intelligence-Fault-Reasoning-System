import inspect
import owlready2
print('signature', inspect.signature(owlready2.Imp))
print('source:')
print(inspect.getsource(owlready2.Imp.__init__))
