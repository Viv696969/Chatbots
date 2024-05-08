import os
msg=input("Enter message= ")
os.system("git add .")
command="git commit -m"+f'"{msg}"'
os.system(command)
os.system("git push")