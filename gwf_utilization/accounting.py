import re


def seconds(time_string):
    '''Converts time string on the form DD-HH:MM:SS to seconds'''

    r = r'(?:([0-9]+)-)?([0-9]{2}):([0-9]{2}):([0-9]{2})'

    days, hours, minutes, seconds = re.match(r, time_string).groups()

    result = int(seconds)
    result += 60 * int(minutes)
    result += 3600 * int(hours)

    if days:
        result += 86400 * int(days)

    return result


class Accountant:

    def __init__(self, sacct_columns, sacct_data):

        self.jobs = []

        for data in sacct_data:

            data_dict = dict(zip(sacct_columns, data))

            self.jobs.append(Job(job_id=data_dict['JobID'],
                                 job_name=data_dict['JobName'],
                                 n_cpus=data_dict['NCPUS'],
                                 cpu_time=data_dict['CPUTime'],
                                 time_limit=data_dict['Timelimit']))


class Job:

    def __init__(self, job_id, job_name, n_cpus, cpu_time, time_limit):
        pass
