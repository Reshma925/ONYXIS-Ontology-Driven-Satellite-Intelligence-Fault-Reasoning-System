import inspect
import owlready2

print('Imp attributes:')
print([a for a in dir(owlready2.Imp) if not a.startswith('_')])
print('\nImp __destroy__ sig:', inspect.signature(owlready2.Imp.__destroy__))
print('\nWorld _remove_imp exists:', hasattr(owlready2.World, '_remove_imp'))
if hasattr(owlready2.World, '_remove_imp'):
    print('World _remove_imp sig:', inspect.signature(owlready2.World._remove_imp))

print('\ndestroy_entity exists:', hasattr(owlready2, 'destroy_entity'))
if hasattr(owlready2, 'destroy_entity'):
    print('destroy_entity sig:', inspect.signature(owlready2.destroy_entity))
