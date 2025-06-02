from django.utils import timezone
from rest_framework import serializers
from .models import ProblemStats, Contest, ProblemType
from django.contrib.auth.models import User

class ProblemTypeStatsSerializer(serializers.Serializer):
    solved = serializers.IntegerField()
    attempted = serializers.IntegerField()
    integrity_index = serializers.FloatField()

class ParticipantSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    problem_types = serializers.DictField(
        child=ProblemTypeStatsSerializer()
    )

class ContestResultSerializer(serializers.Serializer):
    contest_name = serializers.CharField(max_length=255)
    participants = serializers.ListField(child=ParticipantSerializer())

    def create(self, validated_data):
        contest, _ = Contest.objects.get_or_create(
            name=validated_data['contest_name'],
            defaults={"start_time": timezone.now(), "end_time": timezone.now()}
        )

        for participant_data in validated_data['participants']:
            user, _ = User.objects.get_or_create(username=participant_data['name'])

            for problem_type_name, stats in participant_data['problem_types'].items():
                problem_type, _ = ProblemType.objects.get_or_create(name=problem_type_name)

                stats_obj, created = ProblemStats.objects.get_or_create(
                    user=user, contest=contest, problem_type=problem_type,
                    defaults={"solved_count": stats["solved"], "attempted_count": stats["attempted"]}
                )

                if not created:
                    stats_obj.solved_count += stats["solved"]
                    stats_obj.attempted_count += stats["attempted"]
                    stats_obj.save()

        return validated_data


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ['name', 'start_time', 'end_time','dmoj_key']  # Adjust fields based on your model