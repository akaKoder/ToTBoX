import json
import datetime
from datetime import datetime
import pyttsx3
import random
import openai
from term_image.image import from_file
import webbrowser
import os
import re



note_history = []


# Set the API key and model to use
openai.api_key = "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"
model_engine = "text-davinci-003"


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


voices = engine.getProperty('voices')


class Note:
    def __init__(self, content=None, id=None, out_links=None, in_links=None, day=None, month=None, year=None, hour=None,
                 minute=None):
        self.id = id or self.generate_id()
        self.content = content
        self.out_links = out_links or []
        self.in_links = in_links or []
        self.day = day
        self.month = month
        self.year = year
        self.hour = hour
        self.minute = minute

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "out_links": self.out_links,
            "in_links": self.in_links,
            "day": self.day or None,
            "month": self.month or None,
            "year": self.year or None,
            "hour": self.hour or None,
            "minute": self.minute or None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(id=data.get("id"),
                   content=data.get("content"),
                   out_links=data.get("out_links"),
                   in_links=data.get("in_links"),
                   day=data.get("day"),
                   month=data.get("month"),
                   year=data.get("year"),
                   hour=data.get("hour"),
                   minute=data.get("minute"))

    def generate_id(self):
        while True:
            id = random.randint(1, 1000000)
            if id not in Note.all_ids():
                return id

    def saythiscontent(self):
        engine.setProperty('rate', 200)
        whattosay = self.content
        engine.say(whattosay)
        engine.runAndWait()

    def saythiscontentquickly(self):
        engine.setProperty('rate', 300)
        whattosay = self.content
        engine.say(whattosay)
        engine.runAndWait()

    def saythiscontentslowly(self):
        engine.setProperty('rate', 100)
        whattosay = self.content
        engine.say(whattosay)
        engine.runAndWait()

    def is_image(self):
        IMAGES = next((n for n in notes if n.content == "IMAGES"), None)
        return IMAGES.id in self.in_links

    def is_link(self):
        # check if it's a valid URL
        if re.match("^(?:http|ftp)s?://", self.content):
            return True
        # check if it's a valid file path
        if os.path.exists(self.content):
            return True
        return False

    def is_deadline(self, notes):
        """
        Returns true if the note is a deadline, false otherwise.
        """
        DEADLINES = next((n for n in notes if n.content == "DEADLINES"), None)
        return note.id in DEADLINES.out_links

    def add_out_link(self, new_note):
        self.out_links.append(new_note.id)

    def add_in_link(self, new_note):
        self.in_links.append(new_note.id)

    def remove_in_link_from_note_and_opposite(self, index, notes):
        if not self.in_links or index is None:
            return
        in_link_id = self.in_links[index]
        self.in_links.remove(in_link_id)
        in_link_note = next(note for note in notes if note.id == in_link_id)
        in_link_note.out_links.remove(self.id)

    def remove_out_link_from_note_and_opposite(self, index, notes):
        out_link_id = self.out_links[index]
        self.out_links.remove(out_link_id)
        out_link_note = next(note for note in notes if note.id == out_link_id)
        out_link_note.in_links.remove(self.id)

    def update_content(self, new_content):
        self.content = new_content

    def change_content(self):
        new_content = input("Enter new content: ")
        self.update_content(new_content)

    def print_out_links(self, notes):
        if self.out_links:
            for i, id in enumerate(self.out_links):
                out_link_note = next(note for note in notes if note.id == id)
                if out_link_note.is_image():
                    image = from_file(out_link_note.content)
                    image.draw()
                else:
                    print(f"{i + 1}: {out_link_note.content}")
        else:
            print(".")

    def print_in_links(self, notes):
        if self.in_links:
            for i, id in enumerate(self.in_links):
                in_link_note = next(note for note in notes if note.id == id)
                print(f"{i + 1}: {in_link_note.content}")
        else:
            print("This note has no inbound links.")

    def open_content_link(note):
        content = note.content
        if content.startswith("http"):
            webbrowser.open(content)
        elif os.path.exists(content):
            os.startfile(content)
        else:
            print("Invalid link or file path")

    def open_all_outlinks(self):
        for out_link_id in self.out_links:
            out_link_note = find_note_by_id(out_link_id, notes)
            if out_link_note.is_link():
                try:
                    if re.match("^(?:http|ftp)s?://", out_link_note.content):
                        webbrowser.open(out_link_note.content)
                    elif os.path.exists(out_link_note.content):
                        os.startfile(out_link_note.content)
                except Exception as e:
                    print(f"Error opening link: {out_link_note.content}")
                    print(e)


    def reorder_out_links(self, notes):
        if not self.out_links:
            print("There's nothing inside this box to reorder...")
            return
        while True:
            print("Enter the number of the box you want to move, or Q to quit:")
            for i, link_id in enumerate(self.out_links):
                link_note = next(note for note in notes if note.id == link_id)
                print(f"{i}: {link_note.content}")
            selection = input()
            if selection.isdigit():
                index = int(selection)
                if 0 <= index < len(self.out_links):
                    selected_link_id = self.out_links[index]
                    print("Enter the new position for the box (0-based index):")
                    new_position = input()
                    if new_position.isdigit() and 0 <= int(new_position) <= len(self.out_links):
                        self.out_links.remove(selected_link_id)
                        self.out_links.insert(int(new_position), selected_link_id)
                        save_notes(notes)
                    else:
                        print("Out of range...")
                else:
                    print("Are you an invalid? Because the index is.")
            elif selection == "Q":
                save_notes(notes)
                break
            else:
                print("Invalid selection")

    @classmethod
    def all_ids(cls):
        try:
            with open('notes.json', 'r') as f:
                notes = json.load(f, object_hook=cls.from_dict)
        except FileNotFoundError:
            notes = []

        ids = [note.id for note in notes]
        return ids

    def due(self):
        now = datetime.now()
        alarm_time = datetime(year=int(self.year), month=int(self.month), day=int(self.day), hour=int(self.hour),
                              minute=int(self.minute))
        if alarm_time < now:
            return True
        return False


global notes
notes = []


# Load notes from JSON file, or create an empty list if the file doesn't exist
try:
    with open('notes.json', 'r') as f:
        decoder = json.JSONDecoder(object_hook=Note.from_dict)
        notes = decoder.decode(f.read())
except FileNotFoundError:
    notes = []



# Set the initial open_note
global open_note


if notes:
    open_note = notes[0]
else:
    open_note = Note("HOMEBOX")
    notes.append(open_note)


DEADLINES = None
for note in notes:
    if note.content == "DEADLINES":
        DEADLINES = note
        break
if not DEADLINES:
    DEADLINES = Note("DEADLINES")
    notes.append(DEADLINES)


DAILY_REPEATING_TASKS = None
for note in notes:
    if note.content == "DAILY REPEATING TASKS":
        DAILY_REPEATING_TASKS = note
        break
if not DAILY_REPEATING_TASKS:
    DAILY_REPEATING_TASKS = Note("DAILY REPEATING TASKS")
    notes.append(DAILY_REPEATING_TASKS)


TODAY = None
for note in notes:
    if note.content == "TODAY":
        TODAY = note
        break
if not TODAY:
    TODAY = Note("TODAY")
    notes.append(TODAY)

NONREPEATINGTASKS = None
for note in notes:
    if note.content == "NONREPEATINGTASKS":
        NONREPEATINGTASKS = note
        break
if not NONREPEATINGTASKS:
    NONREPEATINGTASKS = Note("NONREPEATINGTASKS")
    notes.append(NONREPEATINGTASKS)


NOTIFICATIONS = None
for note in notes:
    if note.content == "NOTIFICATIONS":
        NOTIFICATIONS = note
        break
if not NOTIFICATIONS:
    NOTIFICATIONS = Note("NOTIFICATIONS")
    notes.append(NOTIFICATIONS)

IMAGES = None
for note in notes:
    if note.content == "IMAGES":
        IMAGES = note
        break
if not IMAGES:
    IMAGES = Note("IMAGES")
    notes.append(IMAGES)


ENTRIES = None
for note in notes:
    if note.content == "ENTRIES":
        ENTRIES = note
        break
if not ENTRIES:
    ENTRIES = Note("ENTRIES")
    notes.append(ENTRIES)


global folder_path
folder_path = "C:\\TOTBOXIMAGE"



def date_entry(open_note, notes):
    # Get the current date and time
    now = datetime.now()
    # Assign the current date and time to the note's attributes
    open_note.year = now.year
    open_note.month = now.month
    open_note.day = now.day
    open_note.hour = now.hour
    open_note.minute = now.minute
    # Find the "ENTRIES" note in the notes list
    entries_note = next(note for note in notes if note.content == "ENTRIES")

    for inlink_id in open_note.in_links:
        inlink_note = find_note_by_id(inlink_id, notes)
        remove_link_between_notes(inlink_note, open_note)

    # Link the current note to the "ENTRIES" note
    link_in_and_out(entries_note, open_note)

    save_notes(notes)

def create_image_notes_from_folder(notes):
    global folder_path
    # Get a list of all files in the specified folder
    files = os.listdir(folder_path)
    image_files = []
    # Filter the list to only include image files
    for file in files:
        if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
            image_files.append(file)

    # Get the fixed "image" note
    IMAGES = next((n for n in notes if n.content == "IMAGES"), None)


    # Iterate through the image files and create a new note for each
    for image_file in image_files:
        # check if the image has been converted to note or not
        image_note_exists = any(n for n in notes if n.content == image_file)
        if not image_note_exists:
            # Create a new note with the local file path of the image as its content and the "image" note in its inlinks
            new_note = Note(content=os.path.join(folder_path, image_file))
            # Add the new note to the list of notes
            notes.append(new_note)
            link_in_and_out(IMAGES, new_note)



def move_allnotes(open_note, notes):
    notes_to_move = []
    for note_id in open_note.out_links:
        notes_to_move.append(find_note_by_id(note_id, notes))
    print("All of this will be moved into the note you search for:")
    for i, note in enumerate(notes_to_move):
        print(f"{i+1}: {note.content}")
    target_note = search_note(notes)
    for note in notes_to_move:
        remove_link_between_notes(open_note, note)
        link_in_and_out(target_note, note)
    print(f"Notes with content: {[note.content for note in notes_to_move]}  has been moved and linked to {target_note.content}")


def move_note(open_note, notes):
    if open_note.out_links:
        print("Current outlinks:")
        for i, note_id in enumerate(open_note.out_links):
            note = find_note_by_id(note_id, notes)
            print(f"{i}: {note.content}")
        selection = int(input("Enter the number of the note you want to move: "))
        note_to_move = find_note_by_id(open_note.out_links[selection], notes)
        remove_link_between_notes(open_note, note_to_move)
        note_to_link = search_note(notes)
        link_in_and_out(note_to_link, note_to_move)
        print(f"Note with content '{note_to_move.content}' has been moved and linked to '{note_to_link.content}'")
    else:
        print("No outlinks to move...")


def go_back_note(notes):
    if note_history:
        last_note_id = note_history.pop()
        open_note = find_note_by_id(last_note_id, notes)
        return open_note
    else:
        print("No previous note found")


def check_notifications():
    today_note = find_note_by_content("TODAY", notes)
    for note in NOTIFICATIONS.out_links:
        reminder = find_note_by_id(note, notes)
        if reminder.due and (reminder.id not in today_note.out_links):
            link_in_and_out(today_note, reminder)
            reminder.day=None
            reminder.month=None
            reminder.year=None
            reminder.hour=None
            reminder.minute=None


def create_notify(open_note, notes):
    # ask user for details of the reminder
    day = input("Enter the day (1-31):") or datetime.now().day
    month = input("Enter the month (1-12):") or datetime.now().month
    year = input("Enter the year (YYYY):") or datetime.now().year
    hour = input("Enter the hour (0-23):") or datetime.now().hour
    minute = input("Enter the minute (0-59):") or datetime.now().minute

    # Set attributes on the open_note object
    open_note.day = day
    open_note.month = month
    open_note.year = year
    open_note.hour = hour
    open_note.minute = minute

    link_in_and_out(NOTIFICATIONS, open_note)
    print("Notification created")


def populate_today_note():
    global notes
    today_note = None
    daily_repeating_tasks_note = None
    non_repeating_note = None

    # Find the "TODAY" note, "DAILY REPEATING TASKS" note and "NONREPEATINGTASKS" note
    for note in notes:
        if note.content == "TODAY":
            today_note = note
        elif note.content == "DAILY REPEATING TASKS":
            daily_repeating_tasks_note = note
        elif note.content == "NONREPEATINGTASKS":
            non_repeating_note = note

    # populate it with the outlinks from the "DAILY REPEATING TASKS" note
    if today_note and daily_repeating_tasks_note:
        for out_link in daily_repeating_tasks_note.out_links:
            note_to_copy = find_note_by_id(out_link, notes)
            if note_to_copy:
                link_in_and_out(today_note, note_to_copy)

    # populate it with the outlinks from the "NONREPEATINGTASKS" note
    if today_note and non_repeating_note:
        for out_link in non_repeating_note.out_links:
            note_to_copy = find_note_by_id(out_link, notes)
            if note_to_copy:
                link_in_and_out(today_note, note_to_copy)


def clear_today_note():
    today_note = find_note_by_content("TODAY", notes)
    out_links_copy = today_note.out_links.copy()
    for out_link in out_links_copy:
        note_to_unlink = find_note_by_id(out_link, notes)
        note_is_from_daily_repeating = note_to_unlink.id in find_note_by_content("DAILY REPEATING TASKS", notes).out_links
        if not note_is_from_daily_repeating:
            if note_to_unlink.id not in find_note_by_content("NONREPEATINGTASKS", notes).out_links:
                link_in_and_out(find_note_by_content("NONREPEATINGTASKS", notes), note_to_unlink)
            remove_link_between_notes(today_note, note_to_unlink)
        else:
            remove_link_between_notes(today_note, note_to_unlink)


def generate_prompt_for_entire_note(note, notes):
    out_links = [find_note_by_id(link, notes).content for link in note.out_links]
    prompt = f"Something smart and concise about {note.content} and : " + ", ".join(out_links)
    print(prompt)
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1
    )
    if response.choices[0].text is None or response.choices[0].text.strip() == "":
        print("Try again later")
    else:
        new_note_content = response.choices[0].text.strip().replace('\n', ' ')
        new_note = Note(new_note_content)
        notes.append(new_note)
        link_in_and_out(note, new_note)

def talktoai():
    user_prompt = input("What are you asking the AI? ")
    response = openai.Completion.create(
        engine=model_engine,
        prompt=user_prompt,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1
    )
    print(response.choices[0].text)


def calculate_deadline_delta(deadline_note):
    now = datetime.now()
    deadline = datetime(int(deadline_note.year), int(deadline_note.month), int(deadline_note.day), int(deadline_note.hour), int(deadline_note.minute))
    delta = deadline - now
    return delta


def set_deadline(open_note, notes):
    # ask user for details of the deadline
    print("Enter the day (1-31):")
    day = input()
    if not day:
        day = datetime.now().day
    else:
        day = int(day)
    print("Enter the month (1-12):")
    month = input()
    if not month:
        month = datetime.now().month
    else:
        month = int(month)
    print("Enter the year (YYYY):")
    year = input()
    if not year:
        year = datetime.now().year
    else:
        year = int(year)
    print("Enter the hour (0-23):")
    hour = input()
    if not hour:
        hour = datetime.now().hour
    else:
        hour = int(hour)
    print("Enter the minute (0-59):")
    minute = input()
    if not minute:
        minute = datetime.now().minute
    else:
        minute = int(minute)

    DEADLINES = next((note for note in notes if note.content == "DEADLINES"), None)
    link_in_and_out(DEADLINES, open_note)

    open_note.day = day
    open_note.month = month
    open_note.year = year
    open_note.hour = hour
    open_note.minute = minute


def link_in_and_out(noteA, noteB):
    noteA.add_out_link(noteB)
    noteB.add_in_link(noteA)


def remove_link_between_notes(noteA, noteB):
    if noteB.id in noteA.out_links:
        noteA.out_links.remove(noteB.id)
    if noteA.id in noteB.in_links:
        noteB.in_links.remove(noteA.id)


def go_to_out_link(open_note, notes, id):
    note_history.append(open_note.id)
    for out_link_id in open_note.out_links:
        if id == out_link_id:
            out_link_note = next(note for note in notes if note.id == id)
            return out_link_note
    print("Error: Invalid outbound link ID.")
    return open_note


def go_to_in_link(open_note, notes, id):
    note_history.append(open_note.id)
    in_link_note = find_note_by_id(id, notes)
    if in_link_note is not None:
        return in_link_note
    else:
        print("Error: Invalid inbound link ID.")
        return open_note


def find_note_by_id(note_id, notes):
    try:
        return next(note for note in notes if note.id == note_id)
    except StopIteration:
        return None

def go_up_after_delete(open_note, notes):
    if open_note.in_links:
        if len(open_note.in_links) < 2:
            # There is only one inbound link, so navigate to it
            in_link_id = open_note.in_links[0]
            open_note = go_to_in_link(open_note, notes, in_link_id)
        else:
            # There are multiple inbound links, so print them and ask the user which one to navigate to
            print("Multiple inbound links:")
            for i, in_link_id in enumerate(open_note.in_links):
                in_link_note = find_note_by_id(in_link_id, notes)
                print(f"{i + 1}: {in_link_note.content}")
            in_link_index = ((int(input("Enter the index of the inbound link to navigate to: "))) - 1)
            in_link_id = open_note.in_links[in_link_index]
            open_note = go_to_in_link(open_note, notes, in_link_id)
    else:
        open_note = notes[0]
    return open_note

def go_up(open_note, notes):
    if open_note.in_links:
        if len(open_note.in_links) < 2:
            # There is only one inbound link, so navigate to it
            in_link_id = open_note.in_links[0]
            open_note = go_to_in_link(open_note, notes, in_link_id)
        else:
            # There are multiple inbound links, so print them and ask the user which one to navigate to
            print("Multiple inbound links:")
            for i, in_link_id in enumerate(open_note.in_links):
                in_link_note = find_note_by_id(in_link_id, notes)
                print(f"{i + 1}: {in_link_note.content}")
            in_link_index = ((int(input("Enter the index of the inbound link to navigate to: ")))-1)
            in_link_id = open_note.in_links[in_link_index]
            open_note = go_to_in_link(open_note, notes, in_link_id)
    else:
        print("Error: This note has no inbound links.")
    return open_note


def search_note(notes):
    query = input("What are you looking for? ").lower()
    terms = query.split()
    matching_notes = []
    for note in notes:
        content = note.content.lower()
        if all(term in content for term in terms):
            matching_notes.append(note)
    if matching_notes:
        for i, note in enumerate(matching_notes):
            print(f"{i}: {note.content}")
        selection = input("Enter the number of the box you're looking for': ")
        return matching_notes[int(selection)]
    else:
        print("Nothing like that found...")


def save_notes(notes):
    # Convert the notes to a list of dictionaries
    data = [note.to_dict() for note in notes]
    # Save the list of dictionaries to the file
    with open('notes.json', 'w') as f:
        json.dump(data, f)


def load_notes():
    # Load the list of dictionaries from the file
    with open('notes.json', 'r') as f:
        data = json.load(f)
    # Convert the dictionaries back into Note objects
    notes = [Note.from_dict(note_data) for note_data in data]
    return notes


def find_note_by_content(content, notes):
    for note in notes:
        if note.content == content:
            return note
    return None


def superdelete(open_note, notes):
    out_links_copy = open_note.out_links.copy()
    for out_link_id in out_links_copy:
        try:
            out_link_note = find_note_by_id(out_link_id, notes)
            for note in notes:
                if open_note.id in note.in_links:
                    note.in_links.remove(open_note.id)
                if open_note.id in note.out_links:
                    note.out_links.remove(open_note.id)
            notes.remove(out_link_note)
        except:
            print("An error occurred while trying to delete a note.")
    try:
        for note in notes:
            if open_note.id in note.in_links:
                note.in_links.remove(open_note.id)
            if open_note.id in note.out_links:
                note.out_links.remove(open_note.id)
        notes.remove(open_note)
    except:
        print("An error occurred while trying to delete the current open note.")
    save_notes(notes)




def delete_current_note(open_note, notes):
    global last_note
    last_note = open_note

    # Go through all notes in the notes list
    for note in notes:
        try:
            # Remove the current note's ID from the in_links and out_links of each note
            if open_note.id in note.in_links:
                note.in_links.remove(open_note.id)
            if open_note.id in note.out_links:
                note.out_links.remove(open_note.id)
        except Exception as e:
            print(f"Error occurred while trying to remove link from note {note.content}: {e}")
    try:
        # Remove the current note from the list of notes
        notes.remove(open_note)
        save_notes(notes)
    except Exception as e:
        print(f"Error occurred while trying to remove note {open_note.content}: {e}")




def link(open_note, notes):
    # Prompt the user to enter the content of the note they want to link to
    query = input("Enter the content of the note to link to: ").lower()
    # Search the notes for a matching note
    matching_notes = [note for note in notes if query in note.content.lower()]
    if matching_notes:
        if len(matching_notes) == 1:
            # There is only one matching note, so use it
            linked_note = matching_notes[0]
        else:
            # There are multiple matching notes, so print them and ask the user which one to link to
            for i, note in enumerate(matching_notes):
                print(f"{i + 1}: {note.content}")
            selection = int(input("Enter the number of the note to link to: ")) - 1
            linked_note = matching_notes[selection]
        # Confirm with the user that they want to link to the selected note
        confirm = input(f"Link to note '{linked_note.content}'? [Y/n] ")
        if confirm.lower() == "y":
            # Check if the linked note is already an out link of the open note
            if linked_note.id not in open_note.out_links:
                # Add the linked note as an out link of the open note
                open_note.add_out_link(linked_note)
            # Add the open note as an in link of the linked note
            linked_note.add_in_link(open_note)
            print("Link created.")
        else:
            print("Link cancelled.")
    else:
        print("Note not found.")


def remove_outlinks_and_corresponding_inlinks(note, notes):
    out_links = note.out_links
    for i in range(len(out_links)):
        linked_note = find_note_by_id(out_links[i], notes)
        print(f"{i+1}. {linked_note.content}")
    user_input = input("Enter the number of the outlink to remove and its corresponding inlink: ")
    try:
        user_input = int(user_input)
        if user_input < 1 or user_input > len(out_links):
            raise ValueError
    except ValueError:
        print("Invalid input, please enter a valid number.")
    else:
        linked_note = find_note_by_id(out_links[user_input-1], notes)
        remove_link_between_notes(note, linked_note)
        remove_link_between_notes(linked_note, note)


def move_inside(open_note, notes):
    while True:
        outlinks_copy = open_note.out_links.copy()
        print("Which note do you want to move? (Enter the corresponding number)")
        for i, outlink_id in enumerate(outlinks_copy):
            print(f"{i+1}. {find_note_by_id(outlink_id, notes).content}")
        user_input = input("Enter the number of the note you want to move or 'stop' to exit: ")
        if user_input.lower() == "stop":
            break
        elif user_input.isdigit():
            note_to_move_index = int(user_input) - 1
            if note_to_move_index < 0 or note_to_move_index >= len(outlinks_copy):
                print("Invalid input. Please enter a number between 1 and", len(outlinks_copy))
            else:
                note_to_move_id = outlinks_copy[note_to_move_index]
                note_to_move = find_note_by_id(note_to_move_id, notes)
                outlinks_copy.pop(note_to_move_index)
                print("Where do you want to move the selected note? (Enter the corresponding number)")
                for i, outlink_id in enumerate(outlinks_copy):
                    print(f"{i+1}. {find_note_by_id(outlink_id, notes).content}")
                user_input = input("Enter the number of the destination note or 'stop' to exit: ")
                if user_input.lower() == "stop":
                    break
                elif user_input.isdigit():
                    destination_index = int(user_input) - 1
                    if destination_index < 0 or destination_index >= len(outlinks_copy):
                        print("Invalid input. Please enter a number between 1 and", len(outlinks_copy))
                    else:
                        destination_id = outlinks_copy[destination_index]
                        destination = find_note_by_id(destination_id, notes)
                        remove_link_between_notes(open_note, note_to_move)
                        link_in_and_out(destination, note_to_move)
                else:
                    print("Invalid input. Please enter a number or 'stop'.")
        else:
            print("Invalid input. Please enter a number or 'stop'.")






def remove_inlinks_and_corresponding_outlinks(note, notes):
    in_links = note.in_links
    print("Select the number of the inlink you want to remove and its corresponding outlink:")
    for i in range(len(in_links)):
        print(f"{i+1}. {find_note_by_id(in_links[i], notes).content}")
    user_input = input()
    try:
        selection = int(user_input)
        if selection > 0 and selection <= len(in_links):
            inlink_to_remove = find_note_by_id(in_links[selection-1], notes)
            remove_link_between_notes(inlink_to_remove, note)
            remove_link_between_notes(find_note_by_id(inlink_to_remove.out_links[0], notes), inlink_to_remove)
        else:
            print("Invalid input, please enter a number within the given range.")
    except ValueError:
        print("Invalid input, please enter a number within the given range.")



def find_orphan_notes(notes):
    orphan_notes = []
    for note in notes:
        if not note.in_links and not note.out_links:
            orphan_notes.append(note)
    if orphan_notes:
        for i, note in enumerate(orphan_notes):
            print(f"{i}: {note.content}")
        selection = input("Enter the number of the orphan note you want to navigate to: ")
        return orphan_notes[int(selection)]
    else:
        print("No orphan notes found.")




def main():

    while True:
        os.system("cls")
        global open_note
        global notes

        if open_note == DEADLINES:
            deadlines = []
            for out_link_id in open_note.out_links:
                deadline_note = next(note for note in notes if note.id == out_link_id)
                deadline_time = datetime(deadline_note.year, deadline_note.month, deadline_note.day,
                                         deadline_note.hour, deadline_note.minute)
                delta_time = deadline_time - datetime.now()
                deadlines.append((delta_time, deadline_note))
            deadlines.sort(key=lambda x: x[0])  # sort deadlines by delta_time
            for i, deadline in enumerate(deadlines, 1):
                delta_time, deadline_note = deadline
                print(f"{i}. There is {delta_time} to go until {deadline_note.content}")
            user_input = input("Enter the number of the deadline you want to go to, or 'b' to go back: ")
            if user_input.isdigit():
                selected_index = int(user_input) - 1
                if 0 <= selected_index < len(deadlines):
                    open_note = deadlines[selected_index][1]
                else:
                    print("Invalid input. Please enter a number between 1 and", len(deadlines))
            elif user_input.lower() == "b":
                open_note = go_back_note(notes)
                save_notes(notes)
        else:
            if open_note is None:
                open_note = notes[0]
            if open_note.id == TODAY.id:
                task_count = len(open_note.out_links)
                print(f"YOU HAVE {task_count} THINGS TO DO TODAY")
                open_note.print_out_links(notes)
            elif open_note == ENTRIES:
                for out_link_id in open_note.out_links:
                    entry_note = next(note for note in notes if note.id == out_link_id)
                    print(
                        f"{entry_note.year}-{entry_note.month}-{entry_note.day} {entry_note.hour}:{entry_note.minute}")
            else:
                if open_note.is_image():
                    image = from_file(open_note.content)
                    image.draw()
                    open_note.print_out_links(notes)
                    check_notifications()
                else:
                    print(open_note.content)
                    open_note.print_out_links(notes)
                    check_notifications()


            user_input = input("?")

            if user_input.isdigit():
                if int(user_input) < 1 or int(user_input) > len(open_note.out_links):
                    print("Invalid input. Please enter a number between 0 and " + str(len(open_note.out_links)))
                else:
                    index = open_note.out_links[(int(user_input) - 1)]
                    open_note = go_to_out_link(open_note, notes, index)

            elif user_input.lower() == "aithis":
                generate_prompt_for_entire_note(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "help":
                print('''
                "M" Move one note
                "MA" Move All notes
                "MI" Move In, as in move one note into another
                "C" Change the content of current note
                "L" Link to note
                "O" reOrder the notes
                "S" Search
                "R" Remove a note, unlinking it from the current note
                "RI" Remove inlink note
                "D" Delete
                "DA" Delete All inside this note and then the note itself
                "B" Back
                "U" Go "up" through the inlinks; if there's only one, it'll go to it straight away
                NOTIFY to create notification that will be added to your TODAY when its due
                AITHIS will take the current note and all its kids to the AI and create a new addition with the result
                ASKAI to ask to the AI directly
                NEWDAY and ENDDAY to start and end the day, populating and clearing the TODAY note
                DEADLINE to make a note into a deadline
                IMAGES to repopulate from images-folder to IMAGES note
                JOURNAL to make current note into a journal entry, dating it and removing it from everything but ENTRIES
                SAYTHIS, SAYTHISQUICKLY and SAYTHISSLOWLY each do to the open note's content what they say they do...
                RUN to run the note's URL/filepath
                RUNALL to run every note in the outlinks
                Quit is pretty self-explanatory''')



            elif user_input.lower() == "images":
                create_image_notes_from_folder(notes)

            elif user_input.lower() == "askai":
                talktoai()

            elif user_input.lower() == "journal":
                date_entry(open_note, notes)

            elif user_input.lower() == "orphans":
                open_note = find_orphan_notes(notes)

            elif user_input.lower() == "m":
                move_note(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "ma":
                move_allnotes(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "notify":
                create_notify(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "run":
                open_note.open_content_link()

            elif user_input.lower() == "runall":
                open_note.open_all_outlinks()

            elif user_input.lower() == "c":
                open_note.change_content()
                save_notes(notes)

            elif user_input.lower() == "mi":
                move_inside(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "da":
                superdelete(open_note, notes)
                open_note = go_up_after_delete(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "l":
                link(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "o":
                open_note.reorder_out_links(notes)
                save_notes(notes)

            elif user_input.lower() == "newday":
                populate_today_note()
                save_notes(notes)

            elif user_input.lower() == "endday":
                clear_today_note()
                save_notes(notes)

            elif user_input.lower() == "s":
                open_note = search_note(notes)

            elif user_input.lower() == "r":
                remove_outlinks_and_corresponding_inlinks(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "ri":
                remove_inlinks_and_corresponding_outlinks(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "saythis":
                Note.saythiscontent(open_note)

            elif user_input.lower() == "saythisquickly":
                Note.saythiscontentquickly(open_note)

            elif user_input.lower() == "saythisslowly":
                Note.saythiscontentslowly(open_note)

            elif user_input.lower() == "d":
                delete_current_note(open_note, notes)
                open_note = go_up_after_delete(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "b":
                open_note = go_back_note(notes)

            elif user_input.lower() == "u":
                open_note = go_up(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "deadline":
                set_deadline(open_note, notes)
                save_notes(notes)

            elif user_input.lower() == "q":
                save_notes(notes)
                break

            elif user_input == "":
                print("ENTER ENTERED")
            else:
                new_note = Note(content=user_input)
                new_note.add_in_link(open_note)  # add the current open_note as an in_link to the new note
                open_note.add_out_link(new_note)
                notes.append(new_note)
                save_notes(notes)


if __name__ == "__main__":
    main()
