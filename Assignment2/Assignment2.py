def fetch_patient_info(info):                   # a function for finding and returning a certain detail about the current patient
    info_dict = {"accuracy": 1, "disease": 2, "incidence": 3, "treatment_name": 4, "treatment_risk": 5}  # a dictionary that maps the "detail" about a patient to its index in the patient's data list.
    index_of_info = info_dict[info]
    for data_list in patients:
        if data_list[0] == patient_name:
            return data_list[index_of_info]


def create_patient():                               # a function for storing patient data to the database and returning an appropriate message.
    info = line[line.index(" ")+1:].split(", ")     # starts from the position of the first whitespace (in order not to get the command) and splits the line by commas to get every detail about a patient.
    patient = info[0]                               # the first element is our patient's name. the global variable patient_name has a comma at the end of it, so we have to declare another variable for patient's name.
    if patient_is_recorded(patient):
        return "Patient {} cannot be recorded due to duplication.".format(patient)
    else:
        patients.append(info)
        return "Patient {} is recorded.".format(patient)


def calculate_probability():                                                                                # a function that returns the probability of the patient having the disease
    incidence, accuracy = fetch_patient_info("incidence"), float(fetch_patient_info("accuracy"))*100
    cases, total_population = int(incidence.split("/")[0]), int(incidence.split("/")[1])
    probability_value = (cases * accuracy) / (cases * accuracy + (total_population-cases) * (100-accuracy))
    return probability_value


def probability():                                      # a function for returning a string denoting the probability of a patient having the disease.
    if patient_is_recorded(patient_name):
        return "Patient {} has a probability of {} of having {}.".format(patient_name, ("{:.2f}".format(calculate_probability()*100)).rstrip("0").rstrip(".") + "%", str.lower(fetch_patient_info("disease")))  # rstrip is used to remove trailing zeros.
    else:
        return "Probability for {} cannot be calculated due to absence.".format(patient_name)


def list_patients():
    table = "Patient\tDiagnosis\tDisease\t\t\tDisease\t\tTreatment\t\tTreatment\nName\tAccuracy\tName\t\t\tIncidence\tName\t\t\tRisk\n-------------------------------------------------------------------------\n"
    # the dictionary below maps the column indexes with their length. 0 being Patient Name column which allows up to 8 characters, 4 being Treatment Name column which allows up to 16 characters etc.
    column_lengths = {0: 8,
                      1: 12,
                      2: 16,
                      3: 12,
                      4: 16,
                      }

    for data_list in patients:            # this loop creates the table.
        for data_index in range(len(data_list)-1):
            column_length = column_lengths[data_index]
            data = "{:.2f}".format(float(data_list[1])*100) + "%" if data_index == 1 else data_list[data_index]     # ternary statement prevents variable "data" from being assigned to the accuracy values of 0.999, 0.975... instead of 99.90%, 99.75%...
            data_length = len(data)
            table += "{}\t".format(data) if data_length % 4 != 0 else data                                      # line 50 to 52 adds appropriate number of tabs.
            data_length = data_length if data_length % 4 == 0 else ((data_length//4)+1) * 4
            table += "\t" * int((column_length - data_length) / 4)
        table += "{}\n".format(str(float(data_list[5])*100).rstrip("0").rstrip(".") + "%")
    return table.rstrip("\n")


def remove_patient():               # this function removes a certain patient's data from the database and returns an appropriate message.
    if patient_is_recorded(patient_name):
        for data_list in patients:
            if data_list[0] == patient_name:
                patients.remove(data_list)
                break
        return "Patient {} is removed.".format(patient_name)
    else:
        return "Patient {} cannot be removed due to absence.".format(patient_name)


def recommend():                    # this function decides on whether the patient should take the treatment and returns a proper message.
    if patient_is_recorded(patient_name):
        message = "NOT to" if float(fetch_patient_info("treatment_risk")) > calculate_probability() else "to"
        return "System suggests {} {} have the treatment.".format(patient_name, message)
    else:
        return "Recommendation for {} cannot be calculated due to absence.".format(patient_name)


def read_file():                                             # this function reads and returns all contents in the doctors_aid_inputs.txt file
    open("doctors_aid_outputs.txt", "w", encoding='utf-8')   # this line is for removing any existing contents in the output file.
    inputfile = open("doctors_aid_inputs.txt", "r", encoding='utf-8')
    contents = inputfile.read()
    inputfile.close()
    return contents


def write_file(content):                                     # writes outputs to doctors_aid_outputs.txt file
    file = open("doctors_aid_outputs.txt", "a", encoding='utf-8')
    file.write(content)
    file.close()


def patient_is_recorded(patient):    # returns True if a patient's data exists in the "patients" list (database) .
    return True if patient in [i[0] for i in patients] else False


patients = []  # this is the multidimensional list that is going to act as a database for patient data.

# this dictionary is used to associate commands in the doctors_aid_inputs.txt file to functions in this program.
function_dict = {"create": create_patient,
                 "probability": probability,
                 "list": list_patients,
                 "remove": remove_patient,
                 "recommendation": recommend, }

lines = read_file()         # stores the contents of doctors_aid_inputs.txt file

for line in lines.split("\n"):           # goes through every line in doctors_aid_inputs file
    line_data = line.split()
    command = line_data[0]
    patient_name = line_data[1] if command != "list" else ""    # "patient_name" global variable stores patient's name and gets used by multiple functions.
    output_line = str(function_dict[command]()) + "\n"  # output_line, calls the related function and stores the returnee.
    write_file(output_line)     # lastly, the output is written to the doctors_aid_outputs file.
