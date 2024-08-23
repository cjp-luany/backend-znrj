import sys
import os
current_file_path = __file__  
current_dir = os.path.dirname(current_file_path)  
parent_dir = os.path.dirname(current_dir)  
sys.path.append(parent_dir)  
import main_note_ai
main_note_ai.latitude, main_note_ai.longitude