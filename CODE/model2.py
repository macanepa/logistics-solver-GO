import pyscipopt
from pprint import pprint

import mcutils as mc


class Model:
    model = pyscipopt.Model("Model_Team_8")
    # model = Model(with_optimizer(SCIP.Optimizer), limits_gap=0.05)
    results = None
    data = None
    parameters = None
    MAX_TIME = None
    output_data = None

def build_model(data, parameters):
    Model.model = pyscipopt.Model("Model_Team_8")
    Model.model.setRealParam('limits/gap', 0.01)
    model = Model.model
    Model.data = data
    Model.parameters = parameters
    # Aux
    MAX_TIME = 120
    Model.MAX_TIME = MAX_TIME
    big_m = 9999999
    parameters

    # Variable Declarations
    mc.mcprint(text='Constructing Variables', color=mc.Color.GREEN)
    x_sjpt = {}  # Quantity arrived of product p from supplier s to warehouse j in time t
    l_sjpt = {}  # Quantity ordered of product p from supplier s to warehouse j in time t
    q_sjpt = {}  # Quantity arrived of containers of product p from supplier s to warehouse j in time t
    y_jt = {}  # 1 if warehouse j is open in time t else 0
    z_jt = {}  # 1 if warehouse j is operative in time t else 0
    w_jkpt = {}  # Quantity transferred of product p from warehouse j to destination k in time t
    o_jkpt = {}  # Quantity transferred of of containers of product p from warehouse j to destination k in time t
    s_jpt = {}  # Quantity of product p stored in warehouse j in time t

    Model.results = {}
    Model.results['x_sjpt'] = x_sjpt
    Model.results['l_sjpt'] = l_sjpt
    Model.results['w_jkpt'] = w_jkpt
    Model.results['z_jt'] = z_jt
    Model.results['s_jpt'] = s_jpt
    Model.results['q_sjpt'] = q_sjpt
    Model.results['o_jkpt'] = o_jkpt

    mc.mcprint(text='Constructing Variable Lsjpt: Quantity ordered of product p from supplier s to warehouse j in time t\n'
                    'Constructing Variable Xsjpt: Quantity arrived of product p from supplier s to warehouse j in time t\n'
                    'Constructing Variable Qsjpt: Quantity arrived of containers of product p from supplier s to warehouse j in time t')

    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    lead_time = time - parameters['LT1_sj'][(supplier, warehouse)]
                    variable_name = f'L[{supplier}][{warehouse}][{item}][{lead_time}]'
                    l_sjpt[(supplier, warehouse, item, lead_time)] = model.addVar(lb=0,
                                                                             ub=None,
                                                                             name=variable_name,
                                                                             vtype="INTEGER")
                    variable_name = f'X[{supplier}][{warehouse}][{item}][{time}]'
                    x_sjpt[(supplier, warehouse, item, time)] = model.addVar(lb=0,
                                                                             ub=None,
                                                                             name=variable_name,
                                                                             vtype="INTEGER")
                    variable_name = f'Q[{supplier}][{warehouse}][{item}][{time}]'
                    q_sjpt[(supplier, warehouse, item, time)] = model.addVar(lb=0,
                                                                             ub=None,
                                                                             name=variable_name,
                                                                             vtype="INTEGER")

    mc.mcprint(text='Constructing Variable Yjt: 1 if warehouse j is open in time t else 0\n'
                    'Constructing Variable Zjt: 1 if warehouse j is operative in time t else 0')
    for warehouse in data['warehouse']:
        for time in range(1, MAX_TIME):
            variable_name = f'Z[{warehouse}][{time}]'
            z_jt[(warehouse, time)] = model.addVar(lb=0, ub=None, name=variable_name, vtype="BINARY")

            variable_name = f'Y[{warehouse}][{time}]'
            y_jt[(warehouse, time)] = model.addVar(lb=0, ub=None, name=variable_name, vtype="BINARY")

    mc.mcprint(text='Constructing Variable Wjkpt: Quantity transfered of product p from warehouse j to destination k in time t')
    for warehouse in data['warehouse']:
        for destination in data['destination']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    variable_name = f'W[{warehouse}][{destination}][{item}][{time}]'
                    w_jkpt[(warehouse, destination, item, time)] = model.addVar(lb=0,
                                                                                ub=None,
                                                                                name=variable_name,
                                                                                vtype="INTEGER")
                    variable_name = f'O[{warehouse}][{destination}][{item}][{time}]'
                    o_jkpt[(warehouse, destination, item, time)] = model.addVar(lb=0,
                                                                                ub=None,
                                                                                name=variable_name,
                                                                                vtype="INTEGER")

    mc.mcprint(text='Constructing Variable Sjpt: Quantity of product p stored in warehouse j in time t')
    for warehouse in data['warehouse']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                variable_name = f'S[{warehouse}][{item}][{time}]'
                s_jpt[(warehouse, item, time)] = model.addVar(lb=0, ub=None, name=variable_name, vtype="INTEGER")

    #  Objective Function
    mc.mcprint(text='Constructing Objective Function', color=mc.Color.GREEN)
    objective_function = model.addVar(name="objective function", lb=None)
    model.addCons(objective_function == (
            pyscipopt.quicksum(
                (w_jkpt[warehouse, destination, item, time]
                for warehouse in data['warehouse']
                for destination in data['destination']
                for item in data['item']
                for time in range(1, MAX_TIME))
                                 )
            +pyscipopt.quicksum(
                (q_sjpt[supplier, warehouse, item, time]
                 for supplier in data['supplier']
                 for warehouse in data['warehouse']
                 for item in data['item']
                 for time in range(1, MAX_TIME)))

            + pyscipopt.quicksum(
                (l_sjpt[supplier, warehouse, item, time]*parameters['MC_sp'][(supplier, item)]
                 for supplier in data['supplier']
                 for warehouse in data['warehouse']
                 for item in data['item']
                 for time in range(-1, MAX_TIME - 2)))

            + pyscipopt.quicksum(
                (y_jt['warehouse002', time]*40000
                 for time in range(1, MAX_TIME)))

            + pyscipopt.quicksum(
                (z_jt['warehouse002', time]*40000
                 for time in range(1, MAX_TIME)))
            + pyscipopt.quicksum(
                (z_jt['warehouse001', time]*50000
                 for time in range(1, MAX_TIME)))

            + pyscipopt.quicksum(
                (s_jpt[warehouse, item, time] * parameters['STO_jp'][(warehouse, item)]
                 for warehouse in data['warehouse']
                 for item in data['item']
                 for time in range(1, MAX_TIME)))
            #
            # + pyscipopt.quicksum(
            #     (l_sjpt[supplier, warehouse, item, time] * parameters['CL1_sj'][(supplier, warehouse)]
            #      for supplier in data['supplier']
            #      for warehouse in data['warehouse']
            #      for item in data['item']
            #      for time in range(1, MAX_TIME)))
            # + pyscipopt.quicksum(
            #     (q_sjpt[supplier, warehouse, item, time] * 5000
            #      for supplier in data['supplier']
            #      for warehouse in data['warehouse']
            #      for item in data['item']
            #      for time in range(1, MAX_TIME)))

            + pyscipopt.quicksum(
                (w_jkpt[warehouse, destination, item, time] * parameters['CL2_sj'][(warehouse, destination)]
                 for warehouse in data['warehouse']
                 for destination in data['destination']
                 for item in data['item']
                 for time in range(1, MAX_TIME)))
            + pyscipopt.quicksum(
                (o_jkpt[warehouse, destination, item, time] * 5000
                 for warehouse in data['warehouse']
                 for destination in data['destination']
                 for item in data['item']
                 for time in range(1, MAX_TIME)))

    ))

    model.setObjective(objective_function, "minimize")

    # TODO: Construct Objective Function

    # Constrains Declarations
    mc.mcprint(text='Constructing Constraints', color=mc.Color.GREEN)

    # Constraint: Demand
    confidence_level = 0.95
    mc.mcprint(text="Constraint: Demand")
    for destination in data['destination']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                model.addCons(pyscipopt.quicksum(
                    w_jkpt[warehouse, destination, item, time] for warehouse in data['warehouse']
                    ) >= (int(parameters['D_kpt'][destination, item, f'{time}']) * confidence_level if (destination, item, f'{time}') in parameters['D_kpt'] else 0))

    # Constraint: Lead time
    mc.mcprint(text="Constraint: Lead time")
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(
                        x_sjpt[supplier, warehouse, item, time] == l_sjpt[supplier, warehouse, item, (time - 2)]
                        )

    # Constraint: Flujo
    mc.mcprint(text="Constraint: Flujo")  # TODO: include storage
    for warehouse in data['warehouse']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                storage_pre = 0
                storage_post = 0
                if (warehouse, item, time - 1) in s_jpt:
                    storage_pre = s_jpt[warehouse, item, time - 1]
                if (warehouse, item, time) in s_jpt:
                    storage_post = s_jpt[warehouse, item, time]
                model.addCons(
                    pyscipopt.quicksum(x_sjpt[supplier, warehouse, item, time] for supplier in data['supplier'])
                    + storage_pre
                    == pyscipopt.quicksum(w_jkpt[warehouse, destination, item, time] for destination in data['destination'])
                    + storage_post
                    )

    # Constraint: Truck capacity
    mc.mcprint(text="Constraint: Truck capacity")
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(x_sjpt[supplier, warehouse, item, time] <= q_sjpt[supplier, warehouse, item, time] * parameters['Cap_p'][item])
                    model.addCons(w_jkpt[warehouse, destination, item, time] <= o_jkpt[warehouse, destination, item, time] *
                                  parameters['Cap_p'][item])

    # Constraint: Supplier capacity
    mc.mcprint(text="Constraint: Supplier capacity")
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(x_sjpt[supplier, warehouse, item, time] <= parameters['SC_sp'][supplier, item])

    # Constraint: Open warehouse
    mc.mcprint(text="Constraint: Open warehouse")
    for warehouse in data['warehouse']:
        for time in range(1,MAX_TIME):
            model.addCons(z_jt[warehouse, time] <= pyscipopt.quicksum(y_jt[warehouse, ttime] for ttime in range(1, time + 1)))  # Can't operate if not open

    # Constraint: Can't open twice
    mc.mcprint(text="Constraint: Can't open twice")
    for warehouse in data['warehouse']:
        model.addCons(pyscipopt.quicksum(y_jt[warehouse, time] for time in range(1, MAX_TIME)) <= 1)

    # Constraint: Don't send to warehouse if not operating
    mc.mcprint(text="Constraint: Don't send to warehouse if not operating")
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(x_sjpt[supplier, warehouse, item, time] <= big_m * z_jt[warehouse, time])

    # Constraint: Don't send to destination if not operating warehouse
    mc.mcprint(text="Constraint: Don't send to destination if not operating warehouse")
    for warehouse in data['warehouse']:
        for destination in data['destination']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(w_jkpt[warehouse, destination, item, time] <= big_m * z_jt[warehouse, time])

    # Constraint: Don't store if not operating warehouse
    mc.mcprint(text="Constraint: Don't store if not operating warehouse")
    for warehouse in data['warehouse']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                model.addCons(s_jpt[warehouse, item, time] <= big_m * z_jt[warehouse, time])

    # Fix Variables
    for key in parameters['y_jt']:
        warehouse = key[0]
        time = int(key[1])
        model.addCons(y_jt[warehouse, time] == parameters['y_jt'][key])

def sort_key(text):
    return text.split(':')[-1].replace(' ', '')


def sort_key_export(text):
    return text.replace('[',' ').split(' ')[-1].replace(' ', '')


def display_optimal_information():
    model = Model.model
    mc.mcprint(text=model.getStatus(), color=mc.Color.YELLOW)
    if model.getStatus() != "infeasible":
        printable_list = []
        for var in model.getVars():
            value = int(model.getVal(var))
            if value != 0:
                printable_list.append("{}:\t{}".format(value, var))
        sort = sorted(printable_list, key=sort_key)
        # for text in sort:
        #     print(text)
        if model.getStatus() == "optimal":
            mc.mcprint(text="Found the optimal solution successfully", color=mc.Color.GREEN)
        if model.getStatus() == "gaplimit":
            mc.mcprint(text="Found the optimal solution successfully (gap limit of 1% has been reached)", color=mc.Color.GREEN)

    else:
        mc.mcprint(text="The instance is INFEASIBLE", color=mc.Color.RED)



def reset_model():
    del Model.model
    Model.model = None
    Model.results = None
    Model.data = None
    Model.parameters = None
