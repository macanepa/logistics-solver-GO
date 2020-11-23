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
    locations = {'demand_london': 'destination001'}
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


    # Fixed Variables
    # Generating: y_jt
    mc.mcprint(text="Generating: Supplier capacity")
    y_jt = {}
    for warehouse in Data.INPUT_DATA['y_jt']:
        y_jt[(warehouse, Data.INPUT_DATA['y_jt'][warehouse]['time'])] = Data.INPUT_DATA['y_jt'][warehouse]['value']


    Data.PARAMETERS = {
        'D_kpt':   D_kpt,
        'Cap_p':   Cap_p,
        'SC_sp': SC_sp,

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
    simulation_file_path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], 'videoconferencing final.doe')
    mc.mcprint(text="Creating Simulation",
               color=mc.Color.PINK)
    mc.DirectoryManager.open_file(mc.DirectoryManager([simulation_folder_path]), simulation_file_path)

def save_output():
    output_file_name = 'solver_output.xls'
    mc.mcprint(text=f'Attempting to save {output_file_name}',
               color=mc.Color.YELLOW)
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet1')

    ws.write(0, 1, 'Demanda')
    ws.write(1, 0, 'c1')
    ws.write(2, 0, 'c2')

    ws.write(1, 1, 350)
    ws.write(2, 1, 250)

    path = os.path.join(ConfigFiles.FIXED_DIRECTORIES['simulation_model'], 'solver_output.xls')
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