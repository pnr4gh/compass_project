
from django.contrib.auth.decorators import  login_required,csrf_exempt
from track.models import Problem, User_Handle, Solved_Problem
from django.http import JsonResponse
import leetcode as lc
from datetime import date





@login_required
@csrf_exempt
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

                        problem = Problem.objects.get(problem_title=questions.stat.question__title)
                        if not Solved_Problem.objects.filter(user=request.user,problem=problem).exists():
                            solved_problem = Solved_Problem(user=request.user,problem=problem)
                            solved_problem.save()
                    except:
                        pass
                data['message'] = "Updated your submissions"
                data["status"] = "ok"
                handle = User_Handle.objects.get(platform__name="Leet Code", user=request.user)
                print(handle)
                handle.last_update = date.today()
                handle.save()
        else:
            data['message'] = "Wrong CSRF or Session ID, Check Cookies.."
    except Exception as e:
        data['message'] = e

        
        
    return JsonResponse(data)