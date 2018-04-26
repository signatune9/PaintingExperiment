from psychopy import visual, core, event, monitors
from bisect import bisect
import csv
import random
import os

# Import settings from params file.
from params import CONDITION, SUBJECT_ID, HRES, VRES, MONITORNAME, FILEPATH

# To Do: Instructions, cleaner buttons?


def read_procedural_csv():
    """
    Reads the procedural file for the experiment.
    Inputs: None.
    Returns: A list containing the procedural file entries.
    """

    if CONDITION == 0:
        with open(SUBJECT_ID + '_BF_FullExpProc.csv', 'rt') as experiment_file:
            procedural_file_reader = csv.reader(experiment_file, delimiter=',')
            procedural_file_list = list(procedural_file_reader)
    else:
        with open(SUBJECT_ID + '_IF_FullExpProc.csv', 'rt') as experiment_file:
            procedural_file_reader = csv.reader(experiment_file, delimiter=',')
            procedural_file_list = list(procedural_file_reader)

    return procedural_file_list


def create_results_file():
    """
    Create the results CSV file for the experiment. Fails if the file already exists.
    Inputs: None.
    Returns: 1 if the file was successfully created, 0 otherwise.
    """

    if CONDITION == 0:
        if os.path.isfile(SUBJECT_ID + '_BF_FullExpResults.csv'):
            return 0
        with open(SUBJECT_ID + '_BF_FullExpResults.csv', 'w+b') as results_file:
            procedure_file_writer = csv.writer(results_file, delimiter=',')
            procedure_file_writer.writerow(["ItemNum", "Phase", "Painting", "Artist", "Schedule", "ConDir",
                                            "ConName", "ConCat", "Block", "Notes", "Accuracy", "Reaction Time",
                                            "Selected Artist"])

    else:
        if os.path.isfile(SUBJECT_ID + '_IF_FullExpResults.csv'):
            return 0
        with open(SUBJECT_ID + '_IF_FullExpResults.csv', 'w+b') as results_file:
            procedure_file_writer = csv.writer(results_file, delimiter=',')
            procedure_file_writer.writerow(["ItemNum", "Phase", "Painting", "Artist", "Schedule", "ConDir",
                                            "ConName", "ConCat", "Block", "Notes", "Accuracy", "Reaction Time",
                                            "Selected Artist"])

    return 1


def get_results_status():
    """
    If the results file already exists, continue from the next trial.
    Inputs: None.
    Return: The trial number to continue from.
    """

    if CONDITION == 0:
        with open(SUBJECT_ID + '_BF_FullExpResults.csv', 'rt') as experiment_file:
            results_reader = csv.reader(experiment_file, delimiter=',')
            results_list = list(results_reader)

    else:
        with open(SUBJECT_ID + '_IF_FullExpResults.csv', 'rt') as experiment_file:
            results_reader = csv.reader(experiment_file, delimiter=',')
            results_list = list(results_reader)

    instructions_index = 0
    for trial in results_list:
        if trial[1] == 'instruct':
            instructions_index = instructions_index + 1

    status = [len(results_list), instructions_index]

    return status


def start_experiment_clock():
    """
    Creates and starts a monotonic clock for the experiment, to be used for recording timings.
    Inputs: None.
    Returns: The MonotonicClock object.
    """

    experiment_clock = core.MonotonicClock()
    return experiment_clock


def get_artists(procedural_file_list):
    """
    Gets a list of the artists being used in the study.
    Inputs: procedural_file_list = The list containing the procedural file entries.
    Returns: A list containing the names of the artists used in the study.
    """

    artists = []

    for entry in procedural_file_list:
        if entry[1] == 'Study':
            if entry[3] not in artists:
                artists.append(entry[3])
        if entry[1] == 'GenTest':
            break

    return artists


def read_trial(procedural_file_list, trial_num):
    """
    Gets the information from the procedural file for the trial number given.
    Inputs: procedural_file_list = The list containing the procedural file entries.
            trial_num = The trial number to read from the procedure file.
    Returns: A list containing the row of the trial number given.
    """

    trial_line = procedural_file_list[trial_num]
    return trial_line


def get_context_list(procedural_file_list):
    """
    Gets a sorted list of (painting_path, context_path) pairs being used for the experiment.
    Inputs: procedural_file_list = The list containing the procedural file entries.
    Returns: A list containing (painting_path, context_path) pairs for all the paintings in the study phase.
    """

    context_list = []

    for trial in procedural_file_list:
        if trial[1] == "Study":
            context_list_entry = [trial[2], trial[3], trial[5], trial[7]]
            if context_list_entry not in context_list:
                context_list.insert(bisect(context_list, context_list_entry), context_list_entry)
        elif trial[1] == "GenTest":
            break

    return context_list


def get_context_images(current_painting, current_artist, context_category, context_list):
    """
    Gets a list of context images to show during recognition tests.
    Inputs: current_painting = The correct painting to be shown for this trial.
            current_artist = The artist of the paintings for this trial.
            context_category = The context category of the correct painting.
            context_list = The list of paintings to context pairs.
    Returns: A list of the paths to the context images to show.
    """

    context_path_list = []

    if context_category == "mm":
        num_manmade = 1
        num_natural = 0
    else:
        num_manmade = 0
        num_natural = 1

    other_artist_paintings = []

    for context_entry in context_list:
        if current_artist == context_entry[1]:
            if current_painting != context_entry[0]:
                print(context_entry)
                other_artist_paintings.append(context_entry)
            else:
                context_path_list.append(context_entry[2])

    random.shuffle(other_artist_paintings)
    for context_entry in other_artist_paintings:
        if context_entry[3] == "mm":
            if num_manmade < 3:
                context_path_list.append(context_entry[2])
                num_manmade += 1
        else:
            if num_natural < 3:
                context_path_list.append(context_entry[2])
                num_natural += 1

    random.shuffle(context_path_list)

    return context_path_list


def draw_instructions(window, mouse, instructions_index):
    """
    Draws the given instructions on the screen and waits for the subject to press the 'Next' button.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            instruction_text = The instructions to be written on the screen.
    Returns: None.
    """

    next_button = visual.Rect(window, width=5.0, height=1.0, lineWidth=1.5, lineColor='black', pos=[10.5, -10])
    next_button_text = visual.TextStim(window, text='Next', color='black', pos=[10.5, -10])

    next_button.draw()
    next_button_text.draw()

    window.flip()

    while True:
        if mouse.isPressedIn(next_button, buttons=[0]):
            break


def draw_study_images(window, painting_path, context_path):
    """
    Draws the given painting and context images. Does not actually flip the window to show the images.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
            context_path = The path to the context image to draw.
    Returns: None.
    """

    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=15, pos=[-9.0, 4])
    context = visual.ImageStim(window, image=FILEPATH + context_path, size=15, pos=[9.0, 4])

    painting.draw()
    context.draw()


def draw_gen_test_image(window, painting_path):
    """
    Draws the given painting image. Does not actually flip the window to show the images.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
    """
    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=15, pos=[0.0, 4])

    painting.draw()


def draw_rec_test_image(window, painting_path, context_paths):
    """
    Draws the given painting image. Draws each of the context images given in the list of context paths.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
            context_paths = A list containing the paths of all the context images to draw.
    Returns: A list containing the ImageStims for each of the context images.
    """

    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=12, pos=[0.0, 8])
    context_images = []
    x_positions = [-8.5, 0, 8.5]
    y_positions = [-2.5, -11]

    i = 0
    for context_path in context_paths:
        context_images.append(visual.ImageStim(window, image=FILEPATH + context_path, size=8,
                                               pos=[x_positions[i % 3], y_positions[i/3]]))
        i = i + 1

    painting.draw()

    for contextImage in context_images:
        contextImage.draw()

    return context_images


def draw_genrec_test_image(window, context_path):
    """
    Draws the given context image. Does not actually flip the window to show the images.
    Inputs: window = The window object being used for the experiment.
            context_path = The path to the context image to draw.
    """

    context = visual.ImageStim(window, image=FILEPATH + context_path, size=15, pos=[0.0, 4])

    context.draw()


def create_buttons(window, num_artists):
    """
    Creates num_artists amount of buttons, arranged in rows of three.
    Inputs: window = The window object being used for the experiment.
            num_artists = The number of artists being used in the experiment.
    Returns: An array containing the button objects.
    """

    button_array = []
    x_positions = [-10.5, 0, 10.5]
    y_positions = [-5, -7.5, -10, -12.5, -15]

    for i in range(0, num_artists):
        button_array.append(visual.Rect(window, width=5.0, height=1.0, lineWidth=1.5, lineColor='black',
                                        pos=[x_positions[i % 3], y_positions[i // 3]]))

    return button_array


def create_artist_button_text(window, artists):
    """
    Creates text displaying artist names for each button. 
    Inputs: window = The window object being used for the experiment.
            artist_array = An array containing the names of the artists being used in the experiment.
    Returns: An array containing the text objects to be placed on top of the buttons.
    """

    button_text_array = []
    x_positions = [-10.5, 0, 10.5]
    y_positions = [-5, -7.5, -10, -12.5, -15]

    for i in range(0, len(artists)):
        button_text_array.append(visual.TextStim(window, pos=[x_positions[i % 3], y_positions[i // 3]], text=artists[i],
                                                 color='black'))

    return button_text_array


def draw_buttons(button_array, button_text_array):
    """
    Draws the buttons and button text onto the frame. Does not actually display the buttons to the subject.
    Inputs: button_array = An array containing containing the button objects.
            button_text_array = An array containing the text objects to be placed on top of the buttons.
    Returns: None.
    """

    for i in range(0, len(button_array)):
        button_array[i].draw()
        button_text_array[i].draw()


def start_trial(window, experiment_clock):
    """
    Starts a trial, displaying the stimuli and buttons and returning the time at which they were displayed.
    Inputs: window = The window object being used for the experiment.
            experiment_clock = The MonotonicClock being used for the experiment.
    Returns: The time at which the trial started.
    """

    window.flip()
    start_time = experiment_clock.getTime()

    return start_time


def get_response(mouse, button_array, artist_array, wait_time, experiment_clock):
    """

    Inputs: mouse = The mouse object being used for the experiment.
            button_array = The array of buttons being used for the trial.
            artist_array = The array of artists that was used for creating the button text for the trial.
            wait_time = The amount of time to wait until ending the trial.
            experiment_clock = The MonotonicClock being used for the experiment.
    Returns: An array containing the time at which the response was recorded and the artist that was selected.
             Returns 0, 'No answer' if no answer is given.
    """

    timer = core.Clock()
    timer.add(wait_time)

    response_array = []

    while timer.getTime() < 0:
        for i in range(0, len(button_array)):
            if mouse.isPressedIn(button_array[i], buttons=[0]):
                time_of_response = experiment_clock.getTime()
                response = artist_array[i]
                response_array.append(time_of_response)
                response_array.append(response)
                return response_array

    response_array.append(0)
    response_array.append('No answer')

    return response_array


def get_accuracy(response, correct_artist):
    """
    Calculates whether the given response was correct.
    Inputs: response = The name of the artist selected by the subject.
            correct_artist = The name of the correct artist for the trial.
    Returns: 1 if the correct artist was selected, 0 otherwise.
    """
    if response == correct_artist:
        accuracy = 1
    else:
        accuracy = 0

    return accuracy


def get_reaction_time(response_time, start_time):
    """
    Gets the reaction time for the trial.
    Inputs: response_time = The time at which the subject responded.
            start_time = The time at which the trial started.
    Returns:
    """

    if response_time != 0:
        return float("{:.5f}".format(response_time - start_time))
    else:
        return 0


def write_trial(trial_row, accuracy, response_time, response):
    """
    Writes the response, response time, and accuracy to the results file.
    Inputs: trial_row = The information for that trial taken from the procedural file.
            accuracy = The accuracy of the response given by the subject.
            response_time = The reaction time of the response by the subject.
            response = The response given by the subject.
    Returns: None
    """
    results_row = trial_row
    results_row.extend((accuracy, response_time, response))
    if CONDITION == 0:
        with open(SUBJECT_ID + '_BF_FullExpResults.csv', 'ab') as experiment_csv:
            procedure_file_writer = csv.writer(experiment_csv, delimiter=',')
            procedure_file_writer.writerow(results_row)

    else:
        with open(SUBJECT_ID + '_IF_FullExpResults.csv', 'ab') as experiment_csv:
            procedure_file_writer = csv.writer(experiment_csv, delimiter=',')
            procedure_file_writer.writerow(results_row)


def show_feedback(window, correct_artist, painting_path):
    """
    Displays feedback for the current trial.
    Inputs: window = The window object being used for the experiment.
            correct_artist = The name of the correct artist for the trial.
            painting_path = The path to the painting image to draw.
    """

    response_text = visual.TextStim(window, pos=[0, -5], text="The correct artist is: \n" + correct_artist,
                                    color='black')
    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=15, pos=[0, 4])

    painting.draw()
    response_text.draw()

    window.flip()
    core.wait(2.5)


def show_buffer_screen(window):
    """
    Clears the screen and shows a white screen for one second.
    Inputs: window = The window object being used for the experiment.
    Returns: None.
    """

    window.flip(clearBuffer=True)
    core.wait(1.0)


def instructions_trial(window, mouse, current_trial, instructions_index):
    """
    Runs an instructions trial of the experiment.
    Inputs: window: The window object being used for the experiment.
            mouse: The mouse object being used for the experiment.
            current_trial: The row from the procedural file containing the information for this trial.
            instructions_index: The index to read in the instructions proc file.
    Returns: None.
    """

    draw_instructions(window, mouse, instructions_index)
    write_trial(current_trial, "NA", "NA", "NA")
    show_buffer_screen(window)


def study_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the study phase.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The MonotonicClock being used for the experiment.
            artists = The list of artists being used for the experiment.
            buttons = The buttons being used for the trial.
    Returns: None.
    """

    random_artists = artists
    random.shuffle(random_artists)
    random_artist_button_text = create_artist_button_text(window, random_artists)
    draw_study_images(window, current_trial[2], current_trial[5])
    draw_buttons(buttons, random_artist_button_text)
    start_time = start_trial(window, experiment_clock)
    response = get_response(mouse, buttons, random_artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])
    show_feedback(window, current_trial[3], current_trial[2])
    write_trial(current_trial, accuracy, reaction_time, response[1])
    show_buffer_screen(window)


def gen_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the generalization test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The MonotonicClock being used for the experiment.
            artists = The list of artists being used for the experiment.
            buttons = The buttons being used for the trial.
    Returns: None.
    """

    artist_button_text = create_artist_button_text(window, artists)
    draw_gen_test_image(window, current_trial[2])
    draw_buttons(buttons, artist_button_text)
    start_time = start_trial(window, experiment_clock)
    response = get_response(mouse, buttons, artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])
    write_trial(current_trial, accuracy, reaction_time, response[1])
    show_buffer_screen(window)


def rec_test_trial(window, mouse, current_trial, experiment_clock, context_list):
    """
    Runs a trial of the detailed recognition test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The MonotonicClock being used for the experiment.
            context_list =
    Returns: None.
    """

    context_images = get_context_images(current_trial[2], current_trial[3], current_trial[7], context_list)
    image_buttons = draw_rec_test_image(window, current_trial[2], context_images)
    start_time = start_trial(window, experiment_clock)
    response = get_response(mouse, image_buttons, context_images, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[5])
    write_trial(current_trial, accuracy, reaction_time, response[1])
    show_buffer_screen(window)


def genrec_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the general recognition test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The MonotonicClock being used for the experiment.
            artists = The list of artists being used for the experiment.
            buttons = The buttons being used for the trial.
    Returns: None.
    """

    artist_button_text = create_artist_button_text(window, artists)
    draw_gen_test_image(window, current_trial[5])
    draw_buttons(buttons, artist_button_text)
    start_time = start_trial(window, experiment_clock)
    response = get_response(mouse, buttons, artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])
    write_trial(current_trial, accuracy, reaction_time, response[1])
    show_buffer_screen(window)


def main():
    """
    Main function, runs the painting experiment based on the parameters defined in params.py.
    """

    # Initialize window and mouse objects.
    my_monitor = monitors.Monitor('test', distance=57, width=30)
    my_monitor.setSizePix((1024, 768))
    my_monitor.saveMon()
    window = visual.Window([HRES, VRES], allowGUI=True, monitor=my_monitor, units='deg', color='white')
    mouse = event.Mouse(visible=True, newPos=None, win=window)

    # Read the procedural csv
    procedural_file_list = read_procedural_csv()

    # Create the results file. Returns 0 if the results file already exists (check for interrupted study)
    new_session = create_results_file()

    if new_session != 1:
        status = get_results_status()
        current_status = status[0]
        instructions_index = status[1]
    else:
        current_status = 0
        instructions_index = 0

    # Start the experiment's clock.
    experiment_clock = start_experiment_clock()

    # Get the artists being used for the experiment.
    artists = get_artists(procedural_file_list)

    # Create buttons for the experiment.
    buttons = create_buttons(window, len(artists))

    context_list = get_context_list(procedural_file_list)

    # Check for each type of trial and run it
    for current_trial in procedural_file_list[current_status:]:

        if current_trial[1] == 'instruct':
            instructions_trial(window, mouse, current_trial, instructions_index)
            instructions_index = instructions_index + 1

        elif current_trial[1] == 'Study':
            study_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[1] == 'GenTest':
            gen_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[1] == 'RecTest':
            rec_test_trial(window, mouse, current_trial, experiment_clock, context_list)

        elif current_trial[1] == 'GenRecTest':
            genrec_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[0] == 'Session2':
            write_trial(current_trial, "NA", "NA", "NA")
            break

        elif current_trial[0] == 'Session1':
            write_trial(current_trial, "NA", "NA", "NA")


main()
