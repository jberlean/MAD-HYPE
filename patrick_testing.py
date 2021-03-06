
# This code is for Patrick to mess around with his budding algorithms

'''
Initialization
'''

# standard libraries
import math

# nonstandard libraries
import numpy as np
import matplotlib.pyplot as plt
from seq_generator import SequencingGenerator as SeqGen
from seq_data import SequencingData

'''
Factory Methods
'''
import math
def erf(z):
        t = 1.0 / (1.0 + 0.5 * abs(z))
        # use Horner's method
        ans = 1 - t * math.exp( -z*z -  1.26551223 +
                                                t * ( 1.00002368 +
                                                t * ( 0.37409196 + 
                                                t * ( 0.09678418 + 
                                                t * (-0.18628806 + 
                                                t * ( 0.27886807 + 
                                                t * (-1.13520398 + 
                                                t * ( 1.48851587 + 
                                                t * (-0.82215223 + 
                                                t * ( 0.17087277))))))))))
        if z >= 0.0: return ans
        else: return -ans

def normal_estimate(s, p, n):
    if p == 1.: return None
    u = n * p
    o = (u * (1-p)) ** 0.5
    return 0.5 * (1 + erf((s-u)/(o*2**0.5)))

def factorial(n): 
    if n < 2: return 1
    return reduce(lambda x, y: x*y, xrange(2, int(n)+1))

def binomial_prob(s, p, n):
    x = 1.0 - p
    a = n - s
    b = s + 1
    c = a + b - 1
    prob = 0.0
    for j in xrange(a, c + 1):
        prob += factorial(c) / (factorial(j)*factorial(c-j)) \
                * x**j * (1 - x)**(c-j)
    return prob
'''
Generate landscapes
'''

## Create a SequencingGenerator object with all the default values:
#    -num_wells = 96
#    -cells_per_well = 35 (constant)
#    -1000 cells, no shared alpha- or beta-chains
#    -cell frequencies distributed by power law
#    -no sequencing error

gen = SeqGen()

## Set the number of wells:


'''
Set distributions
'''

gen.num_wells = 1000
gen.set_cells_per_well(distro_type = 'constant', cells_per_well=100) 
cells = SeqGen.generate_cells(500, 2, 1) 
#cells += SeqGen.generate_cells(250, 2, 1, alpha_start_idx=250, beta_start_idx=251) 
#cells += SeqGen.generate_cells(250, 1, 2, alpha_start_idx=2000, beta_start_idx=2000) 
gen.cells = cells

gen.set_cell_frequency_distribution('power-law', alpha=-1)
gen.chain_misplacement_prob = 10**-9 # Prob of a chain migrating to another well
gen.chain_deletion_prob = 10**-2 # Prob of a chain failing to be amplified

## Save data to a file
data = gen.generate_data()
data.save_data('patrick_testing.txt')


'''
The Meat-and-Potatoes
'''
# get uniques
a_uniques = list(set([a for well in data.well_data for a in well[0]]))
b_uniques = list(set([b for well in data.well_data for b in well[1]]))

well_count = len(data.well_data) # count of wells
w_ab = np.zeros((len(a_uniques),len(b_uniques)))    

f_a = [float(sum([1 for well in data.well_data if i in well[0]]))/well_count for i in a_uniques] 
f_b = [float(sum([1 for well in data.well_data if i in well[1]]))/well_count for i in b_uniques] 
c_a,c_b = len(f_a),len(f_b) # count of uniques
img_ab = None 

for well in data.well_data:
    a_ind = [a_uniques.index(i) for i in well[0]]
    b_ind = [b_uniques.index(i) for i in well[1]]
    a_v,b_v = np.zeros((len(a_uniques),1)),np.zeros((1,len(b_uniques))) 
    np.put(a_v,a_ind,np.ones((len(a_ind))))
    np.put(b_v,b_ind,np.ones((len(b_ind))))
    if img_ab == None: img_ab = np.matmul(a_v,b_v)
    else: img_ab = np.dstack((img_ab,np.matmul(a_v,b_v)))
    #w_ab += np.matmul(a_v,b_v)
    
w_ab = np.sum(img_ab,axis=2)

#p_ab = np.array([[binomial_prob(int(w_ab[i,j]),f_a[i]*f_b[j],well_count) for j in xrange(c_b)] for i in xrange(c_a)])
p_ab = np.array([[normal_estimate(int(w_ab[i,j]),f_a[i]*f_b[j],well_count) for j in xrange(c_b)] for i in xrange(c_a)])

matches = []




for i in xrange(c_a):
    for j in xrange(c_b):
        if p_ab[i,j] > 0.9999 and w_ab[i,j] > 0:
            matches.append([(a_uniques[i],b_uniques[j]),p_ab[i,j],w_ab[i,j],img_ab[i,j,:]]) 
            #print 'Index {},{}: {},{}'.format(i,j,a_uniques[i],b_uniques[j])
            #print w_ab[i,j],p_ab[i,j]
            #print f_a[i],f_b[j]
    
matches.sort(key=lambda x: -x[1])

# filter for matching distribution images


real_matches = data.metadata['cells']
correct,wrong = 0,0
accuracy = [1.]

for m in matches: 
    if m[0] in real_matches:    
        print 'CORRECT: p = {}, {}'.format(m[1],m[0])
        correct += 1
    else:
        print ' WRONG : p = {}, {}'.format(m[1],m[0])
        wrong += 1
    accuracy.append(float(correct)/(correct+wrong))

print '{}/{} correct.'.format(correct,len(real_matches))
print '{}/{} guesses wrong.'.format(wrong,len(matches))


plt.plot(xrange(len(accuracy)),accuracy)
plt.show(block=False)
raw_input('Press enter to exit...')
plt.close()


    
'''
plt.scatter(p_ab,w_ab)
plt.show(block=False)
raw_input('Press enter to exit...')
plt.close()

plt.hist(p_ab.flatten(),50)
plt.show(block=False)
raw_input('Press enter to exit...')
plt.close()
'''

