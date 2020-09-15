import os
import sys
import argparse
import logging
import time

class SubtitleShifter():
    def __init__(self):
        self.APPLICATION_ROOT = ""
        self.logger = ""
        self.log_file_path = ""
        self.seconds = None
        self.shift_type = None
        self.input_file = None
        self.output_file = None
        self.initialize_application()
        self.parse_arguments()
    
    # Function to initialize the logger
    def initialize_application(self):
        self.APPLICATION_ROOT = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.normpath(self.APPLICATION_ROOT + '/' + 'log')
        if not (os.path.isdir(log_dir)):
            os.makedirs(log_dir)
        
        self.logger = logging.getLogger('')
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG)

        # Log file created in the local directory.
        self.log_file_path = os.path.normpath(log_dir + '/' + os.path.basename(sys.argv[0]) + '_' + time.strftime("%Y_%m_%d_%H_%M_%S") + '.log')
        
        log_fh = open(self.log_file_path, "w", encoding="utf-8")
        formatter = logging.Formatter("%(levelname)s\t : %(asctime)s : %(module)s : %(lineno)s : %(message)s")
        
        # file_handler = logging.FileHandler(self.log_file_path)
        # file_handler.setFormatter(logging.Formatter("%(levelname)s\t : %(asctime)s : %(module)s : %(lineno)s : %(message)s"))
        # file_handler.setLevel(logging.DEBUG)
        file_handler = logging.StreamHandler(log_fh)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(levelname)s\t : %(message)s"))
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
    # Function to parse the arguments of the script
    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Script to shift time in SRT file')
        parser.add_argument('--file', '-f', required=True, metavar='INPUT_FILE', type=str,
                            help='Input SRT file')
        parser.add_argument('--output', '-o', required=False, metavar='OUTPUT_FILE', type=str,
                            help='Input SRT file')
        parser.add_argument('--seconds', '-s', required=True, metavar='SECONDS', type=int,
                            help='Number of seconds to be shifted')
        parser.add_argument("--type", '-t', required=True, choices=['+', '-'], help="Type of shift", type=str)
        args = parser.parse_args()
        self.main_function(args)
    
    # Function to exit with an error
    def exit_with_an_error(self):
        self.logger.info("The log file is : " + self.log_file_path)
        sys.exit(-1)
        
    def shift(self, value):
        if self.shift_type == '+':
            return value + self.seconds
        else:
            return value - self.seconds
            
    def shift_doublons(self, lower_time, upper_time):
        if lower_time > 60.0:
            upper_time = upper_time + 1
            lower_time = lower_time - 60.0
        elif lower_time < 0.0:
            upper_time = upper_time - 1
            lower_time = lower_time + 60.0
        return [lower_time,upper_time]
    
    def shift_time(self, time):
        hour,minut,second = time.split(":")
        new_hour = int(hour)
        new_minut = int(minut)
        second = float(second.replace(",","."))
        new_second = self.shift(second)
        new_second, new_minut = self.shift_doublons(new_second, new_minut)
        new_minut, new_hour = self.shift_doublons(new_minut, new_hour)
        new_hour = int(new_hour)
        new_minut = int(new_minut)
        new_second_rounded = "%06.3f" % new_second
        new_time = f"{new_hour:02d}:{new_minut:02d}:{new_second_rounded.replace('.', ',')}"
        return new_time
    
    def shift_content(self):
        new_content = []
        with open(self.input_file) as f:
            content = f.readlines()
            for line in content:
                new_line = line.replace("\n", "")
                if " --> " in new_line:
                    begin_time,end_time = new_line.split(" --> ")
                    new_begin_time = self.shift_time(begin_time)
                    new_end_time = self.shift_time(end_time)
                    new_line = f"{new_begin_time} --> {new_end_time}"
                new_content.append(new_line + "\n")
        with open(self.output_file, 'w') as f:
            f.writelines(new_content)
        self.logger.info(f"The file {self.output_file} has been created !")
    
    def main_function(self, args):
        self.input_file = args.file
        if not os.path.exists(self.input_file):
            self.logger.error(f"The file {self.input_file} does not exists, exiting.")
            self.exit_with_an_error()
        if args.output:
            self.output_file = os.path.join(os.path.dirname(self.input_file), args.output)
        else:
            self.output_file = self.input_file.lower().replace(".srt", "_shifted.srt")
        self.shift_type = args.type
        self.seconds = args.seconds
        self.logger.info(f"The file {self.input_file} will be shifted to {self.shift_type}{self.seconds}")
        self.shift_content()
        

if __name__ == "__main__":
    # execute only if run as a script
    SubtitleShifter()