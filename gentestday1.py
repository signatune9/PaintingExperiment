from psychopy import visual, core, event, monitors

import paintings

# Import settings from params file.
from params import CONDITION, SUBJECT_ID, HRES, VRES, EXPHRES, EXPVRES, SCREENDISTANCE, SCREENWIDTH, FILEPATH

if __name__ == '__main__':

    # Initialize window and mouse objects.
    experiment_monitor = monitors.Monitor('expMonitor', distance=SCREENDISTANCE, width=SCREENWIDTH)
    experiment_monitor.setSizePix((EXPHRES, EXPVRES))
    experiment_monitor.saveMon()
    window = visual.Window([HRES, VRES], allowGUI=True, monitor=experiment_monitor, units='deg', color='white')
    mouse = event.Mouse(visible=True, newPos=None, win=window)

    # Read the procedural csv
    procedural_file_list = paintings.read_procedural_csv()

    # Create the results file. Returns 0 if the results file already exists (check for interrupted study)
    new_session = paintings.create_results_file()

    instructions_index = 0

    # Start the experiment's clock.
    experiment_clock = paintings.start_experiment_clock()

    # Get the artists being used for the experiment.
    artists = paintings.get_artists(procedural_file_list)

    # Create buttons for the experiment.
    buttons = paintings.create_buttons(window, len(artists))

    instruction_counter = 0
    start_index = 0
    for current_trial in procedural_file_list:
        if current_trial[1] == 'instruct':
            instruction_counter += 1
            start_index += 1
            instructions_index += 1
        elif current_trial[1] == 'GenTest':
            break
        else:
            instruction_counter = 0
            start_index += 1

    start_index = start_index - instruction_counter
    end_flag = 0
    for current_trial in procedural_file_list[start_index:]:

        if current_trial[1] != 'GenTest':
            if end_flag == 1:
                break

        if current_trial[1] == 'instruct':
            paintings.instructions_trial(window, mouse, current_trial, instructions_index)
            instructions_index += 1

        elif current_trial[1] == 'GenTest':
            paintings.gen_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons)
            end_flag = 1

        elif current_trial[0] == 'Session1':
            paintings.write_trial(current_trial, "NA", "NA", "NA")

        elif current_trial[1] == 'NA':
            paintings.write_trial(current_trial, "NA", "NA", "NA")