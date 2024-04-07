# Functionality
Simple tracker is a simple time tracking utility. It works by autoassigning times to projects you activate.
The system needs to know who you are; you can add or delete users. Users have properties of:
Firstname
MiddleInitial
Lastname
EMail
You can add, edit or delete users with a simple command:
sitr user add —firstname Tim —lastname Walter —email tech@smartlogics.net
or
sitr user delete —email tech@smartlogics.net
or
sitr user update —email tech@smartlogics.net —middleinitial “K."
Notice that email is being used as the key and must be provided. All other arguments are optional.
sitr users
… so user in plural, gives a simple list of all usrs with all properties, while
sitr user select —email tech@smartlogics.net
selects the user with the E-Mail Adress tech@smartlogics.net as the user actually working with the system.
 
To work with sitr, simply set the user to a valid user at any time. The user selected will remain valid until you pick a different user:
sitr user select —user tech@smartlogics.net
Selects the User  with the e-Mail Adress tech@smartlogics.net as the user who is actually tracking time.
The process is as simple as it gets:
- The first step is to start your day, which is done by a simple command:
sitr —start
- Once your day has started, time is being tracker for a workday. A workday starts on the date when you started.
- Time is accounted to a Pseudo Project called “Unassigned”.
- You assign some Project you are working on, e.g. “Write Report for Management” by using
sitr activate —project “Write Report for Management"
If you are starting a new project, you create one by 
sitr create —project “Write Report for Management” —activate
The —activate is optional; if given, the project is assigned immediately after creation.
- sitr give you a status message:
“Started working on “Write Report for Management” at 08:37. Enjoy!"
- You do your work, hopefully enjoying it ;-)
- Let’s say you have a break, for lunch, or because your spouse calls. You can do so by
sitr break
You get a status message, saying
“You have suspended working on “Write Report for Management" for a break. Enjoy!"
You may add a message, such as “Call from Spouse”, with the —message parameter:
sitr break —message “Call from spouse"
- Once you are ready to continue working, simply perform
sitr continue
You also get a status message, stating “Resuming work on “Write Report for Management”, break time was 31m”.
The time inbetween is accounted to a “Breaks” account, which is different from the “Unassigned” account, because it is a willful break. Once you continue, time is being tracked on the project that was interrupted when you used “sitr pause”, i.e. “Write Report for Management” in this case.
- Once you are done with “Write Report for Management”, just type
sitr done
You can also immediately switch to a new project
sitr done —project “Finish CS50 project"
or simply activate a new program, which finishes the current project automatically, i.e.
sitr activate —project “Finish CS50 project"
In this case, sitr will ask you whether you
"You are currently working on “Write Report for Management”. Stop this and stark working on “Finish CS50 project”? Yn: "
Either way, you always get a short status message once you stop working on a project, which is:
“Working on “Write Report for Management” suspended. Start: 08:37, End: 11:42, Time Tracked: 03h05m"
You can suppress the questioning by using the —noconf parameter, i.e. typing
sitr activate —project “Finish CS50 project” —noconf
will automatically stop any project currently being worked on and start “Finish CS50 project”. The status message that work on “Write Report for Management” has been suspended is displayed, and you also get the status message that you’ve begun working on “Finish CS50 project”.
That’s it - almost. Perhaps you know you have already created a project for writing an arcticle on some new technology, but you have forgotten what name you actually assined to it. You can list all active projects with the following command:
sitr projects
If you like the list to be sorted alphabetically instead of listing the projects in the order of the most current trackings, use
sitr projects —alphabet
Speaking about projects. We have seen that activating a project that is not created will create a project automatically for you. You will, howver, get a prompt that looks like this:
Project “My new project” does not exist. Do you want to create it? Yn: 
If you confirm, the project will be created, and will then be activated, with the corresponding activation prompt being output aswell.
You can also add project manually, using the following command:
sitr project add —name “My new project"
Projects that you create will be in the state “active”, that is you can activate them to track time working on them. Once there is a day where you stop working on the project and have done your last booking, you can archive the project:
sitr project archive —name “My old project"
The project is then archived, which only means it is not listed anymore in the overview you get with sitr projects, and it also cannot be activated for tracking anymore. Use
sitr projects —all 
to list all projects, inlcuding the ones archived. The —all argument can be combined with the —alphabet argument.
If for some reason you need to get the project back from the archive into the active project state, you can unarchive it by using
sitr project archive —name “My old Project” —unarchive
The will bring “My old Project” back into the list of active projects and will allow time trackings on it.
So, coming back to actual work from the little excursion of managing projects:
You have to close your workday at some point. You will not be able to start a new workday unless the old workday has been closed. While begin and end of your workday will usually be on the same date, they do not need to. The hours, however, are always accounted to the workday when you started your work. Normally, you would end your workday by typing
sitr end
Tracking is then suspended, and the day is closed. A project open at this point will be closed, with the status message you already know. The same applies for an eventual break; the break would be ended.
You get a quick summary of your working day, something like:
sitr has recorded the following activities today:
08h15m                   Day started08h23m                   Started working on “Write Report for Management” 10h01m                   Break started10h14m                   Work continued11h23m                    Suspended working on “Write Report for Management”, 02h47m total time.11h25m                   Started working on “Finish CS50 project”13h00m                   Break started, “Meeting new client for lunch”14h10m                   Work continued16h00m                   Suspended working on “Finish CS50 project”, 03h15m total time.16h00m                   Day called.Time Tracking record:“Write Report for Management”: 02:47:00“Finsih CS50 project”: 03:00:00Thanks for using sitr.
Pretty simple, isn’t it?
Now, if you would like to get some data out, you are free to connect to the SQL database model, where you can basically query all the data you need the way you need. If you have a special kind of query you like to run, I have implemented a feature that converts any query in the database to CSV. To make things easy and demonstrate the power and flexibility of this, I have included “Project Times Net Including Breaks”, and “Project Times Net including Breaks rounded”. You can add any query to the database yourself and export it to CSV from the command line, by using the 
sitr export
Command, which takes up to three arguments:
—report “name of report”                   Put the name of your SQL Query in quotes.—output filename                               The file where you want the CSV output to be written to—append                                           Optional, will append data to the file if it already exists.
Let’s say you want Timesheets per month.Then you can create the following script that adds timesheet records for the day by:export DATESTAMP=$(date +%y%m)sitr report —report “Project Times Net Including Breaks” —output "~/Documents/Timesheets/Timesheet${DATESTAMP}.csv" —append
Now, notice that in the example given the actual SQL Report will limit the timespan of the Sheet data, and is fully responsible for the output, be that that it actually outputs one record for each time interval where you worked on something, or be it that it outputs a summary of all the time invested for a particular project. That’s all up to you at the end of the day. I have created it the way that you get a list of all time windows for the day, that is if you have worked multiple times on a certain project, you get multiple time sheet records for it.That’s it.There are a few things to be told about the technology….
# Architecture
I want the application to use the following building blocks:
All functionality is behind a pubslihed Web API. The Web API is built using Tiangolo’s FastAPI.
All Data is modelled using SQLModel, another Package by Tiangolo. This way, we have all the entities we need modeled in a way that business and data access tier objects are derived from the same base (SQLModel Class).
To make things solid, we use the Domain Driven Design Pattern, together with a unit of work and Repo Pattern, to implement the whole access to the database.
As SQLModel is based on SQLAlchemy, we should have no worries using SQLite3 as the underlying database persistence layer, but also use SQL Server or Cosmos DB/Postgres as a data layer when operating the system in the cloud.
We need a few classes and objects:
Users - they are defined pretty well in the system description. The E-Mail Adress is used as the primary key aswell. Additionally, we keep track when the user has been set as the active user for the last time.
Projects - Internal Id is the primary key, on top a project has a name, a state whether is has been archived, a date when archiving was done if it had been archived, a timestamp which is set whenever some booking has occured so we can use that to easily sort without joing, the number of trackings ever done on the project, a date when the project has been created, the userid of the user who has created the project. 
Trackings
A tracking record is written for each event. Events are:
a) Working day (for user) has started or ended
b) Working on a Project was started, or was suspended.
c) A break begun or has ended.
A tracking contains:
Unique id, Date and Time, User, Project Id (null of a working day start/end event, or a break start/end event), Action (“Working day”, “Break”, “Working on project”, Activity (Terms “Starts” or “Ends”),Message (System created, perhaps user created for a break if message parameter is given)
The active user is maintained by the client, it will be passed through the function/Method calls, or later effectively the API calls. So the client needs to maintain the state which user is using the system, but that can, in the case for example of the command line tool calling the API, stored in a simple configuration file or environment variable “SITRUSER” which is initialized on start. if both are not given, the system will ask for an eMail Adress and store it in the configuration file in the home directory in the file .sitrconfig.
While the command line is a nice way to interact with the system for its simplicity, the system is controlled via the API, and the reports are controlled via the database views. These views are not part of the SQLModel, but rather accessed in a “direct” database connection, read “low level” or “directly” into a dictionary and output as css-file, which is created and outputted as a CSV File via the Webserver.
Most users will be able to run the tool locally, i.e. the webserver will run local on some port, and the api will use the local url. the URL is actually the second parameter in the config file .sitrconfig, that points to the server being used. If the tool is used locally and no server is given, a uvicorn server is started with each command line command, then executed, and taken down after the command has finished. while this may take some time, it keeps things simple wich not having to launch a daemon or do any other fancy configuration and background tasks. if a user wants this complexity and can handle it, he or she can always start a daemon and configute it in the config-file, so we maintain flexibility here.
