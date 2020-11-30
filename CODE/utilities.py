import os
import sys
from pprint import pprint
from pathlib import Path
import xlwt

import model2
import mcutils as mc


class ConfigFiles:
    working_dir = Path(os.path.abspath(__file__)).parent.parent
    working_dir = Path(os.getcwd()).parent

    input_data_path = os.path.join(working_dir, 'input_data')
    output_path = os.path.join(working_dir, 'output')
    simulation_path = os.path.join(working_dir, 'simulation_model')

    FIXED_DIRECTORIES = {'input_data':  '{}'.format(input_data_path),
                         'output':      '{}'.format(output_path),
                         'simulation_model':  '{}'.format(simulation_path),
                         'working_dir': '{}'.format(working_dir)}

    DYNAMIC_DIRECTORIES = {'current_input_data': os.path.join(FIXED_DIRECTORIES['input_data'], 'input_data')}


class Data:
    INPUT_DATA = {}
    PARAMETERS = {}


def initialize_directories():
    current_directories = os.listdir(ConfigFiles.FIXED_DIRECTORIES['working_dir'])
    for directory_name in ConfigFiles.FIXED_DIRECTORIES:
        if directory_name == 'working_dir':
            continue
        if directory_name not in current_directories:
            mc.mcprint(text="The directory '{}' doesn't exists.".format(ConfigFiles.FIXED_DIRECTORIES[directory_name]),
                       color=mc.Color.ORANGE)
            os.mkdir(directory_name)
            mc.mcprint(text="Created '{}' successfully".format(ConfigFiles.FIXED_DIRECTORIES[directory_name]),
                       color=mc.Color.GREEN)


def check_argument():
    if len(sys.argv) == 2:
        arg = sys.argv[-1]
        arg = os.path.join(os.getcwd(), arg)  # TODO: Allow absolute path
        if os.path.isdir(arg):
            mc.mcprint(text="Input Data Directory: ({})".format(arg),
                       color=mc.Color.GREEN)
            ConfigFiles.FIXED_DIRECTORIES["input_data"] = arg
        else:
            mc.register_error(error_string="The path '{}' doesn't exist".format(arg))
            mc.mcprint(
                text="Using default directory ({})".format(ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"]),
                color=mc.Color.YELLOW)
    elif len(sys.argv) > 2:
        mc.register_error(error_string="Solver doesn't accept more than 1 argument")
        mc.exit_application(enter_quit=True)


def initialize():
    mc.mcprint(text="Initializing Solver...")
    check_argument()
    initialize_directories()
    import_input_data()


def print_input_data():
    print(mc.Color.PINK)
    pprint(Data.INPUT_DATA)
    print(mc.Color.RESET)


def import_data():
    mc.mcprint(text="Importing from data input directory", color=mc.Color.ORANGE)
    mc.mcprint(text="The current directory is ({})".format(ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"]),
               color=mc.Color.ORANGE)

    path_dirs = {}
    input_data_path = ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"]

    for directory in os.listdir(input_data_path):
        path_dirs[directory] = os.path.join(input_data_path, directory)

    exclude = ['corridor.csv', 'surcharge.csv', 'route_supplier.csv']
    for file_name in path_dirs:
        path = path_dirs[file_name]
        with open(path) as file:
            object_data = {}
            first_line = True
            headers = []
            for line in file:
                line = line.replace(',', ';')
                if line.strip() == "":
                    continue
                if first_line:
                    if file_name in exclude:
                        headers = line.strip().split(";")
                    else:
                        headers = line.strip().split(";")[1:]
                    first_line = False
                    continue
                if file_name not in exclude:
                    split = line.strip().split(";")
                    object_data[split[0]] = {}
                    for index, attribute in enumerate(split[1:]):
                        object_data[split[0]][headers[index]] = attribute
                else:
                    split = line.strip().split(";")
                    object_data["_".join([file_name.split(".")[0]] + split[:2])] = {}
                    for index, attribute in enumerate(split):
                        object_data["_".join([file_name.split(".")[0]] + split[:2])][headers[index]] = attribute

        Data.INPUT_DATA[file_name.split(".")[0]] = object_data
    if len(Data.INPUT_DATA) == 0:
        raise Exception("No compatible data has been found. "
                        "Please please insert valid data or change the input data directory")


def import_data():
    mc.mcprint(text="Importing from data input directory", color=mc.Color.ORANGE)
    mc.mcprint(text="The current directory is ({})".format(ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"]),
               color=mc.Color.ORANGE)

    path_dirs = {}
    input_data_path = ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"]

    for directory in os.listdir(input_data_path):
        path_dirs[directory] = os.path.join(input_data_path, directory)

    exclude = []
    for file_name in path_dirs:
        print(f"Importing data from {mc.Color.CYAN}{file_name}{mc.Color.RESET}... ", end='')
        path = path_dirs[file_name]
        with open(path) as file:
            object_data = {}
            first_line = True
            headers = []
            for line in file:
                if line.strip() == "":
                    continue
                line = line.replace(',', ';')
                if first_line:
                    if file_name in exclude:
                        headers = line.strip().split(";")
                    else:
                        headers = line.strip().split(";")[1:]
                    first_line = False
                    continue
                if file_name not in exclude:
                    split = line.strip().split(";")
                    object_data[split[0]] = {}
                    for index, attribute in enumerate(split[1:]):
                        object_data[split[0]][headers[index]] = attribute
                else:
                    split = line.strip().split(";")
                    object_data["_".join([file_name.split(".")[0]] + split[:2])] = {}
                    for index, attribute in enumerate(split):
                        object_data["_".join([file_name.split(".")[0]] + split[:2])][headers[index]] = attribute
        mc.mcprint(text='Completed!', color=mc.Color.GREEN)
        Data.INPUT_DATA[file_name.split(".")[0]] = object_data

    if len(Data.INPUT_DATA) == 0:
        raise Exception("No compatible data has been found. "
                        "Please please insert valid data or change the input data directory")


def create_parameters():
    data = Data.INPUT_DATA

    if len(data.keys()) == 0:
        raise Exception("There is no data")

    # Generating: Demand
    mc.mcprint(text="Generating: Demand")
    D_kpt = {}
    locations = {'demand_amsterdam': 'destination001',
                 'demand_london': 'destination002',
                 'demand_paris': 'destination003',
                 'demand_stockholm': 'destination004',
                 'demand_kiev': 'destination005',
                 'demand_moscow': 'destination006',
                 'demand_rome': 'destination007',
                 'demand_helsinki': 'destination008',
                 }

    for demand_location in list(filter(lambda x: x in locations, Data.INPUT_DATA)):
        for time in Data.INPUT_DATA[demand_location]:
            for item in Data.INPUT_DATA[demand_location][time]:
                demand = Data.INPUT_DATA[demand_location][time][item]
                D_kpt[(locations[demand_location], item, time)] = demand

    # Generating: Truck capacity
    mc.mcprint(text="Generating: Truck capacity")
    Cap_p = {}
    for item in Data.INPUT_DATA['truck_capacity']:
        Cap_p[item] = Data.INPUT_DATA['truck_capacity'][item]['capacity']

    # Generating: Truck capacity
    mc.mcprint(text="Generating: Truck capacity")
    Cap_p = {}
    for item in Data.INPUT_DATA['truck_capacity']:
        Cap_p[item] = Data.INPUT_DATA['truck_capacity'][item]['capacity']

    # Generating: Supplier capacity
    mc.mcprint(text="Generating: Supplier capacity")
    SC_sp = {}
    for supplier in Data.INPUT_DATA['supplier']:
        for item in Data.INPUT_DATA['item']:
            SC_sp[(supplier, item)] = Data.INPUT_DATA['supplier'][supplier][item]

    # Generating: Lead time in months Leg 1
    mc.mcprint(text="Generating: Lead time in months Leg 1")
    LT1_sj = {}
    for supplier in Data.INPUT_DATA['supplier']:
        for warehouse in Data.INPUT_DATA['warehouse']:
            LT1_sj[(supplier, warehouse)] = int(Data.INPUT_DATA['leg1_delay'][f'{supplier}_{warehouse}']['time_months'])

    # Generating: Lead time in months Leg 2
    mc.mcprint(text="Generating: Lead time in months Leg 2")
    LT2_sj = {}
    for warehouse in Data.INPUT_DATA['warehouse']:
        for destination in Data.INPUT_DATA['destination']:
            LT2_sj[(warehouse, destination)] = int(Data.INPUT_DATA['leg2_delay'][f'{warehouse}_{destination}']['time_months'])

    # Generating: Variable Cost Leg 1
    mc.mcprint(text="Generating: Variable Cost Leg 1")
    CL1_sj = {}
    for supplier in Data.INPUT_DATA['supplier']:
        for warehouse in Data.INPUT_DATA['warehouse']:
            CL1_sj[(supplier, warehouse)] = float(Data.INPUT_DATA['leg1_cost'][f'{supplier}_{warehouse}']['cost'])

    # Generating: Variable Cost Leg 2
    mc.mcprint(text="Generating: Variable Cost Leg 2")
    CL2_sj = {}
    for warehouse in Data.INPUT_DATA['warehouse']:
        for destination in Data.INPUT_DATA['destination']:
            CL2_sj[(warehouse, destination)] = float(Data.INPUT_DATA['leg2_cost'][f'{warehouse}_{destination}']['cost'])

    # Generating: Manufacturing Costs
    mc.mcprint(text="Generating: Manufacturing Costs")
    MC_sp = {}
    for supplier in Data.INPUT_DATA['supplier']:
        for item in Data.INPUT_DATA['item']:
            MC_sp[(supplier, item)] = int(Data.INPUT_DATA['manufacture_cost'][supplier][item])

    # Generating: Storage Costs
    mc.mcprint(text="Generating: Storage Costs")
    STO_jp = {}
    for warehouse in Data.INPUT_DATA['warehouse']:
        for item in Data.INPUT_DATA['item']:
            STO_jp[(warehouse, item)] = int(Data.INPUT_DATA['warehouse'][warehouse][item])



    # Fixed Variables
    # Generating: y_jt
    mc.mcprint(text="Generating: Supplier capacity")
    y_jt = {}
    for warehouse in Data.INPUT_DATA['y_jt']:
        y_jt[(warehouse, Data.INPUT_DATA['y_jt'][warehouse]['time'])] = Data.INPUT_DATA['y_jt'][warehouse]['value']


    Data.PARAMETERS = {
        'D_kpt':   D_kpt,
        'Cap_p':   Cap_p,
        'SC_sp':   SC_sp,
        'LT1_sj':  LT1_sj,
        'LT2_sj':  LT2_sj,
        'CL1_sj':  CL1_sj,
        'CL2_sj':  CL2_sj,
        'MC_sp':  MC_sp,
        'STO_jp':  STO_jp,


        # Fixed Variables
        'y_jt': y_jt,
        }


def select_input_data_folder():
    list_dir = os.listdir(ConfigFiles.FIXED_DIRECTORIES['input_data'])
    excluded_dirs = ['output',
                     '__pycache__',
                     'mcutils']
    menu_list = []
    for directory in list_dir:
        if not os.path.isfile(directory) and directory not in excluded_dirs:
            menu_list.append(directory)

    mc_import_data = mc.Menu(title="Import Input Data", subtitle="Select the directory to import",
                             options=menu_list, back=False)
    selected_index = int(mc_import_data.show())
    selected_folder = menu_list[selected_index - 1]

    ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"] = os.path.join(ConfigFiles.FIXED_DIRECTORIES['input_data'],
                                                                         selected_folder)
    mc.mcprint(ConfigFiles.DYNAMIC_DIRECTORIES["current_input_data"], color=mc.Color.GREEN)
    return selected_folder


def clear_all_data():
    mc.mcprint(text="Applying Rollback...", color=mc.Color.ORANGE)
    Data.INPUT_DATA = {}
    Data.PARAMETERS = {}
    model2.reset_model()


def import_input_data(select_new_folder=False):
    try:
        select_input_data_folder() if select_new_folder else None
        mc.mcprint(text="Importing raw data", color=mc.Color.ORANGE)
        import_data()
        mc.mcprint(text="The data has been imported successfully\n", color=mc.Color.GREEN)
        mc.mcprint(text="Generating parameters from input data", color=mc.Color.ORANGE)
        create_parameters()
        mc.mcprint(text="Parameters has been generated successfully\n", color=mc.Color.GREEN)
        mc.mcprint(text="Constructing Model", color=mc.Color.ORANGE)
        construct_model()
    except Exception as e:
        clear_all_data()
        mc.register_error(error_string="The input directory doesn't contain a valid structure")
        mc.register_error(error_string=e)
        return


def open_simulation():
    simulation_folder_path = ConfigFiles.FIXED_DIRECTORIES['simulation_model']
    simulation_file_path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], 'Modelo Final.doe')
    mc.mcprint(text="Creating Simulation",
               color=mc.Color.PINK)
    mc.DirectoryManager.open_file(mc.DirectoryManager([simulation_folder_path]), simulation_file_path)


def save_output():
    if model2.Model.model.getStatus() not in ['optimal', 'gaplimit']:
        return

    output_file_name = 'solver_output.xls'
    mc.mcprint(text=f'Attempting to save {output_file_name}',
               color=mc.Color.YELLOW)
    wb = xlwt.Workbook()

    Model = model2.Model
    l_sjpt = Model.results['l_sjpt']
    w_jkpt = Model.results['w_jkpt']
    for item in Model.data['item']:
        ws = wb.add_sheet(item)

        ws.write(0, 0, 'periodo')
        ws.write(0, 1, 'supplier001C')
        ws.write(0, 2, 'supplier002C')
        ws.write(0, 3, 'supplier003C')
        ws.write(0, 4, 'supplier004C')

        ws.write(0, 5, 'supplier001L')
        ws.write(0, 6, 'supplier002L')
        ws.write(0, 7, 'supplier003L')
        ws.write(0, 8, 'supplier004L')

        for period in range(1, Model.MAX_TIME + 2):
            ws.write(period, 0, period - 2)

        for s_index, supplier in enumerate(Model.data['supplier']):
            for w_index, warehouse in enumerate(Model.data['warehouse']):
                # item = 'item001'
                for time in range(1, Model.MAX_TIME):
                    value = Model.model.getVal(l_sjpt[(supplier, warehouse, item, time - 2)])
                    ws.write(time, s_index + 1 + (4 * w_index), value)

    path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], output_file_name)
    try:
        wb.save(path)
        mc.mcprint(text=f'{output_file_name} saved successfully',
                   color=mc.Color.GREEN)
    except PermissionError:
        mc.register_error(error_string=f'The file {path} is currently being used. Please close the file and try again)')
        return

    output_file_name = 'solver_output_leg2.xls'
    mc.mcprint(text=f'Attempting to save {output_file_name}',
               color=mc.Color.YELLOW)
    wb = xlwt.Workbook()

    Model = model2.Model
    l_sjpt = Model.results['l_sjpt']
    for item in Model.data['item']:
        ws = wb.add_sheet(item)

        ws.write(0, 0, 'periodo')
        ws.write(0, 1, 'destination001C')
        ws.write(0, 2, 'destination002C')
        ws.write(0, 3, 'destination003C')
        ws.write(0, 4, 'destination004C')
        ws.write(0, 5, 'destination005C')
        ws.write(0, 6, 'destination006C')
        ws.write(0, 7, 'destination007C')
        ws.write(0, 8, 'destination008C')

        ws.write(0,  9, 'destination001C')
        ws.write(0, 10, 'destination002C')
        ws.write(0, 11, 'destination003C')
        ws.write(0, 12, 'destination004C')
        ws.write(0, 13, 'destination005C')
        ws.write(0, 14, 'destination006C')
        ws.write(0, 15, 'destination007C')
        ws.write(0, 16, 'destination008C')


        for period in range(1, Model.MAX_TIME):
            ws.write(period, 0, period)

        for w_index, warehouse in enumerate(Model.data['warehouse']):
            for d_index, destination in enumerate(Model.data['destination']):
                for time in range(1, Model.MAX_TIME):
                    value = Model.model.getVal(w_jkpt[(warehouse, destination, item, time)])
                    ws.write(time, d_index + 1 + (8 * w_index), value)

    path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], output_file_name)
    try:
        wb.save(path)
        mc.mcprint(text=f'{output_file_name} saved successfully',
                   color=mc.Color.GREEN)
    except PermissionError:
        mc.register_error(error_string=f'The file {path} is currently being used. Please close the file and try again)')
        return



    output_file_name = 'solver_output_warehouse.xls'
    mc.mcprint(text=f'Attempting to save {output_file_name}',
               color=mc.Color.YELLOW)
    wb = xlwt.Workbook()

    Model = model2.Model
    z_jt = Model.results['z_jt']
    for warehouse in Model.data['warehouse']:
        ws = wb.add_sheet(warehouse)

        ws.write(0, 0, 'periodo')
        ws.write(0, 1, 'is open?')

        for period in range(1, Model.MAX_TIME):
            ws.write(period, 0, period)

        for time in range(1, Model.MAX_TIME):
            value = Model.model.getVal(z_jt[(warehouse, time)])
            ws.write(time, 1, value)

    path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], output_file_name)
    try:
        wb.save(path)
        mc.mcprint(text=f'{output_file_name} saved successfully',
                   color=mc.Color.GREEN)
    except PermissionError:
        mc.register_error(error_string=f'The file {path} is currently being used. Please close the file and try again)')
        return




    output_file_name = 'solver_output_warehouse.xls'
    mc.mcprint(text=f'Attempting to save {output_file_name}',
               color=mc.Color.YELLOW)
    wb = xlwt.Workbook()

    Model = model2.Model
    s_jpt = Model.results['s_jpt']
    for warehouse in Model.data['warehouse']:
        ws = wb.add_sheet(warehouse)

        ws.write(0, 0, 'periodo')
        ws.write(0, 1, 'item001')
        ws.write(0, 2, 'item002')
        ws.write(0, 3, 'item003')
        ws.write(0, 4, 'item004')

        for period in range(1, Model.MAX_TIME):
            ws.write(period, 0, period)

        for time in range(1, Model.MAX_TIME):
            for i_index, item in enumerate(Model.data['item']):
                value = Model.model.getVal(s_jpt[(warehouse, item, time)])
                ws.write(time, i_index + 1, value)

    path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], output_file_name)
    try:
        wb.save(path)
        mc.mcprint(text=f'{output_file_name} saved successfully',
                   color=mc.Color.GREEN)
    except PermissionError:
        mc.register_error(error_string=f'The file {path} is currently being used. Please close the file and try again)')
        return


    mf_open_simulation = mc.MenuFunction(title='Yes', function=open_simulation)
    simulation_menu = mc.Menu(title=f'Would you like to open a simulation with the results?\n'
                                    f'{mc.Color.RED}    Wait for the splash screen to vanish{mc.Color.RESET}',
                              options=[mf_open_simulation, 'No'],
                              back=False)
    simulation_menu.show()


def optimize():
    # Only if model has been created properly
    if model2.Model.model:
        print(mc.Color.GREEN)
        os.chdir(ConfigFiles.FIXED_DIRECTORIES["output"])  # Change dir to write the problem in output folder
        model2.Model.model.writeProblem()
        print(mc.Color.CYAN)
        model2.Model.model.optimize()
        model2.display_optimal_information()
        os.chdir(ConfigFiles.FIXED_DIRECTORIES['working_dir'])  # Head back to original working directory
        print(mc.Color.RESET)
        save_output()
    else:
        mc.register_error(error_string="The model hasn't been created properly")


def construct_model():
    try:
        model2.build_model(data=Data.INPUT_DATA, parameters=Data.PARAMETERS)
        mc.mcprint(text="Model has been constructed successfully", color=mc.Color.GREEN)
        mc.mcprint(text="\nThe instance is ready to be optimized", color=mc.Color.GREEN)
    except Exception as e:
        mc.register_error(error_string="There was an error generating the model")
        mc.register_error(error_string=e)


def display_parameters():
    pprint(Data.PARAMETERS)


def read_manual(path=None):
    if path:
        print("nice")
    directory_path = ConfigFiles.FIXED_DIRECTORIES['working_dir']
    file_path = os.path.join(directory_path, 'README.pdf')
    dir_manager = mc.DirectoryManager([directory_path])
    dir_manager.open_file(file_path)


def easter_egg():
    with open(os.path.join(ConfigFiles.FIXED_DIRECTORIES['working_dir'], 'old_man.txt')) as file:
        for line in file:
            print(line.strip())
