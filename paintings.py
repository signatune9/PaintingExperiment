from psychopy import visual, core, event, monitors
from bisect import bisect
import csv
import random
import os
import datetime

# Import settings from params file.
from params import CONDITION, SUBJECT_ID, HRES, VRES, EXPHRES, EXPVRES, SCREENWIDTH, FILEPATH, INPUT_MODE

IMAGE_SIZE = (333.0 / HRES) * SCREENWIDTH
IMAGE_Y_POS = IMAGE_SIZE / 2

PAINTING_SIZE = (IMAGE_SIZE*(500.0/333), IMAGE_SIZE)
CONTEXT_SIZE = (IMAGE_SIZE, IMAGE_SIZE)

TOTAL_WIDTH = PAINTING_SIZE[0] + CONTEXT_SIZE[0] + 1
LEFT_CENTER_POINT = TOTAL_WIDTH / -2 + PAINTING_SIZE[0] / 2
RIGHT_CENTER_POINT = TOTAL_WIDTH / 2 - CONTEXT_SIZE[0] / 2

PAINTING_ALIGN_LEFT_POS = (LEFT_CENTER_POINT, IMAGE_Y_POS)
PAINTING_ALIGN_CENTER_POS = (0, IMAGE_Y_POS)
CONTEXT_ALIGN_RIGHT_POS = (RIGHT_CENTER_POINT, IMAGE_Y_POS)
CONTEXT_ALIGN_CENTER_POS = (0, IMAGE_Y_POS)

LABEL_Y_POS = IMAGE_SIZE + 1
LABEL_CENTER_POS = (0.0, LABEL_Y_POS)
LABEL_LEFT_POS = (LEFT_CENTER_POINT, LABEL_Y_POS)
LABEL_RIGHT_POS = (RIGHT_CENTER_POINT, LABEL_Y_POS)

TEXT_HEIGHT = 1.2

BUTTON_SIZE = (6.5, 2)
BUTTON_LINE_WIDTH = 1.5
BUTTON_X_POSITIONS = [-18.75, -11.25, -3.75, 3.75, 11.25, 18.75]
BUTTON_Y_POSITIONS = [-2.5]

MOUSE_X_BUTTON_POSITIONS = [-3, 0, 3]
MOUSE_Y_BUTTON_POSITIONS = [-1, -2.25, -3.5, -4.75, -6]

if IMAGE_SIZE * 6 + 2.25 > SCREENWIDTH:
    REC_CONTEXT_SIZE = (SCREENWIDTH - 2.25) / 6
else:
    REC_CONTEXT_SIZE = IMAGE_SIZE

REC_X_POSITIONS = [(-2.5 * REC_CONTEXT_SIZE - 0.625), (-1.5 * REC_CONTEXT_SIZE - 0.375), (-0.5 * REC_CONTEXT_SIZE - 0.125), (0.5 * REC_CONTEXT_SIZE + 0.125), (1.5 * REC_CONTEXT_SIZE + 0.375), (2.5 * REC_CONTEXT_SIZE + 0.625)]
REC_Y_POSITIONS = [(REC_CONTEXT_SIZE / -2.0) - 1]

NEXT_BUTTON_POS = [5, -5]

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
            procedure_file_writer.writerow(["ItemNum", "Phase", "Painting", "Artist", "Schedule", "ConDir", "ConName", "ConCat", "Block", "Notes", "Subj", "Stimset", "Stimsubset", "Order", "Accuracy", "Reaction Time", "Selected Artist", "Date", "Time"])

    else:
        if os.path.isfile(SUBJECT_ID + '_IF_FullExpResults.csv'):
            return 0
        with open(SUBJECT_ID + '_IF_FullExpResults.csv', 'w+b') as results_file:
            procedure_file_writer = csv.writer(results_file, delimiter=',')
            procedure_file_writer.writerow(["ItemNum", "Phase", "Painting", "Artist", "Schedule", "ConDir", "ConName", "ConCat", "Block", "Notes", "Subj", "Stimset", "Stimsubset", "Order", "Accuracy", "Reaction Time", "Selected Artist", "Date", "Time"])

    return 1


def get_results_status():
    """
    If the results file already exists, finds the next trial to continue from.
    Inputs: None.
    Return: The trial number to continue from and the index of the next instruction to show.
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
            instructions_index += 1

    status = [len(results_list), instructions_index]

    return status


def start_experiment_clock():
    """
    Creates and starts a clock for the experiment, to be used for recording timings.
    Inputs: None.
    Returns: The Clock object.
    """

    experiment_clock = core.Clock()
    return experiment_clock


def get_artists(procedural_file_list):
    """
    Gets a list of the artists being used in the study.
    Inputs: procedural_file_list = The list containing the procedural file entries.
    Returns: A list containing the names of the artists used in the study.
    """

    artists = []
    done_flag = False

    for trial in procedural_file_list:
        if trial[1] != 'Study' and done_flag:
            break

        elif trial[1] != 'Study':
            continue

        else:
            if trial[3] not in artists:
                artists.append(trial[3])
            done_flag = True

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
    Gets a list of [painting_path, artist, context_path, context_type] entries being used for the experiment, sorted
        by painting_path.
    Inputs: procedural_file_list = The list containing the procedural file entries.
    Returns: A list containing the context entries for all the paintings in the study phase.
    """

    context_list = []
    done_flag = False

    for trial in procedural_file_list:
        if trial[1] != 'Study' and done_flag:
            break

        elif trial[1] != 'Study':
            continue

        else:
            context_list_entry = [trial[2], trial[3], trial[5], trial[7]]
            if context_list_entry not in context_list:
                context_list.insert(bisect(context_list, context_list_entry), context_list_entry)
            done_flag = True

    return context_list


def get_context_images(current_painting, current_artist, context_category, context_list):
    """
    Gets a list of six context images to show during recognition tests. One of the images is the matching context image
        for the current painting. The other five images are randomly selected context matches from the artist's other
        paintings. Three of the context images returned will be manmade, the other three will be natural.
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
    done_flag = False

    for context_entry in context_list:
        if current_artist == context_entry[1]:
            if current_painting != context_entry[0]:
                other_artist_paintings.append(context_entry)
            else:
                context_path_list.append(context_entry[2])
            done_flag = True
        elif done_flag:
            break

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

# To Do: Fix instruction logic on restart
def draw_instructions(window, mouse, instruction_name):
    """
    Draws the given instructions on the screen and waits for the subject to press the 'Next' button.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            instruction_text = The instructions to be written on the screen.
    Returns: None.
    """

    with open('InstructStim.csv', 'rt') as instructions_file:
        procedural_file_reader = csv.reader(instructions_file, delimiter=',')
        instructions_file_list = list(procedural_file_reader)

    for row in instructions_file_list:
        if instruction_name == row[1]:
            instruction_path = row[0]

    instruction = visual.ImageStim(window, image=FILEPATH + "images/" + instruction_path, pos=PAINTING_ALIGN_CENTER_POS)
    instruction.size = (instruction.size[0]*0.5, instruction.size[1]*0.5)

    if INPUT_MODE == 0:
        next_button = visual.Rect(window, width=BUTTON_SIZE[0], height=BUTTON_SIZE[1], lineWidth=BUTTON_LINE_WIDTH, lineColor='black', pos=NEXT_BUTTON_POS)
        next_button_text = visual.TextStim(window, text='Next', color='black', pos=NEXT_BUTTON_POS, height=TEXT_HEIGHT)

        next_button.draw()
        next_button_text.draw()

    instruction.draw()
    window.flip()

    if INPUT_MODE == 0:
        while True:
            if mouse.isPressedIn(next_button, buttons=[0]):
                break

    elif INPUT_MODE == 1:
        event.waitKeys(keyList=['1', '2', '3', '6', '7', '8'])

    else:
        event.waitKeys(keyList=['s', 'd', 'f', 'j', 'k', 'l'])


def draw_study_images(window, painting_path, context_path):
    """
    Draws the given painting and context images. Does not actually flip the window to show the images.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
            context_path = The path to the context image to draw.
    Returns: None.
    """

    painting_text = visual.TextStim(window, pos=LABEL_LEFT_POS, text="Painting:", color='black', height=TEXT_HEIGHT)
    context_text = visual.TextStim(window, pos=LABEL_RIGHT_POS, text="Location:", color='black', height=TEXT_HEIGHT)

    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=PAINTING_SIZE, pos=PAINTING_ALIGN_LEFT_POS)
    context = visual.ImageStim(window, image=FILEPATH + context_path, size=CONTEXT_SIZE, pos=CONTEXT_ALIGN_RIGHT_POS)

    painting_text.draw()
    context_text.draw()
    painting.draw()
    context.draw()


def draw_gen_test_image(window, painting_path):
    """
    Draws the given painting image. Does not actually flip the window to show the images.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
    """
    painting_text = visual.TextStim(window, pos=LABEL_CENTER_POS, text="Painting:", color='black', height=TEXT_HEIGHT)
    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=PAINTING_SIZE, pos=PAINTING_ALIGN_CENTER_POS)

    painting_text.draw()
    painting.draw()


def draw_rec_test_image(window, painting_path, context_paths):
    """
    Draws the given painting image. Draws each of the context images given in the list of context paths.
    Inputs: window = The window object being used for the experiment.
            painting_path = The path to the painting image to draw.
            context_paths = A list containing the paths of all the context images to draw.
    Returns: A list containing the ImageStims for each of the context images.
    """
    painting_text = visual.TextStim(window, pos=LABEL_CENTER_POS, text="Painting:", color='black', height=TEXT_HEIGHT)
    painting = visual.ImageStim(window, image=FILEPATH + painting_path, size=PAINTING_SIZE, pos=PAINTING_ALIGN_CENTER_POS)

    context_images = []

    i = 0
    for context_path in context_paths:
        context_images.append(visual.ImageStim(window, image=FILEPATH + context_path, size=(REC_CONTEXT_SIZE, REC_CONTEXT_SIZE), pos=[REC_X_POSITIONS[i % 6], REC_Y_POSITIONS[i/6]]))
        i = i + 1

    painting_text.draw()
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
    context_text = visual.TextStim(window, pos=LABEL_CENTER_POS, text="Location:", color='black', height=TEXT_HEIGHT)
    context = visual.ImageStim(window, image=FILEPATH + context_path, size=CONTEXT_SIZE, pos=CONTEXT_ALIGN_CENTER_POS)

    context_text.draw()
    context.draw()


def create_buttons(window, num_artists):
    """
    Creates num_artists amount of buttons, arranged in rows of three.
    Inputs: window = The window object being used for the experiment.
            num_artists = The number of artists being used in the experiment.
    Returns: An array containing the button objects.
    """

    if INPUT_MODE == 0:
        button_array = []

        for i in range(0, num_artists):
            button_array.append(visual.Rect(window, width=BUTTON_SIZE[0], height=BUTTON_SIZE[1], lineWidth=BUTTON_LINE_WIDTH, lineColor='black', pos=[MOUSE_X_BUTTON_POSITIONS[i % 3], MOUSE_Y_BUTTON_POSITIONS[i // 3]]))

    else:
        button_array = []

        for i in range(0, num_artists):
            button_array.append(visual.Rect(window, width=BUTTON_SIZE[0], height=BUTTON_SIZE[1], lineWidth=BUTTON_LINE_WIDTH, lineColor='black', pos=[BUTTON_X_POSITIONS[i % 6], BUTTON_Y_POSITIONS[i // 6]]))

    return button_array


def create_artist_button_text(window, artists):
    """
    Creates text displaying artist names for each button. 
    Inputs: window = The window object being used for the experiment.
            artist_array = An array containing the names of the artists being used in the experiment.
    Returns: An array containing the text objects to be placed on top of the buttons.
    """

    if INPUT_MODE == 0:
        button_text_array = []

        for i in range(0, len(artists)):
            button_text_array.append(visual.TextStim(window, pos=[MOUSE_X_BUTTON_POSITIONS[i % 3], MOUSE_Y_BUTTON_POSITIONS[i // 3]], text=artists[i], color='black', height=TEXT_HEIGHT))

    else:
        button_text_array = []

        for i in range(0, len(artists)):
            button_text_array.append(visual.TextStim(window, pos=[BUTTON_X_POSITIONS[i % 6], BUTTON_Y_POSITIONS[i // 6]], text=artists[i], color='black', height=TEXT_HEIGHT))

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
            experiment_clock = The Clock being used for the experiment.
    Returns: The time at which the trial started.
    """

    window.flip()
    start_time = experiment_clock.getTime()

    return start_time


def get_response(window, mouse, button_array, artist_array, wait_time, experiment_clock):
    """
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            button_array = The array of buttons being used for the trial.
            artist_array = The array of artists that was used for creating the button text for the trial.
            wait_time = The amount of time to wait until ending the trial.
            experiment_clock = The Clock being used for the experiment.
    Returns: An array containing the time at which the response was recorded and the artist that was selected.
             Returns 0, 'No answer' if no answer is given.
    """

    if INPUT_MODE == 0:
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
        response_array = [0, 'No answer']
        return response_array

    elif INPUT_MODE == 1:
        selected_artist = []

        selection = event.waitKeys(maxWait=wait_time, keyList=['1', '2', '3', '6', '7', '8', 'q'],
                                   timeStamped=experiment_clock)
        if selection is None:
            response_array = [0, 'No answer']
            return response_array
        elif selection[0][0] == '8':
            selected_artist = artist_array[0]
        elif selection[0][0] == '7':
            selected_artist = artist_array[1]
        elif selection[0][0] == '6':
            selected_artist = artist_array[2]
        elif selection[0][0] == '1':
            selected_artist = artist_array[3]
        elif selection[0][0] == '2':
            selected_artist = artist_array[4]
        elif selection[0][0] == '3':
            selected_artist = artist_array[5]
        elif selection[0][0] == 'q':
            window.close()
            core.quit()

        response_array = [selection[0][1], selected_artist]
        return response_array

    else:
        selected_artist = []

        selection = event.waitKeys(maxWait=wait_time, keyList=['s', 'd', 'f', 'j', 'k', 'l', 'q'],
                                   timeStamped=experiment_clock)
        if selection is None:
            response_array = [0, 'No answer']
            return response_array
        elif selection[0][0] == 's':
            selected_artist = artist_array[0]
        elif selection[0][0] == 'd':
            selected_artist = artist_array[1]
        elif selection[0][0] == 'f':
            selected_artist = artist_array[2]
        elif selection[0][0] == 'j':
            selected_artist = artist_array[3]
        elif selection[0][0] == 'k':
            selected_artist = artist_array[4]
        elif selection[0][0] == 'l':
            selected_artist = artist_array[5]
        elif selection[0][0] == 'q':
            window.close()
            core.quit()

        response_array = [selection[0][1], selected_artist]
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


def write_trial(trial_row, accuracy, response_time, response, date, time):
    """
    Writes the response, response time, and accuracy to the results file.
    Inputs: trial_row = The information for that trial taken from the procedural file.
            accuracy = The accuracy of the response given by the subject.
            response_time = The reaction time of the response by the subject.
            response = The response given by the subject.
    Returns: None
    """
    results_row = trial_row
    results_row.extend((accuracy, response_time, response, date, time))
    if CONDITION == 0:
        with open(SUBJECT_ID + '_BF_FullExpResults.csv', 'ab') as experiment_csv:
            procedure_file_writer = csv.writer(experiment_csv, delimiter=',')
            procedure_file_writer.writerow(results_row)

    else:
        with open(SUBJECT_ID + '_IF_FullExpResults.csv', 'ab') as experiment_csv:
            procedure_file_writer = csv.writer(experiment_csv, delimiter=',')
            procedure_file_writer.writerow(results_row)


def show_feedback(window, correct_artist, painting_path, context_path):
    """
    Displays feedback for the current trial.
    Inputs: window = The window object being used for the experiment.
            correct_artist = The name of the correct artist for the trial.
            painting_path = The path to the painting image to draw.
    Returns: None
    """
    response_text = visual.TextStim(window, pos=[0.0, BUTTON_Y_POSITIONS[0]], text="The correct artist is: \n" + correct_artist, color='black', height=TEXT_HEIGHT)
    response_text.draw()

    draw_study_images(window, painting_path, context_path)

    window.flip()
    core.wait(2.5)


def show_response(window, artist_array, selected_artist, button_text_array):
    """
    Displays the selection made by the subject by creating a red box around the selected artist. Does not work if
        INPUT_MODE is set to mouse.
    Inputs: window = The window object being used for the experiment.
            artist_array = The array of artists that was used for creating the button text for the trial.
            selected_artist = The artist that was selected by the subject.
            button_text_array = An array containing the text objects to be placed on top of the buttons.
    Returns: None
    """

    index_loc = artist_array.index(selected_artist)

    box_array = []

    for i in range(0, len(button_text_array)):
        if i == index_loc:
            box_array.append(visual.Rect(window, width=BUTTON_SIZE[0], height=BUTTON_SIZE[1], lineWidth=BUTTON_LINE_WIDTH * 2, lineColor='red', pos=[BUTTON_X_POSITIONS[index_loc % 6], BUTTON_Y_POSITIONS[index_loc // 6]]))
        else:
            box_array.append(visual.Rect(window, width=BUTTON_SIZE[0], height=BUTTON_SIZE[1], lineWidth=BUTTON_LINE_WIDTH, lineColor='black', pos=[BUTTON_X_POSITIONS[i % 6], BUTTON_Y_POSITIONS[i // 6]]))

    for i in range(0, len(button_text_array)):
        box_array[i].draw()
        button_text_array[i].draw()

    window.flip()
    core.wait(0.5)


def show_rec_test_response(window, context_images, response):
    """
    Displays the selection made by the subject by creating a red box around the selected context image. Does not work
        if INPUT_MODE is set to mouse.
    Inputs: window = The window object being used for the experiment.
            context_images = A list containing the paths of all the context images to draw.
            response = The context image that was selected by the subject.
    Returns: None.
    """

    for i in range(0, len(context_images)):
        if response == context_images[i]:
            response_box = visual.Rect(window, width=REC_CONTEXT_SIZE, height=REC_CONTEXT_SIZE, lineWidth=BUTTON_LINE_WIDTH * 2, lineColor='red', pos=[REC_X_POSITIONS[i % 6], REC_Y_POSITIONS[i // 6]])

    response_box.draw()

    window.flip()
    core.wait(0.5)


def show_buffer_screen(window):
    """
    Clears the screen and shows a white screen for one second.
    Inputs: window = The window object being used for the experiment.
    Returns: None.
    """

    window.flip(clearBuffer=True)
    core.wait(1.0)


def instructions_trial(window, mouse, current_trial):
    """
    Runs an instructions trial of the experiment.
    Inputs: window: The window object being used for the experiment.
            mouse: The mouse object being used for the experiment.
            current_trial: The row from the procedural file containing the information for this trial.
            instructions_index: The index to read in the instructions proc file.
    Returns: None.
    """

    draw_instructions(window, mouse, current_trial[9])
    timestamp = datetime.datetime.now()
    write_trial(current_trial, "NA", "NA", "NA", timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
    show_buffer_screen(window)


def study_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the study phase.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The Clock being used for the experiment.
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
    timestamp = datetime.datetime.now()
    response = get_response(window, mouse, buttons, random_artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])

    if INPUT_MODE != 0:
        if response[1] != 'No answer':
            draw_study_images(window, current_trial[2], current_trial[5])
            show_response(window, random_artists, response[1], random_artist_button_text)

    show_feedback(window, current_trial[3], current_trial[2], current_trial[5])
    write_trial(current_trial, accuracy, reaction_time, response[1], timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
    show_buffer_screen(window)


def gen_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the generalization test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The Clock being used for the experiment.
            artists = The list of artists being used for the experiment.
            buttons = The buttons being used for the trial.
    Returns: None.
    """

    artist_button_text = create_artist_button_text(window, artists)
    draw_gen_test_image(window, current_trial[2])
    draw_buttons(buttons, artist_button_text)
    start_time = start_trial(window, experiment_clock)
    timestamp = datetime.datetime.now()
    response = get_response(window, mouse, buttons, artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])

    if INPUT_MODE != 0:
        if response[1] != 'No answer':
            draw_gen_test_image(window, current_trial[2])
            show_response(window, artists, response[1], artist_button_text)

    write_trial(current_trial, accuracy, reaction_time, response[1], timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
    show_buffer_screen(window)


def rec_test_trial(window, mouse, current_trial, experiment_clock, context_list):
    """
    Runs a trial of the detailed recognition test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The Clock being used for the experiment.
            context_list =
    Returns: None.
    """

    context_images = get_context_images(current_trial[2], current_trial[3], current_trial[7], context_list)
    image_buttons = draw_rec_test_image(window, current_trial[2], context_images)
    start_time = start_trial(window, experiment_clock)
    timestamp = datetime.datetime.now()
    response = get_response(window, mouse, image_buttons, context_images, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[5])

    if INPUT_MODE != 0:
        if response[1] != 'No answer':
            draw_rec_test_image(window, current_trial[2], context_images)
            show_rec_test_response(window, context_images, response[1])

    write_trial(current_trial, accuracy, reaction_time, response[1], timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
    show_buffer_screen(window)


def genrec_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons):
    """
    Runs a trial of the general recognition test.
    Inputs: window = The window object being used for the experiment.
            mouse = The mouse object being used for the experiment.
            current_trial = The row from the procedural file containing the information for this trial.
            experiment_clock = The Clock being used for the experiment.
            artists = The list of artists being used for the experiment.
            buttons = The buttons being used for the trial.
    Returns: None.
    """

    artist_button_text = create_artist_button_text(window, artists)
    draw_genrec_test_image(window, current_trial[5])
    draw_buttons(buttons, artist_button_text)
    start_time = start_trial(window, experiment_clock)
    timestamp = datetime.datetime.now()
    response = get_response(window, mouse, buttons, artists, 10.0, experiment_clock)
    reaction_time = get_reaction_time(response[0], start_time)
    accuracy = get_accuracy(response[1], current_trial[3])

    if INPUT_MODE != 0:
        if response[1] != 'No answer':
            draw_genrec_test_image(window, current_trial[5])
            show_response(window, artists, response[1], artist_button_text)

    write_trial(current_trial, accuracy, reaction_time, response[1], timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
    show_buffer_screen(window)


def main():
    """
    Main function, runs the painting experiment based on the parameters defined in params.py.
    """

    # Initialize monitor and window objects.
    experiment_monitor = monitors.Monitor('expMonitor', width=SCREENWIDTH)
    experiment_monitor.setSizePix((EXPHRES, EXPVRES))
    experiment_monitor.saveMon()
    window = visual.Window([HRES, VRES], allowGUI=True, monitor=experiment_monitor, units='cm', color='white', fullscr=True, screen=0)

    # Initialize mouse object.
    mouse = event.Mouse(visible=True, newPos=None, win=window)

    if INPUT_MODE != 0:
        window.mouseVisible = False

    # Read the procedural csv
    procedural_file_list = read_procedural_csv()

    # Create the results file. Returns 0 if the results file already exists (check for interrupted study)
    new_session = create_results_file()

    if new_session != 1:
        status = get_results_status()
        current_status = status[0]
    else:
        current_status = 0

    # Start the experiment's clock.
    experiment_clock = start_experiment_clock()

    # Get the artists being used for the experiment.
    artists = get_artists(procedural_file_list)

    # Create buttons for the experiment.
    buttons = create_buttons(window, len(artists))

    # Get the context list for the experiment.
    context_list = get_context_list(procedural_file_list)

    # Check for each type of trial and run it
    for current_trial in procedural_file_list[current_status:]:

        if current_trial[1] == 'instruct':
            instructions_trial(window, mouse, current_trial)

        elif current_trial[1] == 'Study':
            study_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[1] == 'GenTest':
            gen_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[1] == 'RecTest':
            rec_test_trial(window, mouse, current_trial, experiment_clock, context_list)

        elif current_trial[1] == 'GenRecTest':
            genrec_test_trial(window, mouse, current_trial, experiment_clock, artists, buttons)

        elif current_trial[0] == 'Session1':
            timestamp = datetime.datetime.now()
            write_trial(current_trial, "NA", "NA", "NA", timestamp.date(), timestamp.time().strftime('%H:%M:%S'))

        elif current_trial[0] == 'Session2' or current_trial[0] == 'Session1.2' or current_trial[0] == 'Session3':
            timestamp = datetime.datetime.now()
            write_trial(current_trial, "NA", "NA", "NA", timestamp.date(), timestamp.time().strftime('%H:%M:%S'))
            break

        elif current_trial[1] == 'NA':
            write_trial(current_trial, "NA", "NA", "NA", "NA", "NA")


if __name__ == '__main__':
    main()
