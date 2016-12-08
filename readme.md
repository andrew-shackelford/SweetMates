#Purpose
SweetMates is dedicated to facilitating organization of activities and smoother communication among roommates. With SweetMates, you can create groups to add friends to anonymously chat, schedule tasks, and vote on community issues. This does not fix having bad roommates, but it might help.


#Getting the Website Up and Running
Login to the CS50 IDE, as our website is hosted through the IDE. 

To run our code you must first download the modules needed for this project by running the command in the terminal. In the terminal, make sure you are within the final_project folder by running the command:

`cd ~/workspace/final_project`

Install the necessary requirements by running:

`pip3 install --user -r requirements.txt`

Then start the Flask web server by running:

`flask run`

That command will output a link to the web server; click on it to launch the website.

#Creating a SweetMates Account
The site will load to the login page. If you don’t already have a SweetMates account, navigate to the register page using the “Register” link in the upper right-hand corner. Once on the register page, input a username, your name, password, and then create the account.

Once you have registered, you will be logged in and redirected to the home page.

#Creating a SweetMates Group
Using the navigation sidebar on the left, click on the “New Group” link, and then the “Create a Group” link. Input a desired group name and unique group code (serves as the group username), and create the group. This allows you to create groups for roommates, entryways, or whatever your heart desires.

#Joining a SweetMates Group
Using the navigation sidebar on the left, click on the “New Group” link, and then “Join a Group.” Input the group code and the join code of the group you want to join, and submit your request. You can be in more than one group at a time, but the website will take note of one group that you are currently viewing.


#Adding Others to Your Group
Using the navigation sidebar on the left, click on the “My Group” link, and then “Add Members To Group”. Type in your desired join code, and choose the desired length of time before the code expires. Share this code with others to allow them to join your group. To make a new join code, simply fill out the form again, keeping in mind that this will overwrite any previous join codes and invalidate them.


#Chatting
Using the navigation bar at the top, click “Chats”. This will bring you to an anonymous messaging board for your group. The most recent messages will be at the top, as indicated by the messages’ dates. To look at messages that were sent earlier, click on a different page number below the messaging board. Send an anonymous message by typing your message and clicking send.


#Assigning Chores
To access the chore schedule, click on the “Chores” tab on the upper left-hand side of the head navigation bar. Here, you can see your randomly assigned chores and the date that they should be completed by. Once the chore is finished, click “completed.” All completed chores will appear in the “Chore History” table with the member’s name and the date completed. The best chores to be assigned using SweetMates are repeating chores, as once a chore is completed, it will be randomly assigned to another member of the group. 

If a chore is no longer necessary, you may click “delete” to delete the chore, but a record of your deletion will be added to the Chore History so that your roommates can hold you accountable if need be. You may click through the pages of the Chore History to view past chores, when they were completed, and by whom.

The chores assigned to your other group’s members are also displayed on the page so that everyone can see who is response for which chores by which date.

To create a new chore, use the “New Chore” form at the bottom. Give your chore a name, a frequency deadline to be completed by, and hit submit. This will create the new chore and randomly assign it to a group member.

#Asking Questions
Using the navigation bar at the top, click “Choose”. You can ask everyone in your group a yes or no question by going to the bottom of the page, typing your question, and clicking “Ask Question”. At the top of this page, you will find questions that you have not answered yet. You will not be able to change your mind on these because the record of responses is anonymous, including questions you may have asked. In the middle of the page, you will find a record of responses to questions that you have answered.


#Switching Groups
Click on “All Groups” on the side bar. Click on the group that you want to switch to and view. The groups you will see in the sidebar are all of the groups that you are part of. The one you click on will be the group that you are currently viewing on the website. It will then redirect you to the home page.

#Leaving Groups
To leave a group, click the “Leave Current Group” button on the home page (which you can navigate to by clicking the SweetMates logo on the upper left-hand corner, or by clicking “Current Group” and the current group name), and click “Confirm” on the dialog box that appears. If you leave a group that contains only yourself, that group will be deleted and people will be unable to join it in the future.

#Changing Passwords
Click Change Password on the top right. Change to your desired password according to the form.

#Logging Out
If you have never used a website before, we are sorry. Click the “Log Out” button in the top right corner of the webpage. This will log you out. Duh.