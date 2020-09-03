""" DEFINE EXAMPLE """
# import kubism resources
from kubism.kubism import Model, Object, Field

#import kubism.kube
#kubism.kube.DEBUG = True

# Main example code
def main():
    # Create new model
    model = Model() # Defaults status to SETUP
    # Creates and attaches itself to the state engine

    # Add CPU object to model
    cpu = Object('CPU')
    model.add_sub(cpu) # implies: _/CPU:0

    core = Object('Core')
    core.add_field('Load', 'INTEGER')
    cpu += core

    # Add 4 Cores to CPU
    for _ in range(2):
        cpu /= 'Core'

    # Get Core:0
    core = model.get('Core') # Assumes id=0

    # Add fields to cores (type syncs)
    core += Field('Temp', 'INTEGER')

    # Add one more core (test sync with new objects)
    cpu.add_sub('Core')

    # Print Scope Cascade
    print(model.get_scope_dict(pretty=True))

    # Execute cleanup
    model.cleanup()
    

if __name__ == '__main__':
     main()