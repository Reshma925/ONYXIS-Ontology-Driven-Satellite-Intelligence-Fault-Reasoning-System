import inspect
import owlready2
print('Imp', owlready2.Imp)
print('signature', inspect.signature(owlready2.Imp))
print('doc', owlready2.Imp.__doc__)
