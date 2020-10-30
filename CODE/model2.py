import pyscipopt

import mcutils as mc


class Model:
    model = pyscipopt.Model("Model_Team_8")


def build_model(data, parameters):
    Model.model = pyscipopt.Model("Model_Team_8")
    model = Model.model

    # Aux
    MAX_TIME = 3
    big_m = 9999999
    pa = parameters

    # Variable Declarations
    mc.mcprint(text='Constructing Variables', color=mc.Color.GREEN)
    x_sjpt = {}  # Quantity transfered of product p from supplier s to storage j in time t
    q_sjpt = {}  # Quantity transfered of containers of product p from supplier s to storage j in time t
    y_jt = {}  # 1 if storage j is open in time t else 0
    z_jt = {}  # 1 if storage j is operative in time t else 0
    w_jkpt = {}  # Quantity transfered of product p from storage j to destination k in time t
    s_jpt = {}  # Quantity of product p stored in storage j in time t

    mc.mcprint(text='Constructing Variable X & Q')
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
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

    mc.mcprint(text='Constructing Variable Y & Z')
    for warehouse in data['warehouse']:
        for time in range(1, MAX_TIME):
            variable_name = f'Y[{warehouse}][{time}]'
            y_jt[(warehouse, time)] = model.addVar(lb=0, ub=None, name=variable_name, vtype="BINARY")

            variable_name = f'Z[{warehouse}][{time}]'
            z_jt[(warehouse, time)] = model.addVar(lb=0, ub=None, name=variable_name, vtype="BINARY")

    mc.mcprint(text='Constructing Variable W')
    for warehouse in data['warehouse']:
        for destination in data['destination']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    variable_name = f'W[{warehouse}][{destination}][{item}][{time}]'
                    w_jkpt[(warehouse, destination, item, time)] = model.addVar(lb=0,
                                                                                ub=None,
                                                                                name=variable_name,
                                                                                vtype="INTEGER")

    mc.mcprint(text='Constructing Variable S')
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
                 for time in range(1, MAX_TIME))
        )))
    model.setObjective(objective_function, "minimize")

    # TODO: Construct Objective Function

    # Constrains Declarations
    mc.mcprint(text='Constructing Constraints', color=mc.Color.GREEN)

    # Constraint: Demand
    mc.mcprint(text="Constraint: Demand")
    for destination in data['destination']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                model.addCons(pyscipopt.quicksum(
                    w_jkpt[warehouse, destination, item, time] for warehouse in data['warehouse']
                    ) >= (parameters['D_kpt'][destination, item, f'{time}'] if (destination, item, f'{time}') in parameters['D_kpt'] else 0))

    # Constraint: Flujo
    mc.mcprint(text="Constraint: Flujo")  # TODO: include storage
    for warehouse in data['warehouse']:
        for item in data['item']:
            for time in range(1, MAX_TIME):
                model.addCons(
                    pyscipopt.quicksum(x_sjpt[supplier, warehouse, item, time] for supplier in data['supplier'])
                    == pyscipopt.quicksum(w_jkpt[warehouse, destination, item, time] for destination in data['destination'])
                    )

    # Constraint: Truck capacity
    mc.mcprint(text="Constraint: Truck capacity")
    for supplier in data['supplier']:
        for warehouse in data['warehouse']:
            for item in data['item']:
                for time in range(1, MAX_TIME):
                    model.addCons(x_sjpt[supplier, warehouse, item, time] <= q_sjpt[supplier, warehouse, item, time] * parameters['Cap_p'][item])

def display_optimal_information():
    model = Model.model
    mc.mcprint(text=model.getStatus(), color=mc.Color.YELLOW)
    if model.getStatus() != "infeasible":
        for var in model.getVars():
            value = int(model.getVal(var))
            print("{}:\t{}".format(value, var)) if value != 0 else None
        if model.getStatus() == "optimal":
            mc.mcprint(text="Found the optimal solution successfully", color=mc.Color.GREEN)
    else:
        mc.mcprint(text="The instance is INFEASIBLE", color=mc.Color.RED)


def reset_model():
    del Model.model
    Model.model = None
