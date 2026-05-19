import inspect
import owlready2
print('has _remove_imp', hasattr(owlready2.World, '_remove_imp'))
if hasattr(owlready2.World, '_remove_imp'):
    print(inspect.getsource(owlready2.World._remove_imp))
print('destroy_entity source:')
print(inspect.getsource(owlready2.destroy_entity))
