## This scripts aims to return in which step a certain action must be
## performed

# Time reference: first container to start its execution
sp_list = [15.0, 17.5,22.5]
sp_list2 = [20.0,15.0,30.0]
epochs_change = [44,42,37]
epochs_list = [130,80,70]
time_list = []

for i in range(len(sp_list)):
    time = 0
    for j in range(epochs_list[i]):
        if i ==0:
            time += sp_list[i]
        else:
            if j ==0:
                for w in range(i):
                    time += 5*sp_list[w]
                time += sp_list[i]
            else:
                if j < epochs_change[i]:
                    time += sp_list[i]
                elif j >= epochs_change[i]:
                    time += sp_list2[i]
        time_list.append([time, i, j])

for i in range(len(time_list)):
    counter = 0
    for j in range(len(time_list)):
        if (i !=j) and (time_list[i][0] > time_list[j][0]):
            counter += 1
    time_list[i].append(counter)

for i in range(len(time_list)):
    for j in range(len(time_list)):
        if time_list[j][3] == i:
            print "STEP: {0} - Container {1} - Time: {2} - Epoch {3}".format(time_list[j][3],time_list[j][1],time_list[j][0], time_list[j][2])
        
    
    
