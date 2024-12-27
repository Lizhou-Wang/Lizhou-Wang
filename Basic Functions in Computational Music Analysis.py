# A Set of Basic Functions in Computational Music Analysis
# Code written by Lizhou Wang (王力舟)
# Music Theory Department, Jacobs School of Music, Indiana University

# This file includes:
# - Normal-form and prime-form generator.
# - Interval-class-vector calculator.
# - Maximal-evenness analyzer.
# - Scalar complexity analyzer.
# - Voice-leading- and Euclidean-distance calculator.


                    ### A Comprehensive case test ###

test = [11,0,2,3,6,7,9] 
# Shostakovich's characteristic Phrygian mode with scale degrees 4 lowered.

normal_prime_form(test)
# Output: [6, 7, 9, 11, 0, 2, 3], [0, 1, 3, 4, 6, 8, 9]
# The normal form is [6,7,9,11,0,2,3] and the prime form is[0,1,3,4,6,8,9].

ic_vector(test)
# Output: [0, 1, 3, 4, 6, 8, 9], [3, 3, 5, 4, 4, 2]
# The interval-class vector is [3,3,5,4,4,2].

maximal_even(test)
# Output: False, False
# It is not maximally even in total chromatic;
# and it does not fulfill Myhill's property.

detect_complexity(test, True)
# Output: [6, 7, 9, 11, 0, 2, 3], [True, 22],
# {'1/2': [[6], [0, 2, 3, 4]], '2/3': [[1, 5, 6], [3]],
# '3/4': [[4, 6], [0, 2]], '4/5': [[6], [0, 1, 3]], '5/6': [[2, 4, 5, 6], [0]]},
# [False, 0], {}
# It contains 22 ambiguous intervals and 0 contradiction.

distance_vl_gm(test, False, 'diatonic')
# Output: [0, 1, 4, 5, 7, 9, 10], [0, 2, 3, 5, 7, 9, 10], 2, 1.414
# The minimal distance from this scalar structure to a diatonic scale is
# 2 semitones in terms of voice-leading distance and 1.414 "semitones"
# in terms of Euclidean distance in a 7-dimensional space.



                ### Normal-form and prime-form generator ###

# Calculate the normal and prime forms of a given set.

# Input: a pitch set in pitch-class or MIDI-pitch
# numbers; it allows repetition of pitches or pitch classes.

# Output: normal and prime forms of the input set.

def normal_prime_form (pitch_set):

    # Extract pitch classes, eliminate redundancy,
    # and arrange the result in ascending order.
    num = len(pitch_set)
    for i in range(num):
        pitch_set[i] = pitch_set[i]%12
    pc_set = list(set(pitch_set))
    pc_set.sort()
    
    # If the pitch-class set has only one item,
    # return the result and end the function.
    if len(pc_set) == 1:
        return [pc_set[0]], [0]
    
    # Find and store the most compact permutation(s).
    cardinality = len(pc_set)
    gap_list = []
    n = 0
    while n < cardinality:
        gap_list.append(
            (pc_set[n]-pc_set[n-1])%12)
        n += 1
    gap_max = max(gap_list)
    index = []
    for i, j in enumerate(gap_list):
        if j == gap_max:
            index.append(i)
    tight = []
    for i in index:
        tight.append(pc_set[i:]+pc_set[:i])
    
    # Check each of above permutations. 
    # If smaller intervals occur towards the upper
    # extreme, reverse the order of the permutation.
    for item in tight:
        for i in range(cardinality-1):
            head = (item[i+1]-item[i])%12
            tail = (item[-(i+1)]-item[-(i+2)])%12
            if head < tail:
                break
            elif tail < head:
                item.reverse()
                break
            else:
                continue
    
    # Among above permutations, compare their intervals at 
    # corresponding positions. The first one(s) featuring
    # a smaller interval win(s).
    # If several permutations win, pick up the first one.
    for m in range(cardinality-1):
        gap_list = []
        for n in range(len(tight)):
            gap = min([
                (tight[n][m+1]-tight[n][m])%12, (
                    tight[n][m]-tight[n][m+1])%12])
            gap_list.append(gap)
        gap_min = min(gap_list)
        if gap_list.count(gap_min) == 1:
            normal = tight[gap_list.index(gap_min)]
            break
        elif gap_min == max(gap_list):
            normal = tight
            continue
        else:
            remain = []
            for i, j in enumerate(gap_list):
                if j == gap_min:
                    remain.append(tight[i])
            tight = remain
    if type(normal[0]) == list:
        normal = normal[0]
    result_normal = []
    
    # Check if the winner is in descending order; if so,
    # reverse it into ascent. The normal form is found.
    for pc in normal:
        result_normal.append(pc)
    pci = (result_normal[1]-result_normal[0])%12
    if pci > 6:
        result_normal.reverse()
    
    # Transpose the winner, making it start with PC-0.
    # If it is in descending order, reverse it around
    # the axis PC=0. The prime form is found.
    count = normal[0]
    for i in range(len(normal)):
        normal[i] = (normal[i]-count)%12
    if normal[1] > 6:
        for i in range(1,len(normal)):
            normal[i] = (0-normal[i])%12
    result_prime = normal
    
    return result_normal, result_prime

# Test above function:
for i in [
    [1,3,6,7],
    [2,10,6],
    [60,54],
    [7,0,2,11,2,5],
    [9,7,13,15,3],
    [4,8,2,11],
    [0,10,9,7,6,4,3,1,8],
    [0,6,10,16,20,25],
    [9,5,7,4,0,2,-1]
    ]:
    print(normal_prime_form(i))



                    ### Interval-class-vector calculator ###

# Calculate the interval-class vector (IC content) of 
# the given pitch/pitch-class set.

# Input: a pitch set in pitch-class or MIDI-pitch
# numbers; it allows repetition of pitches or pitch classes.

# Output: (1) the prime form of the input set; and
# (2) the interval-class vector of the input set.

def ic_vector (pitch_set):
    
    # Find the prime form of the input; and
    # create a null vector for later use.
    prime = normal_prime_form(pitch_set)[1]
    vector = [0,0,0,0,0,0]
    count = len(prime)
    
    # Calculate and record the interval classes of 
    # all intervals in the prime form.
    for i in range(len(prime)-1):
        for j in range(1, count):
            upci = prime[-j]-prime[i]
            if upci > 6:
                upci = 12-upci
            vector[upci-1] += 1
        count -= 1
    
    return prime, vector

# Test above function:
for i in [
    [1,3,6,7],
    [2,10,6],
    [60,54],
    [7,2,11,2,5],
    [9,7,13,15,3],
    [0,1,3,4,6,7,9,10],
    [0,10,9,7,6,4,3,1,8],
    [0,6,10,16,20,25],
    [9,5,7,4,0,2,-1]
    ]:
    print(ic_vector(i))



                    ### Maximal-evenness analyzer ###

# This is a helper function to calculate and store all
# intervals among members of the given set.

# Input: a pitch-class set, expected to be an ascending 
# normal or prime form. The function does not change the
# input in anyway (reordering, normal/prime forms, etc.).

# Output: the matrix indicating the intervals between 
# all pairs of different set members.

def interval_matrix (pitch_set):
    
    # Create a matrix showing all intervals among the 
    # set members; calculated in semitones.
    cdt = len(pitch_set)
    matrix = [[0]*cdt for _ in range(cdt)]
    for i in range(cdt):
        pre = pitch_set[i]
        for j in range(cdt):
            post = pitch_set[j]
            interval = (post-pre)%12
            matrix[i][j] = interval
    
    # Extract and store the intervals between all pairs
    # of different set members. The results are organized 
    # according to generic intervals; in each low-level
    # list, the indices indicate starting set members.
    chrom_matrix = []
    for i in range(1, cdt):
        chrom = []
        for j in range(cdt):
            interval = matrix[j][(i+j)%(cdt)]
            chrom.append(interval)
        chrom_matrix.append(chrom)
        
    return chrom_matrix

# Test above function:
for i in [
    [0,3,6,9], # Diminished seventh
    [7,0,3,4], # Major-minor triad
    [2,4,6,7,9,11,1], # Major scale
    [5,7,9,0,2] # Pentatonic scale
    ]:
    print(interval_matrix(i))


# Use Clough-Douthett theorem to check if the given set is
# maximally even in the total chromatic. The theorem states
# that a pc set is maximally even if and only if every generic
# interval is realized either in a single specific interval
# or in two specific intervals in consecutive sizes.
# Moreover, it checks if the set fulfills Myhill's property,
# which means that each diatonic interval is realized in two
# specific intervals in consecutive sizes.

# Input: a pitch set in pitch-class or MIDI-pitch
# numbers; it allows repetition of pitches or pitch classes.

# Output: Two boolean results indicating whether the input set
# is maximally even and fulfills Myhill's property.

def maximal_even (pitch_set):
    
    # Get the prime form of the given set.
    prime = normal_prime_form(pitch_set)[1]
    
    # Get the matrix indicating the intervals between all
    # pairs of different prime-form members.
    chrom_matrix = interval_matrix(prime)
    
    # Test the evenness using Clough and Douthett's theorem;
    # simultaneously, check the Myhill's property.
    maximal_even = True
    myhill = True
    cdt = len(prime)
    for i in range(cdt-1):
        chrom = chrom_matrix[i]
        j = min(chrom)
        k = max(chrom)
        if j == k-1:
            continue
        elif j == k:
            myhill = False
            continue
        elif j < k-1:
            maximal_even = False
            myhill = False
            break
    
    return maximal_even, myhill


# Test above function:
for i in [
    [0,3,6,9], # Diminished seventh
    [7,0,3,4], # Major-minor triad
    [7,9,11,2,4], # pentatonic scale
    [2,4,6,7,9,11,1], # Major scale
    [1,4,5,8,9,12], # Hexatonic scale
    [11,0,2,3,6,7,9,10] # Shostakovich's Phrygian-b4/8 scale
    ]:
    print(maximal_even(i))



                    ### Scalar complexity analyzer ###

# Detect two types of scalar complexity:
# (1) Ambiguity: two intervals with consecutive generic 
# (diatonic) intervals have the same chromatic distance.
# (2) Contradiction: between two pc pairs with consecutive
# generic (diatonic) intervals, the diatonically smaller one 
# has larger specific interval.

# Input: (1) a pitch set in pitch-class or MIDI-pitch
# numbers; it allows repetition of pitches or pitch classes.
# (2) Whether it is transformed into normal form firstly.

# Output: (1) the normal form, if asked to transform; or 
# the input set itself. (2) Whether ambiguity is 
# observed; and the number of cases. (3) All cases of 
# ambiguity, in the format of {generic interval: locations}.
# (4) Whether contradiction is observed; and the number of 
# cases. (5) All cases of contradiction, in the format of 
# {generic interval: locations}.

def detect_complexity (pitch_set, normalize):
    
    # If normalize is True, transform the input set into 
    # the normal form; if not, use the given set directly.
    if normalize == True:
        normal = normal_prime_form(pitch_set)[0]
    else:
        normal = pitch_set
    
    # Get the matrix indicating chromatic intervals between
    # all pairs of different set members.
    chrom_matrix = interval_matrix(normal)
    
    # Use above matrix to find ambiguity and contradiction;
    # record their generic intervals and locations.
    cdt = len(normal)
    ambiguity = False
    ambgt_case = {}
    ambgt_count = 0
    contradiction = False
    contd_case = {}
    contd_count = 0
    # In each pair of consecutive generic intervals:
    for i in range(cdt-2):
        pre = chrom_matrix[i]
        pre_max = max(pre)
        post = chrom_matrix[i+1]
        post_min = min(post)
        
        # The condition means the existence of complexity.
        if pre_max >= post_min:
            label = str(i+1)+'/'+str(i+2)
            loc_con = []
            loc_con_pre = []
            loc_con_post = []
            loc_amb = []
            loc_amb_pre = []
            loc_amb_post = []
            # Check every case of the smaller generic interval.
            # If it chromatically equals/is larger than the
            # minimum of the larger generic interval, a case of
            # ambiguity/complexity is recorded.
            for m, n in enumerate(pre):
                if n > post_min:
                    loc_con_pre.append(m)
                    contd_count += 1
                elif n == post_min:
                    loc_amb_pre.append(m)
                    ambgt_count += 1
            if len(loc_con_pre) > 0:
                contradiction = True
                loc_con.append(loc_con_pre)
            if len(loc_amb_pre) > 0:
                ambiguity = True
                loc_amb.append(loc_amb_pre)
            # Check every case of the larger generic interval.
            # If it chromatically equals/is smaller than the
            # maximum of the smaller generic interval, a case of
            # ambiguity/complexity is recorded.
            for m, n in enumerate(post):
                if n < pre_max:
                    loc_con_post.append(m)
                    contd_count += 1
                elif n == pre_max:
                    loc_amb_post.append(m)
                    ambgt_count += 1
            if len(loc_con_post) > 0:
                contradiction = True
                loc_con.append(loc_con_post)
            if len(loc_amb_post) > 0:
                ambiguity = True
                loc_amb.append(loc_amb_post)
                
            # Collect all recorded cases of complexity.
            if len(loc_con) > 0:
                contd_case.update({label:loc_con})
            if len(loc_amb) > 0:
                ambgt_case.update({label:loc_amb})
        
    return normal, [ambiguity, ambgt_count], ambgt_case, [
        contradiction, contd_count], contd_case

# Test above function:
for i in [
    [0,4,7,10], # Dominant-seventh
    [2,4,6,9,11], # Pentatonic scale
    [7,0,3,4], # Major-minor triad
    [2,4,6,7,9,11,1], # Major scale
    [7,8,10,0,2,3,6] # Harmonic Phrygian scale
    ]:
    print(detect_complexity(i, True))



            ### Voice-leading- and Euclidean-distance calculator ###

# (May be a helper function.) Find out the optimal ascending
# ordering of a given set, which yields the smallest difference
# (voice-leading distance) between it and the referential set.
# When "eucld" is True, the function may also provide the 
# Euclidean distance between the optimal choice and the reference.

# Input: (1) the tested pc set, which will be firstly sorted. 
# (2) The referential set, which will not be sorted. (3) Whether
# the Euclidean distance is calculated.

# Output: (1) the optimal order. (2) Its voice-leading 
# distance to the reference. (3) Its Euclidean distance to the
# reference; if "eucld" is False, None is returned.

def optimal_order (lst_ps, lst_ref, eucld):
    
    lst_ps.sort()
    cdt = len(lst_ps)
    order_list = []
    order_vl_dist = []
    
    # Check all ascending orderings to find the one yielding
    # smallest voice-leading distance to the reference.
    count = 0
    while count < cdt:
        reorder = []
        reorder.extend(lst_ps[-count:])
        reorder.extend(lst_ps[:-count])
        vl_distance = 0
        for i in range(cdt):
            j = reorder[i]
            k = lst_ref[i]
            gap = min([(k-j)%12,(j-k)%12])
            vl_distance += gap
        order_list.append(reorder)
        order_vl_dist.append(vl_distance)
        count += 1
    optimal_dist = min(order_vl_dist)
    optimal_index = order_vl_dist.index(optimal_dist)
    optimal_order = order_list[optimal_index]
    optimal_dist = round(optimal_dist, 3)
    
    # If asked, calculate the Euclidean distance between the
    # selected optimal ordering and the reference.
    if eucld == True:
        eucld_count = 0
        for i in range(cdt):
            j = optimal_order[i]
            k = lst_ref[i]
            gap = min([(k-j)%12,(j-k)%12])
            eucld_count += gap**2
        optimal_eucld = round(eucld_count**0.5, 3)
    else:
        optimal_eucld = None
    
    return optimal_order, optimal_dist, optimal_eucld

# Test above function:
for i,j in [
    [[9,1],[0,6]],# a pair of intervals.
    [[4,7,11,1],[0,2,6,8]],# C# Half-diminished vs. D French-sixth.
    [[7,9,10,2,3],[0,2,5,7,10]],# G Japanese mode vs. Bb pentatonic.
    [[9,11,2,1,5,8,4],[0,2,3,5,7,9,10]]# A harmonic major vs. Bb major.
    ]:
    print(optimal_order(i, j, True))


# Calculate two types of distance between a tested structure
# and a referential structure. The tested "pitch_set" allows
# transpositional and permutational transformation, but not
# inversional transformation. Thus, the function compares the
# two abstract "structures," rather than specific pc content.
# The two distance types are (1) Voice-leading distance, which
# means how many semitones it needs to move from one set to
# another; and (2) Euclidean distance, which means the geometric
# distance between two points representing the two sets in 
# a space in dimensions of the cardinality of the two sets.

# Input: (1) a pitch set in pitch-class or MIDI-pitch
# numbers; it allows repetition of pitches or pitc classes.
# (2) Whether a perfectly even scale is used as the
# referential structure; it may lead to microtonal positions;
# if this variable is set to True, 'reference' should be None.
# (3) If perft_even is set to False, a scalar structure
# is assigned as the reference, either a manually created list
# or a string calling a reference in "ref_dict" dictionary.

# Output: (1) The voice-leading distance between the tested
# structure and the reference. (2) The Euclidean distance
# between the two structure.

def distance_vl_gm (pitch_set, perft_even, reference):
    
    # Extract pitch classes, eliminate redundancy,
    # and arrange the result in ascending order.
    num = len(pitch_set)
    for i in range(num):
        pitch_set[i] = pitch_set[i]%12
    pc_set = list(set(pitch_set))
    cdt = len(pc_set)
    if cdt == 1:
        print('Trivial case: single pitch class.')
        return None
    
    # Create the referential scale. If perft_even is True,
    # the octave is devided equally (and microtonally, when
    # necessary) according to the cardinality of the pc set.
    if perft_even == True:
        unit = 12/cdt
        ref = []
        for i in range(cdt):
            ref.append(round(unit*i, 4))
        if cdt % 2 == 0:
            sum_class_ref = 6
        else:
            sum_class_ref = 0
    # If perft_even is False, the 'reference' variable is
    # checked. If it's a list, it's taken as the reference;
    # if it's a string, corresponding value in ref_dict is
    # selected as the reference.
    else:
        if type(reference) == list:
            reference.sort()
            ref = reference
            sum_class_ref = sum(ref)%12
        else:
            # Each value includes the pc set and its sum class.
            ref_dict = {
                'pentatonic':[[0,2,5,7,10],0],
                'hexatonic':[[1,2,5,6,9,10],9],
                'mystic-6':[[0,3,4,6,8,10],7],
                'diatonic':[[0,2,3,5,7,9,10],0],
                'minor_har':[[0,2,3,5,7,8,11],0],
                'mystic-7':[[0,2,4,5,7,8,10],0],
                'Shost_b4':[[0,2,4,5,6,9,10],0],
                'Shost_b24':[[0,1,4,5,7,9,10],0],
                'Shost_b245':[[0,2,4,5,7,8,10],0],
                'Shost_b248':[[0,2,3,4,5,7,8,11],4],
                'Shost_b2458':[[1,2,3,4,6,7,9,11],7],
                'octatonic':[[0,1,3,4,6,7,9,10],4],
                'enneatonic':[[0,1,3,4,5,7,8,9,11],0],
                'Shost_mode':[[0,1,2,4,5,7,8,9,11],11]
                }
            try:
                ref_info = ref_dict.get(reference)
            except:
                print('Can not find the reference')
                return None
            ref = ref_info[0]
            sum_class_ref = ref_info[1]
        if len(ref) != cdt:
            print('Cardinality Error')
            return None
        
    # Generate all possible sum-class differences between
    # set transpositions and the referential structure.
    distance_list = []
    sum_class = sum(pc_set) % 12
    distance_list.append(
        abs(sum_class_ref - sum_class))
    new_sum = (sum_class + cdt) % 12
    while new_sum != sum_class:
        distance_list.append(
            abs(sum_class_ref - new_sum))
        new_sum = (new_sum + cdt) % 12
    
    # Then, generate the set transpositions whose sum classes
    # are closest to the sum class of the referential scale.
    # If the smallest difference is zero, two more choices
    # are generated, "surrounding" the first one in terms of 
    # sum class; if not, two are created, surrounding the
    # sum class of the reference.
    min_index = []
    distance_min = min(distance_list)
    pick = distance_list.index(distance_min)
    min_index.append(pick)
    if distance_min == 0:
        count = 2
    else:
        count = 1
    while count > 0:
        distance_list[pick] = 12
        distance_min = min(distance_list)
        pick = distance_list.index(distance_min)
        min_index.append(pick)
        count -= 1
    set_list = []
    for i in min_index: 
        set_optimal = [(
            x + i) % 12 for x in pc_set]
        set_optimal.sort()
        set_list.append(set_optimal)
    
    # Find among above sets the one featuring smallest 
    # possible voice-leading distance to the reference;
    # Return the voice-leading and Euclidean distances.
    distance_vl = []
    distance_gm = []
    order = optimal_order(set_list[0], ref, False)
    for i in range(1, len(set_list)):
        order_new = optimal_order(set_list[i], ref, False)
        if order_new[1] < order[1]:
            order = order_new
    pc_set = order[0]
    distance_vl = round(order[1], 3)      
    count_gm = 0
    for i in range(cdt):
        j = pc_set[i]
        k = ref[i]
        gap = min([(k-j)%12,(j-k)%12])
        count_gm += gap**2
    distance_gm = round(count_gm**0.5, 3)
    
    return pc_set, ref, distance_vl, distance_gm

# Test above function:
for i,j,k in [
    [[3,4], True, None],# minor second vs. equal division
    [[3,6,10,13], False, [5,11,1,7]],# minor-minor seventh vs. French-sixth
    [[9,11,12,4,5], False, 'pentatonic'],# Japanese mode vs. pentatonic
    [[5,7,9,10,0,4,2], True, None],# Diatonic scale vs. equal division
    [[0,1,2,4,5,6,8,9,10],False,'Shost_mode']# enneatonic vs. Shostakovich mode
    ]:
    print(distance_vl_gm (i,j,k))

