import os

folder_to_track = "/home/pi/motionvideos"
new_folder = "/home/pi/motionvideos/done"

for filename in os.listdir(folder_to_track):
        if(filename.endswith('.mp4')):
            src = folder_to_track + "/" + filename
            new_destination = new_folder + "/" + filename
            os.rename(src, new_destination)
