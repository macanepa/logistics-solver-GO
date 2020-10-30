import mcutils as mc
import utilities

mc.ColorSettings.print_color = True
mc.ColorSettings.is_dev = False
mc.LogSettings.display_logs = True
utilities.initialize()

about = mc.Credits(authors=['Matías Cánepa (Dev)',
                            'Franco Balocchi',
                            'Enrique García',
                            'Paula Malatesta',
                            'María Paz Ponce',
                            'María-Jesús Torrealba'],
                   team_name='Team 8',
                   github_account='macanepa',
                   email_address='macanepa@miuandes.cl',
                   company_name='Huit Consultora',
                   github_repo='https://github.com/macanepa/logistics-solver-GO')

mf_exit_application = mc.MenuFunction(title='Exit', function=mc.exit_application)
mf_import_input_data = mc.MenuFunction('Change Input Data Folder', utilities.import_input_data, select_new_folder=True)
mf_optimize = mc.MenuFunction(title='Optimize', function=utilities.optimize)
mf_about = mc.MenuFunction(title='About', function=about.print_credits)
mf_display_input_data = mc.MenuFunction(title='Display Input Data', function=utilities.print_input_data)
mf_display_parameters = mc.MenuFunction(title='Display Parameters', function=utilities.display_parameters)
mf_read_manual = mc.MenuFunction(title='Read Manual', function=utilities.read_manual)

mc_main_menu = mc.Menu(title='Huit Consultora Solver',
                       subtitle='Select an Option',
                       options=[mf_import_input_data, mf_optimize, mf_display_input_data, mf_display_parameters,
                                mf_read_manual, mf_about, mf_exit_application], back=False)

while True:
    mc_main_menu.show()
