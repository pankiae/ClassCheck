this is ClassCheck written in the django full stack application. Currently its just the setup need to work on the all functionalities.

The key point of this project are
1. Role based access control.
    - There will super user, teachers and students.
    - Super user can create teachers and students. Super user have all the access.
    - Teachers can create classes and assign students to classes.
    - Students can join classes.

2. Teacher onboarding process
    - After creating the super user, Super user will invite the teachers only.
    - Teachers will accept the invite and create there own account. And after creating the account, techer can create the class proposal. Class proposal include the details like: subject, timing and days per week for the class.
    And the proposal will be sent to the super user. Super user will accept the proposal and create the class.
    - After the class is created, teacher can sent the  invitation to the students.
    - Students will accept the invite and join the classes.
    - While techer took the class, teacher will mark the attendance of the students every day as per the class schedule. Present or Not. After the class is over, teacher cannot change the marked attendance of the students.
    - after submitting the attendnce teacher's attendance will be marked for class. Teacher can submit the attendance of the students for the class last 15 mins of the class. Before that time teacher cannot submit the attendance. And if teacher is unable to submit the attendance in last 15 mins of the class, then it will assume that the teacher were not present in the class or not attended the class.

3. Student onboarding process
    - Student will get the invitation from the teacher over the email and accept the invite or reject the invite.
    - After join the classes.
    - Student can view the class schedule and see if the teacher is marked the attendance or not. But student can't mark the attendance on their own, only techer can mark the attendance.


Focus on the User Interface and User Experience.
1. Super user interface
    - Super user can see all the details of teachers and students.
    - Super user can create classes, assign teachers to classes and assign students to classes.
    - Super user can view the class schedule and see if the teacher attendence and student attendance too.

2. teacher interface
    - Teacher will get the dashboard and see the classes schedule for that day.
    - their may be multiple classes in a day. So for the upcoming class will be sort on the first. After selecting the class, teacher can see the class details. 
    for example:
    Student Roll No. | Name | Class A (Class Name) | Class B (Class Name) | Class C (Class Name) | Class D (Class Name)
    1. | Jordan | Present | Absent | Present | Absent | Present
    2. | Alex | Present | Absent | Present | Absent | Present
    
    - in case the previous class was not done then the whole column will be empty or blurred grey  color.
    
    - Teacher can see the whole classes schedule for that day. Also the other lecture details too. Details like if the previous lecture was marked as present or not. If yes then the student is present or not in that lecture. Current class teacher can only see the whole classes schedule for that day but cannot change that only the owner of the class teacher can change that and only during the class period time. After that the session will be closed and teacher cannot change the attendance.
    - By doing this teachers will see if the students were present in the previous class of not. If not then they ask the questions where they were. Ask it can count as flying from classes.

3. Student interface
    - Student will get the dashboard and see the classes schedule for that day.
    - their may be multiple classes in a day. So for the upcoming class will be sort on the first. After selecting the class, student can see the class details. 
    for example:
    Student Roll No. | Name | Class A (Class Name) | Class B (Class Name) | Class C (Class Name) | Class D (Class Name)
    1. | Jordan | Present | Absent | Present | Absent | Present
    2. | Alex | Present | Absent | Present | Absent | Present
    
    - in case the previous class was not done then the whole column will be empty or blurred grey  color.
    
    - Student can see the whole classes schedule for that day. Also the other lecture details too. Details like if the previous lecture was marked as present or not. If yes then the student is present or not in that lecture.


session [2025-2026]
    department-1 [Admin will provide the department name]
        class-1 [admin will provide the class name]
            subject-1 [admin will provide the subject name]
            subject-2 [admin will provide the subject name]
            subject-3 [admin will provide the subject name]
        class-2 [admin will provide the class name]
            subject-1 [admin will provide the subject name]
            subject-2 [admin will provide the subject name]
            subject-3 [admin will provide the subject name]
    department-2 [Admin will provide the department name]
        class-1 [admin will provide the class name]
            subject-1 [admin will provide the subject name]
            subject-2 [admin will provide the subject name]
            subject-3 [admin will provide the subject name]
        class-2 [admin will provide the class name]
            subject-1 [admin will provide the subject name]
            subject-2 [admin will provide the subject name]
            subject-3 [admin will provide the subject name]
    
            
