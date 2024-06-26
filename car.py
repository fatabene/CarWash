import random
import simpy

RANDOM_SEED = 48
NUM_MACHINES = 2  # Number of machines in the carwash
WASHTIME = 5     # Minutes it takes to clean a car
T_INTER = 7       # Create a car every ~7 minutes
SIM_TIME = 200     # Simulation time in minutes
REPAIR_TIME = 30

class Carwash(object):
    """A carwash has a limited number of machines (``NUM_MACHINES``) to
    clean cars in parallel.

    Cars have to request one of the machines. When they get one, they
    can start the washing process and wait for it to finish (which
    takes ``washtime`` minutes).

    """
    def __init__(self, env, num_machines, washtime):
        self.env = env
        self.machine = simpy.Resource(env, num_machines)
        self.washtime = washtime
        self.repairing = False
        self.queue = simpy.Store(env)  # Skapar för att lagra kön

    def wash(self, car):
        """The washing process. It takes a ``car`` process and tries
        to clean it."""
        
        while self.repairing:
            yield self.env.timeout(1)

        yield self.env.timeout(random.randint(1, 20))
        print("Carwash removed %d%% of %s's dirt." %
              (random.randint(50, 99), car))

    def repair(self, rep_time):
        print("Repairman called at %.2f." % (self.env.now))
        self.repairing = True
        yield self.env.timeout(random.randint(1, 20))
        print("Repairman arrived at %.2f." % (self.env.now))
        
        while self.machine.count != 0:
            yield self.env.timeout(1)
        
        yield self.env.timeout(rep_time)
        print("Repair finished at %.2f." % (self.env.now))
        self.repairing = False

def car(env, name, cw):
    print('%s arrives at the carwash at %.2f.' % (name, env.now))
    with cw.queue.put(name):  # Lägger in bilar i en kö
        yield env.timeout(0)  # Yield 0 för att lägga in bilen i första kön
    
    while cw.repairing:
        
        yield cw.env.timeout(1)
    with cw.machine.request() as request:
        yield request
        
        print('%s enters the carwash at %.2f.' % (name, env.now))
        yield env.process(cw.wash(name))

        print('%s leaves the carwash at %.2f.' % (name, env.now))


def setup(env, num_machines, washtime, t_inter, repair_time):
    """Create a carwash, a number of initial cars, and keep creating cars
    approximately every ``t_inter`` minutes."""
    # Create the carwash
    carwash = Carwash(env, num_machines, washtime)

    i = 0
    # Create 4 initial cars
    for i in range(4):
        env.process(car(env, 'Car %d' % i, carwash))

    # Create more cars while the simulation is running
    while True:
        rnd = random.randint(1, 10)
        yield env.timeout(random.randint(t_inter - 2, t_inter + 2))
        if rnd == 1 and carwash.repairing is False:
            env.process(carwash.repair(repair_time))     
        else:
            i += 1
            env.process(car(env, 'Car %d' % i, carwash))

# Setup and start the simulation
print('Carwash')
print('Check out http://youtu.be/fXXmeP9TvBg while simulating ... ;-)')
random.seed(RANDOM_SEED)  # This helps to reproduce the results

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env, NUM_MACHINES, WASHTIME, T_INTER, REPAIR_TIME))

# Execute!
env.run(until=SIM_TIME)
