from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Batch(models.Model):
    start_year = models.IntegerField()
    end_year = models.IntegerField()

    def __str__(self):
        return str(self.end_year)

class Department(models.Model):
    short_name = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.short_name

class Institution(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Platform(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    @property
    def get_total_count(self):
        return Problem.objects.filter(platform=self).count()

class Complexity(models.Model):
    level = models.CharField(max_length=55)
    
    def __str__(self):
        return self.level
        
class Problem(models.Model):
    problem_title = models.CharField(max_length=255)
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE)
    complexity = models.ForeignKey(Complexity,on_delete=models.CASCADE, null=True)
    problem_slug = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.problem_title

class Tags(models.Model):
    tag = models.CharField(max_length=55)
    
    def __str__(self):
        return self.tag
    
class ProblemType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Problem Type")     

    def __str__(self):
        return self.name  

class Contest(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    dmoj_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name 
    
class ProblemStats(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE, related_name='problem_stats')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='problem_stats', null = True, blank=True)
    problem_type = models.ForeignKey(ProblemType, on_delete=models.CASCADE, related_name="problem_stats")
    solved_count = models.PositiveIntegerField(default=0, verbose_name="Problems Solved")
    attempted_count = models.PositiveIntegerField(default=0, verbose_name="Problems Attempted")

    class Meta:
        unique_together = ("user", "problem_type", "contest")

    @property
    def integrity_index(self):
        return round(self.solved_count / self.attempted_count, 2) if self.attempted_count > 0 else 0.0
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    def __str__(self):
        contest_info = f" | Contest: {self.contest.name}" if self.contest else ""
        return f"{self.user.username} | {self.problem_type.name}: Solved {self.solved_count}, Attempted {self.attempted_count}, Integrity Index: {self.integrity_index}{contest_info}"


class ProblemTags(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    topictags = models.ForeignKey(Tags,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.problem.problem_title + "(" + self.topictags.tag + ")"

class Profile(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=10)
    batch  = models.ForeignKey(Batch, on_delete=models.CASCADE)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    institute = models.ForeignKey(Institution,on_delete=models.CASCADE)
    github_link = models.CharField(max_length=255,null=True)
    linkedin_link = models.CharField(max_length=255,null=True)
    discussion_score = models.IntegerField(default=0)
    no_of_discussion = models.IntegerField(default=0)
    discussion_index = models.FloatField(default=0.0)
    integrity_index = models.FloatField(default=1.0)
    

    def __str__(self):
        return self.user.username
    
    @property
    def get_easy_count(self):
        easy_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Easy").count()
        return easy_count
    
    @property
    def get_medium_count(self):
        medium_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Medium").count()
        return medium_count

    @property
    def get_hard_count(self):
        hard_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Hard").count()
        return hard_count

    @property
    def get_count(self):
        count = Solved_Problem.objects.filter(user=self.user).count()
        return count

    @property
    def get_lc_easy_count(self):
        easy_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Easy",problem__platform__name="Leet Code").count()
        return easy_count
    
    @property
    def get_lc_medium_count(self):
        medium_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Medium",problem__platform__name="Leet Code").count()
        return medium_count

    @property
    def get_lc_hard_count(self):
        hard_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Hard",problem__platform__name="Leet Code").count()
        return hard_count

    @property
    def get_lc_count(self):
        count = Solved_Problem.objects.filter(user=self.user,problem__platform__name="Leet Code").count()
        return count
    
    
    @property
    def get_g4g_easy_count(self):
        easy_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level__in=("Easy","Basic","School"),problem__platform__name="Geeks for Geeks").count()
        return easy_count
    
    @property
    def get_g4g_medium_count(self):
        medium_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Medium",problem__platform__name="Geeks for Geeks").count()
        return medium_count

    @property
    def get_g4g_hard_count(self):
        hard_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Hard",problem__platform__name="Geeks for Geeks").count()
        return hard_count

    @property
    def get_g4g_count(self):
        count = Solved_Problem.objects.filter(user=self.user,problem__platform__name="Geeks for Geeks").count()
        return count
    
    @property
    def get_cf_easy_count(self):
        easy_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Easy",problem__platform__name="Code Forces").count()
        return easy_count
    
    @property
    def get_cf_medium_count(self):
        medium_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Medium",problem__platform__name="Code Forces").count()
        return medium_count

    @property
    def get_cf_hard_count(self):
        hard_count = Solved_Problem.objects.filter(user=self.user,problem__complexity__level="Hard",problem__platform__name="Code Forces").count()
        return hard_count

    @property
    def get_cf_count(self):
        count = Solved_Problem.objects.filter(user=self.user,problem__platform__name="Code Forces").count()
        return count
    
    @property
    def get_leetcode_username(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Leet Code")
        return handle.user_handle

    @property
    def get_leetcode_last_update(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Leet Code")
        return handle.last_update
    
    @property
    def get_g4g_username(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Geeks for Geeks")
        return handle.user_handle

    @property
    def get_g4g_last_update(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Geeks for Geeks")
        return handle.last_update
    
    @property
    def get_code_forces_username(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Code Forces")
        return handle.user_handle

    @property
    def get_code_forces_last_update(self):
        handle = User_Handle.objects.get(user=self.user, platform__name="Code Forces")
        return handle.last_update

class Course(models.Model):
    
    course_title = models.CharField(max_length=255,null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created_by = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.course_title
    @property
    def get_enrolled_count(self):
        count = Course_Enrollement.objects.filter(course=self).count()
        return count
    @property
    def get_assignment_count(self):
        count = Assignment.objects.filter(course=self).count()
        return count
    @property
    def get_problem_count(self):
        count = Assignment_Problems.objects.filter(assignment__course=self).count()
        return count

   
class Course_Enrollement(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " " + self.course.course_title
class Course_Coordinator(models.Model):
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " " + self.course.course_title
   
class User_Handle(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete = models.CASCADE)
    user_handle = models.CharField(max_length=255)
    last_update = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.user_handle


class Solved_Problem(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    date = models.DateField(null=True)

    def get_tags(self):
        # Get related ProblemTags for this Solved_Problem
        problem_tags = ProblemTags.objects.filter(problem=self.problem)
        return [tag.topictags.tag for tag in problem_tags]

class Assignment(models.Model):
    name = models.CharField(max_length=55)
    course = models.ForeignKey(Course,on_delete=models.CASCADE,null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
    
    @property
    def problem_stats(self):
        # Get all problems in the assignment
        problems = self.assignment_problems_set.values_list('problem', flat=True)
        
        # Count problems by complexity
        easy_problems = Problem.objects.filter(id__in=problems, complexity__level="Easy").count()
        medium_problems = Problem.objects.filter(id__in=problems, complexity__level="Medium").count()
        hard_problems = Problem.objects.filter(id__in=problems, complexity__level="Hard").count()

        return (len(problems), easy_problems, medium_problems, hard_problems)


    @property
    def users_stats(self):
        # Get all problems in the assignment
        problems = self.assignment_problems_set.values_list('problem', flat=True)
        # Get users enrolled in the course associated with this assignment
        enrolled_users = User.objects.filter(course_enrollement__course=self.course)
        # Get users who have solved all problems in the assignment
        users_solved_all = enrolled_users.annotate(
            solved_count=models.Count('solved_problem', filter=models.Q(solved_problem__problem__in=problems))
        ).filter(solved_count=len(problems))

        users_solved_half = enrolled_users.annotate(
            solved_count=models.Count('solved_problem', filter=models.Q(solved_problem__problem__in=problems))
        ).filter(solved_count__gte=len(problems)//2).exclude(solved_count=len(problems))

        users_solved_below = enrolled_users.annotate(
            solved_count=models.Count('solved_problem', filter=models.Q(solved_problem__problem__in=problems))
        ).filter(solved_count__lt=len(problems)//2)


        return (enrolled_users.count(),users_solved_all.count(),users_solved_half.count(),users_solved_below.count())

    @property
    def all_problems(self):
        return self.assignment_problems_set.select_related('problem').all()

class Assignment_Problems(models.Model):
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem,on_delete=models.CASCADE)

    def __str__(self):
        return self.assignment.name + " " + self.problem.problem_title
    
    @property
    def get_solved_count(self):
        enrolled_users = User.objects.filter(course_enrollement__course=self.assignment.course)
        count = Solved_Problem.objects.filter(problem=self.problem,user__in=enrolled_users).count()

        return enrolled_users.count(), count

class Discussion(models.Model):
        discussion_name = models.CharField(max_length=55)
        course = models.ForeignKey(Course,on_delete=models.CASCADE)

        def __str__(self):
            return self.discussion_name

    #Discussion model
class discussion_detail(models.Model):
        discussion = models.ForeignKey(Discussion,on_delete=models.CASCADE)
        Not_performed = 0
        Good = 1
        Proficient = 2
        
        INTEGRITY_CHOICES = [
            (Not_performed, 'Not Performed'),
            (Good, 'Good'),
            (Proficient, 'Excellent'),
        ]

        Need_improvement = 0
        Manageable = 1
        Fluent = 2

        COMMUNICATION_CHOICES = [
            (Need_improvement, 'Needs Improvement'),
            (Manageable, 'Manageable'),
            (Fluent, 'Fluent'),
        ]
        
        
        user = models.ForeignKey(User,on_delete=models.CASCADE)
        problem= models.ForeignKey(Problem,on_delete=models.CASCADE)
        integrity_score = models.IntegerField(choices=INTEGRITY_CHOICES, default=Not_performed)
        communication_score = models.IntegerField(choices=COMMUNICATION_CHOICES, default=Need_improvement)
        comments = models.TextField()
        date = models.DateField(auto_now_add=True)

        def __str__(self):
            return self.discussion.discussion_name + " " + self.user.username

    





    
