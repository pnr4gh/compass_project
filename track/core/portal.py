import leetcode as lc
from track.models import Assignment, Assignment_Problems, Course, Course_Enrollement, Platform, Problem, ProblemTags, User_Handle, Solved_Problem, Profile, Batch, Institution, Department, Complexity, Tags
import requests, json
from track.utils import tags, get_cf_level
from django.http import JsonResponse
from datetime import date
from json import JSONDecodeError
from django.core.exceptions import MultipleObjectsReturned
from bs4 import BeautifulSoup

def get_leetcode_problems(request):
    url = "https://leetcode.com/graphql"
    data = {"query":"query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}","variables":{"categorySlug":"","skip":0,"limit":5000,"filters":{}}}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, data=json.dumps(data), headers=headers)
    response = r.json()
    platform = Platform.objects.get(name='Leet Code')
    for question in response['data']['problemsetQuestionList']['questions']:
        if not Problem.objects.filter(platform=platform,problem_slug=question['titleSlug']).exists():
            complexity = Complexity.objects.get(level=question['difficulty'])
            problem = Problem(problem_title=question['title'], platform=platform, problem_slug=question['titleSlug'], complexity= complexity)
            problem.save()

            for topic in question['topicTags']:
                
                tag = Tags.objects.get(tag=topic['name'])
                problem_tag = ProblemTags(problem=problem,topictags=tag)
                problem_tag.save()


def get_g4g_problems(request):
    
    platform = Platform.objects.get(name='Geeks for Geeks')
    
    for page in range(1, 255):  # Assuming you want to fetch pages 1 to 151
        response = requests.get(f"https://practiceapi.geeksforgeeks.org/api/vr/problems/?pageMode=explore&page={page}&sortBy=submissions")
        if response.status_code == 200:
            datas = response.json()
            
            for data in datas["results"]:
               
                
                if not Problem.objects.filter(platform=platform,problem_slug=data["problem_url"]).exists():
                    if data["difficulty"] == "":
                        complexity = Complexity.objects.get(level="Undefined")
                    else:
                        complexity = Complexity.objects.get(level=data["difficulty"])
                    
                    problem = Problem(problem_title=data["problem_name"], platform=platform, problem_slug=data["problem_url"], complexity= complexity)
                    problem.save()
                    
                    for topic in data["tags"]["topic_tags"]:
                        try:
                            
                            tag = Tags.objects.get(tag=topic)
                        except:
                            try:
                                key_tag = tags[topic]
                                tag = Tags.objects.get(tag=key_tag)
                            except KeyError:
                                tag = Tags.objects.create(tag=topic)
                                print(tag.tag)
                            
                        problem_tag = ProblemTags(problem=problem,topictags=tag)
                        problem_tag.save()
   
                    
def get_code_forces_problems(request):
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    platform = Platform.objects.get(name='Code Forces')
    i=1
    if response.status_code == 200:
        datas = response.json()  # Convert response to JSON
        for data in datas["result"]["problems"]:
               
            i+=1
            problem_url = "https://codeforces.com/problemset/problem/" + str(data['contestId']) + "/" + str(data['index'])
            if not Problem.objects.filter(platform=platform,problem_slug=problem_url).exists():
                
                if 'rating' not in data :
                    complexity = Complexity.objects.get(level="Undefined")
                else:
                    score = data['rating']
                    difficulty = get_cf_level(score)
                    complexity = Complexity.objects.get(level=difficulty)
                
                problem = Problem(problem_title=data["name"], platform=platform, problem_slug=problem_url, complexity= complexity)
                problem.save()
                
                for topic in data["tags"]:
                    try:
                        tag = Tags.objects.get(tag=topic)
                    except:
                        key_tag = tags[topic]
                        tag = Tags.objects.get(tag=key_tag)
                    problem_tag = ProblemTags(problem=problem,topictags=tag)
                    problem_tag.save()
        
        
    else:
        print(f"HTTP Error: {response.status_code}")


def update_leet(request,uh):
    
    data = dict()
    data["status"] = "not ok"
    
    try:
        
        token = request.POST.get('lc_csrf')
        leetcode_session = request.POST.get('lc_session')
        configuration = lc.Configuration()
        configuration.api_key["x-csrftoken"] = token
        configuration.api_key["csrftoken"] = token
        configuration.api_key["LEETCODE_SESSION"] = leetcode_session
        configuration.api_key["Referer"] = "https://leetcode.com"
        configuration.debug = False
       
        api_instance =lc.DefaultApi(lc.ApiClient(configuration))
        graphql_request = lc.GraphqlQuery(
        query="""
        {
            user {
            username
            isCurrentUserPremium
            }
        }
        """,
        variables=lc.GraphqlQueryVariables(),
        )
       
        response = api_instance.graphql_post(body=graphql_request)
        
        if response.data.user.username == uh:
            api_response=api_instance.api_problems_topic_get(topic="algorithms")
            #solved_questions=[]
                        
            for questions in api_response.stat_status_pairs:
                                           
                if questions.status=="ac":
                    #solved_questions.append(questions.stat.question__title)
                    
                    try:
                            
                        problem = Problem.objects.get(problem_title=questions.stat.question__title,platform__name="Leet Code")
                        
                        if not Solved_Problem.objects.filter(user=request.user,problem=problem).exists():
                            solved_problem = Solved_Problem(user=request.user,problem=problem)
                            solved_problem.save()
                    except:
                        pass
            data['message'] = "Updated your submissions"
            data["status"] = "ok"
            handle = User_Handle.objects.get(platform__name="Leet Code", user=request.user)
            handle.last_update = date.today()
            handle.save()
        else:
            data['message'] = "Wrong CSRF or Session ID, Check Cookies.."
    except Exception as e:
        data['message'] = e
    
    return JsonResponse(data)



def update_g4g(request,uh):
    
    data = dict()
    # URL and headers
    url = f"https://www.geeksforgeeks.org/user/{uh}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # HTTP request
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            data["status"] = "not ok"
            data['message'] = "Not able to fetch, Technical Issue!"
            return JsonResponse(data)

        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the solved problems section
        problems_section = soup.find('div', class_='solvedProblemContainer_head__ZyIn0')
        if not problems_section:
            data["status"] = "not ok"
            data['message'] = "Not yet started to solve in this portal"
            return JsonResponse(data)

        # Extract and print problem titles
        problems = problems_section.find_all('a')
        
        for problem in problems:
            try:
                title = problem.text.strip()
                problem = Problem.objects.get(platform__name="Geeks for Geeks",problem_title=title)
                if not Solved_Problem.objects.filter(user=request.user,problem=problem).exists():
                    solved_problem = Solved_Problem(user=request.user,problem=problem)
                    solved_problem.save()
                    
            except Exception as e:
                data['message'] = e
                
        data['message'] = "Updated your submissions"
        data["status"] = "ok"
        handle = User_Handle.objects.get(platform__name="Geeks for Geeks", user=request.user)
        handle.last_update = date.today()
        handle.save()
      

    except Exception as e:
        data['message'] = e
        print(e)
    return JsonResponse(data)


def update_code_forces(request,uh):
    
    data = dict()
    data["status"] = "not ok"
    
    try:
        # Fetch all solved problems for the user
        user_url = f"https://codeforces.com/api/user.status?handle={uh}"
        problemset_url = "https://codeforces.com/api/problemset.problems"
            # Fetch user's submissions with exception handling
        user_response = requests.get(user_url, timeout=10)
        user_response.raise_for_status()  # Raise an error for bad status codes
        user_data = user_response.json()
          # Check if user data is valid
        if user_data.get('status') != 'OK' or not user_data.get('result'):
            
            data["status"] = "not ok"
            data['message'] = "Not yet started to solve in this portal"
            return JsonResponse(data)
        
        for submission in user_data['result']:
            
            try:
                if submission.get('verdict') == 'OK':
                    contest_id = submission['problem']['contestId']
                    index = submission['problem']['index']
                    name = submission['problem']['name']
                    problem_url = "https://codeforces.com/problemset/problem/" + str(contest_id) + "/" + str(index)
                    print(contest_id,index,name)
                    try:
                        
                        problem = Problem.objects.get(platform__name="Code Forces",problem_title=name)
                    except MultipleObjectsReturned:
                        try:
                            
                            problem = Problem.objects.get(platform__name="Code Forces",problem_title=name,problem_slug=problem_url)
                        except :
                            
                            problem = Problem.objects.filter(platform__name="Code Forces",problem_title=name)[0]
                    except:
                        pass
                        
                    if not Solved_Problem.objects.filter(user=request.user,problem=problem).exists():
                            solved_problem = Solved_Problem(user=request.user,problem=problem)
                            solved_problem.save()
                    
            except (KeyError, TypeError):
                data['message'] = e
                
        data['message'] = "Updated your submissions"
        data["status"] = "ok"
        handle = User_Handle.objects.get(platform__name="Code Forces", user=request.user)
        handle.last_update = date.today()
        handle.save()
      

    except Exception as e:
        data['message'] = e
        print(e)
    return JsonResponse(data)

