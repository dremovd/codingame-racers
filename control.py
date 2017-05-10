import sys
import math
import numpy

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

have_boost = True
# game loop

def rotate(v, angle):
    angle /= 2 * math.pi
    x, y = v
    x_r, y_r = (
        x * math.cos(angle) - y * math.sin(angle),
        x * math.sin(angle) + y * math.cos(angle),
    )
    return (int(x_r), int(y_r))
    
prev_x, prev_y = 0, 0
velocities = []

def length(a):
    return numpy.sum(a * a) ** 0.5
    
def angle(a):
    return math.atan2(-a[1], a[0])
    
#print >>sys.stderr, angle(
    
def scalar_product(a, b):
    return numpy.sum(a * b)
    
class Point:
    def __init__(self, v):
        self.v = numpy.array(v)
        
    def __repr__(self):
        p = '(%d, %d)' % (self.v[0], self.v[1])
        try:
            p += ', V: %s' % self.velocity
        except AttributeError:
            pass

        try:
            p += ', D: %s' % self.distance
        except AttributeError:
            pass
    
        try:
            p += ', A: %s' % self.angle
        except AttributeError:
            pass
        return p

class Pod():
    def __init__(self, position, velocity, angle, cid):
        self.position = position
        self.velocity = velocity
        self.angle = angle
        self.cid = cid
        

    
    
def get_pod_state():
    x, y, vx, vy, angle, next_checkpoint_id = [int(i) for i in raw_input().split()]
    return Pod(Point([x, y]), Point([vx, vy]), angle, next_checkpoint_id)
    

def get_state():
    p = {
        'pods': [get_pod_state(), get_pod_state()],
        'opponents': [get_pod_state(), get_pod_state()],
    }
        
    return p
    
def collision_soon(a, b):
    steps_ahead = 1
    for steps_ahead in [0.33, 0.66, 1.0]:    
        projected_position_a = a.position.v + steps_ahead * a.velocity.v 
        projected_position_b = b.position.v + steps_ahead * b.velocity.v 
        if length(projected_position_a - projected_position_b) < 850:
            return True
    return False
        
prev_p = {}


total_laps = int(raw_input())
checkpoint_count = int(raw_input())
checkpoints = []
have_boost = [True, True]

for i in range(checkpoint_count):
    checkpoint = Point([int(i) for i in raw_input().split()])
    checkpoints.append(checkpoint) 
    
while True:
    p = get_state()

    #for k, v in p.iteritems():
    #    print >>sys.stderr, '%s: %s' % (k, v)
    
    for i, pod in enumerate(p['pods']):
        print >>sys.stderr, 'NEXT_: %d, %d' % (i, pod.cid)

        velocity_coef = 1
        next_velocity_coef = 5
        next_checkpoint = False
        for j in range(next_velocity_coef):
            projected_position = checkpoint.v - pod.position.v - j * pod.velocity.v
            if length(projected_position) < 600:  
                pod.cid = (pod.cid + 1) % checkpoint_count
                next_checkpoint = True
                break
                
        print >>sys.stderr, 'NEXT: %d, %d' % (i, pod.cid)
        checkpoint = checkpoints[pod.cid]
        aim = Point(checkpoint.v - velocity_coef * pod.velocity.v)
        #if i == 0:
        #    aim = Point(p['opponents'][0].position.v + 5 * p['opponents'][0].velocity.v)
       
        thrust = 100
        for o in p['opponents']:
            if collision_soon(o, pod):
                thrust = 'SHIELD'
                break
            
        
        aim_velocity_angle = (
            2 * math.pi + 
            angle(aim.v - pod.position.v) -
            math.pi * (360 - pod.angle) / 180 
        )
        
        print >>sys.stderr, i, angle(aim.v - pod.position.v), math.pi * (360 - pod.angle) / 180 
        while aim_velocity_angle > math.pi:
            aim_velocity_angle -= 2 * math.pi
            
        thrust = 100 * (1.5 - abs(aim_velocity_angle) / math.pi)
        thrust = int(max(0, min(100, thrust)))
        if i == 0 and collision_soon(p['pods'][1], pod) :
            thrust = 0
        if next_checkpoint:
            thrust = 0


        if (
            have_boost[i] or 
            thrust not in ['SHIELD', 0] and
            have_boost[i] and
            #abs(angle(checkpoint.v - pod.position.v, pod.velocity.v)) <= 0.03 * math.pi and
            length(checkpoint.v - pod.position.v) >= 3000 and
            False
        ):  
            thrust = 'BOOST'
            have_boost[i] = False
        
        
        print '%d %d %s' % (aim.v[0], aim.v[1], thrust)

    prev_p = p
