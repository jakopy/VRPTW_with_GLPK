from pymprog import *

class VRPTW_GLPK():
    def __init__(self,travel_time,time_windows,dist,demand,capacity,siteNames,vehicles,node_pref,vehicleTW):
        self.travel_time = travel_time
        self.time_windows = time_windows
        self.dist = dist
        self.demand = demand
        self.capacity = capacity
        self.siteNames = siteNames
        self.vehicles = vehicles
        self.node_pref = node_pref
        self.vehicleTW = vehicleTW

    def solve(self):
        #vehicle data
        vehicles = self.vehicles
        vehicleTWs = self.vehicleTW

        #time data
        tt = self.travel_time
        node_tw = self.time_windows
        names = self.siteNames
        
        #other data
        dist = self.dist
        demand = self.demand
        capacity = self.capacity

        #sets
        verticies = range(len(names))
        depot = 0
        auxilary_depot = len(verticies)-1
        nodes = verticies[1:auxilary_depot]

        #node preferences
        node_prefs = self.node_pref


#        model = Model('Diesel Fuel Delivery')
        begin('assign')

        #what might fix the problem:
        #make sure one vehicle has only a single route.... or no route at all

        #also we must make sure each place can be touched
        #right now the each matrix is restricted to the constraints

        #node preferences

        #timewindow variables
        a = []
        b = []
        M = 0
        for window in node_tw:
            a.append(window[0])
            b.append(window[1])
            M += window[1]

        #build variables
        #decision variable x
        x = {}
        vehicle_arcs = []
        arcs = []
        veh_arcs = iprod(verticies,verticies,vehicles)
        for k in vehicles:
            for i in verticies:
                for j in verticies:
                    if i != j:
#                        x[i,j,k] = model.addVar(vtype=GRB.BINARY,name="routes")
                        arcs.append((i,j))
                        vehicle_arcs.append((i,j,k))
        sp = {}
        print "starting x"
        x=var('x',veh_arcs,bool)

        print "x done"

        veh_vert = iprod(verticies,vehicles)
        sp=var('sp',verticies,bool)
##        for vehicle in node_prefs:
##            for node_pref in node_prefs[vehicle]:
#        for i in verticies:
#            sp[i] = model.addVar(vtype=GRB.BINARY,name='S+[%s]'%(i))
        s = var('s',veh_vert)
#        s = {}
#        for k in vehicles:
#            for i in nodes:
#                s[i,k] = model.addVar(vtype=GRB.INTEGER,name='vehiclewindow')
        d = var('d',nodes)
        dumvars = [1,2]
        dummy = var('dumb',dumvars)
#        D = {}  #time variable D departure time
#        for i in nodes:
#            D[i] = model.addVar(name='departuretime')


#        model.update()
        print "vars done"

        #constraint 2.1 (objective)
        minimize(sum(tt[i][j]*x[i,j,k]+10000*sp[i] for k in vehicles for i in verticies for j in verticies if i != j and j != 0))
#        model.setObjective(quicksum(tt[i][j]*x[i,j,k]+10000*sp[i] for k in vehicles for i in verticies for j in verticies if i != j and j != auxilary_depot),GRB.MINIMIZE)
        print "objective done"

        #constraint 2.2
        for i in nodes:
            sum(x[i,j,k] for k in vehicles for j in verticies if i != j) == 1
#            model.addConstr(quicksum(x[i,j,k] for k in vehicles for j in verticies if i != j) == 1)

        print "const 2.2 done"
        #constraint 2.3
        for k in vehicles:
            sum(x[0,j,k] for j in verticies if j != 0) == 1
#            model.addConstr(quicksum(x[0,j,k] for j in verticies if j != 0) == 1)
        print "const 2.3 done"

        #constraint 2.4
        for k in vehicles:
            for h in nodes:
                sum(x[i,h,k] for i in verticies if i != h) - sum(x[h,j,k] for j in verticies if h != j)==0
#                model.addConstr(quicksum(x[i,h,k] for i in verticies if i != h) - quicksum(x[h,j,k] for j in verticies if h != j)==0)
        print "const 2.4 done"

        #constraint 2.5
        for k in vehicles:
            sum(x[i,auxilary_depot,k] for i in verticies if i != auxilary_depot)==1
#            model.addConstr(quicksum(x[i,auxilary_depot,k] for i in verticies if i != auxilary_depot)==1)
        print "const 2.5 done"

        #constraint 2.6
        #capacity
##        d = demand
##        Q = capacity
##        for k in vehicles:
##            model.addConstr(quicksum(d[i] for i in nodes)*quicksum(x[i,j,k] for j in verticies if i != j) <= Q)

        #constraint 2.7
        #time windows
        for k in vehicles:
            for i in nodes:
                for j in nodes:
                    if i != j:
                        s[i,k]-s[j,k]+(b[i]+tt[i][j]-a[j])*x[i,j,k]<=b[i]-a[j]
#                        model.addConstr(s[i,k]-s[j,k]+(b[i]+tt[i][j]-a[j])*x[i,j,k]<=b[i]-a[j])
##                        model.addConstr(D[i]-D[j]+(b[i]+tt[i][j]-a[j])*x[i,j,k]<=b[i]-a[j])
                        ##                  model.addConstr(s[i,k]+tt[i][j]-(b[i]-a[j])*(1-x[i,j,k]) <= s[j,k])
##        for i in nodes:
##            model.addConstr(a[i]<=D[i]<=b[i])
        print "const 2.7 done"

       #constraint 2.8
        for k in vehicles:
            for i in nodes:
                a[i] <= s[i,k] <= b[i]
#                model.addConstr(a[i] <= s[i,k] <= b[i])
        print "const 2.8 done"

        #constraint 2.9
        #vehicle preferences
        for vehicle in node_prefs:
            for node_pref in node_prefs[vehicle]:
                if vehicle != 0:
                    sum(x[i,node_pref,vehicle] for i in nodes if i!=node_pref) == 1 - sp[node_pref]
        print "const 2.9 done"

        for k in vehicles:
            for i in verticies:
                x[i,0,k] == 0

#                model.addConstr(quicksum(x[i,node_pref,vehicle] for i in nodes if i!=node_pref) == 1 - sp[node_pref])

        #constraint 3.0
        #vehicle Time window constraints
        #vehicleTWs = {1:[[1,24]],2:[[1,7]]}

        #vehicle Time window constraints
        #vehicleTWs = {1:[[1,24]],2:[[1,7]]}
        #THE IDEA FOR THE EXPANSION
        #produce seperate binary variables on the constraints to ensure
        #that either one can be chosen but one must be chosen
#        for k in vehicleTWs:
#            for i in verticies:
#                for j in verticies:
#                    if i != j:
#                        number_of_time_windows = len(vehicleTWs[k])
#                        count = 0
#                        for VehTW in vehicleTWs[k]:
#                            count +=1
#                            ak = VehTW[0]
#                            bk = VehTW[1]
#                            if number_of_time_windows > 1:
#                                if count == 1:
#                                    p = 1
##                                    model.addConstr(dummy[1]==1) # if dummy[1] is 1 we are un restricted
#                                    s[i,k]-s[j,k]+(bk+tt[i][j]-ak)*x[i,j,k]<=bk-ak+10000*dummy[1]
#                                    s[i,k] <= bk+10000*dummy[1]
#                                    s[i,k] >= ak-10000*dummy[1]
#                                if count == 2:
##                                    model.addConstr(dummy[2]==0) #at least 1 constraint must be chosen
#                                    s[i,k]-s[j,k]+(bk+tt[i][j]-ak)*x[i,j,k]<=bk-ak+10000*dummy[2]
#                                    s[i,k] <= bk+10000*dummy[2] #if dummy[2] is 1, we are un restricted
#                                    s[i,k] >= ak-10000*dummy[2] #if dummy[2] is 1 we are un restricted
                        #un restricted means there is a solution
#                                dummy[1]+dummy[2] == 1 # at least one dummy must be valid
##                                print k, ak, bk, "count: ",count
#                            else:
                            # no dummy variables
#                                s[i,k]-s[j,k]+(bk+tt[i][j]-ak)*x[i,j,k]<=bk-ak
#                                s[i,k] <= bk
#                                s[i,k] >= ak
        def report():
            assign = [(i,j,k) for i in verticies for j in verticies for k in vehicles]
            for i,j,k in assign:
                if x[i,j,k].primal >0:
                    print (i,j,k)
        #solver(int,br_tech=glpk.GLP_BR_PCH)
        solve()#lm_tim=1
        report()
        save(mps='17_save.mps',sol='_save.sol')
        end()
#        model.setParam('OutputFlag',True)
#        model.optimize()
#        # Print Solution
#        if model.status == GRB.Status.OPTIMAL:
#            solution = model.getAttr('x')
#            arcsol = []
#            for i in range(0,len(solution),1):
#                if solution[i] == 1:
#                    if i <= len(vehicle_arcs):
#                        print vehicle_arcs[i] , " : ", solution[i]
#                        arcsol.append(arcs[i])
        result_set = None
        return result_set

if __name__ == "__main__":

    #node list data
    #the directed set, goes back to the depot at the end
    siteNames = ["Depot","Loc 1","Loc 2","Loc 3","Loc 4",
                 "Loc 5","Loc 6","Depot"]

    sites = range(len(siteNames))
    clients = sites[1:]
    #print "THE LENGTH OF CLIENTS: " + str(len(clients))

    #demand data
    demand = [ 0,1000, 1200, 1600, 1400, 1200, 1000, 0]
    demandsum = 0
    for i in demand:
        demandsum += i
    #print "THE DEMAND SUM IS: " + str(demandsum)

    #distance data
    dist = [[0, 59.3, 31.6, 47.8, 34.2, 47.1, 36.1, 31.9],
            [62.2, 0, 27.9, 21.0, 77.5, 30.0, 27.1, 44.7],
            [32.2, 27.7, 0, 16.2, 50.0, 39.4, 24.9, 42.6],
            [50.7, 21.0, 16.4, 0, 66.1, 49.7, 35.2, 52.9],
            [34.4, 77.4, 49.6, 65.9, 0, 80.8, 67.1, 65.5],
            [46.9, 30.1, 39.6, 49.7, 80.5, 0, 14.4, 15.0],
            [36.9, 27.1, 25.2, 35.2, 67.1, 14.4, 0, 17.6],
            [31.9, 44.7, 62.8, 52.8, 65.6, 15.0, 17.6, 0]]

    #capacity of bus data
    capacity = 50000
    vehicleTW = {1:[[1,24]],2:[[1,24]]}

    #Time window data
    travel_time = [[0, 1, 1, 1, 1, 1, 1, 1],
                   [1, 0, 1, 1, 1, 1, 1, 1],
                   [1, 1, 0, 1, 1, 1, 1, 1],
                   [1, 1, 1, 0, 1, 1, 1, 1],
                   [1, 1, 1, 1, 0, 1, 1, 1],
                   [1, 1, 1, 1, 1, 0, 1, 1],
                   [1, 1, 1, 1, 1, 1, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 0]]
    service_time = [0, 1, 1, 1, 1, 1, 1, 1]
    time_windows = [[1,19],[1,2],[1,2],[1,2],[1,7],[1,5],[9,12],[11,15]]


    #vehicle data
    vehicles = [1,2,3,5]#,3,4,5,6,7,8,9]

    #sitter preferences
    node_pref = {0:[1,2,3],1:[1,2],2:[3,4]}

    #execute the function
    problem = VRPTW_GLPK(travel_time,time_windows,dist,demand,capacity,siteNames,vehicles,node_pref,vehicleTW)
    solution = problem.solve()

    #parse the sol
##    for bus in solution:
##        distance = solution[bus][0]
##        demand = solution[bus][1]
##        routelist = solution[bus][2]
##        print bus
##        print distance
##        print demand
##        print routelist
